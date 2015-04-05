# -*- coding: utf-8 -*-

"""
Created on 2015-03-29
:author: Cruxlog (cruxlog@pixelblaster.ro)
"""

from pyramid.view import view_config
from busybrowse.resources import Palet, Product


@view_config(name='add_palet', permission='view',
             renderer='busybrowse:templates/paletsdb.pt')
def add_palet(context, request):
    return {}

@view_config(name='add_product', permission='view',
             renderer='busybrowse:templates/paletsdb.pt')
def add_product(context, request):
    return {}

@view_config(name='edit', permission='view',
             context=Palet,
             renderer='busybrowse:templates/paletsdb.pt')
def edit_palet(context, request):
    return {}

@view_config(name='edit', permission='view',
             context=Product,
             renderer='busybrowse:templates/paletsdb.pt')
def edit_product(context, request):
    return {}
