import logging
import json
import redis
from dataclasses import asdict
from allocation import config
from allocation.domain import events

r = redis.Redis(**config.get_redis_host_and_port())


def publish(channel, event: events.Event):
    print(channel, event)
    logging.debug(f'publishing: channel={channel}, event={event}')
    r.publish(channel, json.dumps(asdict(event)))
