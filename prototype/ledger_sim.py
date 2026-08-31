"""NEXST delay-tolerant ledger experiment v0.1.

This module intentionally models a small engineering question rather than a
cryptocurrency. Two isolated nodes can accept local reservations, exchange
immutable operations after an artificial one-way delay, and detect resource
overcommitment during reconciliation.

The experiment is dependency-free and does not implement signatures,
consensus, smart contracts, networking, or real resource attestations.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import heapq
import json
from typing import Dict, Iterable, List, Mapping, Tuple


@dataclass(frozen=True)
class Reservation:
    op_id: str
    node_id: str
    sequence: int
    resource: str
    amount: int
    created_at: int

    def __post_init__(self) -> None:
        if not self.op_id:
            raise ValueError("op_id must be non-empty")
        if not self.node_id:
            raise ValueError("node_id must be non-empty")
        if self.sequence <= 0:
            raise ValueError("sequence must be positive")
        if not self.resource:
            raise ValueError("resource must be non-empty")
        if self.amount <= 0:
            raise ValueError("amount must be positive")
        if self.created_at < 0:
            raise ValueError("created_at cannot be negative")


class LedgerNode:
    """Local append-only reservation ledger with deterministic reconciliation."""

    def __init__(self, node_id: str, capacities: Mapping[str, int]) -> None:
        if not node_id:
            raise ValueError("node_id must be non-empty")
        if not capacities:
            raise ValueError("at least one resource capacity is required")
        if any(value < 0 for value in capacities.values()):
            raise ValueError("capacities cannot be negative")

        self.node_id = node_id
        self.capacities: Dict[str, int] = dict(capacities)
        self._operations: Dict[str, Reservation] = {}
        self._next_sequence = 1

    @property
    def operations(self) -> Tuple[Reservation, ...]:
        return tuple(
            sorted(
                self._operations.values(),
                key=lambda op: (op.created_at, op.node_id, op.sequence, op.op_id),
            )
        )

    def reserved(self, resource: str) -> int:
        return sum(op.amount for op in self._operations.values() if op.resource == resource)

    def remaining(self, resource: str) -> int:
        if resource not in self.capacities:
            raise KeyError(resource)
        return self.capacities[resource] - self.reserved(resource)

    def reserve(self, resource: str, amount: int, created_at: int) -> Reservation:
        """Accept a reservation using only the node's currently visible state."""

        if resource not in self.capacities:
            raise KeyError(resource)
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self.remaining(resource):
            raise ValueError("reservation exceeds locally visible capacity")

        sequence = self._next_sequence
        self._next_sequence += 1
        op = Reservation(
            op_id=f"{self.node_id}:{sequence}",
            node_id=self.node_id,
            sequence=sequence,
            resource=resource,
            amount=amount,
            created_at=created_at,
        )
        self._operations[op.op_id] = op
        return op

    def merge(self, operations: Iterable[Reservation]) -> int:
        """Merge immutable operations by identity; conflicting reuse fails closed."""

        added = 0
        for op in operations:
            existing = self._operations.get(op.op_id)
            if existing is not None:
                if existing != op:
                    raise ValueError(f"operation identity collision: {op.op_id}")
                continue
            self._operations[op.op_id] = op
            added += 1
        return added

    def reconciliation(self) -> Dict[str, object]:
        resources: Dict[str, Dict[str, object]] = {}
        overall = "CONSISTENT"
        for resource, capacity in sorted(self.capacities.items()):
            reserved = self.reserved(resource)
            remaining = capacity - reserved
            if remaining < 0:
                status = "CONFLICT_OVERCOMMITTED"
                overall = "CONFLICT_OVERCOMMITTED"
            else:
                status = "CONSISTENT"
            resources[resource] = {
                "capacity": capacity,
                "reserved": reserved,
                "remaining": remaining,
                "status": status,
            }
        return {
            "node_id": self.node_id,
            "status": overall,
            "resources": resources,
            "operation_count": len(self._operations),
        }


class DelayedLink:
    """Deterministic one-way transport queue with an artificial light-time delay."""

    def __init__(self, delay_seconds: int) -> None:
        if delay_seconds < 0:
            raise ValueError("delay_seconds cannot be negative")
        self.delay_seconds = delay_seconds
        self._queue: List[Tuple[int, int, LedgerNode, Tuple[Reservation, ...]]] = []
        self._counter = 0

    def send(self, sender: LedgerNode, receiver: LedgerNode, sent_at: int) -> int:
        if sent_at < 0:
            raise ValueError("sent_at cannot be negative")
        self._counter += 1
        delivery_at = sent_at + self.delay_seconds
        payload = sender.operations
        heapq.heappush(
            self._queue,
            (delivery_at, self._counter, receiver, payload),
        )
        return delivery_at

    def deliver_due(self, now: int) -> int:
        delivered_batches = 0
        while self._queue and self._queue[0][0] <= now:
            _, _, receiver, payload = heapq.heappop(self._queue)
            receiver.merge(payload)
            delivered_batches += 1
        return delivered_batches


def demo(delay_seconds: int = 180) -> Dict[str, object]:
    """Run the canonical partition/conflict/reconciliation demonstration."""

    capacities = {"energy_kwh": 100}
    earth = LedgerNode("earth", capacities)
    mars = LedgerNode("mars", capacities)
    link = DelayedLink(delay_seconds)

    earth.reserve("energy_kwh", 60, created_at=0)
    mars.reserve("energy_kwh", 60, created_at=0)

    earth_local = earth.reconciliation()
    mars_local = mars.reconciliation()

    earth_to_mars = link.send(earth, mars, sent_at=1)
    mars_to_earth = link.send(mars, earth, sent_at=1)
    link.deliver_due(now=1 + delay_seconds - 1 if delay_seconds else 1)
    before_delivery = {
        "earth_operation_count": len(earth.operations),
        "mars_operation_count": len(mars.operations),
    }
    link.deliver_due(now=1 + delay_seconds)

    return {
        "experiment": "NEXST_DELAY_LEDGER_SIM_0.1",
        "delay_seconds": delay_seconds,
        "scheduled_delivery": {
            "earth_to_mars": earth_to_mars,
            "mars_to_earth": mars_to_earth,
        },
        "local_before_reconciliation": {
            "earth": earth_local,
            "mars": mars_local,
        },
        "before_delivery": before_delivery,
        "after_reconciliation": {
            "earth": earth.reconciliation(),
            "mars": mars.reconciliation(),
        },
        "operations": [asdict(op) for op in earth.operations],
    }


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True))
