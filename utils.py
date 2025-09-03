import pandas as pd
import os
from datetime import datetime
from models import Product, Transaction, User, DataManager

# توابع کمکی برای مدیریت فایل‌های Excel

def load_products_from_excel(data_manager: DataManager, file_path: str = 'products.xlsx'):
    """بارگذاری کالاها از فایل Excel"""
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        for _, row in df.iterrows():
            product = Product(
                code=row['کد'],
                name=row['نام'],
                category=row['دسته‌بندی'],
                capacity=int(row['ظرفیت']),
                current_stock=int(row['موجودی فعلی'])
            )
            data_manager.add_product(product)
    else:
        print(f"فایل {file_path} یافت نشد. فایل جدید ایجاد خواهد شد.")

def save_products_to_excel(data_manager: DataManager, file_path: str = 'products.xlsx'):
    """ذخیره کالاها به فایل Excel"""
    data = []
    for product in data_manager.get_products():
        data.append({
            'کد': product.code,
            'نام': product.name,
            'دسته‌بندی': product.category,
            'ظرفیت': product.capacity,
            'موجودی فعلی': product.current_stock
        })
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)

def load_transactions_from_excel(data_manager: DataManager, file_path: str = 'transactions.xlsx'):
    """بارگذاری تراکنش‌ها از فایل Excel"""
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        for _, row in df.iterrows():
            transaction = Transaction(
                product_code=row['کد محصول'],
                transaction_type=row['نوع تراکنش'],
                quantity=int(row['مقدار']),
                date=pd.to_datetime(row['تاریخ']),
                user=row['کاربر']
            )
            data_manager.add_transaction(transaction)
    else:
        print(f"فایل {file_path} یافت نشد. فایل جدید ایجاد خواهد شد.")

def save_transactions_to_excel(data_manager: DataManager, file_path: str = 'transactions.xlsx'):
    """ذخیره تراکنش‌ها به فایل Excel"""
    data = []
    for transaction in data_manager.get_transactions():
        data.append({
            'کد محصول': transaction.product_code,
            'نوع تراکنش': transaction.transaction_type,
            'مقدار': transaction.quantity,
            'تاریخ': transaction.date,
            'کاربر': transaction.user
        })
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)

def load_users_from_excel(data_manager: DataManager, file_path: str = 'users.xlsx'):
    """بارگذاری کاربران از فایل Excel"""
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        for _, row in df.iterrows():
            user = User(
                username=row['نام کاربری'],
                password=row['رمز عبور'],
                role=row['نقش']
            )
            data_manager.add_user(user)
    else:
        print(f"فایل {file_path} یافت نشد. فایل جدید ایجاد خواهد شد.")

def save_users_to_excel(data_manager: DataManager, file_path: str = 'users.xlsx'):
    """ذخیره کاربران به فایل Excel"""
    data = []
    for user in data_manager.get_users():
        data.append({
            'نام کاربری': user.username,
            'رمز عبور': user.password,
            'نقش': user.role
        })
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)

def validate_product(product: Product) -> bool:
    """اعتبارسنجی داده‌های کالا"""
    if not product.code or not product.name or product.capacity < 0 or product.current_stock < 0:
        return False
    return True

def validate_transaction(transaction: Transaction, products: list) -> bool:
    """اعتبارسنجی تراکنش"""
    product_codes = [p.code for p in products]
    if transaction.product_code not in product_codes or transaction.quantity <= 0 or transaction.transaction_type not in ['ورود', 'خروج']:
        return False
    return True