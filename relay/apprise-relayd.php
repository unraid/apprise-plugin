#!/usr/bin/env php
<?php
// SPDX-License-Identifier: BSD-2-Clause

$socketPath = getenv("APPRISE_RELAY_SOCKET") ?: "/var/run/apprise/apprise.sock";
$pidFile = getenv("APPRISE_RELAY_PID") ?: "/var/run/apprise/apprise-relayd.pid";
$agentScript = getenv("APPRISE_RELAY_AGENT") ?: "/boot/config/plugins/dynamix/notifications/agents/Apprise.sh";
$requestTimeout = (int) (getenv("APPRISE_RELAY_TIMEOUT") ?: "30");
$maxBodyBytes = 16384;
$running = true;

function relay_log(string $message, int $priority = LOG_INFO): void
{
    if (function_exists("openlog")) {
        openlog("apprise-relayd", LOG_PID, LOG_DAEMON);
        syslog($priority, $message);
        closelog();
    }
    fwrite(STDERR, "[apprise-relayd] {$message}\n");
}

function send_json($conn, int $status, array $payload): void
{
    $reason = [
        200 => "OK",
        202 => "Accepted",
        400 => "Bad Request",
        404 => "Not Found",
        405 => "Method Not Allowed",
        413 => "Payload Too Large",
        500 => "Internal Server Error",
        503 => "Service Unavailable",
        504 => "Gateway Timeout",
    ][$status] ?? "OK";

    $body = json_encode($payload, JSON_UNESCAPED_SLASHES) . "\n";
    fwrite(
        $conn,
        "HTTP/1.1 {$status} {$reason}\r\n" .
        "Content-Type: application/json\r\n" .
        "Connection: close\r\n" .
        "Content-Length: " . strlen($body) . "\r\n" .
        "\r\n" .
        $body
    );
}

function read_http_request($conn, int $maxBodyBytes): array
{
    stream_set_timeout($conn, 5);
    $raw = "";
    while (strpos($raw, "\r\n\r\n") === false && strpos($raw, "\n\n") === false && strlen($raw) <= 8192) {
        $chunk = fread($conn, 1024);
        if ($chunk === false || $chunk === "") {
            break;
        }
        $raw .= $chunk;
    }

    $separator = strpos($raw, "\r\n\r\n") !== false ? "\r\n\r\n" : "\n\n";
    $parts = explode($separator, $raw, 2);
    if (count($parts) !== 2) {
        return ["error" => "Malformed HTTP request"];
    }

    [$headerText, $body] = $parts;
    $lines = preg_split("/\r?\n/", $headerText);
    $requestLine = trim(array_shift($lines) ?? "");
    $requestParts = preg_split("/\s+/", $requestLine, 3);
    if (count($requestParts) < 2) {
        return ["error" => "Malformed HTTP request line"];
    }

    $headers = [];
    foreach ($lines as $line) {
        if (strpos($line, ":") === false) {
            continue;
        }
        [$name, $value] = explode(":", $line, 2);
        $headers[strtolower(trim($name))] = trim($value);
    }

    $contentLength = isset($headers["content-length"]) ? (int) $headers["content-length"] : 0;
    if ($contentLength > $maxBodyBytes) {
        return ["error" => "Request body is too large", "status" => 413];
    }

    while (strlen($body) < $contentLength) {
        $chunk = fread($conn, $contentLength - strlen($body));
        if ($chunk === false || $chunk === "") {
            break;
        }
        $body .= $chunk;
    }

    return [
        "method" => strtoupper($requestParts[0]),
        "target" => $requestParts[1],
        "headers" => $headers,
        "body" => substr($body, 0, $contentLength),
    ];
}

function scalar_string($value): string
{
    if (is_bool($value)) {
        return $value ? "true" : "false";
    }
    if (is_scalar($value)) {
        return (string) $value;
    }
    return "";
}

function clean_text($value, int $maxLength, bool $singleLine = false): string
{
    $text = scalar_string($value);
    $text = str_replace("\0", "", $text);
    $text = preg_replace("/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/", "", $text) ?? "";
    if ($singleLine) {
        $text = preg_replace("/[\r\n]+/", " ", $text) ?? "";
    }
    return trim(substr($text, 0, $maxLength));
}

function normalize_tags($value): string
{
    if (is_array($value)) {
        $value = implode(",", array_map("scalar_string", $value));
    }
    $tags = clean_text($value, 512, true);
    $tags = preg_replace("/\s+/", "", $tags) ?? "";
    if ($tags === "") {
        return "";
    }
    if (!preg_match("/^[A-Za-z0-9_.:-]+(?:,[A-Za-z0-9_.:-]+)*$/", $tags)) {
        throw new InvalidArgumentException("Tags must be comma-separated names containing only letters, numbers, dots, underscores, colons, or hyphens");
    }
    return $tags;
}

function request_payload(array $request): array
{
    $body = $request["body"] ?? "";
    $contentType = strtolower($request["headers"]["content-type"] ?? "");
    if (strpos($contentType, "application/json") !== false || strpos(ltrim($body), "{") === 0) {
        $payload = json_decode($body, true);
        if (!is_array($payload)) {
            throw new InvalidArgumentException("Request body must be valid JSON");
        }
        return $payload;
    }

    $payload = [];
    parse_str($body, $payload);
    return $payload;
}

