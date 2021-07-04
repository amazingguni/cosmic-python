from allocation.adapters import email
from typing import Optional
from datetime import date
from allocation.domain import model, events
from allocation.domain.model import OrderLine, Batch
from allocation.service_layer.unit_of_work import AbstractUnitOfWork


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def add_batch(event: events.BatchCreated,
              uow: AbstractUnitOfWork) -> None:
    with uow:
        product = uow.products.get(sku=event.sku)
        if not product:
            product = model.Product(event.sku, batches=[])
            uow.products.add(product)
        product.batches.append(
            Batch(event.reference, event.sku, event.quantity, event.eta))
        uow.commit()


def allocate(event: events.AllocationRequired, uow: AbstractUnitOfWork) -> str:
    line = OrderLine(event.order_id, event.sku, event.quantity)
    with uow:
        product = uow.products.get(line.sku)
        if not product:
            raise InvalidSku(f'Invalid sku {line.sku}')
        batchref = product.allocate(line)
        uow.commit()
    return batchref


def send_out_of_stock_notification(event: events.OutOfStock,
                                   uow: AbstractUnitOfWork):
    email.send(
        'stock@made.com',
        f'Out of stock for {event.sku}',
    )


def change_batch_quantity(
        event: events.BatchQuantityChanged,
        uow: AbstractUnitOfWork):
    with uow:
        product = uow.products.get_by_batch_reference(
            batch_reference=event.reference)
        product.change_batch_quantity(
            reference=event.reference, quantity=event.quantity)
        uow.commit()
