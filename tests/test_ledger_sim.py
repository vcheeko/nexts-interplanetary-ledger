import unittest

from prototype.ledger_sim import DelayedLink, LedgerNode, Reservation, demo


class DelayLedgerSimulationTests(unittest.TestCase):
    def test_partition_is_locally_valid_then_reconciliation_detects_overcommit(self):
        earth = LedgerNode("earth", {"energy_kwh": 100})
        mars = LedgerNode("mars", {"energy_kwh": 100})
        earth.reserve("energy_kwh", 60, created_at=0)
        mars.reserve("energy_kwh", 60, created_at=0)

        self.assertEqual(earth.reconciliation()["status"], "CONSISTENT")
        self.assertEqual(mars.reconciliation()["status"], "CONSISTENT")

        link = DelayedLink(delay_seconds=180)
        link.send(earth, mars, sent_at=1)
        link.send(mars, earth, sent_at=1)
        self.assertEqual(link.deliver_due(now=180), 0)
        self.assertEqual(len(earth.operations), 1)
        self.assertEqual(len(mars.operations), 1)

        self.assertEqual(link.deliver_due(now=181), 2)
        self.assertEqual(earth.reconciliation()["status"], "CONFLICT_OVERCOMMITTED")
        self.assertEqual(mars.reconciliation()["status"], "CONFLICT_OVERCOMMITTED")
        self.assertEqual(earth.remaining("energy_kwh"), -20)
        self.assertEqual(mars.remaining("energy_kwh"), -20)

    def test_duplicate_merge_is_idempotent(self):
        earth = LedgerNode("earth", {"cargo_kg": 100})
        mars = LedgerNode("mars", {"cargo_kg": 100})
        earth.reserve("cargo_kg", 10, created_at=0)

        self.assertEqual(mars.merge(earth.operations), 1)
        self.assertEqual(mars.merge(earth.operations), 0)
        self.assertEqual(len(mars.operations), 1)

    def test_operation_identity_collision_fails_closed(self):
        node = LedgerNode("earth", {"energy_kwh": 100})
        original = Reservation("mars:1", "mars", 1, "energy_kwh", 10, 0)
        conflicting = Reservation("mars:1", "mars", 1, "energy_kwh", 20, 0)

        self.assertEqual(node.merge([original]), 1)
        with self.assertRaises(ValueError):
            node.merge([conflicting])

    def test_local_node_rejects_reservation_beyond_visible_capacity(self):
        node = LedgerNode("mars", {"energy_kwh": 100})
        node.reserve("energy_kwh", 80, created_at=0)
        with self.assertRaises(ValueError):
            node.reserve("energy_kwh", 21, created_at=1)

    def test_demo_returns_same_reconciled_operation_set_on_both_nodes(self):
        result = demo(delay_seconds=180)
        self.assertEqual(result["before_delivery"]["earth_operation_count"], 1)
        self.assertEqual(result["before_delivery"]["mars_operation_count"], 1)
        self.assertEqual(result["after_reconciliation"]["earth"]["operation_count"], 2)
        self.assertEqual(result["after_reconciliation"]["mars"]["operation_count"], 2)
        self.assertEqual(result["after_reconciliation"]["earth"]["status"], "CONFLICT_OVERCOMMITTED")
        self.assertEqual(result["after_reconciliation"]["mars"]["status"], "CONFLICT_OVERCOMMITTED")

    def test_zero_delay_can_deliver_immediately(self):
        earth = LedgerNode("earth", {"energy_kwh": 100})
        mars = LedgerNode("mars", {"energy_kwh": 100})
        earth.reserve("energy_kwh", 10, created_at=0)
        link = DelayedLink(delay_seconds=0)
        self.assertEqual(link.send(earth, mars, sent_at=5), 5)
        self.assertEqual(link.deliver_due(now=5), 1)
        self.assertEqual(mars.reserved("energy_kwh"), 10)


if __name__ == "__main__":
    unittest.main()
