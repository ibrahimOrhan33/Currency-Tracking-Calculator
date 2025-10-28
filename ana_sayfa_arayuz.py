import sys
from loguru import logger
import random
import datetime
import requests
import xml.etree.ElementTree as ET
from ana_sayfa import Ui_Form
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizePolicy, QComboBox, QCompleter, QLabel, QTableWidgetItem
from PyQt6.QtCore import QStringListModel, Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import QDateTime

log_file = "logs.log"
logger.remove()
logger.add(sys.stdout, level="INFO", colorize=True)
logger.add(log_file, level="DEBUG", rotation="500 MB", compression="zip")

def get_exchange_rates():
    try:
        url = "https://www.tcmb.gov.tr/kurlar/today.xml"
        response = requests.get(url)
        response.encoding = 'utf-8'
        root = ET.fromstring(response.text)

        currencies = {'TRY': 1.0}
        for currency in root.findall('Currency'):
            code = currency.get('CurrencyCode')
            forex_selling = currency.find('ForexSelling').text
            if forex_selling:
                currencies[code] = float(forex_selling.replace(',', '.'))

        logger.info("Döviz kurları başarıyla alındı.")
        return currencies
    except Exception as e:
        logger.error(f"Döviz kurları alınırken bir hata oluştu: {e}")
        return {}

class MarqueeLabel(QLabel):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Arial", 14))
        self.setStyleSheet("background-color: black; color: white;")
        self.setFixedHeight(30)

        self.items = items
        self.text = "   ".join(items)
        self.offset = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.scrollText)
        self.timer.start(30)

    def scrollText(self):
        self.offset += 2
        text_width = self.fontMetrics().horizontalAdvance(self.text)
        if self.offset > text_width + self.width():
            self.offset = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("black"))
        painter.setPen(QColor("white"))
        painter.setFont(self.font())

        text_width = self.fontMetrics().horizontalAdvance(self.text)
        x = self.width() - self.offset
        painter.drawText(x, self.height() - 10, self.text)

class AnaPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.ana = Ui_Form()
        self.ana.setupUi(self)
        ui = self.ana
        ui.lne_arama.textChanged.connect(self.filtrele)

        # Döviz kurlarını alıyoruz
        exchange_rates = get_exchange_rates()
        if not exchange_rates:
            logger.warning("Döviz kurları alınamadı, uygulama çalışmaya devam ediyor.")

        birim = list(exchange_rates.keys())
        fiyat = list(exchange_rates.values())

        kaydirilacak_liste = [f"{b}: {f:.2f}" for b, f in zip(birim, fiyat)]

        self.marquee = MarqueeLabel(kaydirilacak_liste, self)

        slider_layout = QVBoxLayout(ui.wdg_slider)
        slider_layout.addWidget(self.marquee)
        ui.wdg_slider.setLayout(slider_layout)

        ui.lbl_sonuc.setVisible(False)

        ui.tbl_kur.setRowCount(len(birim))           
        ui.tbl_kur.setColumnCount(2)                 
        ui.tbl_kur.setHorizontalHeaderLabels(["Birim", "Fiyat"])

        for i, (b, f) in enumerate(zip(birim, fiyat)):
            ui.tbl_kur.setItem(i, 0, QTableWidgetItem(b))
            ui.tbl_kur.setItem(i, 1, QTableWidgetItem(f"{f:.4f}"))

        ui.cmb_secilen1.addItems(birim)
        ui.cmb_secilen2.addItems(birim)

        completer1 = QCompleter(birim, self)
        completer1.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)  
        ui.cmb_secilen1.setCompleter(completer1)

        completer2 = QCompleter(birim, self)
        completer2.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        ui.cmb_secilen2.setCompleter(completer2)

        def hesapla():
            try:
                miktar = float(ui.lne_miktar.text())
                secilen1 = ui.cmb_secilen1.currentIndex()
                secilen2 = ui.cmb_secilen2.currentIndex()
                
                kur_orani = fiyat[secilen2] / fiyat[secilen1]
                sonuc = miktar * kur_orani

                ui.lbl_sonuc.setText(f"{sonuc:.2f}")
                ui.lbl_sonuc.setVisible(True)

                logger.info(f"Hesaplama tamamlandı: {miktar} {birim[secilen2]} = {sonuc:.2f} {birim[secilen1]}")
            except ValueError:
                ui.lbl_sonuc.setText("Geçerli bir sayı giriniz!")
                ui.lbl_sonuc.setVisible(True)
                logger.warning("Geçerli bir sayı girilmedi.")

        ui.btn_hesapla.clicked.connect(hesapla)

    
    def filtrele(self, text):
        ui = self.ana
        aranan = text.lower()

        for row in range(ui.tbl_kur.rowCount()):
            item = ui.tbl_kur.item(row, 0)
            if item:
                birim = item.text().lower()
                if aranan in birim:
                    ui.tbl_kur.setRowHidden(row, False)
                else:
                    ui.tbl_kur.setRowHidden(row, True)

