import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from models import DataManager
from main_window import MainWindow

if __name__ == '__main__':
    """ورژن ساده برای تست برنامه - بدون لاگین"""
    app = QApplication(sys.argv)

    # تنظیم جهت راست به چپ برای رابط کاربری فارسی
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    # تنظیم فونت برای نمایش بهتر فارسی
    font = QFont()
    font.setFamily("Arial")
    font.setPointSize(10)
    app.setFont(font)

    # ایجاد نمونه مدیریت داده
    data_manager = DataManager()

    # ایجاد پنجره اصلی
    window = MainWindow(data_manager)
    window.show()

    # اجرای برنامه
    sys.exit(app.exec())