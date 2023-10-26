import requests

from config import settings

s = requests.Session()
s.headers.update({"Authorization": f"Bearer {settings.API_TOKEN}"})
main_url = "http://localhost:1337"


def get_or_create_user(chat_id, users_reply, username):
    user_ = get_api_handler("get", f"/api/users?filters[chat_id][$eq]={chat_id}")
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
        user_ = get_api_handler("post", "/api/users", data=data)
    return user_


def get_products():
    return get_api_handler("get", "/api/products")


def get_product(query):
    return get_api_handler("get", f"/api/products/{query}")


def get_picture(query):
    pic = get_api_handler("get", f"/api/products/{query}?populate=picture")
    return pic


def create_order(query):
    data = {"data": {"weight": 0.5, "product": {"connect": [int(query)]}}}
    return get_api_handler("post", "/api/orders", data=data)


def get_cart(chat_id):
    cart = get_api_handler("get", f"/api/carts?filters[chat_id][$eq]={chat_id}")
    return cart


def get_or_create_cart(chat_id, order):
    cart = get_cart(chat_id)
    if not cart["data"]:
        data = {
            "data": {
                "chat_id": chat_id,
                "orders": {"connect": [order["data"]["id"]]},
            }
        }
        cart = get_api_handler("post", "/api/carts", data=data)
    else:
        data = {
            "data": {
                "orders": {"connect": [order["data"]["id"]]},
            }
        }
        cart = get_api_handler("put", f'/api/carts/{cart["data"][0]["id"]}', data=data)
    return cart


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
    print(cart["data"][0]["id"])
    data = {
        "data": {
            "users_permissions_user": user_["id"],
        }
    }
    cart = get_api_handler("put", f'/api/carts/{cart["data"][0]["id"]}', data=data)
    return cart


def get_api_handler(method, url, data=None):
    methods = {"post": s.post, "get": s.get, "put": s.put, "del": s.delete}
    r = methods[method](url=main_url + url, json=data)
    content_type = r.headers.get("Content-Type")
    if "application/json" in content_type:
        return r.json()
    return r


if __name__ == "__main__":
    # user = get_or_create_user("6416664703", "fraktsia@gmail.com", "yerkin_as")
    add_user_to_cart("6416664703", "fraktsia@gmail.com", "yerkin_as")
