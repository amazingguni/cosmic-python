from datetime import datetime
from http import HTTPStatus
from flask import Flask, request, jsonify

from allocation import views
from allocation import bootstrap
from allocation.domain import commands
from allocation.service_layer import unit_of_work
from allocation.service_layer.handlers import InvalidSku


bus = bootstrap.bootstrap()
app = Flask(__name__)


@app.route('/allocate', methods=['POST'])
def allocate_endpoint():
    try:
        command = commands.Allocate(
            request.json['order_id'], request.json['sku'], request.json['quantity'])
        bus.handle(command)
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
    bus.handle(command)
    return 'OK', HTTPStatus.CREATED


@app.route('/allocations/<order_id>', methods=['GET'])
def allocations_view_endpoint(order_id):
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    result = views.allocations(order_id, uow)
    if not result:
        return 'not found', HTTPStatus.NOT_FOUND
    return jsonify(result), HTTPStatus.OK
