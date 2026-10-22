import copy
import hashlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("update_cask", Path(__file__).with_name("update-cask.py"))
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class UpdateCaskTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.cask = Path(self.temp.name) / "cot.rb"
        self.original = 'cask "cot" do\n  version "1.13.3"\n  sha256 "' + "a" * 64 + '"\nend\n'
        self.cask.write_text(self.original)
        self.payload = b"test DMG bytes"
        self.release = {
            "tag_name": "v1.13.4",
            "draft": False,
            "prerelease": False,
            "assets": [{
                "name": "cot_1.13.4_aarch64.dmg",
                "state": "uploaded",
                "browser_download_url": "https://github.com/cot-intelligence/cot/releases/download/v1.13.4/cot_1.13.4_aarch64.dmg",
                "digest": "sha256:" + hashlib.sha256(self.payload).hexdigest(),
                "size": len(self.payload),
            }],
        }

    def rejected(self, release, payload=None):
        with patch.object(updater, "urlopen", return_value=io.BytesIO(payload or self.payload)):
            with self.assertRaises(ValueError):
                updater.update(release, self.cask)
        self.assertEqual(self.cask.read_text(), self.original)

    def test_verified_download_updates_version_and_checksum(self):
        with patch.object(updater, "urlopen", return_value=io.BytesIO(self.payload)):
            updater.update(self.release, self.cask)
        self.assertIn('version "1.13.4"', self.cask.read_text())
        self.assertIn(hashlib.sha256(self.payload).hexdigest(), self.cask.read_text())

    def test_corrupt_download_leaves_cask_unchanged(self):
        self.rejected(self.release, b"modified download")

    def test_incomplete_download_leaves_cask_unchanged(self):
        self.release["assets"][0]["size"] += 1
        self.rejected(self.release)

    def test_unpublished_and_prerelease_are_rejected(self):
        for field in ("draft", "prerelease"):
            release = copy.deepcopy(self.release)
            release[field] = True
            self.rejected(release)

    def test_downgrade_is_rejected(self):
        self.release["tag_name"] = "v1.13.2"
        self.rejected(self.release)

    def test_unexpected_url_and_missing_digest_are_rejected(self):
        for field, value in (("browser_download_url", "https://example.com/cot.dmg"), ("digest", "")):
            release = copy.deepcopy(self.release)
            release["assets"][0][field] = value
            self.rejected(release)


if __name__ == "__main__":
    unittest.main()
