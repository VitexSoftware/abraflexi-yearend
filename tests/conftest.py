import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as app_module  # noqa: E402


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


@pytest.fixture
def connection():
    return {
        "url": "https://demo.abraflexi.eu:5434",
        "company": "demo",
        "user": "winstrom",
        "password": "winstrom",
    }


class FakeAbraFlexi:
    """Records constructor/call args and returns a scripted result."""

    instances = []

    def __init__(self, init=None, options=None):
        self.init = init
        self.options = options or {}
        self.evidence = self.options.get("evidence")
        self.default_url_params = {}
        self.calls = []
        FakeAbraFlexi.instances.append(self)

    def perform_request(self, url_suffix="", method="GET", format_type=None, binary=False):
        self.calls.append(("perform_request", url_suffix, method))
        if isinstance(self.result, Exception):
            raise self.result
        return self.result

    def get_all_from_abraflexi(self, params=None):
        self.calls.append(("get_all_from_abraflexi", params))
        if isinstance(self.result, Exception):
            raise self.result
        return self.result

    def insert_to_abraflexi(self, data=None):
        self.calls.append(("insert_to_abraflexi", data))
        if isinstance(self.result, Exception):
            raise self.result
        return self.result

    result = True


@pytest.fixture(autouse=True)
def reset_fake_instances():
    FakeAbraFlexi.instances = []
    yield
    FakeAbraFlexi.instances = []


def make_fake(result):
    """Build a FakeAbraFlexi subclass that always returns/raises `result`."""

    class _Fake(FakeAbraFlexi):
        pass

    _Fake.result = result
    return _Fake
