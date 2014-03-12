'''
test_aio.py - Unit tests for Dugong

Copyright (c) Nikolaus Rath <Nikolaus@rath.org>

This module may be distributed under the terms of the Python Software Foundation
License Version 2.  The complete license text may be retrieved from
http://hg.python.org/cpython/file/65f2c92ed079/LICENSE.
'''


if __name__ == '__main__':
    import sys
    import pytest
    sys.exit(pytest.main([__file__] + sys.argv[1:]))


import socket
from select import EPOLLIN
from dugong import PollNeeded, AioFuture
import asyncio
import logging

log = logging.getLogger(__name__)

def read(sock):
    for i in range(3):
        log.debug('yielding')
        yield PollNeeded(sock.fileno(), EPOLLIN)
        log.debug('trying to read')
        buf = sock.recv(100)
        assert buf.decode() == 'text-%03d' % i
        log.debug('got: %s', buf)

def write(sock):
    for i in range(3):
        log.debug('sleeping')
        yield from asyncio.sleep(1)
        buf = ('text-%03d' % i).encode()
        log.debug('writing %s', buf)
        sock.send(buf)

def test_aio_future():
    loop = asyncio.get_event_loop()
    (sock1, sock2) = socket.socketpair()

    asyncio.Task(write(sock2))
    read_fut = AioFuture(read(sock1))
    read_fut.add_done_callback(lambda fut: loop.stop())
    loop.call_later(6, loop.stop)
    loop.run_forever()

    assert read_fut.done()

