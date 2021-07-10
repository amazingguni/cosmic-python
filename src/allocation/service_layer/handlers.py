from allocation.adapters import email
from allocation.domain import model, events, commands
from allocation.domain.model import OrderLine, Batch
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


def send_out_of_stock_notification(event: events.OutOfStock,
                                   uow: AbstractUnitOfWork):
    email.send(
        'stock@made.com',
        f'Out of stock for {event.sku}',
    )


def change_batch_quantity(
        command: commands.ChangeBatchQuantity,
        uow: AbstractUnitOfWork):
    with uow:
        product = uow.products.get_by_batch_reference(
            batch_reference=command.reference)
        product.change_batch_quantity(
            reference=command.reference, quantity=command.quantity)
        uow.commit()
