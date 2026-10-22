# Graveyard Keeper Archipelago Data

This repository is the versioned data boundary between the Graveyard Keeper
APWorld and the GraveyardKeepelago client.

## Contents

- `contract/graveyard_keeper_contract.json`: generated public item and location contract;
- `schemas/client-contract.schema.json`: formal JSON Schema for the contract;
- `validate_contract.py`: dependency-free semantic and content-hash validator;
- `DATA_CLASSIFICATION.md`: ownership rules for shared and private data.

The fragmented authoring data remains in the APWorld. Do not edit the generated
contract by hand. Generate it from the APWorld and then validate it:

```powershell
.venv\Scripts\python.exe worlds/graveyard_keeper/tools/build_client_contract.py `
  --output external/graveyard_keeper_data/contract/graveyard_keeper_contract.json
python external/graveyard_keeper_data/validate_contract.py
```

The validator uses only the Python standard library. Consumers must reject an
unsupported `schema_version` and a mismatching `content_hash`.
