import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from prepare_plugin_release import update_plugin_changelog  # noqa: E402


class UpdatePluginChangelogTest(unittest.TestCase):
    def test_preserves_literal_changelog_title(self) -> None:
        plg = """<PLUGIN>
<CHANGES>
## Apprise Notification Agent
###&version; (&pluginVersion;)
- Current placeholder.

###2026.01.01.0000.1-0.1.3 (0.1.3)
- Previous release.
</CHANGES>
</PLUGIN>
"""

        updated = update_plugin_changelog(
            plg,
            "2026.05.21.1409.10-0.1.4",
            "0.1.4",
            "- Release notes.",
        )

        self.assertIn("## Apprise Notification Agent\n###&version; (&pluginVersion;)\n- Release notes.", updated)
        self.assertIn("###2026.05.21.1409.10-0.1.4 (0.1.4)", updated)
        self.assertIn("###2026.01.01.0000.1-0.1.3 (0.1.3)", updated)

    def test_preserves_entity_changelog_title(self) -> None:
        plg = """<PLUGIN>
<CHANGES>
##&name;
###&version; (&pluginVersion;)
- Current placeholder.
</CHANGES>
</PLUGIN>
"""

        updated = update_plugin_changelog(
            plg,
            "2026.05.21.1409.10-0.1.4",
            "0.1.4",
            "- Release notes.",
        )

        self.assertIn("##&name;\n###&version; (&pluginVersion;)\n- Release notes.", updated)
        self.assertIn("###2026.05.21.1409.10-0.1.4 (0.1.4)", updated)

    def test_rejects_missing_changelog_title(self) -> None:
        plg = """<PLUGIN>
<CHANGES>
###&version; (&pluginVersion;)
- Current placeholder.
</CHANGES>
</PLUGIN>
"""

        with self.assertRaisesRegex(SystemExit, "Unable to find PLG changelog title"):
            update_plugin_changelog(plg, "2026.05.21.1409.10-0.1.4", "0.1.4", "- Release notes.")


if __name__ == "__main__":
    unittest.main()
