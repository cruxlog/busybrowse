# -*- coding: utf-8 -*-

"""
Created on 2015-03-29
:author: Cruxlog (cruxlog@pixelblaster.ro)
"""

from busybrowse.resources import Palet
from kotti import DBSession
from pyramid.view import view_config


@view_config(name='paletsdb', permission='view',
             renderer='busybrowse:templates/paletsdb.pt')
def paletsdb_index(context, request):
    palets = DBSession.query(Palet)
    return {'palets': palets}


# from pyramid.view import view_config
# from pyramid.view import view_defaults
#
# from busybrowse import _
# from busybrowse.resources import CustomContent
# from busybrowse.fanstatic import css_and_js
# from busybrowse.views import BaseView
#

# @view_defaults(context=CustomContent, permission='view')
# class CustomContentViews(BaseView):
#     """ Views for :class:`busybrowse.resources.CustomContent` """
#
#     @view_config(name='view', permission='view',
#                  renderer='busybrowse:templates/custom-content-default.pt')
#     def default_view(self):
#         """ Default view for :class:`busybrowse.resources.CustomContent`
#
#         :result: Dictionary needed to render the template.
#         :rtype: dict
#         """
#
#         return {
#             'foo': _(u'bar'),
#         }
#
#     @view_config(name='alternative-view', permission='view',
#                  renderer='busybrowse:templates/custom-content-alternative.pt')
#     def alternative_view(self):
#         """ Alternative view for :class:`busybrowse.resources.CustomContent`.
#         This view requires the JS / CSS resources defined in
#         :mod:`busybrowse.fanstatic`.
#
#         :result: Dictionary needed to render the template.
#         :rtype: dict
#         """
#
#         css_and_js.need()
#
#         return {
#             'foo': _(u'bar'),
#         }
