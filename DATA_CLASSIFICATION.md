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
