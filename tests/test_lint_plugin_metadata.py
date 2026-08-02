import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lint_plugin_metadata import (  # noqa: E402
    agent_icon_basename,
    agent_script_basename,
    lint_agent_assets,
)


AGENT_XML = """<?xml version="1.0" encoding="utf-8"?>
<Agent>
  <Name>Apprise Notification Agent</Name>
</Agent>
"""

PLG = """<PLUGIN>
<FILE Run="/bin/bash" Method="install">
<INLINE>
install -m 0644 /boot/config/plugins/apprise/apprise.png /usr/local/emhttp/plugins/dynamix/icons/apprisenotificationagent.png
</INLINE>
</FILE>
<FILE Run="/bin/bash" Method="remove">
<INLINE>
rm -f /boot/config/plugins/dynamix/notifications/agents/Apprise_Notification_Agent.sh
rm -f /boot/config/plugins/dynamix/notifications/agents-disabled/Apprise_Notification_Agent.sh
</INLINE>
</FILE>
</PLUGIN>
"""


class AgentAssetNameTest(unittest.TestCase):
    def test_icon_basename_matches_dynamix_lookup(self) -> None:
        self.assertEqual(
            agent_icon_basename("Apprise Notification Agent"),
            "apprisenotificationagent.png",
        )

    def test_script_basename_matches_dynamix_lookup(self) -> None:
        self.assertEqual(
            agent_script_basename("Apprise Notification Agent"),
            "Apprise_Notification_Agent.sh",
        )


class LintAgentAssetsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = Path("agents/Apprise.xml")
        self.tree = ET.ElementTree(ET.fromstring(AGENT_XML))
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)

    def write_plg(self, text: str) -> Path:
        plg = self.tmp / "apprise.plg"
        plg.write_text(text)
        return plg

    def test_accepts_matching_asset_names(self) -> None:
        lint_agent_assets(self.write_plg(PLG), self.agent, self.tree)

    def test_rejects_stale_icon_name(self) -> None:
        stale = PLG.replace("apprisenotificationagent.png", "apprise.png")
        with self.assertRaisesRegex(SystemExit, "requires the icon to be installed"):
            lint_agent_assets(self.write_plg(stale), self.agent, self.tree)

    def test_rejects_stale_agent_script_name(self) -> None:
        stale = PLG.replace("Apprise_Notification_Agent.sh", "Apprise.sh")
        with self.assertRaisesRegex(SystemExit, "requires the remove method to delete"):
            lint_agent_assets(self.write_plg(stale), self.agent, self.tree)


if __name__ == "__main__":
    unittest.main()
