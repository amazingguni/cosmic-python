from typing import Optional
from datetime import date

from allocation.domain import model
from allocation.domain.model import OrderLine, Batch
from allocation.service_layer.unit_of_work import AbstractUnitOfWork


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date],
              uow: AbstractUnitOfWork) -> None:
    with uow:
        product = uow.products.get(sku=sku)
        if not product:
            product = model.Product(sku, batches=[])
            uow.products.add(product)
        product.batches.append(Batch(ref, sku, qty, eta))
        uow.commit()


def allocate(order_id: str, sku: str, qty: int, uow: AbstractUnitOfWork) -> str:
    line = OrderLine(order_id, sku, qty)
    with uow:
        product = uow.products.get(line.sku)
        if not product:
            raise InvalidSku(f'Invalid sku {line.sku}')
        batchref = product.allocate(line)
        uow.commit()
    return batchref
