from IPMCL import l_current

from flask import Flask, request
from loguru import logger

import threading
import logging
import inspect
import ctypes

code_buffer = str()


app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


def code_buffer_read():
    global code_buffer
    return code_buffer


def code_buffer_write(code):
    global code_buffer
    code_buffer = code


@app.route("/", methods=['GET'])
def code_input():
    global code_buffer
    code = request.args.get("code")
    code_buffer_write(code)

    return """<script>window.open("about:blank","_self").close()</script>"""


class server(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.__is_running = True
        self.port = int(port)

    def run(self):
        logger.info(l_current["Minecraft"]["Auth"]["LocalServerStarted"])

        app.run("localhost", self.port, threaded=True)


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)

    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")

    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread, SystemExit)


def start_server_thread(port):
    server_thread = server(port=port)
    server_thread.start()

    return server_thread.ident
