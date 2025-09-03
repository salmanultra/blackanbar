from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class Product:
    """کلاس مدل کالا"""
    code: str
    name: str
    category: str
    capacity: int  # ظرفیت انبار
    current_stock: int  # موجودی فعلی

@dataclass
class Transaction:
    """کلاس مدل تراکنش"""
    product_code: str
    transaction_type: str  # 'ورود' یا 'خروج'
    quantity: int
    date: datetime
    user: str  # نام کاربر

@dataclass
class User:
    """کلاس مدل کاربر"""
    username: str
    password: str  # هش باید بشه اما ساد نگه می‌داریم
    role: str  # مثلاً 'مدیر' یا 'کارمند'

class DataManager:
    """مدیریت داده‌ها در حافظه"""
    def __init__(self):
        self.products: List[Product] = []
        self.transactions: List[Transaction] = []
        self.users: List[User] = []

    def add_product(self, product: Product):
        self.products.append(product)

    def update_product(self, code: str, updated_product: Product):
        for i, p in enumerate(self.products):
            if p.code == code:
                self.products[i] = updated_product
                break

    def delete_product(self, code: str):
        self.products = [p for p in self.products if p.code != code]

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)
        # به‌روزرسانی موجودی کالا
        for p in self.products:
            if p.code == transaction.product_code:
                if transaction.transaction_type == 'ورود':
                    p.current_stock += transaction.quantity
                elif transaction.transaction_type == 'خروج':
                    p.current_stock -= transaction.quantity
                break

    def add_user(self, user: User):
        self.users.append(user)

    def get_users(self):
        return self.users

    # سایر متدهای مفید
    def get_products(self):
        return self.products

    def get_transactions(self):
        return self.transactions

    def get_product_by_code(self, code: str):
        for p in self.products:
            if p.code == code:
                return p
        return None

    def get_transactions_by_product(self, product_code: str):
        return [t for t in self.transactions if t.product_code == product_code]