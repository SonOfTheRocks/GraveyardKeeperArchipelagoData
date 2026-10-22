# Graveyard Keeper Archipelago Data

This repository owns the shared source data consumed directly by both the
Graveyard Keeper APWorld and the GraveyardKeepelago client.

- `items/**/*.json`: stable AP item definitions;
- `item_grants.json`: the in-game effect for every received item;
- `locations.json`: explicitly authored AP reward locations;
- `quest_reward_triggers.json`: client-side checks for quest rewards;
- `manifest.json`: the explicit compatibility `data_version`.

There is no generated aggregate file and no content hash. Git pins the exact
data revision used for a build. `data_version` is bumped only when a data change
requires coordinated consumer behavior. Validate changes with:

```powershell
python validate_data.py
python -m unittest discover -s tests -t .
```
