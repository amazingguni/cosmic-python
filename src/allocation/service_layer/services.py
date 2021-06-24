from typing import Optional
from datetime import date

from allocation.domain import model
from allocation.domain.model import OrderLine, Batch
from allocation.adapters.repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(order_id: str, sku: str, qty: int,
             repo: AbstractRepository, session) -> str:
    line = OrderLine(order_id, sku, qty)
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f'Invalid sku {line.sku}')
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date],
              repo: AbstractRepository, session) -> None:
    repo.add(Batch(ref, sku, qty, eta))
    session.commit()
