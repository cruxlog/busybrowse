# -*- coding: utf-8 -*-

"""
Created on 2015-03-29
:author: Cruxlog (cruxlog@pixelblaster.ro)
"""

from __future__ import absolute_import

from fanstatic import Group
from fanstatic import Library
from fanstatic import Resource


library = Library("busybrowse", "static")

css = Resource(
    library,
    "styles.css",
    minified="styles.min.css")
js = Resource(
    library,
    "scripts.js",
    minified="scripts.min.js")

css_and_js = Group([css, js])
