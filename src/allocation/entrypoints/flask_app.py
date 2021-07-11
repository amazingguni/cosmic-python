from datetime import datetime
from http import HTTPStatus
from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from allocation import views
from allocation import config
from allocation.domain import commands
from allocation.adapters import orm
from allocation.service_layer import unit_of_work, messagebus
from allocation.service_layer.handlers import InvalidSku


orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


@app.route('/allocate', methods=['POST'])
def allocate_endpoint():
    try:
        command = commands.Allocate(
            request.json['order_id'], request.json['sku'], request.json['quantity'])
        messagebus.handle(
            command, unit_of_work.SqlAlchemyUnitOfWork())
    except InvalidSku as e:
        return {'message': str(e)}, HTTPStatus.BAD_REQUEST
    return 'OK', HTTPStatus.ACCEPTED


@app.route('/add-batch', methods=['POST'])
def add_batch():
    eta = request.json['eta']
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    command = commands.CreateBatch(
        request.json['reference'],
        request.json['sku'],
        request.json['quantity'],
        eta)
    messagebus.handle(command, unit_of_work.SqlAlchemyUnitOfWork())
    return 'OK', HTTPStatus.CREATED


@app.route('/allocations/<order_id>', methods=['GET'])
def allocations_view_endpoint(order_id):
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    result = views.allocations(order_id, uow)
    if not result:
        return 'not found', HTTPStatus.NOT_FOUND
    return jsonify(result), HTTPStatus.OK
