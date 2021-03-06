import pytest
from allocation.adapters import repository
from allocation.domain import model

pytestmark = pytest.mark.usefixtures("mappers")


def test_get_by_batch_reference(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = repository.SqlAlchemyProductRepository(session)
    b1 = model.Batch(reference='b1', sku='sku1', quantity=100, eta=None)
    b2 = model.Batch(reference='b2', sku='sku1', quantity=100, eta=None)
    b3 = model.Batch(reference='b3', sku='sku2', quantity=100, eta=None)

    p1 = model.Product(sku='sku1', batches=[b1, b2])
    p2 = model.Product(sku='sku2', batches=[b3])

    repo.add(p1)
    repo.add(p2)

    assert repo.get_by_batch_reference('b2') == p1
    assert repo.get_by_batch_reference('b3') == p2
