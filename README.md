# Graveyard Keeper Archipelago Data

This repository owns the shared source data consumed directly by both the
Graveyard Keeper APWorld and the GraveyardKeepelago client.

- `items/**/*.json`: stable AP item definitions;
- `item_grants.json`: the in-game effect for every received item;
- `locations.json`: explicitly authored AP reward locations;
- `quest_reward_triggers.json`: client-side checks for quest rewards;
- `technologies.json`: native technology IDs, native parents, actual research checks and reward sources;
- `manifest.json`: the explicit compatibility `data_version`.

Data version 9 contains only the specific `Bats Trap` (grant `trap_id: bats`) and
`Green Slime Trap` (grant `trap_id: green_slimes`), both classified
`TRAP`. The optional `trap_percentage` replaces filler; relative weights
in the APWorld's `trap_weights` mapping choose the item during generation.
The client queues that exact type and spawns four of its monsters during normal
gameplay. Main icons show the monster; the quality corner shows a skull. Foreign
game previews retain the AP main icon. There is no general random monster trap
or compatibility handler for it. This is an unreleased development project;
The APWorld owns the network item IDs. Both consumers must use version 9.
There are 488 item definitions; local seeds from earlier data versions must be regenerated.

Technology definitions contain only their actual research locations:
- Each of the 28 recipe-book technologies (`recipe_item`) defines one check.
- Each of the 153 self-researched technologies defines three checks, deliberately
  awarded together when that technology is researched.
- The three quest technologies (`quest_reward`: First slice, Grave plate, Iron)
  define no research checks; their existing quest reward already covers the action.

This gives 487 research checks. Unused second/third book checks and extra quest
research checks have been removed from the definitions, regions and public location
map rather than retained as reserved addresses. This pre-release cleanup changes
research location IDs; use new version-8 seeds. `parents` contains the actual native
IDs, including the Cyrillic capital letter in `Сomfort of faith`.

The 25 legacy technology-group items remain defined, but are excluded from new
APWorld pools. Native technology progress/world effects remain separate from
received recipe/work/perk ownership. Book previews and reload recovery use the same
active location subset. Quest-root previews show the actual quest reward without
reporting research checks. Previews do not publish hints.

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
