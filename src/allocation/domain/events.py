from dataclasses import dataclass
from typing import Optional
from datetime import date


class Event:
    pass


@dataclass
class BatchCreated(Event):
    reference: str
    sku: str
    quantity: int
    eta: Optional[date] = None


@dataclass
class OutOfStock(Event):
    sku: str


@dataclass
class AllocationRequired(Event):
    order_id: str
    sku: str
    quantity: int


@dataclass
class BatchQuantityChanged(Event):
    reference: str
    quantity: int
