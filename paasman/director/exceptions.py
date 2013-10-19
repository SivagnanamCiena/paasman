# -*- coding: utf-8 -*-

class NodeCreationError(Exception):
    """Exception that occoured during creation of a instance/vm in the cluster"""

class AppUploadError(Exception):
    """Exception that occoured during storage phase of the application file"""