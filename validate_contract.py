from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_CONTRACT = ROOT / "contract" / "graveyard_keeper_contract.json"
EXPECTED_TOP_LEVEL_FIELDS = {"schema_version", "content_hash", "game", "items", "locations"}
DLCS = {"BASE_GAME", "STRANGER_SINS", "GAME_OF_CRONE", "BETTER_SAVE_SOUL"}
CLASSIFICATIONS = {"PROGRESSION", "USEFUL", "FILLER", "TRAP"}
HASH_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")

GRANT_FIELDS = {
    "game_item": {"item_id"},
    "craft_unlock": {"craft_ids"},
    "progressive_craft_unlock": {"stages"},
    "work_unlock": {"work_ids", "perk_ids"},
    "progressive_work_unlock": {"stages"},
    "perk_unlock": {"perk_id", "craft_ids", "work_ids"},
    "permanent_buff": {"buff_id", "resource_types", "icon"},
    "relation": {"npc_id", "amount"},
    "research_points": {"color", "amount"},
    "technology_unlock": {"technology_ids"},
    "flow_script": {"script_id"},
}

TRIGGER_FIELDS = {
    "flow_quest_reward": ({"graph", "node_id"}, {"answer_index"}),
    "flow_relation_reward": ({"graph", "node_id"}, {"answer_index"}),
    "craft_reward": ({"craft_id"}, set()),
    "technology_reward": ({"technology_id"}, set()),
    "world_item_reward": ({"item_id"}, set()),
}


class ContractValidationError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractValidationError(message)


def _require_fields(value: dict[str, Any], expected: set[str], context: str) -> None:
    actual = set(value)
    _require(actual == expected, f"{context}: expected fields {sorted(expected)}, found {sorted(actual)}")


def _require_non_empty_string(value: Any, context: str, *, allow_empty: bool = False) -> None:
    _require(isinstance(value, str), f"{context}: expected a string")
    if not allow_empty:
        _require(bool(value.strip()), f"{context}: string must not be empty")


def _require_string_list(value: Any, context: str) -> None:
    _require(isinstance(value, list), f"{context}: expected a list")
    for index, entry in enumerate(value):
        _require_non_empty_string(entry, f"{context}[{index}]")
    _require(len(value) == len(set(value)), f"{context}: duplicate values are not allowed")


def _validate_grant(grant: Any, context: str) -> None:
    _require(isinstance(grant, dict), f"{context}: expected an object")
    grant_type = grant.get("type")
    _require(grant_type in GRANT_FIELDS, f"{context}: unsupported grant type {grant_type!r}")
    _require_fields(grant, {"type"} | GRANT_FIELDS[grant_type], context)

    for field in ("item_id", "perk_id", "buff_id", "npc_id", "script_id"):
        if field in grant:
            _require_non_empty_string(grant[field], f"{context}.{field}")
    for field in ("craft_ids", "work_ids", "perk_ids", "resource_types", "technology_ids"):
        if field in grant:
            _require_string_list(grant[field], f"{context}.{field}")
    if "stages" in grant:
        _require(isinstance(grant["stages"], list) and grant["stages"], f"{context}.stages: expected a non-empty list")
        for index, stage in enumerate(grant["stages"]):
            _require_string_list(stage, f"{context}.stages[{index}]")
    if "amount" in grant:
        _require(isinstance(grant["amount"], int) and grant["amount"] > 0, f"{context}.amount: expected a positive integer")
    if "color" in grant:
        _require(grant["color"] in {"red", "green", "blue"}, f"{context}.color: unsupported color")
    if "icon" in grant:
        _require_non_empty_string(grant["icon"], f"{context}.icon", allow_empty=True)


def _validate_trigger(trigger: Any, context: str) -> None:
    _require(isinstance(trigger, dict), f"{context}: expected an object")
    trigger_type = trigger.get("type")
    _require(trigger_type in TRIGGER_FIELDS, f"{context}: unsupported trigger type {trigger_type!r}")
    required, optional = TRIGGER_FIELDS[trigger_type]
    actual = set(trigger)
    _require(
        {"type"} | required <= actual <= {"type"} | required | optional,
        f"{context}: invalid fields {sorted(actual)}",
    )
    for field in required:
        _require_non_empty_string(trigger[field], f"{context}.{field}")
    if "answer_index" in trigger:
        _require(
            isinstance(trigger["answer_index"], int) and trigger["answer_index"] >= 0,
            f"{context}.answer_index: expected a non-negative integer",
        )


