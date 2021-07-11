import requests
from allocation import config


def post_to_add_batch(reference, sku, quantity, eta):
    url = config.get_api_url()
    r = requests.post(
        f'{url}/add-batch', json={
            'reference': reference, 'sku': sku, 'quantity': quantity, 'eta': eta}
    )
    assert r.status_code == 201


def post_to_allocate(order_id, sku, quantity, expect_success=True):
    url = config.get_api_url()
    r = requests.post(
        f'{url}/allocate', json={
            'order_id': order_id, 'sku': sku, 'quantity': quantity}
    )
    if expect_success:
        assert r.status_code == 202
    return r


def get_allocation(order_id):
    url = config.get_api_url()
    return requests.get(f'{url}/allocations/{order_id}')
