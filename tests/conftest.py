import pytest
from app.core.config import get_app_settings
from app.db.config import close_db, init_db
from tortoise.contrib.test import finalizer, initializer
from tortoise.transactions import current_transaction_map

from tests.init_db import init_db_datas

settings = get_app_settings()


@pytest.fixture(scope="session", autouse=True)
def create_db(request):
    db_url = settings.database_url
    initializer(["app.db.table.karupu", "app.db.table.auth"], db_url="sqlite://:memory:")
    init_db_datas()
    request.addfinalizer(finalizer)
