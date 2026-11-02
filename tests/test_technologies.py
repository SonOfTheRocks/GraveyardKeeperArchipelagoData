import json
import shutil
import tempfile
import unittest
from pathlib import Path

from . import validation

ROOT = validation.ROOT
DataValidationError = validation.DataValidationError
load_and_validate = validation.load_and_validate


class TestTechnologies(unittest.TestCase):
    def test_technologies_are_validated_as_runtime_data(self):
        data = load_and_validate()
        self.assertEqual(184, len(data["technologies"]))
        self.assertEqual(487, len({location for technology in data["technologies"].values()
                                  for location in technology["locations"]}))
        for game_id, technology in data["technologies"].items():
            expected = 0 if "quest_reward" in technology else 1 if "recipe_item" in technology else 3
            with self.subTest(technology=game_id):
                self.assertEqual(expected, len(technology["locations"]))

    def test_invalid_technology_metadata_is_rejected(self):
        for change in ("missing check", "duplicate check", "unknown dlc", "duplicate region",
                       "extra book check", "extra quest check"):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "data"
                shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
                technologies = json.loads((root / "technologies.json").read_text(encoding="utf-8"))
                first = next(key for key, value in technologies.items()
                             if "recipe_item" not in value and "quest_reward" not in value)
                second = next(key for key in technologies if key != first)
                if change == "missing check":
                    technologies[first]["locations"].pop()
                elif change == "duplicate check":
                    technologies[first]["locations"][1] = technologies[first]["locations"][0]
                elif change == "unknown dlc":
                    technologies[first]["dlc"] = "UNKNOWN"
                elif change == "duplicate region":
                    technologies[second]["region"] = technologies[first]["region"]
                else:
                    field = "recipe_item" if change == "extra book check" else "quest_reward"
                    target = next(value for value in technologies.values() if field in value)
                    target["locations"].append("Unexpected research check")
                (root / "technologies.json").write_text(json.dumps(technologies), encoding="utf-8")
                with self.assertRaises(DataValidationError):
                    load_and_validate(root)
