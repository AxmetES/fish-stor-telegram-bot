import requests

from urllib.parse import urljoin


def get_or_create_user(chat_id, main_url, headers, users_reply, username):
    data = {f'filters[{chat_id}][$eq]': '{chat_id}'}
    request_url = urljoin(main_url, f"/api/users")
    r = requests.get(url=request_url, json=data, headers=headers)
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
        r = requests.post(url=request_url, json=data, headers=headers)
        r.raise_for_status()
    content_type = r.headers.get("Content-Type")
    if "application/json" in content_type:
        return r.json()
    return r


def get_products(main_url, headers):
    request_url = urljoin(main_url, "/api/products")
    r = requests.get(url=request_url, headers=headers)
    r.raise_for_status()
    content_type = r.headers.get("Content-Type")
    if "application/json" in content_type:
        return r.json()
    return r


def get_product(query, main_url, headers):
    request_url = urljoin(main_url, f"/api/products/{query}")
    r = requests.get(url=request_url, headers=headers)
    r.raise_for_status()
    content_type = r.headers.get("Content-Type")
    if "application/json" in content_type:
        return r.json()
    return r


def get_picture(query, main_url, headers):
    payload = {
        'populate': 'picture'
    }
    request_url = urljoin(main_url, f'/api/products/{query}')
    r = requests.get(url=request_url, params=payload, headers=headers)
    r.raise_for_status()
    if "application/json" in r.headers.get("Content-Type"):
        return r.json()
    return r


def create_order(query, main_url, headers):
    data = {"data": {"weight": 0.5, "product": {"connect": [int(query)]}}}
    request_url = urljoin(main_url, "/api/orders")
    r = requests.post(url=request_url, json=data, headers=headers)
    r.raise_for_status()
    content_type = r.headers.get("Content-Type")
    if "application/json" in content_type:
        return r.json()
    return r


def get_cart(chat_id, main_url, headers):
    data = {f'filters[{chat_id}][$eq]': chat_id}
    request_url = urljoin(main_url, f"/api/carts")
    r = requests.get(url=request_url, json=data, headers=headers)
    r.raise_for_status()
    content_type = r.headers.get("Content-Type")
    if "application/json" in content_type:
        return r.json()
    return r


def get_or_create_cart(chat_id, order, main_url, headers):
    cart = get_cart(chat_id, main_url, headers=headers)
    if not cart["data"]:
        data = {
            "data": {
                "chat_id": chat_id,
                "orders": {"connect": [order["data"]["id"]]},
            }
        }
        request_url = urljoin(main_url, "/api/carts")
        r = requests.post(url=request_url, json=data, headers=headers)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type")
    else:
        data = {
            "data": {
                "orders": {"connect": [order["data"]["id"]]},
            }
        }
        request_url = urljoin(main_url, f'/api/carts/{cart["data"][0]["id"]}')
        r = requests.put(url=request_url, json=data, headers=headers)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type")
    if "application/json" in content_type:
        return r.json()
    return r


def get_orders(chat_id, main_url, headers):
    orders = []
    request_url = urljoin(main_url, "/api/carts?populate[orders][populate][0]=product")
    cart = requests.get(url=request_url, headers=headers)
    cart.raise_for_status()
    for product in cart.json()["data"]:
        if product["attributes"]["chat_id"] == str(chat_id):
            orders = product["attributes"]["orders"]["data"]
    return orders


def del_order(id_, main_url, headers):
    request_url = urljoin(main_url, f"/api/orders/{id_}")
    r = requests.delete(url=request_url, headers=headers)
    r.raise_for_status()
    content_type = r.headers.get("Content-Type")
    if "application/json" in content_type:
        return r.json()
    return r


def add_user_to_cart(chat_id, main_url, headers, users_reply, username):
    user_ = get_or_create_user(chat_id, main_url, headers, users_reply, username)
    cart = get_cart(chat_id, main_url, headers)
    data = {
        "data": {
            "users_permissions_user": user_["id"],
        }
    }
    request_url = urljoin(main_url, f'/api/carts/{cart["data"][0]["id"]}')
    r = requests.put(url=request_url, json=data, headers=headers)
    r.raise_for_status()
    content_type = r.headers.get("Content-Type")
    if "application/json" in content_type:
        return r.json()
    return r
