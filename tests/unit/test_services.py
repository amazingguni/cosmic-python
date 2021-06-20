import pytest
from datetime import date, timedelta

from src.allocation.adapters import repository
from src.allocation.domain.model import Batch, OrderLine
from src.allocation.service_layer import services


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches: list[Batch]):
        self._batches = set(batches)

    def add(self, batch: Batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)

    @staticmethod
    def for_batch(ref, sku, qty, eta=None):
        return FakeRepository([
            Batch(ref, sku, qty, eta),
        ])


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    repo = FakeRepository.for_batch(
        'batch1', 'COMPLICATED-LAMP', 100, eta=None)

    result = services.allocate(
        'o1', 'COMPLICATED-LAMP', 10, repo, FakeSession())

    assert result == 'batch1'


def test_error_for_invalid_sku():
    repo = FakeRepository.for_batch(
        'b1', 'AREALSKU', 100, eta=None)
    with pytest.raises(services.InvalidSku, match='Invalid sku NONEXISTENTSKU'):
        services.allocate('o1', 'NONEXISTENTSKU', 10, repo, FakeSession())


def test_commits():
    repo = FakeRepository.for_batch(
        'b1', 'OMINOUS-MIRROR', 100, eta=None)
    session = FakeSession()

    services.allocate('o1', 'OMINOUS-MIRROR', 10, repo, session)
    assert session.committed is True


today = date.today()
tomorrow = today + timedelta(days=1)
later = today + timedelta(days=7)


def test_prefers_warehouse_batches_to_shipments():
    in_stock_batch = Batch('in-stock-batch', 'RETRO-CLOCK', 100, eta=None)
    shipment_batch = Batch('shipment-batch', 'RETRO-CLOCK', 100, eta=tomorrow)
    repo = FakeRepository([in_stock_batch, shipment_batch])
    session = FakeSession()

    services.allocate('oref', 'RETRO-CLOCK', 10, repo, session)

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100
