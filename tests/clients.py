from typing import Any, Dict, Union

import jwt
from django.conf import settings
from ninja import NinjaAPI, Router
from ninja.testing import TestClient
from ninja.testing.client import NinjaResponse


class AuthClient(TestClient):
    def __init__(
        self, router_or_app: Union[NinjaAPI, Router], token: str
    ) -> None:
        self.router_or_app = router_or_app
        self.token = token

    def get(
        self,
        path: str,
        data: Dict = {},
        **request_params: Dict,
    ) -> "NinjaResponse":
        request_params["headers"] = {"Authorization": f"Bearer {self.token}"}
        return super().get(path, data, **request_params)

    def post(
        self,
        path: str,
        data: Dict = {},
        json: Any = None,
        **request_params: Any,
    ) -> "NinjaResponse":
        request_params["headers"] = {"Authorization": f"Bearer {self.token}"}
        return super().post(path, data, json, **request_params)

    def patch(
        self,
        path: str,
        data: Dict = ...,
        json: Any = None,
        **request_params: Any,
    ) -> "NinjaResponse":
        request_params["headers"] = {"Authorization": f"Bearer {self.token}"}
        return super().patch(path, data, json, **request_params)

    def put(
        self,
        path: str,
        data: Dict = ...,
        json: Any = None,
        **request_params: Any,
    ) -> "NinjaResponse":
        request_params["headers"] = {"Authorization": f"Bearer {self.token}"}
        return super().put(path, data, json, **request_params)

    def delete(
        self,
        path: str,
        data: Dict = ...,
        json: Any = None,
        **request_params: Any,
    ) -> "NinjaResponse":
        request_params["headers"] = {"Authorization": f"Bearer {self.token}"}
        return super().delete(path, data, json, **request_params)
