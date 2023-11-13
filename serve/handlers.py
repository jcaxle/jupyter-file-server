"""Jupyter server example handlers."""
import os
from jupyter_server.auth import authorized
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.extension.handler import ExtensionHandlerJinjaMixin, ExtensionHandlerMixin
import tornado
from tornado.web import StaticFileHandler
from mimetypes import guess_type
from tornado import httputil, gen


BASEDIR_NAME = os.path.dirname(__file__)
BASEDIR_PATH = os.path.abspath(BASEDIR_NAME)

FILES_ROOT = "/home/jovyan/"


class DefaultHandler(ExtensionHandlerMixin, JupyterHandler):
    """Default API handler."""

    @tornado.web.authenticated
    def get(self, path):
        """Get the extension response."""
        self.write(f"sent path: {os.fspath(path)}")
        file_location = os.path.join(FILES_ROOT, path)
        self.write(f"mod path: {os.fspath(file_location)}")
        self.write(f"type: {guess_type(file_location)}")
        # The name of the extension to which this handler is linked.
        self.log.info(f"Extension Name in {self.name} Default Handler: {self.name}")
        # A method for getting the url to static files (prefixed with /static/<name>).
        self.log.info(
            "1Static URL for / in simple_ext1 Default Handler: {}".format(self.static_url(path="/"))
        )
        self.write("<h1>Hello Simple 1 - I am the default...</h1>")
        self.write(f"3Config in {self.name} Default Handler: {self.config}")

class AuthFileHandler(JupyterHandler, StaticFileHandler):

    def _initialize(self,path) -> None:
        StaticFileHandler._initialize(path)

    @tornado.web.authenticated
    def prepare(self):
        pass
    
class FileHandler(ExtensionHandlerMixin, JupyterHandler):
    @tornado.web.authenticated
    @gen.coroutine
    def get(self, path):
        file_location = os.path.join(FILES_ROOT, path)
        if not os.path.isfile(file_location):
            raise tornado.web.HTTPError(status_code=404)
        content_type, _ = guess_type(file_location)
        if content_type:
            self.add_header('Content-Type', "image/tiff")
        
        request_range = None
        range_header = self.request.headers.get("Range")
        if range_header:
            # As per RFC 2616 14.16, if an invalid Range header is specified,
            # the request will be treated as if the header didn't exist.
            request_range = httputil._parse_request_range(range_header)

        if request_range:
            start, end = request_range
            size = os.path.getsize(file_location)
            if (start is not None and start >= size) or end == 0:
                # As per RFC 2616 14.35.1, a range is not satisfiable only: if
                # the first requested byte is equal to or greater than the
                # content, or when a suffix with length 0 is specified
                self.set_status(416)  # Range Not Satisfiable
                self.add_header("Content-Type", "text/plain")
                self.add_header("Content-Range", "bytes */%s" % (size, ))
                return
            if start is not None and start < 0:
                start += size
            if end is not None and end > size:
                # Clients sometimes blindly use a large range to limit their
                # download size; cap the endpoint at the actual file size.
                end = size

            self.set_status(206)  # Partial Content
            self.add_header("Content-Range",
                            httputil._get_content_range(start, end, size))
            self.write(httputil._get_content_range(start, end, size))
        else:
            start = end = None

        content = self.get_content(file_location, start, end)

        self.write("seek as success")
            
        #with open(file_location, "rb") as source_file:
        #    self.write(source_file.read())
    

    # This is causing 503 error
    def get_content(self, abspath, start=None, end=None):
        if not start or not end:
            # No range, read all
            with open(abspath, "rb") as fd:
                chunk = fd.read()
        else:
            with open(abspath, "rb") as file:
                # Start at starting pos
                if start > 0:
                    file.seek(start)
                #chunk = None
                # read file
                chunk = file.read(end-start)
                #chunk = file.read(end-start)
        return chunk
                    

    @tornado.web.authenticated
    def head(self, path):
        file_location = os.path.join(FILES_ROOT, path)
        if not os.path.isfile(file_location):
            raise tornado.web.HTTPError(status_code=404)
        content_type, _ = guess_type(file_location)
        if content_type:
            self.add_header('Content-Type', content_type)


class BaseTemplateHandler(ExtensionHandlerJinjaMixin, ExtensionHandlerMixin, JupyterHandler):
    """The base template handler."""

    pass

class ErrorHandler(BaseTemplateHandler):
    """An error handler."""

    def get(self, path):
        """Write_error renders template from error.html file."""
        self.write_error(400)
