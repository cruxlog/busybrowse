from busybrowse.resources import Palet, Product
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
    """ Returns a list of palets
    """

    doc = xlrd.open_workbook(path)
    sheet = doc.sheets()[0]
    header = dict([(k, x.value) for k, x in enumerate(sheet.row(0))])

    palets = []
    current_palet = []
    for i in range(1, sheet.nrows):
        if not sheet.row(i)[0].value.strip():
            palets.append(current_palet[:])
            current_palet = []
            continue
        current_palet.append(_product_row(sheet.row(i), header))

    return palets


def main(xls_path):

    palets = parse_xls(xls_path)

    print "Got {} palets".format(len(palets))

    i = 0
    for palet_data in palets:
        import pdb; pdb.set_trace()
        palet = Palet.create()
        for product_row in palet_data:
            Product.create(palet, **product_row)

        print "Imported palet", palet
        i += 1
        if i == 3:
            break

    import transaction; transaction.commit()

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
