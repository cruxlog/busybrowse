#from db import Pallet, Product, session
#import os
from busybrowse.resources import Palet, Product
from amazon.api import AmazonAPI, AsinNotFound
from kotti import get_settings
from kotti import DBSession
from kotti.util import command
from sqlalchemy.sql.expression import not_
import lxml.etree
import time
import xlrd


def print_response(text):
    e = lxml.etree.fromstring(text)
    print lxml.etree.tostring(e, pretty_print=True)


def _product_row(row, header):
    res = {}
    for k, v in header.items():
        val = row[k].value
        if val:
            res[v] = row[k].value
    return res


def parse_xls(path):
    """ Returns a list of pallets
    """

    doc = xlrd.open_workbook(path)
    sheet = doc.sheets()[0]
    header = dict([(k, x.value) for k, x in enumerate(sheet.row(0))])

    pallets = []
    current_pallet = []
    for i in range(1, sheet.nrows):
        if not sheet.row(i)[0].value.strip():
            pallets.append(current_pallet[:])
            current_pallet = []
            continue
        current_pallet.append(_product_row(sheet.row(i), header))

    return pallets


not_found = set()

def update_product(product):
    settings = get_settings()

    AMAZON_ACCESS_KEY = settings['busybrowse.AMAZON_ACCESS_KEY']
    AMAZON_SECRET_KEY = settings['busybrowse.AMAZON_SECRET_KEY']
    AMAZON_ASSOC_TAG = settings['busybrowse.AMAZON_ASSOC_TAG']

    print "Updating", product.title
    AZ = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)

    if not product.asin:
        print "No ASIN"
        # todo: update from here using EAN
        info = "http://www.upcindex.com/746775167080"
        return

    if product.asin in not_found:
        print "On not found list"
        return

    # first, try to find product info that already exists
    other = DBSession.query(Product).filter(
        Product.asin == product.asin,
        not_(Product.amazon_title == None)
    ).first()

    if other is not None:
        print "Getting info from", other.id, other.title
        if other.annotations == 'notfound':
            not_found.add(product.asin)
        product.annotations = other.annotations
        product.amazon_title = other.amazon_title
        product.description = other.description
        DBSession.commit()
        return

    counter = 0
    while True:
        try:
            info = AZ.lookup(ItemId=product.asin)
            #time.sleep(1)
            break
        except AsinNotFound:
            print "ASIN not found", product.asin
            # TODO: try other sites
            not_found.add(product.asin)
            product.annotations = "notfound"
            return
        except:
            counter += 1
            if counter > 10:
                print "Too many errors"
                return
            time.sleep(1)

    product.amazon_title = info.title
    product.description = info.editorial_review
    product.annotations = info.to_string()
    DBSession.commit()


def update_with_amazon():
    products = DBSession.query(Product)
    count = products.count()
    i = 0
    for product in products:
        i += 1
        print "Updating {} of {}".format(i, count)
        if product.annotations:
            print "Already updated", product
            continue
        update_product(product)


def main(xls_path):

    import pdb; pdb.set_trace()
    # for fname in os.listdir('xls'):
    #     fpath = os.path.join('xls', fname)
    #     pallets.extend(parse_xls(fpath))

    pallets = parse_xls(xls_path)

    print "Got {} pallets".format(len(pallets))

    for pallet_row in pallets:
        pallet = Palet.create()
        DBSession.add(pallet)
        for product_row in pallet_row:
            pallet.entries.append(Product(product_row))

        print "Imported pallet", pallet

    DBSession.commit()


def importer_command():
    __doc__ = """ Import an XLS file.

    Usage:
        busybrowse-importer <config_uri> <xls-path>

    Options:
        -h --help   Show this help screen
    """
    return command(
        lambda args:main(xls_path=args['<xls-path>']),
        __doc__
    )
