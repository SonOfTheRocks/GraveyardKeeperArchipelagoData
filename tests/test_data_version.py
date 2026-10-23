import unittest

from check_data_version import (
    DataVersionError,
    requires_data_version_bump,
    validate_data_version_change,
)


class TestDataVersion(unittest.TestCase):
    def test_every_runtime_data_source_requires_a_version_bump(self):
        paths = (
            "items/misc/items.json",
            "items/quest/items.json",
            "item_grants.json",
            "locations.json",
            "quest_reward_triggers.json",
        )
        for path in paths:
            with self.subTest(path=path):
                self.assertTrue(requires_data_version_bump([path]))
                with self.assertRaises(DataVersionError):
                    validate_data_version_change(4, 4, [path])

    def test_higher_version_accepts_runtime_data_changes(self):
        validate_data_version_change(4, 5, ["items/misc/items.json"])

    def test_docs_tests_and_schemas_do_not_require_a_version_bump(self):
        paths = [
            "README.md",
            "schemas/shared-data.schema.json",
            "tests/test_data.py",
            "validate_data.py",
        ]
        self.assertFalse(requires_data_version_bump(paths))
        validate_data_version_change(4, 4, paths)

    def test_decreasing_version_never_satisfies_a_required_bump(self):
        with self.assertRaises(DataVersionError):
            validate_data_version_change(4, 3, ["locations.json"])


if __name__ == "__main__":
    unittest.main()
