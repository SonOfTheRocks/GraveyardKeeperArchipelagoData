import copy
import json
import unittest

from validate_contract import (
    ROOT,
    ContractValidationError,
    calculate_content_hash,
    load_and_validate,
    validate_contract,
)


class TestContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = load_and_validate()

    def test_contract_is_valid(self):
        validate_contract(self.contract)

    def test_changed_content_is_rejected_without_a_new_hash(self):
        changed = copy.deepcopy(self.contract)
        first_item = next(iter(changed["items"].values()))
        first_item["name"] += " changed"
        with self.assertRaisesRegex(ContractValidationError, "does not match hash"):
            validate_contract(changed)

    def test_duplicate_network_name_is_rejected(self):
        changed = copy.deepcopy(self.contract)
        first, second = list(changed["items"].values())[:2]
        second["name"] = first["name"]
        changed["content_hash"] = calculate_content_hash(changed)
        with self.assertRaisesRegex(ContractValidationError, "duplicate network name"):
            validate_contract(changed)

    def test_schema_file_is_valid_json(self):
        schema_path = ROOT / "schemas" / "client-contract.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertEqual(1, schema["properties"]["schema_version"]["const"])


if __name__ == "__main__":
    unittest.main()
