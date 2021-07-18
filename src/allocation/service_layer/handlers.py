from dataclasses import asdict
from typing import Type, Callable

from allocation.adapters import redis_eventpublisher
from allocation.adapters.notifications import AbstractNotifications
from allocation.domain import model, events, commands
from allocation.domain.model import OrderLine, Batch
from allocation.service_layer import unit_of_work
from allocation.service_layer.unit_of_work import AbstractUnitOfWork


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def add_batch(command: commands.CreateBatch,
              uow: AbstractUnitOfWork) -> None:
    with uow:
        product = uow.products.get(sku=command.sku)
        if not product:
            product = model.Product(command.sku, batches=[])
            uow.products.add(product)
        product.batches.append(
            Batch(command.reference, command.sku, command.quantity, command.eta))
        uow.commit()


def allocate(command: commands.Allocate, uow: AbstractUnitOfWork) -> str:
    line = OrderLine(command.order_id, command.sku, command.quantity)
    with uow:
        product = uow.products.get(line.sku)
        if not product:
            raise InvalidSku(f'Invalid sku {line.sku}')
        batchref = product.allocate(line)
        uow.commit()
    return batchref


def reallocate(event: events.Deallocated, uow: AbstractUnitOfWork) -> str:
    with uow:
        product = uow.products.get(sku=event.sku)
        product.events.append(commands.Allocate(**asdict(event)))
        uow.commit


def send_out_of_stock_notification(
        event: events.OutOfStock,
        notifications: AbstractNotifications):
    notifications.send(
        'stock@made.com',
        f'Out of stock for {event.sku}',
    )


def change_batch_quantity(
        command: commands.ChangeBatchQuantity,
        uow: AbstractUnitOfWork):
    with uow:
        product = uow.products.get_by_batch_reference(
            batch_reference=command.batch_reference)
        product.change_batch_quantity(
            reference=command.batch_reference, quantity=command.quantity)
        uow.commit()


def publish_allocated_event(
    event: events.Allocated,
    uow: unit_of_work.AbstractUnitOfWork,


):
    redis_eventpublisher.publish('line_allocated', event)


def add_allocation_to_read_model(
    event: events.Allocated,
    uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            '''
            INSERT INTO allocations_view (order_id, sku, batch_reference)
            VALUES (:order_id, :sku, :batch_reference)
            ''',
            dict(order_id=event.order_id, sku=event.sku,
                 batch_reference=event.batch_reference)
        )
        uow.commit()


def remove_allocation_from_read_model(
    event: events.Deallocated,
    uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            '''
            DELETE FROM allocations_view
            WHERE order_id = :order_id AND sku = :sku
            ''',
            dict(order_id=event.order_id, sku=event.sku)
        )
        uow.commit()


EVENT_HANDLERS = {
    events.Allocated: [
        publish_allocated_event,
        add_allocation_to_read_model,
    ],
    events.Deallocated: [
        remove_allocation_from_read_model,
        reallocate,
    ],
    events.OutOfStock: [send_out_of_stock_notification],
}  # type: dict[Type[events.Event], list[Callable]]

COMMAND_HANDLERS = {
    commands.CreateBatch: add_batch,
    commands.ChangeBatchQuantity: change_batch_quantity,
    commands.Allocate: allocate,
}  # type: dict[Type[commands.Command], Callable]
