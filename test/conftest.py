import os
import shutil
import tempfile

import pytest

from db.server.keipy_db import KeiPyDB


@pytest.fixture
def test_db():
    temp_dir = tempfile.mkdtemp()
    db = KeiPyDB(temp_dir)
    tx = db.new_transaction()
    yield db, tx
    tx.commit()
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
