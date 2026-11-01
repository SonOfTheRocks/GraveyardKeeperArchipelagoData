from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Iterable


SHARED_DATA_FILES = {
    "item_grants.json",
    "locations.json",
    "quest_reward_triggers.json",
    "technologies.json",
}
SHARED_DATA_DIRECTORIES = ("items/",)


class DataVersionError(ValueError):
    pass


def requires_data_version_bump(changed_paths: Iterable[str]) -> bool:
    return any(
        path in SHARED_DATA_FILES or path.startswith(SHARED_DATA_DIRECTORIES)
        for path in changed_paths
    )


def validate_data_version_change(
    base_version: int,
    current_version: int,
    changed_paths: Iterable[str],
) -> None:
    if requires_data_version_bump(changed_paths) and current_version <= base_version:
        raise DataVersionError(
            "Shared runtime data changed, but manifest.json data_version was not increased "
            f"(base={base_version}, current={current_version})."
        )


def _git(*arguments: str) -> str:
    result = subprocess.run(
        ("git", *arguments),
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout


def check_against_git_ref(base_ref: str) -> None:
    changed_paths = [
        line.strip()
        for line in _git("diff", "--name-only", f"{base_ref}...HEAD").splitlines()
        if line.strip()
    ]
    base_manifest = json.loads(_git("show", f"{base_ref}:manifest.json"))
    with open("manifest.json", encoding="utf-8-sig") as manifest_file:
        current_manifest = json.load(manifest_file)
    validate_data_version_change(
        base_manifest["data_version"],
        current_manifest["data_version"],
        changed_paths,
    )


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python check_data_version.py <base-git-ref>", file=sys.stderr)
        return 2
    try:
        check_against_git_ref(sys.argv[1])
    except (DataVersionError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Shared data version is consistent with the changed files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
