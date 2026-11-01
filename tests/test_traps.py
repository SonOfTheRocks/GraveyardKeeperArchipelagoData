import unittest
from unittest.mock import patch

from validate_data import DataValidationError, _load, load_and_validate


class TestTraps(unittest.TestCase):
    def test_monster_trap_has_a_stable_id_and_supported_grant(self):
        data = load_and_validate()
        trap = data["items"]["ITEM_MONSTERS_TRAP"]
        self.assertEqual(487, trap["id"])
        self.assertEqual("TRAP", trap["classification"])
        self.assertEqual({"type": "trap", "trap_id": "monsters"}, data["grants"]["ITEM_MONSTERS_TRAP"])

    def test_distinct_monster_traps_have_distinct_ids_and_grants(self):
        data = load_and_validate()
        for key, code, trap_id in (("ITEM_BATS_TRAP", 488, "bats"), ("ITEM_GREEN_SLIME_TRAP", 489, "green_slimes")):
            with self.subTest(key=key):
                self.assertEqual(code, data["items"][key]["id"])
                self.assertEqual("TRAP", data["items"][key]["classification"])
                self.assertEqual({"type": "trap", "trap_id": trap_id}, data["grants"][key])

    def test_invalid_trap_contract_is_rejected(self):
        for change, message in (
            ("missing id", "trap IDs must be explicit"),
            ("zero id", "expected a positive integer"),
            ("boolean id", "expected a positive integer"),
            ("legacy id", "overlap reserved legacy IDs"),
            ("duplicate id", "duplicate explicit IDs"),
            ("unknown trap", "unsupported trap_id"),
            ("wrong classification", "trap grants require TRAP classification"),
            ("wrong grant", "TRAP items require a trap grant"),
        ):
            def load_changed(path):
                result = _load(path)
                if path.name == "traps.json":
                    trap = result["ITEM_MONSTERS_TRAP"]
                    if change == "missing id":
                        trap.pop("id")
                    elif change in ("zero id", "boolean id", "legacy id"):
                        trap["id"] = {"zero id": 0, "boolean id": True, "legacy id": 1}[change]
                    elif change == "wrong classification":
                        trap["classification"] = "FILLER"
                elif path.name == "item_grants.json":
                    if change == "unknown trap":
                        result["ITEM_MONSTERS_TRAP"]["trap_id"] = "unknown"
                    elif change == "wrong grant":
                        result["ITEM_MONSTERS_TRAP"] = {"type": "game_item", "item_id": "stone"}
                if change == "duplicate id" and path.parent.name == "items" and path.name != "traps.json":
                    next(iter(result.values()))["id"] = 487
                return result

            with self.subTest(change=change), patch("validate_data._load", side_effect=load_changed):
                with self.assertRaisesRegex(DataValidationError, message):
                    load_and_validate()
