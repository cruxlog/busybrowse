# -*- coding: utf-8 -*-

"""
Created on 2015-03-29
:author: Cruxlog (cruxlog@pixelblaster.ro)
"""

#from kotti.interfaces import IDefaultWorkflow
#from zope.interface import implements

from amazon.api import AmazonAPI, AsinNotFound
from busybrowse import _
from kotti import get_settings
from kotti.resources import Base
from kotti.resources import Content
from kotti.resources import DBSession
from kotti.resources import get_root
from kotti.util import title_to_name
from sqlalchemy import Boolean, Float
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String  #, DateTime
from sqlalchemy import Table
from sqlalchemy import Unicode
from sqlalchemy.orm import relationship
from sqlalchemy.sql import functions
from sqlalchemy.sql.expression import not_
import lxml.etree
import time


not_found = set()



NS = {'a': "http://webservices.amazon.com/AWSECommerceService/2011-08-01"}

def xpath(el, qs):
    return el.xpath(qs, namespaces=NS)


URLType = String(512)


product_to_secondary_categories_table = Table(
    'p2sc', Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id')),
    Column('category_id', Integer, ForeignKey('categories.id')),
)


class Category(Content):
    __tablename__ = "categories"
    id = Column(Integer, ForeignKey('contents.id'), primary_key=True)

    products_with_main_category = relationship(
        "Product", backref="main_category",
        foreign_keys="[Product.main_category_id]"
        ) # many to one

    products_with_secondary_category = relationship(
        "Product", secondary=product_to_secondary_categories_table,\
        backref="secondary_categories",
    )

    @classmethod
    def get_or_create(cls, title):
        c = DBSession.query(Category).filter_by(title=title).first()
        if c is None:
            c = Category(title=title)
            root = get_root()
            id = title_to_name(u"Category {}".format(title),
                               blacklist=root.keys())
            get_root()[id] = c

        return c


class Palet(Content):
    __tablename__ = 'palets'

    id = Column(Integer, ForeignKey('contents.id'), primary_key=True)
    unique_id = Column(Integer) # used by humans, can be edited

    of_interest = Column(Boolean)   # daca e selectata ca fiind de interes
    entries = relationship("Product", backref='palet',
                           foreign_keys="[Product.palet_id]")

    type_info = Content.type_info.copy(
        name=u'Palet',
        title=_(u'Palet'),
        add_view=u'add_palet',
        addable_to=[u'Document'],
        selectable_default_views=[
            #("alternative-view", _(u"alternative view")),
        ],
    )

    @classmethod
    def create(cls):
        m = DBSession.query(functions.max(cls.unique_id)).scalar()
        m = int(m or 0)
        entry = cls()
        entry.unique_id = m + 1
        DBSession.add(entry)
        return entry

    @property
    def title(self):
        return "Palet #{}".format(self.unique_id)

    def __repr__(self):
        return self.title


