from allocation.adapters import orm
import abc

from allocation.domain import model


class AbstractProductRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: set[model.Product]

    def add(self, product: model.Product):
        self._add(product)
        self.seen.add(product)

    def get(self, sku) -> model.Product:
        product = self._get(sku)
        if product:
            self.seen.add(product)
        return product

    def get_by_batch_reference(self, batch_reference) -> model.Product:
        product = self._get_by_batch_reference(batch_reference)
        if product:
            self.seen.add(product)
        return product

    @abc.abstractmethod
    def _add(self, product: model.Product):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, sku) -> model.Product:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_batch_reference(self, batch_reference) -> model.Product:
        raise NotImplementedError


class SqlAlchemyProductRepository(AbstractProductRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, product):
        self.session.add(product)

    def _get(self, sku) -> model.Product:
        return self.session.query(model.Product).filter_by(sku=sku).first()

    def _get_by_batch_reference(self, batch_reference):
        return (
            self.session.query(model.Product).join(model.Batch).filter(
                orm.batches.c.reference == batch_reference).first()
        )
