from typing import Type, Callable, Union
import logging
from allocation.domain import events, commands
from allocation.service_layer import unit_of_work, handlers

logger = logging.getLogger(__name__)
Message = Union[commands.Command, events.Event]


class MessageBus:
    def __init__(
        self,
        uow: unit_of_work.AbstractUnitOfWork,
        event_handlers: dict[type[events.Event], list[callable]],
        command_handlers: dict[type[events.Event], callable],
    ):
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers

    def handle(self, message: Message):
        self.queue = [message]
        while self.queue:
            message = self.queue.pop(0)
            if isinstance(message, events.Event):
                self.handle_event(message)
            elif isinstance(message, commands.Command):
                self.handle_command(message)
            else:
                raise Exception(f'{message} was not an Event or Command')

    def handle_event(self, event: events.Event):
        for handler in self.event_handlers[type(event)]:
            try:
                logging.debug(
                    f'handling event {event} with handler {handler}')
                handler(event)
                self.queue.extend(self.uow.collect_new_events())
            except Exception:
                logger.error(
                    f'Exception handling event {event}')
                continue

    def handle_command(self, command: commands.Command):
        logger.debug(f'handling command {command}')
        try:
            handler = self.command_handlers[type(command)]
            handler(command)
            self.queue.extend(self.uow.collect_new_events())
        except Exception:
            logger.exception(f'Exception handling command {command}')
            raise
