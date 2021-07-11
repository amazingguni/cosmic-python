import logging
import json
import redis
from allocation import config
from allocation.adapters import orm
from allocation.domain import commands
from allocation.service_layer import messagebus, unit_of_work

r = redis.Redis(**config.get_redis_host_and_port())


def main():
    orm.start_mappers()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe('change_batch_quantity')

    for m in pubsub.listen():
        handle_change_batch_quantity(m)


def handle_change_batch_quantity(m):
    logging.debug(f'handling {m}')
    data = json.loads(m['data'])
    command = commands.ChangeBatchQuantity(
        batch_reference=data['batch_reference'], quantity=data['quantity'])
    messagebus.handle(command, uow=unit_of_work.SqlAlchemyUnitOfWork())


if __name__ == '__main__':
    main()
