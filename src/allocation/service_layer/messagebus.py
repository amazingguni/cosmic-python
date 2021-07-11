from typing import Type, Callable, Union
import logging
from tenacity import Retrying, RetryError, stop_after_attempt, wait_exponential
from allocation.domain import events, commands
from allocation.service_layer import unit_of_work, handlers

logger = logging.getLogger(__name__)
Message = Union[commands.Command, events.Event]


def handle(
        message: Message,
        uow: unit_of_work.AbstractUnitOfWork,):
    results = []
    queue = [message]
    while queue:
        message = queue.pop(0)
        if isinstance(message, events.Event):
            handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            cmd_result = handle_command(message, queue, uow)
            results.append(cmd_result)
        else:
            raise Exception(f'{message} was not an Event or Command')
    return results


def handle_event(
        event: events.Event,
        queue: list[Message],
        uow: unit_of_work.AbstractUnitOfWork):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            for attemp in Retrying(
                stop=stop_after_attempt,
                wait=wait_exponential()
            ):
                with attemp:
                    logging.debug(
                        f'handling event {event} with handler {handler}')
                    handler(event, uow=uow)
                    queue.extend(uow.collect_new_events())
        except RetryError as retry_failure:
            logger.error(
                f'Failed to handle event {retry_failure.last_attempt.attempt_number} times, ' +
                'giving up!')
            continue


def handle_command(
        command: commands.Command,
        queue: list[Message],
        uow: unit_of_work.AbstractUnitOfWork):
    logger.debug(f'handling command {command}')
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = handler(command, uow=uow)
        queue.extend(uow.collect_new_events())
        return result
    except Exception:
        logger.exception(f'Exception handling command {command}')
        raise


EVENT_HANDLERS = {
    events.Allocated: [handlers.publish_allocated_event],
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}  # type: dict[Type[events.Event], list[Callable]]

COMMAND_HANDLERS = {
    commands.CreateBatch: handlers.add_batch,
    commands.ChangeBatchQuantity: handlers.change_batch_quantity,
    commands.Allocate: handlers.allocate,
}  # type: dict[Type[commands.Command], Callable]
