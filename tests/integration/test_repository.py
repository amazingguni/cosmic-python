from allocation.domain.model import Batch, OrderLine
from allocation.adapters.repository import SqlAlchemyRepository


def test_repository_can_save_a_batch(session):
    batch = Batch('batch1', 'RUSTY-SOAPDISH', 100, eta=None)

    repo = SqlAlchemyRepository(session)
    repo.add(batch)
    session.commit()

    rows = session.execute(
        'SELECT reference, sku, purchased_quantity, eta FROM "batches"'
    )
    assert list(rows) == [('batch1', 'RUSTY-SOAPDISH', 100, None)]


def insert_order_line(session):
    session.execute(
        "INSERT INTO order_lines (order_id, sku, quantity)"
        ' VALUES ("order1", "GENERIC-SOFA", 12)'
    )
    [[orderline_id]] = session.execute(
        "SELECT id FROM order_lines WHERE order_id=:order_id AND sku=:sku",
        dict(order_id="order1", sku="GENERIC-SOFA"),
    )
    return orderline_id


def insert_batch(session, batch_id):
    session.execute(
        "INSERT INTO batches (reference, sku, purchased_quantity, eta)"
        ' VALUES (:batch_id, "GENERIC-SOFA", 100, null)',
        dict(batch_id=batch_id),
    )
    [[batch_id]] = session.execute(
        'SELECT id FROM batches WHERE reference=:batch_id AND sku="GENERIC-SOFA"',
        dict(batch_id=batch_id),
    )
    return batch_id


def insert_allocation(session, orderline_id, batch_id):
    session.execute(
        "INSERT INTO allocations (orderline_id, batch_id)"
        " VALUES (:orderline_id, :batch_id)",
        dict(orderline_id=orderline_id, batch_id=batch_id),
    )


def test_repository_can_retrieve_a_batch_with_allocations(session):
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session, 'batch1')
    insert_batch(session, 'batch2')
    insert_allocation(session, orderline_id, batch1_id)

    repo = SqlAlchemyRepository(session)
    retrieved = repo.get('batch1')

    expected = Batch('batch1', 'GENERIC-SOFA', 100, eta=None)
    assert retrieved == expected
    assert retrieved.sku == expected.sku
    assert retrieved.purchased_quantity == expected.purchased_quantity
    assert retrieved._allocations == {
        OrderLine('order1', 'GENERIC-SOFA', 12)
    }
