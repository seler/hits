import asyncio

import pytest

from file_queue import Queue


@pytest.fixture
def queue(tmpdir):
    return Queue(tmpdir / "testqueuefile")


@pytest.mark.asyncio
async def test_queue_gets_the_same_that_puts(queue):
    await queue.put("asdf")
    assert await queue.get() == "asdf"


@pytest.mark.asyncio
async def test_queue_removes_on_get(queue):
    pass


@pytest.mark.asyncio
async def test_queue_get_waits_until_put(queue):
    data_coroutine = queue.get()
    await asyncio.sleep(0.2)
    await queue.put("asdf")
    assert await data_coroutine == "asdf"


@pytest.mark.asyncio
async def test_queue_get_waits(queue):
    try:
        await asyncio.wait_for(queue.get(), timeout=0.2)
    except asyncio.TimeoutError:
        pass
    else:
        pytest.fail("queue.get did not wait")
