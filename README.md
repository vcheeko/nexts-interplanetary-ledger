# NEXST — Interplanetary Resource-Ledger Concept

[![quality](https://github.com/vcheeko/nexts-interplanetary-ledger/actions/workflows/quality.yml/badge.svg?branch=main)](https://github.com/vcheeko/nexts-interplanetary-ledger/actions/workflows/quality.yml)

**Status: concept study + first dependency-free delay/reconciliation experiment — no working protocol, smart contract, Layer-2 network or external integration is implemented.**

NEXST (New Earth X-space System & Transit) is an exploratory product/system concept for a future environment where Earth and Mars cannot depend on low-latency communication.

The core question is:

> How might a resource-accounting system remain useful when communication between planets is delayed by the speed of light and continuous synchronization is impossible?

The repository should be read as **speculative systems design plus bounded engineering experiments**, not as a deployed protocol or validated blockchain architecture.

## Why the problem is interesting

Earth–Mars communication can involve minutes of one-way light-time delay depending on orbital geometry. That does not make distributed ledgers impossible, but it creates a very different systems problem from a terrestrial network where nodes can usually communicate in milliseconds or seconds.

A future interplanetary system may therefore need to tolerate:

- long and variable communication delays;
- temporary network partitions;
- local operation while disconnected from Earth;
- delayed reconciliation between planetary domains;
- explicit handling of conflicting or stale state;
- strong auditability for scarce physical resources.

## Concept hypothesis

Instead of treating the project primarily as a speculative cryptocurrency, NEXST explores whether digital accounting could represent **real resource constraints** such as energy or transport capacity.

Illustrative units could include:

- **Energy unit** — an accounting claim tied to a measured quantity of generated or available energy;
- **Mass / cargo-capacity unit** — an accounting claim tied to a measured quantity of transport or storage capacity.

These are conceptual examples only. No token is currently issued, and no physical resource is represented or guaranteed by this repository.

## Possible architecture direction

A future prototype could investigate a delay-tolerant model such as:

```text
Local Mars ledger/state
        ↓
Local validation and operation
        ↓
Signed batch / checkpoint
        ↓
Delayed interplanetary transport
        ↓
Earth-side reconciliation
        ↓
Conflict / audit handling
```

Questions worth testing include:

1. Which operations must remain local when Earth is unreachable?
2. What state can safely be reconciled later?
3. How are conflicts detected and resolved?
4. Which resources require trusted measurement or external attestations?
5. What failure modes appear under long partitions and delayed checkpoints?
6. Is a blockchain actually useful here, or would a simpler signed replicated ledger be better?

That last question is intentional: the project should not assume blockchain is the answer before the problem is tested.

## Experiment 001 — delayed reconciliation

The first bounded prototype is in [`prototype/ledger_sim.py`](prototype/ledger_sim.py), with the frozen experiment contract in [`EXPERIMENT_001.md`](EXPERIMENT_001.md).

It models two isolated nodes with the same visible resource capacity. Each node may accept a reservation that is valid against its **locally visible** state. Their immutable operation histories are then exchanged after an artificial one-way delay.

The canonical v0.1 case deliberately makes Earth and Mars each reserve `60` units from a visible capacity of `100`. Both are locally consistent during the partition. After delayed reconciliation, both detect a combined reservation of `120` and report `CONFLICT_OVERCOMMITTED`.

This demonstrates conflict **detection**, not conflict resolution, consensus or a production ledger.

Run it locally with:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python prototype/ledger_sim.py
```

The repository quality workflow runs the same dependency-free test suite and a deterministic demo assertion.

## Current implementation

**Implemented today:**

- public concept document;
- dependency-free Python simulation of isolated local reservations;
- deterministic artificial one-way transport delay;
- immutable operation exchange and idempotent duplicate handling;
- fail-closed operation-identity collision detection;
- deterministic overcommitment detection after reconciliation;
- automated unit tests and CI candidate.

**Not implemented today:**

- a production ledger or consensus protocol;
- cryptographic signatures or authenticated transport;
- conflict-resolution policy;
- trusted resource measurement/oracles;
- Solidity smart contracts;
- a Layer-2 protocol;
- Chainlink or other oracle integration;
- Starlink integration;
- Tesla energy integration;
- SpaceX telemetry or cargo integration;
- Mars deployment;
- issued tokens or resource certificates.

## Relationship to named companies and technologies

Names such as SpaceX, Starlink, Tesla, Chainlink, Bitcoin and Ethereum may be useful reference points when discussing possible future infrastructure or design trade-offs.

**NEXST is not affiliated with, endorsed by, integrated with or authorized by those companies or projects.** Any future integration would require separate technical validation, permissions where applicable, and real interfaces that do not exist here today.

## Next engineering gate

Experiment 001 intentionally stops before choosing how a real system should resolve conflicts. After the exact candidate is tested, the next project decision is which bounded question Experiment 002 should answer, for example:

1. deterministic conflict-resolution policy;
2. signed checkpoint / tamper-detection model;
3. repeated partitions and reconnect cycles;
4. independent resource domains rather than one shared global capacity.

Only after such experiments should the project decide whether Solidity, an L2 design, a conventional database, signed append-only logs or another architecture is appropriate.

---

**NEXST remains an exploratory systems project. The goal is to turn ambitious ideas into reproducible engineering questions before making implementation claims.**
