# -*- coding: utf-8 -*-

"""
Created on 2015-03-29
:author: Cruxlog (cruxlog@pixelblaster.ro)
"""

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
import logging

log = logging.getLogger("BB")

#import bottlenose.api
#regions = bottlenose.api.SERVICE_DOMAINS.keys()
regions = ['US', 'UK', 'CA', 'FR', 'DE', 'IT', 'ES', 'CN', 'IN', 'JP']

not_found = set()
NS = {'a': "http://webservices.amazon.com/AWSECommerceService/2011-08-01"}
URLType = String(512)

def xpath(el, qs):
    return el.xpath(qs, namespaces=NS)


product_to_secondary_categories_table = Table(
    'p2sc', Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id')),
    Column('category_id', Integer, ForeignKey('categories.id')),
)

NOASIN = "NOASIN"
NOTFOUND = "NOTFOUND"
ERRORS = "ERRORS"

error_codes = [NOASIN, NOTFOUND, ERRORS]


class NotFound(Base):
    id = Column(Integer, primary_key=True)
    asin = Column(String, index=True)

    def __init__(self, asin):
        self.asin = asin


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    title = Column(Unicode(200), index=True)

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
            DBSession.add(c)

        return c


class Palet(Content):
    __tablename__ = 'palets'

    type_info = Content.type_info.copy(
        name=u'Palet',
        title=_(u'Palet'),
        add_view=u'add_palet',
        addable_to=[u'Document'],
        selectable_default_views=[],
    )

    id = Column(Integer, ForeignKey('contents.id'), primary_key=True)
    unique_id = Column(Integer, index=True)

    of_interest = Column(Boolean)   # daca e selectata ca fiind de interes

    @classmethod
    def create(cls):
        m = int(DBSession.query(functions.max(cls.unique_id)).scalar() or 0)
        m += 1

        root = get_root()['paletdb']
        title = u"Palet {}".format(m)
        name = title_to_name(title, blacklist=root.keys())
        self = cls(name=name, title=title)
        self.unique_id = m
        root[name] = self
        return self

    def price_of_products(self):
        return DBSession.query(
            functions.sum(Product.net_price).label('total_price')
        ).filter(Product.parent_id==self.id).all()[0][0]

    def number_of_products(self):
        children = DBSession.query(Product.id).filter(
            Product.parent_id == self.id)
        return children.count()

    def wanted_products(self):
        children = DBSession.query(Product.id).filter(
            Product.parent_id == self.id)
        query = children.filter(Product.of_interest==True)
        return query.count()

    def not_wanted_products(self):
        children = DBSession.query(Product.id).filter(
            Product.parent_id == self.id)
        query = children.filter(Product.of_interest==False)
        return query.count()


