#!/usr/bin/env python3
"""Tiny byte forwarder so an agent in a --network none container can reach ONE model endpoint and nothing else.

host side:       fwd.py unix2tcp SOCK_PATH HOST PORT     (listen on a unix socket, connect to the model server)
container side:  fwd.py tcp2unix LISTEN_PORT SOCK_PATH   (listen on 127.0.0.1:PORT, connect to the mounted socket)
stdlib only; runs on the host python and the image's python.
"""
import asyncio, os, sys


async def pipe(r, w):
    try:
        while data := await r.read(65536):
            w.write(data)
            await w.drain()
    except (ConnectionError, asyncio.CancelledError):
        pass
    finally:
        try:
            w.close()
        except Exception:  # noqa: BLE001
            pass


async def main():
    mode = sys.argv[1]
    if mode == "unix2tcp":
        sock, host, port = sys.argv[2], sys.argv[3], int(sys.argv[4])

        async def handle(r, w):
            ur, uw = await asyncio.open_connection(host, port)
            await asyncio.gather(pipe(r, uw), pipe(ur, w))

        if os.path.exists(sock):
            os.unlink(sock)
        srv = await asyncio.start_unix_server(handle, path=sock)
        os.chmod(sock, 0o666)
    elif mode == "tcp2unix":
        port, sock = int(sys.argv[2]), sys.argv[3]

        async def handle(r, w):
            ur, uw = await asyncio.open_unix_connection(sock)
            await asyncio.gather(pipe(r, uw), pipe(ur, w))

        srv = await asyncio.start_server(handle, "127.0.0.1", port)
    else:
        sys.exit(__doc__)
    async with srv:
        await srv.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
