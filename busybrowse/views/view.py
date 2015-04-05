# -*- coding: utf-8 -*-

"""
Created on 2015-03-29
:author: Cruxlog (cruxlog@pixelblaster.ro)
"""

from busybrowse.resources import Palet
from busybrowse.resources import Product
from kotti import DBSession
from pyramid.view import view_config


@view_config(name='paletsdb', permission='view',
             renderer='busybrowse:templates/paletsdb.pt')
def paletsdb_index(context, request):
    palets = DBSession.query(Palet)
    return {'palets': palets}


@view_config(name='view', context=Palet, permission='view',
             renderer='busybrowse:templates/palet.pt')
def view_palet(context, request):
    return {}


@view_config(name="mark", context=Palet, permission='view', renderer='json')
def mark_of_interest_palet(context, request):
    of_interest = bool(request.POST.get('of_interest', '').lower() == 'true')
    context.of_interest = of_interest

    return {'of_interest': of_interest, 'context_id': context.id}


@view_config(name="mark", context=Product, permission='view', renderer='json')
def mark_of_interest_product(context, request):
    of_interest = bool(request.POST.get('of_interest', '').lower() == 'true')
    products = DBSession.query(Product).filter(Product.asin==context.asin)
    count = products.update({"of_interest": of_interest})
    print "Marked ", count
    return {'of_interest': of_interest, 'context_id': context.id}
