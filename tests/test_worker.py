import pytest

from worker import process


class FakeQueue:
    async def put(self, value):
        pass

    async def get(self):
        return {"whetever": "whatever"}


@pytest.fixture
def queue():
    return FakeQueue()


@pytest.fixture
def download():
    async def _download(**kwargs):
        return {"whetever": "whatever"}

    return _download


@pytest.fixture
def convert():
    async def _convert(**kwargs):
        return

    return _convert


@pytest.mark.asyncio
async def test_process(queue, download, convert):
    await process(queue, download, convert)
