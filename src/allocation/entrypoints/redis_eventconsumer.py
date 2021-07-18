import logging
import json
import redis
from allocation import config, bootstrap
from allocation.domain import commands
from allocation.service_layer import messagebus, unit_of_work

r = redis.Redis(**config.get_redis_host_and_port())

logger = logging.getLogger(__name__)


def main():
    logger.info('Redis pubsub starting')
    bus = bootstrap.bootstrap()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe('change_batch_quantity')

    for m in pubsub.listen():
        handle_change_batch_quantity(m, bus)


def handle_change_batch_quantity(m, bus):
    logger.debug(f'handling {m}')
    data = json.loads(m['data'])
    command = commands.ChangeBatchQuantity(
        batch_reference=data['batch_reference'], quantity=data['quantity'])
    bus.handle(command)


if __name__ == '__main__':
    main()
