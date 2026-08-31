# EXPERIMENT-001 — Delayed reconciliation under partition

**Status:** PREPARED / DEPENDENCY-FREE PROTOTYPE / NOT A PROTOCOL

## Question

Can two isolated planetary nodes continue accepting locally valid resource reservations and later detect that their combined history overcommitted a shared resource after delayed synchronization?

## Frozen v0.1 scenario

- Earth visible capacity: `100 energy_kwh`
- Mars visible capacity: `100 energy_kwh`
- Earth locally reserves: `60 energy_kwh`
- Mars locally reserves: `60 energy_kwh`
- artificial one-way delay: `180 seconds`
- before exchange: both nodes are locally `CONSISTENT`
- after both immutable operation sets arrive: both nodes must report `CONFLICT_OVERCOMMITTED`
- expected reconciled total: `120 energy_kwh`
- expected remaining capacity: `-20 energy_kwh`

This scenario deliberately demonstrates a conflict. v0.1 does **not** resolve the conflict or choose a winner.

## What the prototype proves when tests pass

The repository can mechanically demonstrate:

1. local operation during a communication partition;
2. a deterministic artificial transport delay;
3. immutable operation exchange by identity;
4. idempotent duplicate delivery;
5. fail-closed rejection when one operation identity is reused for different content;
6. detection of global overcommitment after reconciliation.

## What it does not prove

- blockchain or consensus correctness;
- cryptographic signatures or authenticated transport;
- Byzantine-fault tolerance;
- trusted resource measurement/oracles;
- a valid economic token design;
- conflict resolution fairness;
- Mars/Earth networking feasibility;
- SpaceX, Starlink, Tesla, Chainlink or other third-party integration.

`SIMULATION_PASS != PROTOCOL_VALIDATED != RESOURCE_BACKED != DEPLOYED`

## Reproduce locally

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python prototype/ledger_sim.py
```

The second command prints a JSON record containing the local pre-reconciliation state, scheduled delivery time, operation counts before delivery and final conflict state.

## Next Human Gate

After CI returns on the exact candidate, choose which engineering question EXPERIMENT-002 should test:

1. deterministic conflict-resolution policy;
2. signed checkpoint / tamper-detection model;
3. repeated partitions and reconnect cycles;
4. independent resource domains instead of one shared global capacity.

No choice is implied by this experiment.
