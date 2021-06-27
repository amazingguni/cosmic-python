import pytest

from allocation.adapters import repository
from allocation.domain.model import Product
from allocation.service_layer import services, unit_of_work


class FakeRepository(repository.AbstractProductRepository):
    def __init__(self, products: list[Product]):
        self._products = set(products)

    def add(self, product: Product):
        self._products.add(product)

    def get(self, sku):
        for p in self._products:
            if p.sku == sku:
                return p
        return None
        # return next(p for p in self._products if p.sku == sku)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch('batch1', 'COMPLICATED-LAMP', 100, None, uow)

    result = services.allocate(
        'o1', 'COMPLICATED-LAMP', 10, uow)

    assert result == 'batch1'


def test_allocate_errors_for_invalid_sku():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'AREALSKU', 100, None, uow)

    with pytest.raises(services.InvalidSku, match='Invalid sku NONEXISTENTSKU'):
        services.allocate('o1', 'NONEXISTENTSKU', 10, uow)


def test_commits():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'OMINOUS-MIRROR', 100, None, uow)

    services.allocate('o1', 'OMINOUS-MIRROR', 10, uow)
    assert uow.committed is True


def test_add_batch_for_new_product():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'CRUNCHY-ARMCHAIR', 100, None, uow)
    assert uow.products.get('CRUNCHY-ARMCHAIR') is not None
    assert uow.committed
