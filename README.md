# Graveyard Keeper Archipelago Data

This repository owns the shared source data consumed directly by both the
Graveyard Keeper APWorld and the GraveyardKeepelago client.

- `items/**/*.json`: stable AP item definitions;
- `item_grants.json`: the in-game effect for every received item;
- `locations.json`: explicitly authored AP reward locations;
- `quest_reward_triggers.json`: client-side checks for quest rewards;
- `technologies.json`: native technology IDs, native parents, reserved research addresses and reward sources;
- `manifest.json`: the explicit compatibility `data_version`.

Data version 6 adds separate `Bats Trap` (AP ID 488, grant `trap_id: bats`) and
`Green Slime Trap` (AP ID 489, grant `trap_id: green_slimes`), both classified
`TRAP`. The optional `trap_percentage` replaces filler; relative weights
`bats_trap_weight` and `green_slime_trap_weight` choose the item during generation.
The client queues that exact type and spawns four of its monsters during normal
gameplay. Main icons show the monster; the quality corner shows a skull. Foreign
game previews retain the AP main icon. All earlier names and IDs remain unchanged,
including the former random `Monsters Trap` at reserved ID 487, excluded from new
pools. Both consumers must use version 6; older seeds require regeneration.

The technology behavior introduced in version 4 is retained. Each of the 28 technology
recipe items (`recipe_item`) uses only its first research location; locations 2 and 3
are not generated. Ordinary research retains three checks. Technologies with a
`quest_reward` (First slice, Grave plate, Iron) complete their existing quest reward
without a second set of research checks. `parents` contains the actual native IDs,
including the Cyrillic capital letter in `Сomfort of faith`.

The 25 legacy technology-group items remain defined, but are excluded from new
APWorld pools. Native technology progress/world effects remain separate from
received recipe/work/perk ownership. Book previews and reload recovery use the same
active location subset. Quest-root previews show the actual quest reward without
reporting research checks. Previews do not publish hints. Version 3 seeds must be regenerated;
their three-check books and obsolete group items are not silently reinterpreted.

There is no generated aggregate file and no content hash. Git pins the exact
data revision used for a build. Because APWorld and client compare
`data_version` exactly, every change to the runtime data files must bump it.
Changes limited to documentation, schemas, validators, or tests do not.

Flow triggers retain the JSON export reference as `node_id` for analysis and
graph-tool traceability. `runtime_node_id` is the corresponding one-based
FlowCanvas node index used by the game client; the two identifiers are not
interchangeable.

Craft triggers distinguish completing a recipe (`craft_completion_reward`)
from receiving a recipe or blueprint (`craft_unlock_reward`). The distinction
prevents recipe access from completing a location that requires actually
crafting its output.

Validate changes with:

```powershell
python validate_data.py
python -m unittest discover -s tests -t .
```

Pull requests compare against their base branch and reject runtime data changes
that do not increase `data_version`.
