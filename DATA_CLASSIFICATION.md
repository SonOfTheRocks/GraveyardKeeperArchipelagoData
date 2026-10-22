# Data ownership and classification

## Shared public contract

The neutral data repository owns the generated
`contract/graveyard_keeper_contract.json`. Both the APWorld and client pin the
same repository commit as a Git submodule.

The contract exposes only data required across that boundary:

- stable AP item keys and network names;
- DLC, classification, pool amount, and concrete client grant for every item;
- stable AP location keys and network names;
- DLC and parent region for every location;
- the client-side trigger or triggers that check each quest-reward location;
- schema version and a deterministic content hash.

## APWorld-owned authoring data

These files remain canonical in the APWorld and generate the public contract:

- `data/items/**/*.json`;
- `data/item_grants.json`;
- `data/locations.json`;
- `data/quest_reward_triggers.json`;
- the location and DLC portions of `data/regions.json` needed to expand
  generated technology locations.

They remain APWorld-owned because they participate directly in seed generation
or use the APWorld's authoring structure. The client must not parse them.

## APWorld-private data

The following data is deliberately excluded from the shared contract:

- `quest_events.json` and its reachability requirements;
- `quest_node_names.json`, which is flow-analysis presentation metadata;
- recipe, workstation, vendor, buildable, material-group, and progressive-item
  logic under `data/logic/`;
- full region topology, events, and exits;
- raw dumps, decompiled sources, and generated graph reports.

## Update workflow

1. Edit and validate the canonical APWorld authoring data.
2. Regenerate the contract into the neutral repository checkout.
3. Run `validate_contract.py` and both consumer test suites.
4. Commit and push the neutral data repository.
5. Update both parent repositories to the exact same submodule commit.
6. Commit those two submodule-pointer updates with any required consumer code.

Never copy-edit one consumer's contract. A difference between submodule commits
is a release-blocking compatibility error.
