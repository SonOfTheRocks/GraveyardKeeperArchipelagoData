from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DLCS = {"BASE_GAME", "STRANGER_SINS", "GAME_OF_CRONE", "BETTER_SAVE_SOUL"}
CLASSIFICATIONS = {"PROGRESSION", "USEFUL", "FILLER", "TRAP"}
GRANT_FIELDS = {
    "game_item": {"item_id"}, "craft_unlock": {"craft_ids"},
    "progressive_craft_unlock": {"stages"}, "work_unlock": {"work_ids", "perk_ids"},
    "progressive_work_unlock": {"stages"}, "perk_unlock": {"perk_id", "craft_ids", "work_ids"},
    "permanent_buff": {"buff_id", "resource_types", "icon"}, "relation": {"npc_id", "amount"},
    "research_points": {"color", "amount"}, "technology_unlock": {"technology_ids"},
    "flow_script": {"script_id"},
}
TRIGGER_FIELDS = {
    "flow_quest_reward": ({"graph", "node_id", "runtime_node_id"}, {"answer_index"}),
    "flow_relation_reward": ({"graph", "node_id", "runtime_node_id"}, {"answer_index"}),
    "craft_reward": ({"craft_id"}, set()), "technology_reward": ({"technology_id"}, set()),
    "world_item_reward": ({"item_id"}, set()),
}


class DataValidationError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DataValidationError(message)


def _load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise DataValidationError(f"Could not load {path}: {error}") from error


def _string(value: Any, context: str, *, allow_empty: bool = False) -> None:
    _require(isinstance(value, str) and (allow_empty or bool(value.strip())), f"{context}: expected a non-empty string")


def _string_list(value: Any, context: str) -> None:
    _require(isinstance(value, list), f"{context}: expected a list")
    for index, entry in enumerate(value):
        _string(entry, f"{context}[{index}]")
    _require(len(value) == len(set(value)), f"{context}: duplicate values")


def _validate_grant(value: Any, context: str) -> None:
    _require(isinstance(value, dict), f"{context}: expected an object")
    grant_type = value.get("type")
    _require(grant_type in GRANT_FIELDS, f"{context}: unsupported type {grant_type!r}")
    _require(set(value) == {"type"} | GRANT_FIELDS[grant_type], f"{context}: invalid fields")
    for field in ("item_id", "perk_id", "buff_id", "npc_id", "script_id"):
        if field in value:
            _string(value[field], f"{context}.{field}")
    for field in ("craft_ids", "work_ids", "perk_ids", "resource_types", "technology_ids"):
        if field in value:
            _string_list(value[field], f"{context}.{field}")
    if "stages" in value:
        _require(isinstance(value["stages"], list) and value["stages"], f"{context}.stages: expected a non-empty list")
        for index, stage in enumerate(value["stages"]):
            _string_list(stage, f"{context}.stages[{index}]")
    if "amount" in value:
        _require(isinstance(value["amount"], int) and value["amount"] > 0, f"{context}.amount: expected a positive integer")
    if "color" in value:
        _require(value["color"] in {"red", "green", "blue"}, f"{context}.color: unsupported color")
    if "icon" in value:
        _string(value["icon"], f"{context}.icon", allow_empty=True)


def load_and_validate(root: Path = ROOT) -> dict[str, Any]:
    manifest = _load(root / "manifest.json")
    _require(set(manifest) == {"data_version"}, "manifest: expected only data_version")
    _require(isinstance(manifest["data_version"], int) and manifest["data_version"] > 0, "manifest.data_version: expected a positive integer")

    items: dict[str, Any] = {}
    for path in sorted((root / "items").rglob("*.json")):
        if "unused" in path.parts:
            continue
        for key, value in _load(path).items():
            _require(key not in items, f"item {key}: defined more than once")
            items[key] = value
    _require(bool(items), "items: expected at least one item")
    labels: set[str] = set()
    for key, item in items.items():
        context = f"items.{key}"
        _require(bool(re.fullmatch(r"ITEM_[A-Za-z0-9_]+", key)), f"{context}: invalid key")
        common = {"label", "dlc", "classification"}
        allowed = (common, common | {"amount"}, common | {"unlocks", "researches"})
        _require(isinstance(item, dict) and set(item) in allowed, f"{context}: invalid fields")
        _string(item["label"], f"{context}.label")
        _require(item["label"] not in labels, f"{context}.label: duplicate network name")
        labels.add(item["label"])
        _require(item["dlc"] in DLCS, f"{context}.dlc: unsupported DLC")
        _require(item["classification"] in CLASSIFICATIONS, f"{context}.classification: unsupported classification")
        _require(isinstance(item.get("amount", 1), int) and item.get("amount", 1) > 0, f"{context}.amount: expected a positive integer")
        if "unlocks" in item:
            _string_list(item["unlocks"], f"{context}.unlocks")
            _string_list(item["researches"], f"{context}.researches")

    grants = _load(root / "item_grants.json")
    _require(set(grants) == set(items), "item_grants: keys must exactly match item definitions")
    for key, grant in grants.items():
        _validate_grant(grant, f"item_grants.{key}")

    locations = _load(root / "locations.json")
    location_labels: set[str] = set()
    for key, location in locations.items():
        context = f"locations.{key}"
        _require(bool(re.fullmatch(r"LOCATION_[A-Za-z0-9_]+", key)), f"{context}: invalid key")
        _require(isinstance(location, dict) and set(location) == {"label", "parent_region"}, f"{context}: invalid fields")
        _string(location["label"], f"{context}.label")
        _require(location["label"] not in location_labels, f"{context}.label: duplicate network name")
        location_labels.add(location["label"])
        _string(location["parent_region"], f"{context}.parent_region")

    triggers = _load(root / "quest_reward_triggers.json")
    _require(set(triggers) <= set(locations), "quest_reward_triggers: contains unknown location keys")
    for key, entries in triggers.items():
        _require(isinstance(entries, list), f"quest_reward_triggers.{key}: expected a list")
        seen: set[str] = set()
        for index, trigger in enumerate(entries):
            context = f"quest_reward_triggers.{key}[{index}]"
            trigger_type = trigger.get("type") if isinstance(trigger, dict) else None
            _require(trigger_type in TRIGGER_FIELDS, f"{context}: unsupported type {trigger_type!r}")
            required, optional = TRIGGER_FIELDS[trigger_type]
            _require({"type"} | required <= set(trigger) <= {"type"} | required | optional, f"{context}: invalid fields")
            for field in required - {"runtime_node_id"}:
                _string(trigger[field], f"{context}.{field}")
            if "runtime_node_id" in trigger:
                _require(isinstance(trigger["runtime_node_id"], int) and trigger["runtime_node_id"] > 0,
                         f"{context}.runtime_node_id: expected a positive integer")
            if "answer_index" in trigger:
                _require(isinstance(trigger["answer_index"], int) and trigger["answer_index"] >= 0, f"{context}.answer_index: expected a non-negative integer")
            serialized = json.dumps(trigger, sort_keys=True, separators=(",", ":"))
            _require(serialized not in seen, f"{context}: duplicate trigger")
            seen.add(serialized)

    return {"manifest": manifest, "items": items, "grants": grants, "locations": locations, "triggers": triggers}


def main() -> int:
    try:
        data = load_and_validate(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT)
    except DataValidationError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Valid shared data: version={data['manifest']['data_version']} items={len(data['items'])} locations={len(data['locations'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
