# -*- coding: utf-8 -*-

"""
Created on 2015-03-29
:author: Cruxlog (cruxlog@pixelblaster.ro)
"""

pytest_plugins = "kotti"

from pytest import fixture


@fixture(scope='session')
def custom_settings():
    import busybrowse.resources
    busybrowse.resources  # make pyflakes happy
    return {
        'kotti.configurators': 'kotti_tinymce.kotti_configure '
                               'busybrowse.kotti_configure'}
