# from PySide.QtCore import Qt, QUrl
# from PySide.QtGui import QListWidgetItem, QPixmap
# from PySide.QtGui import QMainWindow, QApplication, QImage, QGraphicsScene
# from PySide.QtNetwork import QNetworkRequest, QNetworkAccessManager
# from PySide.QtNetwork import QNetworkReply
# from busybrowse.db import session, Pallet, Product
# from busybrowse.viewer_window import Ui_EntriesEditor
# from collections import defaultdict
# from functools32 import lru_cache
# import locale
# import lxml.html
# import sys
#
# NS = {
#     'a': "http://webservices.amazon.com/AWSECommerceService/2011-08-01",
# }
#
# def xpath(el, qs):
#     return el.xpath(qs, namespaces=NS)
#
#
# class MainWindow(QMainWindow, Ui_EntriesEditor):
#
#     def __init__(self, parent=None):
#         super(MainWindow, self).__init__(parent)
#         self.setupUi(self)
#
#         pallets = [p for p in session.query(Pallet)]    # if p.entries
#         map(self.add_pallet_to_dropdown, pallets)
#
#         row = self.palletSelector.currentIndex()
#         self.changePallet(row)
#         self.palletSelector.currentIndexChanged.connect(self.changePallet)
#
#         self.entriesList.currentRowChanged.connect(self.display_entry)
#         self.entriesList.setCurrentRow(0)
#
#         self.saveButton.clicked.connect(self.save_and_close)
#         self.browserButton.clicked.connect(self.open_in_browser)
#         #self.deliverAllButton.clicked.connect(self.deliver_all)
#
#     def save_and_close(self):
#         session.commit()
#         return
#
#     def open_in_browser(self):
#         return
#
#     @lru_cache()
#     def get_entry_details(self, entry):
#         result = {
#             'amazon_title': '',
#             'categories': [],
#             'description': '',
#             'features': [],
#             'image': '',
#             'main_category': 'UNKNOWNCAT',
#             'price': 'NOPRICE',
#             'title': entry.title,
#         }
#         if (not entry.annotations) or \
#                 (entry.annotations and entry.annotations == u'notfound'):
#             return result
#
#         root = lxml.etree.fromstring(entry.annotations)
#
#         images = [
#             xpath(elimg, 'a:URL')[0].text
#             for elimg in xpath(root, '//a:LargeImage')
#         ]
#         image = images and images[0] or ''
#
#         categories = [
#             x for x in xpath(root, '//a:BrowseNode/a:Name/text()')
#             if x != 'Categories'
#         ]
#         main_category = xpath(root, '//a:ProductGroup/text()')
#         main_category = main_category and main_category[0] or 'nomaincategory'
#
#         description = xpath(root, '//a:Content/text()')
#         description = description and description[0] or ''
#
#         human_price = xpath(root, '//a:Price/a:FormattedPrice/text()')
#         human_price = human_price and human_price[0] or 'NOPRICE'
#
#         features = xpath(root, '//a:Feature/text()')
#
#         result.update({
#             'amazon_title': entry.amazon_title or '',
#             'categories': categories,
#             'description': description,
#             'features': features,
#             'image': image,
#             'main_category': main_category,
#             'price': human_price,
#             'title': entry.amazon_title or entry.title,
#         })
#
#         return result
#
#     def add_pallet_to_dropdown(self, pallet):
#         # categories = defaultdict(lambda:0)
#         # for entry in pallet.entries:
#         #     details = self.get_entry_details(entry)
#         #     categories[details['main_category']] += 1
#         #
#         # pallet_title = u"{} - {} products - {}".format(
#         #     pallet.title or 'Untitled Pallet',
#         #     len(pallet.entries),
#         #     ' | '.join(['{}({})'.format(k, v) for k, v in categories.items()])
#         # )
#         pallet_title = pallet.title
#
#         self.palletSelector.addItem(
#             pallet_title,
#             (pallet.id, pallet_title)
#         )
#
#         ix = self.palletSelector.count() - 1
#         font = self.palletSelector.font()
#         font.setBold(True)
#         self.palletSelector.setItemData(ix, font, Qt.FontRole)
#
#     def changePallet(self, index):
#         pallet_id = self.palletSelector.itemData(index)[0]
#         self.entries = session.query(Pallet).get(int(pallet_id)).entries
#         self.displayEntries()
#
#     def display_entry(self, row):
#         if row < 0:
#             return  # end of list
#         item = self.entriesList.item(row)
#
#         # mark item with normal font, as it has been viewed
#         font = item.font()
#         font.setBold(False)
#         item.setFont(font)
#
#         entry_id = item.data(3)
#         entry = session.query(Product).get(int(entry_id))
#         entry.viewed = True
#
#         D = self.get_entry_details(entry)
#
#         # 'amazon_title': entry.amazon_title or '',
#         # 'categories': categories,
#         # 'description': description,
#         # 'features': features,
#         # 'image': image,
#         # 'main_category': main_category,
#         # 'price': human_price,
#         # 'title': entry.amazon_title or entry.title,
#
#         self.entryDescription.setUndoRedoEnabled(False)
#         self.entryDescription.setText("<h3>" + D['title'] + "</h3>")
#         elhtml = lxml.html.fragment_fromstring
#
#         el = elhtml(u"""<div>
#                     <div>{}</div>
#                     <p><strong>Pret amazon:</strong>{}</p>
#                     <p><strong>Pret XLS:</strong>{}</p>
#                     <p><strong>Main category</strong>{}</p>
#                     <div>
#                         <strong>Categories:</strong>
#                         <ul>{}</ul>
#                     </div>
#                     </div>
#                     """.format(
#                         D['description'],
#                         D['price'],
#                         u'{:n}'.format(entry.net_price or 0),
#                         D['main_category'],
#                         "\n".join([u"<li>{}</li>".format(x)
#                                    for x in D['categories']]),
#                     )
#         )
#
#         self.entryDescription.append(lxml.html.tostring(el))
#         self.entryDescription.verticalScrollBar().setValue(0)
#
#         self.labelNotes.setText(
#             "Pret Amazon: {}; Pret XLS: {}".format('','')
#         )
#
#         if  D['image']:
#             mgr = QNetworkAccessManager(self)
#             mgr.finished[QNetworkReply].connect(self._callback_show_image)
#             mgr.get(QNetworkRequest(QUrl(D['image'])))
#
#     def _callback_show_image(self, reply):
#         image = QImage()
#         image.loadFromData(reply.readAll())
#         scene = QGraphicsScene()
#         pixmap = QPixmap()
#         pixmap.convertFromImage(image)
#         scene.addPixmap(pixmap)
#         self.picturesBrowser.setScene(scene)
#
#     def deliver_all(self):
#         pass
#
#     def _display(self, entry):
#         return True
#
#     def displayEntries(self):
#         entries = self.entries
#         self.entriesList.clear()
#         # brush = QBrush(Qt.red)
#         for entry in entries:
#             if not self._display(entry):
#                 continue
#
#             title = entry.amazon_title or entry.title
#
#             item = QListWidgetItem(title)
#             font = item.font()
#             font.setBold(not bool(entry.viewed))
#             # font.setStrikeOut(bool(entry.rejected))
#             item.setFont(font)
#             # if bool(entry.deliverable):
#             #     item.setForeground(brush)
#             item.setData(3, entry.id)
#             self.entriesList.addItem(item)
#
#
# def main():
#     locale.setlocale(locale.LC_TIME, "C")
#     app = QApplication(sys.argv)
#     frame = MainWindow()
#     frame.show()
#     app.exec_()
#
#
# if __name__ == "__main__":
#     main()
