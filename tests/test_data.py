import json
import unittest

from validate_data import ROOT, load_and_validate


class TestSharedData(unittest.TestCase):
    def test_shared_data_is_valid(self):
        data = load_and_validate()
        self.assertGreater(data["manifest"]["data_version"], 0)
        self.assertEqual(set(data["items"]), set(data["grants"]))

    def test_schema_files_are_valid_json(self):
        for name in ("manifest.schema.json", "shared-data.schema.json"):
            with self.subTest(name=name):
                schema = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
                self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])

    def test_every_flow_trigger_has_a_runtime_node_id(self):
        data = load_and_validate()
        flow_triggers = [
            trigger
            for triggers in data["triggers"].values()
            for trigger in triggers
            if trigger["type"].startswith("flow_")
        ]

        self.assertEqual(300, len(flow_triggers))
        self.assertTrue(all(trigger["runtime_node_id"] > 0 for trigger in flow_triggers))


if __name__ == "__main__":
    unittest.main()
