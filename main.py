import sys
from loguru import logger
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtCore import Qt, QElapsedTimer
from PyQt6.QtGui import QPixmap
from ana_sayfa_arayuz import AnaPage

log_file = "logs.log"
logger.remove()
logger.add(sys.stdout, level="INFO", colorize=True)
logger.add(log_file, level="DEBUG", rotation="500 MB", compression="zip")

app = QApplication(sys.argv)

pixmap = QPixmap("assets/APP.png")
if pixmap.isNull():
    logger.error("❌ HATA: 'assets/APP.png' bulunamadı!")
    sys.exit(1)

splash = QSplashScreen(pixmap)
splash.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
splash.show()

app.processEvents()

timer = QElapsedTimer()
timer.start()
while timer.elapsed() < 5000:
    app.processEvents()

window = AnaPage()
window.show()
splash.finish(window)

logger.info("Uygulama başlatıldı.")

sys.exit(app.exec())
