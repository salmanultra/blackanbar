import sys
from PyQt6.QtWidgets import (
QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QFormLayout,
QDialog, QSpinBox, QDateTimeEdit, QTextEdit, QSplitter, QStackedWidget,
QMessageBox, QStatusBar, QHeaderView, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QDateTime
from PyQt6.QtGui import QFont, QColor, QPixmap
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('QtAgg')  # استفاده از QtAgg backend برای PyQt6

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from models import Product, Transaction, User, DataManager
from utils import (
    load_products_from_excel, save_products_to_excel,
    load_transactions_from_excel, save_transactions_to_excel,
    load_users_from_excel, save_users_to_excel,
    validate_product, validate_transaction
)

class MainWindow(QMainWindow):
    def __init__(self, data_manager, current_user=None):
        super().__init__()
        self.data_manager = data_manager
        self.current_user = current_user
        self.restart_requested = False
        self.init_ui()
        self.load_data()  # بارگذاری داده‌ها از فایل‌های Excel

    def init_ui(self):
        """راه‌اندازی رابط کاربری مدرن"""
        self.setWindowTitle('🎯 سیستم انبارداری مدرن')
        self.setGeometry(100, 100, 1400, 900)

        # تنظیم سبک مدرن با گرادینت آبی تیره و بنفش
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f0f23, stop:1 #1a1a2e);
                color: #ffffff;
            }

            /* نوار کناری مدرن */
            #sidebar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #16213e, stop:1 #0f0f23);
                border: none;
                border-radius: 0;
                min-width: 280px;
                max-width: 280px;
            }

            /* دکمه‌های نوار کناری */
            #sidebar QPushButton {
                background: transparent;
                color: #e0e7ff;
                border: none;
                padding: 18px 25px;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 600;
                text-align: left;
                margin: 8px 15px;
                transition: all 0.3s ease;
            }

            #sidebar QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e40af, stop:1 #3b82f6);
                color: #ffffff;
                margin-left: 10px;
                margin-right: 20px;
                transform: translateX(5px);
            }

            #sidebar QPushButton:checked,
            #sidebar QPushButton[selected="true"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3b82f6, stop:1 #1d4ed8);
                color: #ffffff;
                border: 1px solid #60a5fa;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            }

            /* دکمه‌های اصلی */
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3b82f6, stop:1 #1d4ed8);
                color: #ffffff;
                border: none;
                padding: 12px 24px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            }

            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1d4ed8, stop:1 #1e40af);
                box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
                transform: translateY(-2px);
            }

            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e40af, stop:1 #1e3a8a);
                box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
                transform: translateY(1px);
            }

            /* دکمه‌های خطرناک */
            QPushButton[danger="true"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #dc2626, stop:1 #b91c1c);
            }

            QPushButton[danger="true"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #b91c1c, stop:1 #991b1b);
            }

            /* عنوان‌ها */
            QLabel {
                color: #f1f5f9;
                font-size: 16px;
                font-weight: 500;
            }

            QLabel[title="true"] {
                color: #ffffff;
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 10px;
            }

            QLabel[subtitle="true"] {
                color: #cbd5e1;
                font-size: 14px;
                font-weight: 400;
            }

            /* جداول مدرن */
            QTableWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e293b, stop:1 #0f172a);
                color: #f1f5f9;
                gridline-color: #334155;
                border: 1px solid #475569;
                border-radius: 12px;
                selection-background-color: #3b82f6;
                alternate-background-color: #0f162a;
            }

            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #334155;
            }

            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e40af, stop:1 #3730a3);
                color: #ffffff;
                padding: 12px 8px;
                border: none;
                font-weight: 600;
                font-size: 14px;
                text-align: center;
                border-radius: 0;
            }

            /* ورودی‌ها */
            QLineEdit, QComboBox, QSpinBox, QDateTimeEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e293b, stop:1 #334155);
                color: #f1f5f9;
                border: 2px solid #475569;
                padding: 10px 12px;
                border-radius: 8px;
                font-size: 14px;
                transition: all 0.3s ease;
            }

            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateTimeEdit:focus {
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
            }

            /* نوار وضعیت مدرن */
            QStatusBar {
                color: #94a3b8;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f172a, stop:1 #1e293b);
                border-top: 1px solid #475569;
                padding: 8px 16px;
            }

            /* مخزن‌کننده */
            QSplitter::handle {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #475569, stop:1 #334155);
                width: 1px;
            }

            /* دیالوگ‌ها */
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f172a, stop:1 #1e293b);
                color: #f1f5f9;
                border-radius: 16px;
            }

            /* کارت‌های داشبورد */
            QWidget[card="true"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 41, 59, 0.9), stop:1 rgba(15, 23, 42, 0.9));
                border: 1px solid rgba(71, 85, 105, 0.5);
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                backdrop-filter: blur(20px);
            }
        """)

        # چرخنده اصلی
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        # نوار کناری مدرن
        self.sidebar = self.create_modern_sidebar()
        splitter.addWidget(self.sidebar)

        # ناحیه مرکزی با QStackedWidget
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("""
            QStackedWidget {
                background: transparent;
                border-radius: 16px;
                margin: 20px;
            }
        """)
        splitter.addWidget(self.stack)

        # صفحات مدرن
        self.dashboard_page = self.create_modern_dashboard_page()
        self.products_page = self.create_modern_products_page()
        self.transactions_page = self.create_modern_transactions_page()
        self.reports_page = self.create_modern_reports_page()
        self.users_page = self.create_modern_users_page()

        self.stack.addWidget(self.dashboard_page)  # ایندکس 0
        self.stack.addWidget(self.products_page)    # 1
        self.stack.addWidget(self.transactions_page) # 2
        self.stack.addWidget(self.reports_page)     # 3
        self.stack.addWidget(self.users_page)       # 4

        # نوار وضعیت مدرن
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('🚀 سیستم انبارداری مدرن آماده است!')

        # تنظیم نسبت‌ها
        splitter.setSizes([280, 1120])

        # تنظیم انیمیشن‌ها
        self.setup_animations()

    def create_modern_sidebar(self):
        """ایجاد نوار کناری مدرن"""
        widget = QWidget()
        widget.setObjectName("sidebar")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 40, 20, 40)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # لوگو
        try:
            from PyQt6.QtGui import QPixmap

            logo_label = QLabel()
            pixmap = QPixmap("logow.png").scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_label.setStyleSheet("""
                QLabel {
                    margin-bottom: 20px;
                    padding: 10px 0;
                    border-bottom: 1px solid #475569;
                    border-radius: 8px;
                    background: rgba(71, 85, 105, 0.2);
                }
            """)
        except Exception as e:
            # اگر لوگو پیدا نشد، از متن استفاده کنیم
            logo_label = QLabel("🎯 انبار\nمدیریت")
            logo_label.setStyleSheet("""
                QLabel {
                    color: #60a5fa;
                    font-size: 24px;
                    font-weight: 700;
                    margin-bottom: 20px;
                    padding: 20px 0;
                    text-align: center;
                    border-bottom: 1px solid #475569;
                }
            """)

        layout.addWidget(logo_label)

        # دکمه‌های ناوبری مدرن
        self.nav_buttons = []
        buttons = [
            ('🏠 داشبورد', self.show_dashboard, 'نمایش آماری سیستم'),
            ('📦 کالاها', self.show_products, 'مدیریت کالا‌ها'),
            ('🔄 تراکنش‌ها', self.show_transactions, 'ثبت و مشاهده تراکنش‌ها'),
            ('📊 گزارش‌ها', self.show_reports, 'نمودارها و گزارش‌ها'),
            ('👥 کاربران', self.show_users, 'مدیریت کاربران')
        ]

        for text, handler, tooltip in buttons:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.clicked.connect(handler)
            btn.setToolTip(tooltip)
            btn.setProperty("navBtn", "true")
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        layout.addStretch()

        # اطلاعات کاربر و گزینه خروج
        user_section = QWidget()
        user_layout = QVBoxLayout(user_section)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(8)

        # اطلاعات کاربر
        if self.current_user:
            user_name = self.current_user.username
            user_role = self.current_user.role
        else:
            user_name = "مدیر سیستم"
            user_role = "مدیر"

        user_info = QLabel(f"👤 {user_name}\n🔸 {user_role}")
        user_info.setStyleSheet("""
            QLabel {
                color: #cbd5e1;
                font-size: 12px;
                font-weight: 500;
                padding: 12px 0;
                text-align: center;
                border-top: 1px solid #475569;
                background: rgba(71, 85, 105, 0.2);
                border-radius: 6px;
            }
        """)
        user_layout.addWidget(user_info)

        # دکمه خروج
        logout_btn = QPushButton("🚪 خروج")
        logout_btn.setStyleSheet("""
            QPushButton {
                background: rgba(239, 68, 68, 0.1);
                color: #ef4444;
                border: 1px solid #ef4444;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                transition: all 0.3s ease;
                margin: 0 20px;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.2);
                border-color: #dc2626;
                color: #dc2626;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        user_layout.addWidget(logout_btn)

        layout.addWidget(user_section)
        return widget

    def setup_animations(self):
        """تنظیم انیمیشن‌ها"""
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

        self.fade_animation = QPropertyAnimation(self.stack, b"opacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def show_dashboard(self):
        self.stack.setCurrentIndex(0)
        self.update_nav_selection(0)
        self.status_bar.showMessage('📊 داشبورد سیستم نمایش داده شد.')

    def show_products(self):
        self.stack.setCurrentIndex(1)
        self.update_nav_selection(1)
        self.refresh_products_table()
        self.status_bar.showMessage('📦 مدیریت کالاها فعال شد.')

    def show_transactions(self):
        self.stack.setCurrentIndex(2)
        self.update_nav_selection(2)
        self.refresh_transactions_table()
        self.status_bar.showMessage('🔄 مدیریت تراکنش‌ها فعال شد.')

    def show_reports(self):
        self.stack.setCurrentIndex(3)
        self.update_nav_selection(3)
        self.refresh_reports()
        self.status_bar.showMessage('📈 گزارش‌ها و نمودارها نمایش داده شد.')

    def show_users(self):
        self.stack.setCurrentIndex(4)
        self.update_nav_selection(4)
        self.refresh_users_table()
        self.status_bar.showMessage('👥 مدیریت کاربران فعال شد.')

    def update_nav_selection(self, index):
        """به‌روزرسانی انتخاب نوار کناری"""
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def show_dashboard(self):
        self.stack.setCurrentIndex(0)
        self.status_bar.showMessage('داشبورد نمایش داده شد.')

    def show_products(self):
        self.stack.setCurrentIndex(1)
        self.refresh_products_table()
        self.status_bar.showMessage('مدیریت کالاها.')

    def show_transactions(self):
        self.stack.setCurrentIndex(2)
        self.refresh_transactions_table()
        self.status_bar.showMessage('مدیریت تراکنش‌ها.')

    def show_reports(self):
        self.stack.setCurrentIndex(3)
        self.refresh_reports()
        self.status_bar.showMessage('گزارش‌ها.')

    def show_users(self):
        self.stack.setCurrentIndex(4)
        self.refresh_users_table()
        self.status_bar.showMessage('مدیریت کاربران.')

    def create_modern_dashboard_page(self):
        """صفحه داشبورد مدرن"""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # عنوان داشبورد
        title = QLabel("📊 داشبورد سیستم انبارداری")
        title.setProperty("title", "true")
        main_layout.addWidget(title)

        # زیرعنوان
        subtitle = QLabel("نمای کلی از وضعیت انبار و فعالیت‌های سیستم")
        subtitle.setProperty("subtitle", "true")
        main_layout.addWidget(subtitle)

        # کارت‌های آماری
        stats_layout = QHBoxLayout()

        self.stats_cards = []
        stats_data = [
            ("📦 کالاها", "total_products", "#3b82f6"),
            ("🔄 تراکنش‌ها", "total_transactions", "#10b981"),
            ("📈 موجودی کل", "total_stock", "#f59e0b"),
            ("⚠️ موجودی کم", "low_stock", "#ef4444")
        ]

        for icon_text, data_type, color in stats_data:
            card = self.create_stats_card(icon_text, color)
            stats_layout.addWidget(card)
            self.stats_cards.append((card, data_type))

        main_layout.addLayout(stats_layout)

        # چارت‌های داشبورد
        charts_widget = QWidget()
        charts_layout = QHBoxLayout(charts_widget)

        # چارت موجودی
        stock_chart_card = self.create_chart_card("📊 وضعیت موجودی کالا‌ها", "stock_chart")
        charts_layout.addWidget(stock_chart_card)

        # چارت تراکنش‌ها
        transactions_chart_card = self.create_chart_card("📈 فعالیت‌های اخیر", "transactions_chart")
        charts_layout.addWidget(transactions_chart_card)

        main_layout.addWidget(charts_widget)

        # به‌روزرسانی اولیه داده‌ها
        QTimer.singleShot(500, self.update_modern_dashboard_stats)

        return widget

    def create_stats_card(self, title, color):
        """ایجاد کارت آماری مدرن"""
        card = QWidget()
        card.setProperty("card", "true")
        card.setFixedSize(250, 120)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)

        # عنوان کارت
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 8px;
            }}
        """)
        layout.addWidget(title_label)

        # مقدار
        value_label = QLabel("0")
        value_label.setObjectName("value")
        value_label.setStyleSheet("""
            QLabel#value {
                color: #ffffff;
                font-size: 32px;
                font-weight: 700;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(value_label)

        # توضیحات
        desc_label = QLabel("")
        desc_label.setObjectName("description")
        desc_label.setStyleSheet("""
            QLabel#description {
                color: #94a3b8;
                font-size: 12px;
                font-weight: 500;
            }
        """)
        layout.addWidget(desc_label)

        return card

    def create_chart_card(self, title, chart_type):
        """ایجاد کارت چارت"""
        card = QWidget()
        card.setProperty("card", "true")
        card.setMinimumSize(300, 250)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)

        # عنوان چارت
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #60a5fa;
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)

        # ناحیه چارت
        chart_widget = QWidget()
        chart_widget.setObjectName(chart_type)
        chart_widget.setMinimumHeight(200)
        layout.addWidget(chart_widget)

        return card

    def update_modern_dashboard_stats(self):
        """به‌روزرسانی آمار داشبورد مدرن"""
        products = self.data_manager.get_products()
        transactions = self.data_manager.get_transactions()

        stats_values = {
            "total_products": len(products),
            "total_transactions": len(transactions),
            "total_stock": sum(p.current_stock for p in products),
            "low_stock": len([p for p in products if p.current_stock < 10])
        }

        stats_descriptions = {
            "total_products": "کالای ثبت شده",
            "total_transactions": "تراکنش انجام شده",
            "total_stock": "مجموع موجودی",
            "low_stock": "نیاز به replenishment"
        }

        for i, (card, data_type) in enumerate(self.stats_cards):
            value_label = card.findChild(QLabel, "value")
            desc_label = card.findChild(QLabel, "description")

            if value_label:
                value_label.setText(str(stats_values.get(data_type, 0)))
            if desc_label:
                desc_label.setText(stats_descriptions.get(data_type, ""))

        # به‌روزرسانی چارت‌ها
        self.update_dashboard_charts()

    def logout(self):
        """خروج از سیستم و بازگشت به صفحه لاگین"""
        reply = QMessageBox.question(
            self,
            'تأیید خروج',
            f'آیا مطمئن هستید که می‌خواهید از کاربر \"{self.current_user.username if self.current_user else "ناشناس"}\" خارج شوید؟',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.restart_requested = True
            self.hide()
            # ذخیره داده‌ها هنگام خروج
            save_products_to_excel(self.data_manager)
            save_transactions_to_excel(self.data_manager)
            save_users_to_excel(self.data_manager)

    def update_dashboard_charts(self):
        """به‌روزرسانی چارت‌های داشبورد"""
        # پاک کردن چارت‌های قبلی
        stock_chart = self.findChild(QWidget, "stock_chart")
        if stock_chart:
            for child in stock_chart.children():
                if hasattr(child, 'deleteLater'):
                    child.deleteLater()

        transactions_chart = self.findChild(QWidget, "transactions_chart")
        if transactions_chart:
            for child in transactions_chart.children():
                if hasattr(child, 'deleteLater'):
                    child.deleteLater()

        # ایجاد چارت جدید موجودی
        self.create_stock_chart()

        # ایجاد چارت فعالیت‌ها (در آینده)

    def create_stock_chart(self):
        """ایجاد چارت موجودی کالا‌ها"""
        try:
            products = self.data_manager.get_products()
            if products:
                figure = Figure(figsize=(5, 4), dpi=80)
                figure.patch.set_facecolor('none')

                ax = figure.add_subplot(111)
                ax.set_facecolor('none')

                names = [p.name[:10] if len(p.name) > 10 else p.name for p in products]
                stocks = [p.current_stock for p in products]
                capacities = [p.capacity for p in products]

                x = range(len(names))
                ax.bar(x, stocks, label='موجودی فعلی', color='#3b82f6', alpha=0.8)
                ax.bar(x, [cap - stock for cap, stock in zip(capacities, stocks)],
                      bottom=stocks, label='ظرفیت باقی', color='#94a3b8', alpha=0.4)

                ax.set_title('وضعیت موجودی کالا‌ها', fontsize=12, color='#ffffff', pad=20)
                ax.set_xlabel('کالا', fontsize=10, color='#cbd5e1')
                ax.set_ylabel('مقدار', fontsize=10, color='#cbd5e1')
                ax.set_xticks(x)
                ax.set_xticklabels(names, rotation=45, ha='right', fontsize=8, color='#cbd5e1')
                ax.grid(True, alpha=0.2, color='#475569')
                ax.legend(fontsize=8)

                # رنگ‌آمیزی محورها و گرید
                ax.tick_params(colors='#cbd5e1')
                ax.spines['bottom'].set_color('#475569')
                ax.spines['top'].set_color('#475569')
                ax.spines['left'].set_color('#475569')
                ax.spines['right'].set_color('#475569')

                canvas = FigureCanvas(figure, self.findChild(QWidget, "stock_chart"))
                layout = QVBoxLayout(self.findChild(QWidget, "stock_chart"))
                layout.addWidget(canvas)
                layout.setContentsMargins(0, 0, 0, 0)

        except Exception as e:
            print(f"خطا در ایجاد چارت: {e}")

    def create_modern_products_page(self):
        """صفحه مدیریت کالاها مدرن"""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # عنوان و نوار جستجو
        header_layout = QHBoxLayout()

        title = QLabel("📦 مدیریت کالاها")
        title.setProperty("title", "true")
        title.setStyleSheet("margin-bottom: 0px;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # نوار جستجو
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 جستجو:")
        search_label.setStyleSheet("color: #cbd5e1; font-size: 14px; margin-right: 8px;")
        search_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجو بر اساس نام، کد یا دسته‌بندی...")
        self.search_input.setMaximumWidth(300)
        self.search_input.textChanged.connect(self.filter_products_table)
        search_layout.addWidget(self.search_input)

        header_layout.addLayout(search_layout)
        main_layout.addLayout(header_layout)

        # جدول کالاها مدرن
        table_card = QWidget()
        table_card.setProperty("card", "true")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(20, 15, 20, 15)

        self.products_table = QTableWidget()
        self.products_table.setColumnCount(8)
        self.products_table.setHorizontalHeaderLabels(['کد', 'نام', 'دسته‌بندی', 'ظرفیت', 'موجودی فعلی', 'وضعیت', 'کاهش', 'افزایش'])
        self.products_table.horizontalHeader().setStretchLastSection(True)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.products_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # تنظیم اندازه ستون‌ها
        self.products_table.setColumnWidth(0, 80)   # کد
        self.products_table.setColumnWidth(1, 200)  # نام
        self.products_table.setColumnWidth(2, 150)  # دسته‌بندی
        self.products_table.setColumnWidth(3, 100)  # ظرفیت
        self.products_table.setColumnWidth(4, 120)  # موجودی فعلی
        self.products_table.setColumnWidth(5, 100)  # وضعیت

        table_layout.addWidget(self.products_table)
        main_layout.addWidget(table_card)

        # نوار ابزار
        toolbar_layout = QHBoxLayout()

        # دکمه‌های اصلی
        button_group = QHBoxLayout()
        button_group.setSpacing(15)

        add_btn = QPushButton('➕ افزودن کالا')
        add_btn.clicked.connect(self.add_product)
        add_btn.setStyleSheet("QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #10b981, stop:1 #059669); }")

        edit_btn = QPushButton('✏️ ویرایش')
        edit_btn.clicked.connect(self.edit_product)

        delete_btn = QPushButton('🗑️ حذف')
        delete_btn.clicked.connect(self.delete_product)
        delete_btn.setProperty("danger", "true")

        refresh_btn = QPushButton('🔄 تازه‌سازی')
        refresh_btn.clicked.connect(self.refresh_products_table)
        refresh_btn.setStyleSheet("QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #8b5cf6, stop:1 #7c3aed); }")

        save_btn = QPushButton('💾 ذخیره به Excel')
        save_btn.clicked.connect(lambda: save_products_to_excel(self.data_manager))

        button_group.addWidget(add_btn)
        button_group.addWidget(edit_btn)
        button_group.addWidget(delete_btn)
        button_group.addWidget(refresh_btn)
        button_group.addWidget(save_btn)
        button_group.addStretch()

        toolbar_layout.addLayout(button_group)

        # آمار محصولات
        stats_layout = QVBoxLayout()
        self.products_count_label = QLabel("📊 0 کالا")
        self.products_count_label.setStyleSheet("color: #cbd5e1; font-size: 14px; font-weight: 600;")
        stats_layout.addWidget(self.products_count_label)

        self.products_stock_label = QLabel("📈 موجودی کل: 0")
        self.products_stock_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        stats_layout.addWidget(self.products_stock_label)

        toolbar_layout.addLayout(stats_layout)

        main_layout.addLayout(toolbar_layout)

        return widget

    def refresh_products_table(self):
        """به‌روزرسانی جدول کالاها مدرن با امکان تنظیم سریع تعداد"""
        products = self.data_manager.get_products()
        self.products_table.setRowCount(len(products))

        for row, product in enumerate(products):
            # کد
            code_item = QTableWidgetItem(product.code)
            code_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.products_table.setItem(row, 0, code_item)

            # نام
            name_item = QTableWidgetItem(product.name)
            self.products_table.setItem(row, 1, name_item)

            # دسته‌بندی
            category_item = QTableWidgetItem(product.category)
            self.products_table.setItem(row, 2, category_item)

            # ظرفیت
            capacity_item = QTableWidgetItem(str(product.capacity))
            capacity_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.products_table.setItem(row, 3, capacity_item)

            # موجودی فعلی
            stock_item = QTableWidgetItem(str(product.current_stock))
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.products_table.setItem(row, 4, stock_item)

            # وضعیت
            status_item = self.create_status_indicator(product)
            self.products_table.setItem(row, 5, status_item)

            # دکمه کاهش
            decrease_btn = QPushButton("➖")
            decrease_btn.setFixedSize(40, 30)
            decrease_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc2626;
                    color: #ffffff;
                    border: none;
                    border-radius: 6px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #b91c1c;
                }
                QPushButton:pressed {
                    background-color: #991b1b;
                }
                QPushButton:disabled {
                    background-color: #6b7280;
                    color: #9ca3af;
                }
            """)
            decrease_btn.clicked.connect(lambda checked, p=product: self.decrease_product_stock(p))
            decrease_btn.setEnabled(product.current_stock > 0)
            self.products_table.setCellWidget(row, 6, decrease_btn)

            # دکمه افزایش
            increase_btn = QPushButton("➕")
            increase_btn.setFixedSize(40, 30)
            increase_btn.setStyleSheet("""
                QPushButton {
                    background-color: #059669;
                    color: #ffffff;
                    border: none;
                    border-radius: 6px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #047857;
                }
                QPushButton:pressed {
                    background-color: #065f46;
                }
            """)
            increase_btn.clicked.connect(lambda checked, p=product: self.increase_product_stock(p))
            self.products_table.setCellWidget(row, 7, increase_btn)

        # به‌روزرسانی آمار
        self.update_products_stats(products)

    def create_status_indicator(self, product):
        """ایجاد نشانگر وضعیت محصول"""
        if product.current_stock == 0:
            status = "❌ خالی"
            color = "#ef4444"
        elif product.current_stock < product.capacity * 0.1:
            status = "⚠️ کم"
            color = "#f59e0b"
        elif product.current_stock > product.capacity * 0.9:
            status = "📦 پر"
            color = "#10b981"
        else:
            status = "✅ نرمال"
            color = "#3b82f6"

        status_item = QTableWidgetItem(status)
        status_item.setBackground(QColor(color))
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return status_item

    def update_products_stats(self, products):
        """به‌روزرسانی آمار محصولات"""
        total_products = len(products)
        total_stock = sum(p.current_stock for p in products)
        total_capacity = sum(p.capacity for p in products)

        if hasattr(self, 'products_count_label'):
            self.products_count_label.setText(f"📊 {total_products} کالا")

        if hasattr(self, 'products_stock_label'):
            self.products_stock_label.setText(f"📈 موجودی کل: {total_stock}/{total_capacity}")

    def filter_products_table(self):
        """فیلتر کردن جدول محصولات با ساختار جدید"""
        search_text = self.search_input.text().lower()
        products = self.data_manager.get_products()

        filtered_products = []
        for product in products:
            search_target = f"{product.code} {product.name} {product.category}".lower()
            if search_text in search_target:
                filtered_products.append(product)

        # نمایش محصولات فیلتر شده با ساختار جدید
        self.products_table.setRowCount(len(filtered_products))
        for row, product in enumerate(filtered_products):
            # کد
            code_item = QTableWidgetItem(product.code)
            code_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.products_table.setItem(row, 0, code_item)

            # نام
            name_item = QTableWidgetItem(product.name)
            self.products_table.setItem(row, 1, name_item)

            # دسته‌بندی
            category_item = QTableWidgetItem(product.category)
            self.products_table.setItem(row, 2, category_item)

            # ظرفیت
            capacity_item = QTableWidgetItem(str(product.capacity))
            capacity_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.products_table.setItem(row, 3, capacity_item)

            # موجودی فعلی
            stock_item = QTableWidgetItem(str(product.current_stock))
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.products_table.setItem(row, 4, stock_item)

            # وضعیت
            status_item = self.create_status_indicator(product)
            self.products_table.setItem(row, 5, status_item)

            # پاک کردن دکمه‌های قبلی
            self.products_table.setCellWidget(row, 6, None)
            self.products_table.setCellWidget(row, 7, None)

            # دکمه کاهش
            decrease_btn = QPushButton("➖")
            decrease_btn.setFixedSize(40, 30)
            decrease_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc2626;
                    color: #ffffff;
                    border: none;
                    border-radius: 6px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #b91c1c;
                }
                QPushButton:pressed {
                    background-color: #991b1b;
                }
                QPushButton:disabled {
                    background-color: #6b7280;
                    color: #9ca3af;
                }
            """)
            decrease_btn.clicked.connect(lambda checked, p=product: self.decrease_product_stock(p))
            decrease_btn.setEnabled(product.current_stock > 0)
            self.products_table.setCellWidget(row, 6, decrease_btn)

            # دکمه افزایش
            increase_btn = QPushButton("➕")
            increase_btn.setFixedSize(40, 30)
            increase_btn.setStyleSheet("""
                QPushButton {
                    background-color: #059669;
                    color: #ffffff;
                    border: none;
                    border-radius: 6px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #047857;
                }
                QPushButton:pressed {
                    background-color: #065f46;
                }
            """)
            increase_btn.clicked.connect(lambda checked, p=product: self.increase_product_stock(p))
            self.products_table.setCellWidget(row, 7, increase_btn)

        # به‌روزرسانی آمار برای محصولات فیلتر شده
        self.update_products_stats(filtered_products)

    def add_product(self):
        dialog = ProductDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            product = Product(dialog.code.text(), dialog.name.text(), dialog.category.text(),
                              dialog.capacity.value(), 0)
            if validate_product(product):
                self.data_manager.add_product(product)
                self.refresh_products_table()
                self.status_bar.showMessage('کالا اضافه شد.')
            else:
                QMessageBox.warning(self, 'خطا', 'داده‌های کالا نامعتبر است.')

    def edit_product(self):
        """ویرایش کالا انتخاب‌شده"""
        selected_row = self.products_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, 'خطا', 'هیچ کالایی انتخاب نشده است.')
            return
        product = self.data_manager.get_products()[selected_row]
        dialog = ProductDialog()
        dialog.code.setText(product.code)
        dialog.name.setText(product.name)
        dialog.category.setText(product.category)
        dialog.capacity.setValue(product.capacity)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_product = Product(dialog.code.text(), dialog.name.text(), dialog.category.text(),
                                      dialog.capacity.value(), product.current_stock)
            if validate_product(updated_product):
                self.data_manager.update_product(product.code, updated_product)
                self.refresh_products_table()
                self.status_bar.showMessage('کالا ویرایش شد.')
            else:
                QMessageBox.warning(self, 'خطا', 'داده‌های کالا نامعتبر است.')

    def delete_product(self):
        """حذف کالا انتخاب‌شده"""
        selected_row = self.products_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, 'خطا', 'هیچ کالایی انتخاب نشده است.')
            return
        product = self.data_manager.get_products()[selected_row]
        reply = QMessageBox.question(self, 'تأیید', f'آیا مطمئن هستید که می‌خواهید کالا {product.name} را حذف کنید؟',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.data_manager.delete_product(product.code)
            self.refresh_products_table()
            self.status_bar.showMessage('کالا حذف شد.')

    def create_modern_transactions_page(self):
        """صفحه مدیریت تراکنش‌ها مدرن"""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # عنوان
        title = QLabel("🔄 مدیریت تراکنش‌ها")
        title.setProperty("title", "true")
        main_layout.addWidget(title)

        # جدول تراکنش‌ها مدرن
        table_card = QWidget()
        table_card.setProperty("card", "true")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(20, 15, 20, 15)

        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels(['کد محصول', 'نام کالا', 'نوع تراکنش', 'مقدار', 'تاریخ', 'کاربر'])
        self.transactions_table.setAlternatingRowColors(True)
        self.transactions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.transactions_table.horizontalHeader().setStretchLastSection(True)

        table_layout.addWidget(self.transactions_table)
        main_layout.addWidget(table_card)

        # دکمه‌های مدرن
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        add_btn = QPushButton('➕ افزودن تراکنش')
        add_btn.clicked.connect(self.add_transaction)
        add_btn.setStyleSheet("QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #10b981, stop:1 #059669); }")

        save_btn = QPushButton('💾 ذخیره به Excel')
        save_btn.clicked.connect(lambda: save_transactions_to_excel(self.data_manager))

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)

        return widget

    def refresh_transactions_table(self):
        """به‌روزرسانی جدول تراکنش‌ها"""
        transactions = self.data_manager.get_transactions()
        self.transactions_table.setRowCount(len(transactions))
        for row, transaction in enumerate(transactions):
            self.transactions_table.setItem(row, 0, QTableWidgetItem(transaction.product_code))
            self.transactions_table.setItem(row, 1, QTableWidgetItem(transaction.transaction_type))
            self.transactions_table.setItem(row, 2, QTableWidgetItem(str(transaction.quantity)))
            self.transactions_table.setItem(row, 3, QTableWidgetItem(transaction.date.strftime('%Y-%m-%d %H:%M')))
            self.transactions_table.setItem(row, 4, QTableWidgetItem(transaction.user))

        # تنظیم اندازه ستون‌ها
        self.transactions_table.resizeColumnsToContents()
        if transactions:
            self.transactions_table.horizontalHeader().setStretchLastSection(True)

    def add_transaction(self):
        dialog = TransactionDialog(self.data_manager.get_products())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            transaction = Transaction(dialog.product_combo.currentText().split(' - ')[0],
                                      dialog.type_combo.currentText(), dialog.quantity.value(),
                                      dialog.date.dateTime().toPyDateTime(), 'مدیر')  # موقت
            if validate_transaction(transaction, self.data_manager.get_products()):
                self.data_manager.add_transaction(transaction)
                self.refresh_transactions_table()
                self.status_bar.showMessage('تراکنش اضافه شد.')
            else:
                QMessageBox.warning(self, 'خطا', 'داده‌های تراکنش نامعتبر است.')

    def create_modern_reports_page(self):
        """صفحه گزارش‌ها مدرن"""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # عنوان
        title = QLabel("📊 گزارش‌ها و تحلیل‌ها")
        title.setProperty("title", "true")
        main_layout.addWidget(title)

        # چارت‌های مختلف
        charts_container = QWidget()
        charts_layout = QHBoxLayout(charts_container)
        charts_layout.setSpacing(20)

        # چارت میله‌ای موجودی
        stock_chart_card = QWidget()
        stock_chart_card.setProperty("card", "true")
        stock_chart_card.setMinimumSize(400, 300)
        stock_layout = QVBoxLayout(stock_chart_card)
        stock_layout.setContentsMargins(20, 15, 20, 15)

        stock_title = QLabel("📈 وضعیت موجودی کالا‌ها")
        stock_title.setStyleSheet("color: #60a5fa; font-size: 16px; font-weight: 600; margin-bottom: 10px;")
        stock_layout.addWidget(stock_title)

        self.reports_chart_widget = QWidget()
        self.reports_chart_widget.setMinimumHeight(250)
        stock_layout.addWidget(self.reports_chart_widget)

        charts_layout.addWidget(stock_chart_card)

        # چارت دایره‌ای توزیع (در آینده)
        distribution_card = QWidget()
        distribution_card.setProperty("card", "true")
        distribution_card.setMinimumSize(300, 300)
        dist_layout = QVBoxLayout(distribution_card)
        dist_layout.setContentsMargins(20, 15, 20, 15)

        dist_title = QLabel("🥧 توزیع دسته‌بندی‌ها")
        dist_title.setStyleSheet("color: #60a5fa; font-size: 16px; font-weight: 600; margin-bottom: 10px;")
        dist_layout.addWidget(dist_title)

        self.distribution_chart_widget = QWidget()
        self.distribution_chart_widget.setMinimumHeight(250)
        dist_layout.addWidget(self.distribution_chart_widget)

        charts_layout.addWidget(distribution_card)

        main_layout.addWidget(charts_container)

        # آمار خلاصه
        summary_card = QWidget()
        summary_card.setProperty("card", "true")
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(20, 15, 20, 15)

        summary_title = QLabel("📋 آمار خلاصه")
        summary_title.setStyleSheet("color: #60a5fa; font-size: 16px; font-weight: 600; margin-bottom: 15px;")
        summary_layout.addWidget(summary_title)

        # در آینده آمار پیشرفته اینجا اضافه خواهد شد
        summary_text = QLabel("آمار پیشرفته در نسخه‌های بعدی در دسترس خواهد بود")
        summary_text.setStyleSheet("color: #cbd5e1; font-size: 14px; text-align: center;")
        summary_layout.addWidget(summary_text)

        main_layout.addWidget(summary_card)

        return widget

    def refresh_reports(self):
        """به‌روزرسانی گزارش‌ها با نمودار موجودی"""
        try:
            # پاک کردن قبلی اگر وجود دارد
            if hasattr(self, 'chart_canvas') and self.chart_canvas:
                try:
                    # پیدا کردن چارت ها
                    stock_chart = self.findChild(QWidget, "stock_chart")
                    if stock_chart and stock_chart.layout():
                        stock_chart.layout().removeWidget(self.chart_canvas)
                    self.chart_canvas.deleteLater()
                    self.chart_canvas = None
                except Exception as e:
                    print(f"خطا در پاک کردن چارت قدیمی: {e}")

            # نمودار جدید
            figure = Figure(figsize=(6, 4), dpi=80)
            figure.patch.set_facecolor('none')
            if hasattr(FigureCanvas, '__init__') and FigureCanvas.__doc__:
                # اگر FigureCanvas نیاز به parent دارد
                canvas = FigureCanvas(figure)
            else:
                # اگر FigureCanvas نیاز به parent دارد
                canvas = FigureCanvas(figure)
            ax = figure.add_subplot(111)
            ax.set_facecolor('none')

            # تنظیم رنگ‌های تاریک برای تم مدرن
            ax.tick_params(colors='#cbd5e1')
            ax.spines['bottom'].set_color('#475569')
            ax.spines['top'].set_color('#475569')
            ax.spines['left'].set_color('#475569')
            ax.spines['right'].set_color('#475569')
            ax.grid(True, alpha=0.2, color='#475569')

            products = self.data_manager.get_products()
            if products:
                names = [p.name[:15] + '...' if len(p.name) > 15 else p.name for p in products]  # محدود کردن طول نام‌ها
                stocks = [p.current_stock for p in products]

                bars = ax.bar(range(len(names)), stocks, color='#3b82f6', alpha=0.8)

                ax.set_title('📊 وضعیت موجودی کالا‌ها', fontsize=14, color='#ffffff', pad=20)
                ax.set_xlabel('کالا', fontsize=12, color='#cbd5e1')
                ax.set_ylabel('موجودی', fontsize=12, color='#cbd5e1')
                ax.set_xticks(range(len(names)))
                ax.set_xticklabels(names, rotation=45, ha='right', fontsize=10, color='#cbd5e1')

                # اضافه کردن مقادیر روی میله‌ها
                for i, v in enumerate(stocks):
                    ax.text(i, v + max(stocks)*0.01, str(v), ha='center', va='bottom', fontsize=9, color='#ffffff')
            else:
                ax.text(0.5, 0.5, '🔍 هیچ کالایی موجود نیست\nبرای شروع، کالا اضافه کنید',
                       transform=ax.transAxes, ha='center', va='center',
                       fontsize=12, color='#94a3b8')

            # اضافه کردن به رابط کاربری
            stock_chart_widget = self.findChild(QWidget, "stock_chart")
            if stock_chart_widget:
                if stock_chart_widget.layout() is None:
                    stock_chart_widget.setLayout(QVBoxLayout())
                stock_chart_widget.layout().addWidget(canvas)
                self.chart_canvas = canvas
            else:
                # اگر ویجت پیدا نشد، مستقیماً اضافه کنیم
                self.reports_chart_widget.layout().addWidget(canvas)
                self.chart_canvas = canvas

        except Exception as e:
            print(f"خطا در ایجاد نمودار گزارش: {e}")
            # نمایش خطا به کاربر
            # در صورت خطا، نمایش اطلاعات به شکل متن
            if stock_chart_widget:
                fallback_label = QLabel("📝 اطلاعات موجودی کالا‌ها:\n" +
                                      "\n".join([f"• {p.name}: {p.current_stock}"
                                               for p in self.data_manager.get_products()]))
                fallback_label.setStyleSheet("""
                    QLabel {
                        color: #cbd5e1;
                        font-size: 14px;
                        padding: 20px;
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 rgba(30, 41, 59, 0.8), stop:1 rgba(15, 23, 42, 0.8));
                        border-radius: 12px;
                        border: 1px solid rgba(71, 85, 105, 0.5);
                    }
                """)
                if stock_chart_widget.layout() is None:
                    stock_chart_widget.setLayout(QVBoxLayout())
                stock_chart_widget.layout().addWidget(fallback_label)

    def create_modern_users_page(self):
        """صفحه مدیریت کاربران مدرن"""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # عنوان
        title = QLabel("👥 مدیریت کاربران")
        title.setProperty("title", "true")
        main_layout.addWidget(title)

        # جدول کاربران مدرن
        table_card = QWidget()
        table_card.setProperty("card", "true")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(20, 15, 20, 15)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(['نام کاربری', 'رمز عبور', 'نقش', 'وضعیت'])
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.users_table.horizontalHeader().setStretchLastSection(True)

        # تنظیم اندازه ستون‌ها
        self.products_table.setColumnWidth(0, 80)   # کد
        self.products_table.setColumnWidth(1, 200)  # نام
        self.products_table.setColumnWidth(2, 150)  # دسته‌بندی
        self.products_table.setColumnWidth(3, 100)  # ظرفیت
        self.products_table.setColumnWidth(4, 120)  # موجودی فعلی
        self.products_table.setColumnWidth(5, 100)  # وضعیت
        self.products_table.setColumnWidth(6, 80)   # کاهش
        self.products_table.setColumnWidth(7, 80)   # افزایش

        # تنظیم اندازه ستون‌ها
        self.users_table.setColumnWidth(0, 150)  # نام کاربری
        self.users_table.setColumnWidth(1, 120)  # رمز عبور (مخفی نمایش داده می‌شود)
        self.users_table.setColumnWidth(2, 100)  # نقش
        self.users_table.setColumnWidth(3, 80)   # وضعیت

        table_layout.addWidget(self.users_table)
        main_layout.addWidget(table_card)

        # دکمه‌های مدرن
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        add_btn = QPushButton('➕ افزودن کاربر')
        add_btn.clicked.connect(self.add_user)
        add_btn.setStyleSheet("QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #10b981, stop:1 #059669); }")

        edit_btn = QPushButton('✏️ ویرایش')
        edit_btn.clicked.connect(self.edit_user)

        delete_btn = QPushButton('🗑️ حذف')
        delete_btn.clicked.connect(self.delete_user)
        delete_btn.setProperty("danger", "true")

        save_btn = QPushButton('💾 ذخیره به Excel')
        save_btn.clicked.connect(lambda: save_users_to_excel(self.data_manager))

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)

        return widget

    def refresh_users_table(self):
        """به‌روزرسانی جدول کاربران"""
        users = self.data_manager.get_users()
        self.users_table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.users_table.setItem(row, 0, QTableWidgetItem(user.username))
            self.users_table.setItem(row, 1, QTableWidgetItem(user.password))
            self.users_table.setItem(row, 2, QTableWidgetItem(user.role))

        # تنظیم اندازه ستون‌ها
        self.users_table.resizeColumnsToContents()
        if users:
            self.users_table.horizontalHeader().setStretchLastSection(True)

    def add_user(self):
        dialog = UserDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            user = User(dialog.username.text(), dialog.password.text(), dialog.role.currentText())
            self.data_manager.add_user(user)
            self.refresh_users_table()

    def edit_user(self):
        """ویرایش کاربر انتخاب‌شده (در نسخه‌های آینده)"""
        QMessageBox.information(self, 'اطلاعیه', 'امکان ویرایش کاربران در نسخه‌های بعدی اضافه خواهد شد.')

    def delete_user(self):
        """حذف کاربر انتخاب‌شده (در نسخه‌های آینده)"""
        QMessageBox.information(self, 'اطلاعیه', 'امکان حذف کاربران در نسخه‌های بعدی اضافه خواهد شد.')

    def increase_product_stock(self, product):
        """افزایش موجودی محصول به صورت دستی"""
        try:
            from datetime import datetime

            # افزایش موجودی
            old_stock = product.current_stock
            product.current_stock += 1

            # ایجاد تراکنش خودکار برای ثبت تغییر
            transaction = Transaction(product.code, 'ورود', 1, datetime.now(), 'تنظیم دستی')
            if validate_transaction(transaction, self.data_manager.get_products()):
                self.data_manager.add_transaction(transaction)

            # به‌روزرسانی جدول
            self.refresh_products_table()
            self.status_bar.showMessage(f'📈 موجودی {product.name} به {product.current_stock} افزایش یافت.')

        except Exception as e:
            QMessageBox.warning(self, 'خطا', f'امکان افزایش موجودی وجود ندارد:\n{str(e)}')

    def decrease_product_stock(self, product):
        """کاهش موجودی محصول به صورت دستی"""
        try:
            from datetime import datetime

            if product.current_stock <= 0:
                QMessageBox.information(self, 'اطلاعیه', 'موجودی محصول صفر است و نمی‌توان کاهش داد.')
                return

            # کاهش موجودی
            old_stock = product.current_stock
            product.current_stock -= 1

            # ایجاد تراکنش خودکار برای ثبت تغییر
            transaction = Transaction(product.code, 'خروج', 1, datetime.now(), 'تنظیم دستی')
            if validate_transaction(transaction, self.data_manager.get_products()):
                self.data_manager.add_transaction(transaction)

            # به‌روزرسانی جدول
            self.refresh_products_table()
            self.status_bar.showMessage(f'📉 موجودی {product.name} به {product.current_stock} کاهش یافت.')

        except Exception as e:
            QMessageBox.warning(self, 'خطا', f'امکان کاهش موجودی وجود ندارد:\n{str(e)}')

    def load_data(self):
        """بارگذاری داده‌ها از فایل‌های Excel"""
        load_products_from_excel(self.data_manager)
        load_transactions_from_excel(self.data_manager)
        load_users_from_excel(self.data_manager)

    def closeEvent(self, event):
        """ذخیره داده‌ها هنگام خروج"""
        reply = QMessageBox.question(self, 'خروج', 'آیا می‌خواهید از برنامه خارج شوید؟ داده‌ها ذخیره می‌شوند.',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            save_products_to_excel(self.data_manager)
            save_transactions_to_excel(self.data_manager)
            save_users_to_excel(self.data_manager)
            self.status_bar.showMessage('داده‌ها ذخیره شدند. برنامه بسته شد.')
            event.accept()
        else:
            event.ignore()

# دیالوگ لاگین برای احراز هویت کاربران
class LoginDialog(QDialog):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.current_user = None
        self.init_login_ui()

    def init_login_ui(self):
        """راه‌اندازی رابط کاربری لاگین"""
        self.setWindowTitle('🚪 ورود به سیستم انبارداری')
        self.setFixedSize(500, 400)
        self.setModal(True)

        # اگر کاربری وجود ندارد، کاربر پیش‌فرض ایجاد کنیم
        if not self.data_manager.get_users():
            default_user = User(username="admin", password="123456", role="مدیر")
            self.data_manager.add_user(default_user)

        # تنظیم سبک مدرن برای دیالوگ لاگین
        self.setStyleSheet("""
            LoginDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1b4b, stop:1 #312e81);
                border-radius: 20px;
                border: 2px solid #4f46e5;
            }

            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: 500;
            }

            QLabel[title="true"] {
                font-size: 24px;
                font-weight: 700;
                color: #60a5fa;
                margin-bottom: 10px;
            }

            QLabel[logo="true"] {
                border: none;
                background: transparent;
                padding: 20px;
            }

            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e293b, stop:1 #334155);
                color: #f1f5f9;
                border: 2px solid #475569;
                padding: 12px 15px;
                border-radius: 10px;
                font-size: 14px;
                selection-background-color: #3b82f6;
            }

            QLineEdit:focus {
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
            }

            QLineEdit[username="true"] {
                padding-left: 40px;
                padding-right: 15px;
            }

            QLineEdit[password="true"] {
                padding-left: 40px;
                padding-right: 15px;
            }

            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3b82f6, stop:1 #1d4ed8);
                color: #ffffff;
                border: none;
                padding: 12px 30px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                transition: all 0.3s ease;
            }

            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1d4ed8, stop:1 #1e40af);
                box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
            }

            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e40af, stop:1 #1e3a8a);
            }

            QPushButton[danger="true"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #dc2626, stop:1 #b91c1c);
            }

            QPushButton[danger="true"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #b91c1c, stop:1 #991b1b);
            }

            QLabel[error="true"] {
                color: #ef4444;
                font-size: 12px;
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid #ef4444;
                border-radius: 6px;
                padding: 8px;
                margin-top: 5px;
            }
        """)

        # ایجاد لیوت اصلی
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # لوگو
        try:
            from PyQt6.QtWidgets import QLabel
            from PyQt6.QtGui import QPixmap, QIcon

            logo_label = QLabel()
            logo_label.setProperty("logo", "true")
            pixmap = QPixmap("logow.png").scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(logo_label)
        except Exception as e:
            # اگر لوگو پیدا نشد، از متن استفاده کنیم
            logo_label = QLabel("🎯 انبار\nمدیریت")
            logo_label.setProperty("title", "true")
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(logo_label)

        # عنوان
        title = QLabel("ورود به سیستم")
        title.setProperty("title", "true")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # فیلد نام کاربری
        username_layout = QVBoxLayout()

        username_label = QLabel("👤 نام کاربری:")
        username_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        username_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setProperty("username", "true")
        self.username_input.setPlaceholderText("نام کاربری خود را وارد کنید...")
        self.username_input.setMaximumWidth(400)
        username_layout.addWidget(self.username_input)

        layout.addLayout(username_layout)

        # فیلد رمز عبور
        password_layout = QVBoxLayout()

        password_label = QLabel("🔒 رمز عبور:")
        password_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        password_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setProperty("password", "true")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("رمز عبور خود را وارد کنید...")
        self.password_input.setMaximumWidth(400)
        self.password_input.returnPressed.connect(self.attempt_login)  # Enter برای لاگین
        password_layout.addWidget(self.password_input)

        layout.addLayout(password_layout)

        # نمایش خطا (مخفی به صورت پیش‌فرض)
        self.error_label = QLabel("")
        self.error_label.setProperty("error", "true")
        self.error_label.hide()
        layout.addWidget(self.error_label)

        # دکمه‌ها
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        exit_btn = QPushButton("🚪 خروج")
        exit_btn.setProperty("danger", "true")
        exit_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(exit_btn)

        login_btn = QPushButton("🔑 ورود")
        login_btn.clicked.connect(self.attempt_login)
        buttons_layout.addWidget(login_btn)

        layout.addLayout(buttons_layout)

        # تنظیماتی برای نمایش مرکز صفحه
        self.setWindowIcon(QIcon("logow.png")) if "logow.png" in globals() or " logo.png" in globals() else None

        # تنظیم فوکوس اولیه
        self.username_input.setFocus()

    def attempt_login(self):
        """تلاش برای احراز هویت کاربر"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.show_error("نام کاربری و رمز عبور نمی‌تواند خالی باشد!")
            return

        # جستجو در لیست کاربران
        users = self.data_manager.get_users()
        for user in users:
            if user.username == username and user.password == password:
                # ورود موفق
                self.current_user = user
                self.accept()
                return

        # ورود ناموفق
        self.show_error("نام کاربری یا رمز عبور اشتباه است!")
        self.password_input.clear()
        self.password_input.setFocus()

    def show_error(self, message):
        """نمایش پیام خطا"""
        self.error_label.setText(message)
        self.error_label.show()

        # انیمیشن لرزش برای تأکید روی خطا
        from PyQt6.QtCore import QTimer, QPropertyAnimation

        shake_animation = QPropertyAnimation(self, b"pos")
        shake_animation.setDuration(500)
        shake_animation.setKeyValueAt(0, self.pos())
        shake_animation.setKeyValueAt(0.1, self.pos() + (10, 0))
        shake_animation.setKeyValueAt(0.2, self.pos() + (-10, 0))
        shake_animation.setKeyValueAt(0.3, self.pos() + (10, 0))
        shake_animation.setKeyValueAt(0.4, self.pos() + (-10, 0))
        shake_animation.setKeyValueAt(0.5, self.pos())
        shake_animation.start()

    def get_current_user(self):
        """برگرداندن کاربر فعلی"""
        return self.current_user

# دیالوگ‌ها برای افزودن موجودیت‌ها

class ProductDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('افزودن کالا')
        self.resize(400, 200)

        layout = QFormLayout(self)
        self.code = QLineEdit()
        self.code.setPlaceholderText('کد یکتا برای کالا را وارد کنید')
        self.code.setToolTip('کد باید یکتا باشد')
        self.name = QLineEdit()
        self.name.setPlaceholderText('نام کامل کالا')
        self.category = QLineEdit()
        self.category.setPlaceholderText('دسته‌بندی کالا (اختیاری)')
        self.capacity = QSpinBox()
        self.capacity.setMaximum(1000000)
        self.capacity.setToolTip('ظرفیت انبار به عدد')

        layout.addRow('کد:', self.code)
        layout.addRow('نام:', self.name)
        layout.addRow('دسته‌بندی:', self.category)
        layout.addRow('ظرفیت:', self.capacity)

        buttons = QWidget()
        btn_layout = QHBoxLayout(buttons)
        ok_btn = QPushButton('تأیید')
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton('لغو')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(buttons)

class TransactionDialog(QDialog):
    def __init__(self, products):
        super().__init__()
        self.setWindowTitle('افزودن تراکنش')
        self.resize(400, 200)

        layout = QFormLayout(self)
        self.product_combo = QComboBox()
        for p in products:
            self.product_combo.addItem(f'{p.code} - {p.name}')
        self.product_combo.setToolTip('محصول مورد نظر را انتخاب کنید')
        self.type_combo = QComboBox()
        self.type_combo.addItems(['ورود', 'خروج'])
        self.type_combo.setToolTip('نوع تراکنش را انتخاب کنید')
        self.quantity = QSpinBox()
        self.quantity.setMaximum(1000000)
        self.quantity.setToolTip('مقدار عددی مثبت وارد کنید')
        self.date = QDateTimeEdit()
        self.date.setDateTime(QDateTime.currentDateTime())
        self.date.setToolTip('تاریخ و زمان تراکنش')

        layout.addRow('محصول:', self.product_combo)
        layout.addRow('نوع:', self.type_combo)
        layout.addRow('مقدار:', self.quantity)
        layout.addRow('تاریخ:', self.date)

        buttons = QWidget()
        btn_layout = QHBoxLayout(buttons)
        ok_btn = QPushButton('تأیید')
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton('لغو')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(buttons)

class UserDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('افزودن کاربر')
        self.resize(400, 200)

        layout = QFormLayout(self)
        self.username = QLineEdit()
        self.username.setPlaceholderText('نام کاربری یکتا')
        self.username.setToolTip('نام کاربری باید یکتا باشد')
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText('رمز عبور قوی')
        self.password.setToolTip('رمز عبور حداقل ۶ کاراکتر')
        self.role = QComboBox()
        self.role.addItems(['مدیر', 'کارمند'])
        self.role.setToolTip('نقش کاربر در سیستم')

        layout.addRow('نام کاربری:', self.username)
        layout.addRow('رمز عبور:', self.password)
        layout.addRow('نقش:', self.role)

        buttons = QWidget()
        btn_layout = QHBoxLayout(buttons)
        ok_btn = QPushButton('تأیید')
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton('لغو')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addWidget(buttons)