class Product(Content):
    __tablename__ = 'products'

    # Foreign keys for relationships
    id = Column(Integer, ForeignKey('contents.id'), primary_key=True)
    # self.palet
    palet_id = Column(Integer, ForeignKey('palets.id'), index=True)
    # self.main_category
    main_category_id = Column(Integer, ForeignKey('categories.id'), index=True)

    # inherited from kotti Content
    #title = Column(Unicode(512), index=True)
    #description = Column(Unicode)      # amazon product description

    # state of product: used, as new, etc
    condition = Column(Unicode(128))   # C-Ware

    # price for product as defined in XLS. Currency is Euro
    net_price = Column(Float(asdecimal=True))

    # Link to Amazon page for this product
    amazon_link = Column(URLType)

    # A link to an image showing this product
    image = Column(URLType)

    # Title from Amazon
    amazon_title = Column(Unicode(512), index=True)

    # Name of product, as expressed in XLS file
    product_name = Column(Unicode(512), index=True)

    # ASIN code, used to identify product on AMAZON
    asin = Column(Unicode(128), index=True)

    # EAN Code
    ean = Column(Unicode(128), index=True)

    #
    # Section for extracted info, comes from AMAZON API call
    #

    # raw result of call to Amazon API
    amazon_data = Column(Unicode)               # xml product result

    # Amazon human readable price
    human_price = Column(Unicode(40))

    # information about some features defining product
    features = Column(Unicode)

    #
    # Are we interested in this product?
    #

    viewed = Column(Boolean, index=True)        # a fost vazut produsul?
    of_interest = Column(Boolean, index=True)   # selectata ca fiind de interes

    type_info = Content.type_info.copy(
        name=u'Product',
        title=_(u'Product'),
        add_view=u'add_product',
        addable_to=[u'Document'],
        selectable_default_views=[],
    )

    @classmethod
    def create_from_row(cls, palet, **info):
        """
            {u'ASIN': u'B000FA1A0E',
            u'Bezeichnung': u'Seat 2 Go Pick Up',
            u'Condition': u'C-Ware',
            u'EAN': 7290004222222.0,
            u'Lager_id': u'W15-BM3355',
            u'Land': u'DE',
            u'SKU': u'P15161-477',
            u'VK netto': 19.85}]
        """

        product_name = info.get('Bezeichnung') or info.get('Itemname')
        name = title_to_name(product_name, blacklist=palet.keys())

        self = Product(title=product_name)
        self.asin = info.get('ASIN')
        self.ean = info.get('EAN')
        self.condition = info['Condition']
        self.net_price = info['VK netto']
        palet[name] = self

        self.fetch_and_update()

        DBSession.commit()

        return self

    def _extract_data(self):
        result = {
            'amazon_title': '',
            'categories': [],
            'description': '',
            'features': [],
            'image': '',
            'main_category': None,
            'human_price': 'NOPRICE',
            'title': self.product_name,
        }

        if (not self.amazon_data) or (self.amazon_data == u'notfound'):
            return result

        root = lxml.etree.fromstring(self.amazon_data)

        images = [
            xpath(elimg, 'a:URL')[0].text
            for elimg in xpath(root, '//a:LargeImage')
        ]
        image = images and images[0] or ''

        _categories = [
            x for x in xpath(root, '//a:BrowseNode/a:Name/text()')
            if x != 'Categories'
        ]
        categories = [Category.get_or_create(title) for title in _categories]

        _main_category = xpath(root, '//a:ProductGroup/text()')
        _main_category = _main_category and _main_category[0] or 'NoMainCategory'
        main_category = Category.get_or_create(_main_category)

        description = xpath(root, '//a:Content/text()')
        description = description and description[0] or ''

        human_price = xpath(root, '//a:Price/a:FormattedPrice/text()')
        human_price = human_price and human_price[0] or 'NOPRICE'

        features = xpath(root, '//a:Feature/text()')

        result.update({
            'title': self.amazon_title or self.title,
            'amazon_title': self.amazon_title or '',
            'description': description,

            'main_category': main_category,
            'categories': categories,

            'features': features,
            'image': image,
            'price': human_price,
        })

        return result

    def fetch_and_update(self):
        settings = get_settings()

        AMAZON_ACCESS_KEY = settings['busybrowse.AMAZON_ACCESS_KEY']
        AMAZON_SECRET_KEY = settings['busybrowse.AMAZON_SECRET_KEY']
        AMAZON_ASSOC_TAG = settings['busybrowse.AMAZON_ASSOC_TAG']

        print "Updating", self.title
        AZ = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)

        if not self.asin:
            print "No ASIN"
            # todo: update from here using EAN
            info = "http://www.upcindex.com/746775167080"
            return

        if self.asin in not_found:
            print "On not found list"
            return

        # first, try to find product info that already exists
        other = DBSession.query(Product).filter(
            Product.asin == self.asin,
            not_(Product.amazon_title == None)
        ).first()

        if other is not None:
            print "Getting info from", other.id, other.title
            if other.amazon_data == 'notfound':
                not_found.add(self.asin)
            self.amazon_data = other.amazon_data
            self.amazon_title = other.amazon_title
            self.description = other.description
            DBSession.commit()
            return

        counter = 0
        while True:
            try:
                info = AZ.lookup(ItemId=self.asin)
                #time.sleep(1)
                break
            except AsinNotFound:
                print "ASIN not found", self.asin
                # TODO: try other sites
                not_found.add(self.asin)
                self.amazon_data = "notfound"
                return
            except:
                counter += 1
                if counter > 10:
                    print "Too many errors"
                    return
                time.sleep(1)

        self.amazon_title = info.title
        self.description = info.editorial_review
        self.amazon_data = info.to_string()


def populate():
    from kotti.populate import populate as kotti_populate
    from kotti.resources import Document
    from kotti.resources import get_root

    kotti_populate()
    root = get_root()
    if 'paletdb' not in root.keys():
        paletdb = Document('paletdb', title="Palets Database")
        root['paletdb'] = paletdb
