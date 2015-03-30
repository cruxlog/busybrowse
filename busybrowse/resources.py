# -*- coding: utf-8 -*-

"""
Created on 2015-03-29
:author: Cruxlog (cruxlog@pixelblaster.ro)
"""

from busybrowse import _
from kotti.interfaces import IDefaultWorkflow
from kotti.resources import Content
from kotti.resources import DBSession
from sqlalchemy import Boolean, Float
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String  #, DateTime
from sqlalchemy import Unicode
from sqlalchemy.orm import relationship
from sqlalchemy.sql import functions
from zope.interface import implements


URLType = String(512)


class Pallet(Content):
    __tablename__ = 'pallets'

    id = Column(Integer, ForeignKey('contents.id'), primary_key=True)
    unique_id = Column(Integer) # used by humans, can be edited

    of_interest = Column(Boolean)   # daca e selectata ca fiind de interes
    # entries = relationship("Product", backref='pallet',
    #                        foreign_keys=['products.c.pallet_id'])

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

    id = Column(Integer, ForeignKey('contents.id'), primary_key=True)
    pallet_id = Column(Integer, ForeignKey('pallets.id'), index=True)

    title = Column(Unicode(512), index=True)
    condition = Column(Unicode(128))   # C-Ware
    net_price = Column(Float(asdecimal=True))

    amazon_link = Column(URLType)
    description = Column(Unicode)      # amazon product description
    amazon_title = Column(Unicode(512), index=True)
    asin = Column(Unicode(128), index=True)
    ean = Column(Unicode(128), index=True)

    annotations = Column(Unicode)               # xml product result
    viewed = Column(Boolean, index=True)        # a fost vazut produsul?
    of_interest = Column(Boolean, index=True)   # selectata ca fiind de interes

    def __init__(self, info):
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
        self.asin = info.get('ASIN')
        self.ean = info.get('EAN')
        self.title = info.get('Bezeichnung') or info.get('Itemname')
        self.condition = info['Condition']
        self.net_price = info['VK netto']


class CustomContent(Content):
    """ A custom content type. """

    implements(IDefaultWorkflow)

    id = Column(Integer, ForeignKey('contents.id'), primary_key=True)
    custom_attribute = Column(Unicode(1000))

    type_info = Content.type_info.copy(
        name=u'CustomContent',
        title=_(u'CustomContent'),
        add_view=u'add_custom_content',
        addable_to=[u'Document'],
        selectable_default_views=[
            ("alternative-view", _(u"Alternative view")),
        ],
    )

    def __init__(self, custom_attribute=None, **kwargs):
        """ Constructor

        :param custom_attribute: A very custom attribute
        :type custom_attribute: unicode

        :param **kwargs: Arguments that are passed to the base class(es)
        :type **kwargs: see :class:`kotti.resources.Content`
        """

        super(CustomContent, self).__init__(**kwargs)

        self.custom_attribute = custom_attribute
