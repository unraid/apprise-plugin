#!/bin/bash
# SPDX-License-Identifier: BSD-2-Clause

set -u

PLUGIN_DIR="/usr/local/emhttp/plugins/apprise"
DAEMON="${PLUGIN_DIR}/scripts/apprise-relayd.php"
RUN_DIR="/var/run/apprise"
PID_FILE="${RUN_DIR}/apprise-relayd.pid"
SOCKET="${RUN_DIR}/apprise.sock"
LOG_FILE="/var/log/apprise-relayd.log"

php_bin() {
  if [[ -n "${PHP_BIN:-}" ]]; then
    printf '%s\n' "$PHP_BIN"
    return
  fi
  command -v php 2>/dev/null || true
}

is_running() {
  [[ -f "$PID_FILE" ]] || return 1
  local pid
  pid="$(cat "$PID_FILE" 2>/dev/null || true)"
  [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null
}

start() {
  if is_running; then
    echo "apprise-relayd is already running (pid $(cat "$PID_FILE"))"
    return 0
  fi

  local php
  php="$(php_bin)"
  if [[ -z "$php" || ! -x "$php" ]]; then
    echo "Unable to start apprise-relayd: php not found" >&2
    return 1
  fi
  if [[ ! -f "$DAEMON" ]]; then
    echo "Unable to start apprise-relayd: $DAEMON not found" >&2
    return 1
  fi

  mkdir -p "$RUN_DIR"
  rm -f "$PID_FILE" "$SOCKET"
  APPRISE_RELAY_SOCKET="$SOCKET" APPRISE_RELAY_PID="$PID_FILE" \
    nohup "$php" "$DAEMON" >>"$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
  sleep 1

  if is_running && [[ -S "$SOCKET" ]]; then
    echo "apprise-relayd started (pid $(cat "$PID_FILE"))"
    return 0
  fi

  echo "apprise-relayd failed to start" >&2
  tail -20 "$LOG_FILE" 2>/dev/null >&2 || true
  rm -f "$PID_FILE" "$SOCKET"
  return 1
}

stop() {
  if is_running; then
    local pid
    pid="$(cat "$PID_FILE")"
    kill "$pid" 2>/dev/null || true
    for _ in 1 2 3 4 5; do
      kill -0 "$pid" 2>/dev/null || break
      sleep 1
    done
    kill -0 "$pid" 2>/dev/null && kill -9 "$pid" 2>/dev/null || true
    echo "apprise-relayd stopped"
  fi
  rm -f "$PID_FILE" "$SOCKET"
}

status() {
  if is_running; then
    echo "apprise-relayd is running (pid $(cat "$PID_FILE"))"
  else
    echo "apprise-relayd is stopped"
    return 1
  fi
}

case "${1:-status}" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  restart)
    stop
    start
    ;;
  status)
    status
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status}" >&2
    exit 2
    ;;
esac
