from datetime import datetime
from http import HTTPStatus
from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from allocation import config
from allocation.domain import events
from allocation.adapters import orm
from allocation.service_layer import unit_of_work, messagebus, handlers


orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


@app.route('/allocate', methods=['POST'])
def allocate_endpoint():
    try:
        event = events.AllocationRequired(
            request.json['order_id'], request.json['sku'], request.json['quantity'])
        results = messagebus.handle(event, unit_of_work.SqlAlchemyUnitOfWork())
        batchref = results.pop(0)
    except handlers.InvalidSku as e:
        return {'message': str(e)}, HTTPStatus.BAD_REQUEST
    return {'batchref': batchref}, 201


@app.route('/add_batch', methods=['POST'])
def add_batch():
    eta = request.json['eta']
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    event = events.BatchCreated(
        request.json['reference'],
        request.json['sku'],
        request.json['quantity'],
        eta)
    messagebus.handle(event, unit_of_work.SqlAlchemyUnitOfWork())
    return 'OK', HTTPStatus.CREATED
