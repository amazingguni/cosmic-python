from allocation.service_layer import unit_of_work


def allocations(order_id: str, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        results = uow.session.execute(
            '''
            SELECT sku, batch_reference
            FROM allocations_view
            WHERE order_id = :order_id
            ''',
            dict(order_id=order_id)
        )
    return [{'sku': sku, 'batch_reference': batch_reference}
            for sku, batch_reference in results]
