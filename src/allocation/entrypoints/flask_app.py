from http import HTTPStatus
from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.allocation import config
from src.allocation.domain import model
from src.allocation.adapters import orm, repository
from src.allocation.service_layer import services


orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


@app.route('/allocate', methods=['POST'])
def allocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    try:
        batchref = services.allocate(
            request.json['order_id'], request.json['sku'], request.json['qty'], repo, session)
    except (model.OutOfStock, services.InvalidSku) as e:
        return {'message': str(e)}, HTTPStatus.BAD_REQUEST
    return {'batchref': batchref}, 201
