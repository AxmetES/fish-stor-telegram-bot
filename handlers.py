import requests

from urllib.parse import urljoin

from config import settings

s = requests.Session()
s.headers.update({"Authorization": f"Bearer {settings.API_TOKEN}"})
main_url = settings.MAIN_URL


def get_or_create_user(chat_id, users_reply, username):
    data = {f'filters[{chat_id}][$eq]': '{chat_id}'}
    request_url = urljoin(main_url, f"/api/users")
    r = s.get(url=request_url, json=data)
    r.raise_for_status()
    if r:
        return r.json()[0]
    else:
        data = {
            "username": username,
            "email": users_reply,
            "chat_id": chat_id,
            "role": 2,
            "password": "123456",
        }
        request_url = urljoin(main_url, "/api/users")
        r = s.post(url=request_url, json=data)
        r.raise_for_status()
    content_type = r.headers.get("Content-Type")
    if "application/json" in content_type:
        return r.json()
    return r


def get_products():
    request_url = urljoin(main_url, "/api/products")
    r = s.get(url=request_url)
    r.raise_for_status()
    content_type = r.headers.get("Content-Type")
    if "application/json" in content_type:
        return r.json()
    return r


def get_product(query):
    request_url = urljoin(main_url, f"/api/products/{query}")
    r = s.get(url=request_url)
    r.raise_for_status()
    content_type = r.headers.get("Content-Type")
    if "application/json" in content_type:
        return r.json()
    return r


def get_picture(query):
    payload = {
        'populate': 'picture'
    }
    request_url = urljoin(main_url, f'/api/products/{query}')
    r = s.get(url=request_url, params=payload)
    r.raise_for_status()
    content_type = r.headers.get("Content-Type")
    if "application/json" in content_type:
        return r.json()
    return r


def create_order(query):
    data = {"data": {"weight": 0.5, "product": {"connect": [int(query)]}}}
    request_url = urljoin(main_url, "/api/orders")
    r = s.post(url=request_url, json=data)
    r.raise_for_status()
    content_type = r.headers.get("Content-Type")
    if "application/json" in content_type:
        return r.json()
    return r


def get_cart(chat_id):
    data = {f'filters[{chat_id}][$eq]': chat_id}
    request_url = urljoin(main_url, f"/api/carts")
    r = s.get(url=request_url, json=data)
    r.raise_for_status()
    content_type = r.headers.get("Content-Type")
    if "application/json" in content_type:
        return r.json()
    return r


def get_or_create_cart(chat_id, order):
    cart = get_cart(chat_id)
    if not cart["data"]:
        data = {
            "data": {
                "chat_id": chat_id,
                "orders": {"connect": [order["data"]["id"]]},
            }
        }
        request_url = urljoin(main_url, "/api/carts")
        r = s.post(url=request_url, json=data)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type")
    else:
        data = {
            "data": {
                "orders": {"connect": [order["data"]["id"]]},
            }
        }
        request_url = urljoin(main_url,f'/api/carts/{cart["data"][0]["id"]}')
        r = s.put(url=request_url, json=data)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type")
    if "application/json" in content_type:
        return r.json()
    return r


def get_orders(chat_id):
    orders = []
    request_url = urljoin(main_url, "/api/carts?populate[orders][populate][0]=product")
    cart = s.get(url=request_url)
    cart.raise_for_status()
    for product in cart.json()["data"]:
        if product["attributes"]["chat_id"] == str(chat_id):
            orders = product["attributes"]["orders"]["data"]
    return orders


def del_order(id_):
    request_url = urljoin(main_url, f"/api/orders/{id_}")
    r = s.delete(url=request_url)
    r.raise_for_status()
    content_type = r.headers.get("Content-Type")
    if "application/json" in content_type:
        return r.json()
    return r


def add_user_to_cart(chat_id, users_reply, username):
    user_ = get_or_create_user(chat_id, users_reply, username)
    cart = get_cart(chat_id)
    data = {
        "data": {
            "users_permissions_user": user_["id"],
        }
    }
    request_url = urljoin(main_url, f'/api/carts/{cart["data"][0]["id"]}')
    r = s.put(url=request_url, json=data)
    r.raise_for_status()
    content_type = r.headers.get("Content-Type")
    if "application/json" in content_type:
        return r.json()
    return r

