# -*- coding: utf-8 -*-

"""
Created on 2015-03-29
:author: Cruxlog (cruxlog@pixelblaster.ro)
"""

from kotti.resources import Document
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('busybrowse')


def kotti_configure(settings):
    """ Add a line like this to you .ini file::

            kotti.configurators =
                busybrowse.kotti_configure

        to enable the ``busybrowse`` add-on.

    :param settings: Kotti configuration dictionary.
    :type settings: dict
    """

    settings['kotti.populators'] = 'busybrowse.resources.populate'
    settings['pyramid.includes'] += ' busybrowse'
    settings['kotti.available_types'] += ' busybrowse.resources.Palet busybrowse.resources.Product'
    settings['kotti.fanstatic.view_needed'] += ' busybrowse.fanstatic.css_and_js'
    settings['kotti.alembic_dirs'] += ' busybrowse:alembic'

    Document.type_info.selectable_default_views.append(
        ('paletsdb', 'Palets DB')
    )


def includeme(config):
    """ Don't add this to your ``pyramid_includes``, but add the
    ``kotti_configure`` above to your ``kotti.configurators`` instead.

    :param config: Pyramid configurator object.
    :type config: :class:`pyramid.config.Configurator`
    """

    config.add_translation_dirs('busybrowse:locale')
    config.add_static_view('static-busybrowse', 'busybrowse:static')

    config.scan(__name__)
