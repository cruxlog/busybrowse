# -*- coding: utf-8 -*-

"""
Created on 2015-03-29
:author: Cruxlog (cruxlog@pixelblaster.ro)
"""

from pyramid.view import view_config

@view_config(name='add_palet', permission='view',
             renderer='busybrowse:templates/paletsdb.pt')
def add_palet(context, request):
    return {}

@view_config(name='add_product', permission='view',
             renderer='busybrowse:templates/paletsdb.pt')
def add_product(context, request):
    return {}

# import colander
# from kotti.views.edit import ContentSchema
# from kotti.views.form import AddFormView
# from kotti.views.form import EditFormView
# from pyramid.view import view_config
#
# from busybrowse import _
# from busybrowse.resources import CustomContent
#

# class CustomContentSchema(ContentSchema):
#     """ Schema for CustomContent. """
#
#     custom_attribute = colander.SchemaNode(
#         colander.String(),
#         title=_(u"Custom attribute"))
#
#
# @view_config(name=CustomContent.type_info.add_view, permission='add',
#              renderer='kotti:templates/edit/node.pt')
# class CustomContentAddForm(AddFormView):
#     """ Form to add a new instance of CustomContent. """
#
#     schema_factory = CustomContentSchema
#     add = CustomContent
#     item_type = _(u"CustomContent")
#
#
# @view_config(name='edit', context=CustomContent, permission='edit',
#              renderer='kotti:templates/edit/node.pt')
# class CustomContentEditForm(EditFormView):
#     """ Form to edit existing CustomContent objects. """
#
#     schema_factory = CustomContentSchema


