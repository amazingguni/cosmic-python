from typing import Optional
from dataclasses import dataclass
from datetime import date


@dataclass(unsafe_hash=True)
class OrderLine:
    order_id: str
    sku: str
    quantity: int


class Batch:
    def __init__(self, ref: str, sku: str, quantity: int, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self.__purchased_quantity = quantity
        self.__allocations = set()

    def allocate(self, line: OrderLine):
        if not self.can_allocate(line):
            return
        self.__allocations.add(line)

    def can_allocate(self, line: OrderLine) -> bool:
        if self.sku != line.sku:
            return False
        return self.available_quantity >= line.quantity

    def deallocate(self, line: OrderLine):
        if line in self.__allocations:
            self.__allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.quantity for line in self.__allocations)

    @property
    def available_quantity(self) -> int:
        return self.__purchased_quantity - self.allocated_quantity

    def __eq__(self, other) -> bool:
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta


def allocate(line: OrderLine, batches: list[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f'Out of stock for sku {line.sku}')


class OutOfStock(Exception):
    pass