def calculate_content_hash(contract: dict[str, Any]) -> str:
    content = {key: value for key, value in contract.items() if key != "content_hash"}
    canonical = json.dumps(
        content,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(canonical).hexdigest()}"


def validate_contract(contract: Any) -> None:
    _require(isinstance(contract, dict), "contract: expected an object")
    _require_fields(contract, EXPECTED_TOP_LEVEL_FIELDS, "contract")
    _require(contract["schema_version"] == 1, "contract.schema_version: only version 1 is supported")
    _require(contract["game"] == "Graveyard Keeper", "contract.game: unexpected game")
    _require(isinstance(contract["content_hash"], str) and HASH_PATTERN.fullmatch(contract["content_hash"]), "contract.content_hash: invalid format")
    _require(contract["content_hash"] == calculate_content_hash(contract), "contract.content_hash: content does not match hash")

    items = contract["items"]
    _require(isinstance(items, dict) and items, "contract.items: expected a non-empty object")
    item_names: set[str] = set()
    for item_key, item in items.items():
        context = f"contract.items.{item_key}"
        _require(bool(re.fullmatch(r"ITEM_[A-Za-z0-9_]+", item_key)), f"{context}: invalid stable key")
        _require(isinstance(item, dict), f"{context}: expected an object")
        _require_fields(item, {"name", "dlc", "classification", "amount", "grant"}, context)
        _require_non_empty_string(item["name"], f"{context}.name")
        _require(item["name"] not in item_names, f"{context}.name: duplicate network name {item['name']!r}")
        item_names.add(item["name"])
        _require(item["dlc"] in DLCS, f"{context}.dlc: unsupported DLC")
        _require(item["classification"] in CLASSIFICATIONS, f"{context}.classification: unsupported classification")
        _require(isinstance(item["amount"], int) and item["amount"] > 0, f"{context}.amount: expected a positive integer")
        _validate_grant(item["grant"], f"{context}.grant")

    locations = contract["locations"]
    _require(isinstance(locations, dict) and locations, "contract.locations: expected a non-empty object")
    location_names: set[str] = set()
    for location_key, location in locations.items():
        context = f"contract.locations.{location_key}"
        _require(bool(re.fullmatch(r"LOCATION_[A-Za-z0-9_]+", location_key)), f"{context}: invalid stable key")
        _require(isinstance(location, dict), f"{context}: expected an object")
        _require_fields(location, {"name", "dlc", "parent_region", "triggers"}, context)
        _require_non_empty_string(location["name"], f"{context}.name")
        _require(location["name"] not in location_names, f"{context}.name: duplicate network name {location['name']!r}")
        location_names.add(location["name"])
        _require(location["dlc"] in DLCS, f"{context}.dlc: unsupported DLC")
        _require_non_empty_string(location["parent_region"], f"{context}.parent_region")
        _require(isinstance(location["triggers"], list), f"{context}.triggers: expected a list")
        serialized_triggers: set[str] = set()
        for index, trigger in enumerate(location["triggers"]):
            _validate_trigger(trigger, f"{context}.triggers[{index}]")
            serialized = json.dumps(trigger, sort_keys=True, separators=(",", ":"))
            _require(serialized not in serialized_triggers, f"{context}.triggers[{index}]: duplicate trigger")
            serialized_triggers.add(serialized)


def load_and_validate(path: Path = DEFAULT_CONTRACT) -> dict[str, Any]:
    try:
        contract = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContractValidationError(f"Could not load {path}: {error}") from error
    validate_contract(contract)
    return contract


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CONTRACT
    try:
        contract = load_and_validate(path)
    except ContractValidationError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(
        f"Valid contract: schema={contract['schema_version']} "
        f"items={len(contract['items'])} locations={len(contract['locations'])} "
        f"hash={contract['content_hash']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
