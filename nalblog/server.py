import os
import SocketServer
import BaseHTTPServer
import SimpleHTTPServer

import threading


class ThreadingSimpleServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass


def get_server(port=8000, path=None):
    if path:
        os.chdir(path)

    server = ThreadingSimpleServer(('', port), SimpleHTTPServer.SimpleHTTPRequestHandler)

    server_thread = threading.Thread(target=server.serve_forever)

    return server_thread
