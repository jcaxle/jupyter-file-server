"""Jupyter server example handlers."""
import os
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.extension.handler import ExtensionHandlerJinjaMixin, ExtensionHandlerMixin
import tornado
from tornado.web import StaticFileHandler


BASEDIR_NAME = os.path.dirname(__file__)
BASEDIR_PATH = os.path.abspath(BASEDIR_NAME)

FILES_ROOT = "/home/jovyan/"


class DefaultHandler(ExtensionHandlerMixin, JupyterHandler):
    """Default API handler."""

    @tornado.web.authenticated
    def get(self, path):
        """Get the extension response."""
        self.write("<h1>Hello Simple 1 - I am the default...</h1>")
        self.write("For usage and more, please click <a href=\"https://github.com/jcaxle/polus-server-ext\">here</a>")

class AuthFileHandler(JupyterHandler, StaticFileHandler):

    def _initialize(self,path) -> None:
        StaticFileHandler._initialize(path)

    @tornado.web.authenticated
    def prepare(self):
        pass


class BaseTemplateHandler(ExtensionHandlerJinjaMixin, ExtensionHandlerMixin, JupyterHandler):
    """The base template handler."""

    pass

class ErrorHandler(BaseTemplateHandler):
    """An error handler."""

    def get(self, path):
        """Write_error renders template from error.html file."""
        self.write_error(400)
