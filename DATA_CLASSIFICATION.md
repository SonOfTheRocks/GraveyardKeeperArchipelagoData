# Data ownership and classification

## Shared source data

This repository is authoritative for item definitions, item grants, explicit
reward locations, reward triggers, and the compatibility `data_version`.
Consumers pin this repository as a Git submodule and read these files directly.

## APWorld-private data

Quest requirements, region topology, recipes, vendors, progressive mappings,
raw dumps, decompiled sources, and graph presentation metadata remain in the
APWorld repository. They are not a client API.

## Compatibility

The Git submodule commit identifies the exact source snapshot used at build
time. `manifest.json` serves a different purpose: its integer `data_version` is
sent in slot data and compared by the client at connection time. Compatible
edits may keep the current version. Any edit requiring new client or APWorld
behavior must increment it and update both consumers together.

## Recipe classification defaults

Recipe/blueprint ownership items (`ITEM_LEARN_*` and `ITEM_BP_*`) declare only
`FILLER` or `USEFUL`. Use `USEFUL` for hand-selected quality-of-life recipes.
The APWorld dynamically promotes recipes referenced by active logic to
progression for each player world. Consumers must use the server's item flags
for seed-specific presentation; item grants, names and stage order are unchanged.

## Traps and stable IDs

Trap items declare `TRAP`, an explicit positive `id`, and a `trap` grant. Currently
supported IDs are `bats` and `green_slimes`; `monsters` remains supported only for
the reserved old item/queue format. `Bats Trap` reserves 488, `Green Slime Trap`
reserves 489, and the old `Monsters Trap` retains 487. Explicit IDs cannot overlap the legacy IDs or
each other. The existing 486 items retain their historical implicit IDs;
explicit-ID additions do not advance the legacy counter.

Trap definitions are excluded from the ordinary declared pool. After balancing
the pool, the APWorld replaces a configured percentage of filler copies with
traps, selected using their relative per-player weights. The old random trap is
never generated. Useful and progression copies remain available.