function run_agent(string $agentScript, array $payload, int $timeout): array
{
    if (!is_file($agentScript)) {
        return [503, ["ok" => false, "error" => "Apprise notification agent is not configured or is disabled"]];
    }

    $title = clean_text($payload["title"] ?? $payload["subject"] ?? "Container notification", 512, true);
    $message = clean_text($payload["body"] ?? $payload["message"] ?? $payload["description"] ?? "", 8192);
    $importance = strtolower(clean_text($payload["importance"] ?? $payload["type"] ?? "normal", 32, true));
    $importanceMap = [
        "info" => "normal",
        "normal" => "normal",
        "warning" => "warning",
        "warn" => "warning",
        "alert" => "alert",
        "failure" => "alert",
        "critical" => "alert",
    ];
    if (!isset($importanceMap[$importance])) {
        throw new InvalidArgumentException("Importance must be one of normal, warning, or alert");
    }
    $importance = $importanceMap[$importance];
    $tags = normalize_tags($payload["tags"] ?? $payload["tag"] ?? "");

    if ($message === "" && $title === "") {
        throw new InvalidArgumentException("Notification title or body is required");
    }

    $env = [
        "PATH" => "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "SUBJECT" => $title,
        "DESCRIPTION" => $message,
        "IMPORTANCE" => $importance,
        "APPRISE_RELAY_TITLE" => $title,
        "APPRISE_RELAY_MESSAGE" => $message,
    ];
    if ($tags !== "") {
        $env["APPRISE_RELAY_TAGS"] = $tags;
    }

    $descriptorSpec = [
        0 => ["pipe", "r"],
        1 => ["pipe", "w"],
        2 => ["pipe", "w"],
    ];

    $process = proc_open("/bin/bash " . escapeshellarg($agentScript), $descriptorSpec, $pipes, "/", $env);
    if (!is_resource($process)) {
        return [500, ["ok" => false, "error" => "Unable to start Apprise notification agent"]];
    }

    fclose($pipes[0]);
    stream_set_blocking($pipes[1], false);
    stream_set_blocking($pipes[2], false);
    $stdout = "";
    $stderr = "";
    $deadline = time() + max(1, $timeout);

    $exitCode = 1;
    do {
        $stdout .= stream_get_contents($pipes[1]);
        $stderr .= stream_get_contents($pipes[2]);
        $status = proc_get_status($process);
        if (!$status["running"]) {
            $exitCode = (int) $status["exitcode"];
            break;
        }
        if (time() >= $deadline) {
            proc_terminate($process);
            foreach ($pipes as $pipe) {
                if (is_resource($pipe)) {
                    fclose($pipe);
                }
            }
            proc_close($process);
            return [504, ["ok" => false, "error" => "Apprise notification timed out"]];
        }
        usleep(100000);
    } while (true);

    $stdout .= stream_get_contents($pipes[1]);
    $stderr .= stream_get_contents($pipes[2]);
    fclose($pipes[1]);
    fclose($pipes[2]);
    proc_close($process);

    if ($exitCode !== 0) {
        relay_log("Apprise notification agent exited with status {$exitCode}", LOG_ERR);
        return [500, ["ok" => false, "error" => "Apprise notification failed"]];
    }

    return [202, ["ok" => true]];
}

function handle_connection($conn, string $agentScript, int $timeout, int $maxBodyBytes): void
{
    $request = read_http_request($conn, $maxBodyBytes);
    if (isset($request["error"])) {
        send_json($conn, $request["status"] ?? 400, ["ok" => false, "error" => $request["error"]]);
        return;
    }

    $path = parse_url($request["target"], PHP_URL_PATH) ?: "/";
    if ($request["method"] === "GET" && $path === "/health") {
        send_json($conn, 200, ["ok" => true, "configured" => is_file($agentScript)]);
        return;
    }

    if ($path !== "/notify") {
        send_json($conn, 404, ["ok" => false, "error" => "Unknown endpoint"]);
        return;
    }
    if ($request["method"] !== "POST") {
        send_json($conn, 405, ["ok" => false, "error" => "Use POST /notify"]);
        return;
    }

    try {
        $payload = request_payload($request);
        [$status, $response] = run_agent($agentScript, $payload, $timeout);
        if ($status >= 500) {
            relay_log($response["error"] ?? "Notification failed", LOG_ERR);
        }
        send_json($conn, $status, $response);
    } catch (InvalidArgumentException $error) {
        send_json($conn, 400, ["ok" => false, "error" => $error->getMessage()]);
    }
}

if (function_exists("pcntl_async_signals")) {
    pcntl_async_signals(true);
    pcntl_signal(SIGTERM, function () use (&$running): void {
        $running = false;
    });
    pcntl_signal(SIGINT, function () use (&$running): void {
        $running = false;
    });
}

$socketDir = dirname($socketPath);
if (!is_dir($socketDir) && !mkdir($socketDir, 0755, true) && !is_dir($socketDir)) {
    relay_log("Unable to create {$socketDir}", LOG_ERR);
    exit(1);
}

if (file_exists($socketPath)) {
    unlink($socketPath);
}

$server = stream_socket_server("unix://{$socketPath}", $errno, $errstr);
if (!$server) {
    relay_log("Unable to listen on {$socketPath}: {$errstr} ({$errno})", LOG_ERR);
    exit(1);
}

chmod($socketPath, 0666);
file_put_contents($pidFile, getmypid() . PHP_EOL);
relay_log("listening on {$socketPath}");

while ($running) {
    $conn = @stream_socket_accept($server, 1);
    if (!$conn) {
        continue;
    }
    handle_connection($conn, $agentScript, $requestTimeout, $maxBodyBytes);
    fclose($conn);
}

fclose($server);
@unlink($socketPath);
@unlink($pidFile);
relay_log("stopped");
