import json
import shutil
import tempfile
import unittest
from pathlib import Path

from validate_data import ROOT, DataValidationError, load_and_validate


class TestTechnologies(unittest.TestCase):
    def test_technologies_are_validated_as_runtime_data(self):
        data = load_and_validate()
        self.assertEqual(184, len(data["technologies"]))
        self.assertEqual(552, len({location for technology in data["technologies"].values()
                                  for location in technology["locations"]}))

    def test_invalid_technology_metadata_is_rejected(self):
        for change in ("missing check", "duplicate check", "unknown dlc", "duplicate region"):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "data"
                shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
                technologies = json.loads((root / "technologies.json").read_text(encoding="utf-8"))
                first, second = list(technologies)[:2]
                if change == "missing check":
                    technologies[first]["locations"].pop()
                elif change == "duplicate check":
                    technologies[first]["locations"][1] = technologies[first]["locations"][0]
                elif change == "unknown dlc":
                    technologies[first]["dlc"] = "UNKNOWN"
                else:
                    technologies[second]["region"] = technologies[first]["region"]
                (root / "technologies.json").write_text(json.dumps(technologies), encoding="utf-8")
                with self.assertRaises(DataValidationError):
                    load_and_validate(root)
