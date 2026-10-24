# Graveyard Keeper Archipelago Data

This repository owns the shared source data consumed directly by both the
Graveyard Keeper APWorld and the GraveyardKeepelago client.

- `items/**/*.json`: stable AP item definitions;
- `item_grants.json`: the in-game effect for every received item;
- `locations.json`: explicitly authored AP reward locations;
- `quest_reward_triggers.json`: client-side checks for quest rewards;
- `manifest.json`: the explicit compatibility `data_version`.

There is no generated aggregate file and no content hash. Git pins the exact
data revision used for a build. Because APWorld and client compare
`data_version` exactly, every change to the runtime data files must bump it.
Changes limited to documentation, schemas, validators, or tests do not.

Flow triggers retain the JSON export reference as `node_id` for analysis and
graph-tool traceability. `runtime_node_id` is the corresponding one-based
FlowCanvas node index used by the game client; the two identifiers are not
interchangeable.

Validate changes with:

```powershell
python validate_data.py
python -m unittest discover -s tests -t .
```

Pull requests compare against their base branch and reject runtime data changes
that do not increase `data_version`.