class Product(Content):
    __tablename__ = 'products'

    type_info = Content.type_info.copy(
        name=u'Product',
        title=_(u'Product'),
        add_view=u'add_product',
        addable_to=[u'Document'],
        selectable_default_views=[],
    )

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

    __xml = None

    @property
    def _xml(self):
        if self.__xml is None:
            root = lxml.etree.fromstring(self.amazon_data)
            self.__xml = root
        return self.__xml

    @classmethod
    def create(cls, palet, **info):
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

        title = info.get('Bezeichnung') or info.get('Itemname')
        name = title_to_name(title, blacklist=palet.keys())

        self = Product(title=title)
        palet[name] = self

        self.asin = info.get('ASIN')
        self.ean = info.get('EAN')

        self.condition = info['Condition']
        self.net_price = info['VK netto']

        self.amazon_data = self._get_amazon_data()

        log.info(u"Recorded new product %s", self.title)

        if self.amazon_data in error_codes:
            return self

        self.amazon_title         = self._extract_title()
        self.description          = self._extract_description()
        self.amazon_link          = self._extract_amazon_link()
        self.image                = self._extract_image()
        self.secondary_categories = self._extract_categories()
        self.main_category        = self._extract_main_category()
        self.features             = self._extract_features()
        self.human_price          = self._extract_human_price()

        log.info(u"Extracted amazon info %s", self.amazon_link)

        return self

    def thumbnail(self):
        return self._extract_image('Medium')

    def _extract_image(self, size='Large'):
        images = [
            xpath(elimg, 'a:URL')[0].text
            for elimg in xpath(self._xml, '//a:%sImage' % size)
        ]
        image = images and images[0] or ''
        return image

    def _extract_description(self):
        try:
            description = u'\n'.join(
                xpath(self._xml,
                    '//a:EditorialReviews/a:EditorialReview/a:Content/text()')
            )
        except:
            description = u""
        return description

    def _extract_title(self):
        try:
            return xpath(self._xml, '//a:ItemAttributes/a:Title/text()')[0]
        except:
            return u""

    def _extract_amazon_link(self):
        link = xpath(self._xml, '//a:DetailPageURL/text()')[0]
        return link

    def _extract_categories(self):
        _categories = [
            x for x in xpath(self._xml, '//a:BrowseNode/a:Name/text()')
            if x != 'Categories'
        ]
        categories = [Category.get_or_create(title) for title in _categories]
        return categories

    def _extract_main_category(self):
        _main_category = xpath(self._xml, '//a:ProductGroup/text()')
        _main_category = _main_category and _main_category[0] or 'NoMainCategory'
        main_category = Category.get_or_create(_main_category)
        return main_category

    def _extract_human_price(self):
        node = xpath(self._xml, '//a:Price/a:FormattedPrice/text()')
        if node:
            return node[0]

        node = xpath(self._xml, '//a:ListPrice/a:FormattedPrice/text()')
        if node:
            return node[0]

    def _extract_features(self):
        features = xpath(self._xml, '//a:Feature/text()')
        return u'\n'.join(features)

    def _get_amazon_data(self):
        settings = get_settings()

        AMAZON_ACCESS_KEY = settings['busybrowse.AMAZON_ACCESS_KEY']
        AMAZON_SECRET_KEY = settings['busybrowse.AMAZON_SECRET_KEY']
        AMAZON_ASSOC_TAG = settings['busybrowse.AMAZON_ASSOC_TAG']

        if not self.asin:
            # print "No ASIN"
            # todo: update from here using EAN
            # info = "http://www.upcindex.com/746775167080"
            return NOASIN

        if DBSession.query(NotFound.id).filter_by(asin = self.asin).count():
            log.info(u"On not found list %s", self.asin)
            return NOTFOUND

        # first, try to find product info that already exists
        other = DBSession.query(Product).filter(
            Product.asin == self.asin,
            not_(Product.amazon_title == None)
        ).first()

        if other is not None:
            log.info(u"Getting info from %s: %s", other.id, other.title)
            return other.amazon_data

        info = None
        for region in regions:
            counter = 0
            while True:
                AZ = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY,
                               AMAZON_ASSOC_TAG, region=region)
                try:
                    info = AZ.lookup(ItemId=self.asin)
                    break
                except AsinNotFound:
                    info = None
                    break
                except:
                    counter += 1
                    if counter > 10:
                        log.info("Too many errors")
                        break

                    time.sleep(1)
                    continue

                break

            if info is None:
                continue
            else:
                break

        if info is None:
            log.info("ASIN not found: %s", self.asin)   # TODO: try other sites
            notfound = NotFound(self.asin)
            DBSession.add(notfound)
            return NOTFOUND

        return info.to_string()


def populate():
    from kotti.populate import populate as kotti_populate
    from kotti.resources import Document
    from kotti.resources import get_root

    kotti_populate()
    root = get_root()
    if 'paletdb' not in root.keys():
        paletdb = Document('paletdb', title="Palets Database")
        root['paletdb'] = paletdb

