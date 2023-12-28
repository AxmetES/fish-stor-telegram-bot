import requests

from urllib.parse import urljoin

from config import settings

s = requests.Session()
s.headers.update({"Authorization": f"Bearer {settings.API_TOKEN}"})
main_url = settings.MAIN_URL


def get_or_create_user(chat_id, users_reply, username):
    data = {f'filters[{chat_id}][$eq]': '{chat_id}'}

    user_ = get_api_handler("get", f"/api/users", data=data)
    if user_:
        return user_[0]
    else:
        data = {
            "username": username,
            "email": users_reply,
            "chat_id": chat_id,
            "role": 2,
            "password": "123456",
        }
        return get_api_handler("post", "/api/users", data=data)


def get_products():
    return get_api_handler("get", "/api/products")


def get_product(query):
    return get_api_handler("get", f"/api/products/{query}")


def get_picture(query):
    payload = {
        'populate': 'picture'
    }
    return get_api_handler("get", f'/api/products/{query}', params=payload)


def create_order(query):
    data = {"data": {"weight": 0.5, "product": {"connect": [int(query)]}}}
    return get_api_handler("post", "/api/orders", data=data)


def get_cart(chat_id):
    data = {f'filters[{chat_id}][$eq]': chat_id}
    return get_api_handler("get", f"/api/carts", data=data)


def get_or_create_cart(chat_id, order):
    cart = get_cart(chat_id)
    if not cart["data"]:
        data = {
            "data": {
                "chat_id": chat_id,
                "orders": {"connect": [order["data"]["id"]]},
            }
        }
        return get_api_handler("post", "/api/carts", data=data)
    else:
        data = {
            "data": {
                "orders": {"connect": [order["data"]["id"]]},
            }
        }
        return get_api_handler("put", f'/api/carts/{cart["data"][0]["id"]}', data=data)


def get_orders(chat_id):
    orders = []
    carts = get_api_handler("get", "/api/carts?populate[orders][populate][0]=product")
    for cart in carts["data"]:
        if cart["attributes"]["chat_id"] == str(chat_id):
            orders = cart["attributes"]["orders"]["data"]
    return orders


def del_order(id_):
    get_api_handler("del", f"/api/orders/{id_}")


def add_user_to_cart(chat_id, users_reply, username):
    user_ = get_or_create_user(chat_id, users_reply, username)
    cart = get_cart(chat_id)
    data = {
        "data": {
            "users_permissions_user": user_["id"],
        }
    }
    return get_api_handler("put", f'/api/carts/{cart["data"][0]["id"]}', data=data)


def get_api_handler(method, url, data=None, params=None):
    methods = {"post": s.post, "get": s.get, "put": s.put, "del": s.delete}
    request_url = urljoin(main_url, url)
    r = methods[method](url=request_url, json=data, params=params)
    r.raise_for_status()
    content_type = r.headers.get("Content-Type")
    if "application/json" in content_type:
        return r.json()
    return r
