from io import BytesIO
from urllib.parse import urljoin

import requests


class Strapi:
    def __init__(self, main_url, headers):
        self.main_url = main_url
        self.s = requests.Session()
        self.s.headers.update(headers)

    def get_or_create_user(self, chat_id, users_reply, username):
        data = {f'filters[{chat_id}][$eq]': '{chat_id}'}
        request_url = urljoin(self.main_url, "/api/users")
        r = self.s.get(url=request_url, json=data)
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
            request_url = urljoin(self.main_url, "/api/users")
            r = self.s.post(url=request_url, json=data)
            r.raise_for_status()
        content_type = r.headers.get("Content-Type")
        if "application/json" in content_type:
            return r.json()
        return r

    def get_products(self):
        print(self.main_url)
        print(type(self.main_url))
        request_url = urljoin(self.main_url, "/api/products")
        r = self.s.get(url=request_url)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type")
        if "application/json" in content_type:
            return r.json()
        return r

    def get_product(self, query):
        request_url = urljoin(self.main_url, f"/api/products/{query}")
        r = self.s.get(url=request_url)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type")
        if "application/json" in content_type:
            return r.json()
        return r

    def get_picture(self, query):
        payload = {
            'populate': 'picture'
        }
        request_url = urljoin(self.main_url, f'/api/products/{query}')
        r = self.s.get(url=request_url, params=payload)
        r.raise_for_status()
        if "application/json" in r.headers.get("Content-Type"):
            return r.json()
        return r

    def create_order(self, query):
        data = {"data": {"weight": 0.5, "product": {"connect": [int(query)]}}}
        request_url = urljoin(self.main_url, "/api/orders")
        r = self.s.post(url=request_url, json=data)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type")
        if "application/json" in content_type:
            return r.json()
        return r

    def get_cart(self, chat_id):
        data = {f'filters[{chat_id}][$eq]': chat_id}
        request_url = urljoin(self.main_url, f"/api/carts")
        r = self.s.get(url=request_url, json=data)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type")
        if "application/json" in content_type:
            return r.json()
        return r

    def get_or_create_cart(self, chat_id, order):
        cart = self.get_cart(chat_id)
        if not cart["data"]:
            data = {
                "data": {
                    "chat_id": chat_id,
                    "orders": {"connect": [order["data"]["id"]]},
                }
            }
            request_url = urljoin(self.main_url, "/api/carts")
            r = self.s.post(url=request_url, json=data)
            r.raise_for_status()
            content_type = r.headers.get("Content-Type")
        else:
            data = {
                "data": {
                    "orders": {"connect": [order["data"]["id"]]},
                }
            }
            request_url = urljoin(self.main_url, f'/api/carts/{cart["data"][0]["id"]}')
            r = self.s.put(url=request_url, json=data)
            r.raise_for_status()
            content_type = r.headers.get("Content-Type")
        if "application/json" in content_type:
            return r.json()
        return r

    def get_orders(self, chat_id):
        orders = []
        request_url = urljoin(self.main_url, "/api/carts?populate[orders][populate][0]=product")
        cart = self.s.get(url=request_url)
        cart.raise_for_status()
        for product in cart.json()["data"]:
            if product["attributes"]["chat_id"] == str(chat_id):
                orders = product["attributes"]["orders"]["data"]
        return orders

    def del_order(self, id_):
        request_url = urljoin(self.main_url, f"/api/orders/{id_}")
        r = self.s.delete(url=request_url)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type")
        if "application/json" in content_type:
            return r.json()
        return r

    def add_user_to_cart(self, chat_id, users_reply, username):
        user_ = self.get_or_create_user(chat_id, users_reply, username)
        cart = self.get_cart(chat_id)
        data = {
            "data": {
                "users_permissions_user": user_["id"],
            }
        }
        request_url = urljoin(self.main_url, f'/api/carts/{cart["data"][0]["id"]}')
        r = self.s.put(url=request_url, json=data)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type")
        if "application/json" in content_type:
            return r.json()
        return r

    def get_img(self, pic_url):
        request_url = urljoin(self.main_url, pic_url)
        response = requests.get(url=request_url)
        response.raise_for_status()
        image_data = BytesIO(response.content)
        return image_data
