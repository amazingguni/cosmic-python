import abc
from . import models


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: models.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> models.Batch:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> list[models.Batch]:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch):
        self.session.add(batch)

    def get(self, reference) -> models.Batch:
        return self.session.query(models.Batch).filter_by(reference=reference).one()

    def list(self) -> list[models.Batch]:
        return self.session.query(models.Batch).all()
