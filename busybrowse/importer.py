#from amazon.api import AmazonAPI, AsinNotFound
#from db import Pallet, Product, session
#from kotti import get_settings
#from sqlalchemy.sql.expression import not_
#import os
#import time

from busybrowse.resources import Palet, Product
from kotti import DBSession
from kotti.util import command
import lxml.etree
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


def main(xls_path):

    pallets = parse_xls(xls_path)

    print "Got {} pallets".format(len(pallets))

    for pallet_row in pallets:
        pallet = Palet.create()
        DBSession.add(pallet)
        for product_row in pallet_row:
            pallet.children.append(Product.create_from_row(product_row))

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


# def update_with_amazon(self):
#     products = DBSession.query(Product)
#     count = products.count()
#     i = 0
#     for product in products:
#         i += 1
#         print "Updating {} of {}".format(i, count)
#         if product.annotations:
#             print "Already updated", product
#             continue
#         self.update_product(product)
