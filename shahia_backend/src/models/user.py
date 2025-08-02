from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_type = db.Column(db.Enum('customer', 'restaurant', 'delivery_agent', 'admin', name='user_types'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text)
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    restaurants = db.relationship('Restaurant', backref='owner', lazy=True)
    orders_as_customer = db.relationship('Order', foreign_keys='Order.user_id', backref='customer', lazy=True)
    orders_as_delivery_agent = db.relationship('Order', foreign_keys='Order.delivery_agent_id', backref='delivery_agent', lazy=True)
    reviews = db.relationship('RestaurantReview', backref='reviewer', lazy=True)
    location_logs = db.relationship('LocationLog', backref='delivery_agent', lazy=True)

    def __repr__(self):
        return f'<User {self.name}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'user_type': self.user_type,
            'name': self.name,
            'email': self.email,
            'phone_number': self.phone_number,
            'address': self.address,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }

class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    
    restaurant_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(255))
    opening_time = db.Column(db.Time)
    closing_time = db.Column(db.Time)
    is_open = db.Column(db.Boolean, default=True)
    logo_url = db.Column(db.String(255))
    cover_image_url = db.Column(db.String(255))
    rating = db.Column(db.Numeric(2, 1), default=0.0)
    delivery_fee = db.Column(db.Numeric(10, 2), default=0.0)
    min_order_value = db.Column(db.Numeric(10, 2), default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    categories = db.relationship('Category', backref='restaurant', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='restaurant', lazy=True)
    reviews = db.relationship('RestaurantReview', backref='restaurant', lazy=True)

    def to_dict(self):
        return {
            'restaurant_id': self.restaurant_id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'address': self.address,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'phone_number': self.phone_number,
            'email': self.email,
            'opening_time': self.opening_time.strftime('%H:%M') if self.opening_time else None,
            'closing_time': self.closing_time.strftime('%H:%M') if self.closing_time else None,
            'is_open': self.is_open,
            'logo_url': self.logo_url,
            'cover_image_url': self.cover_image_url,
            'rating': float(self.rating) if self.rating else 0.0,
            'delivery_fee': float(self.delivery_fee) if self.delivery_fee else 0.0,
            'min_order_value': float(self.min_order_value) if self.min_order_value else 0.0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Category(db.Model):
    __tablename__ = 'categories'
    
    category_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    restaurant_id = db.Column(db.String(36), db.ForeignKey('restaurants.restaurant_id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    products = db.relationship('Product', backref='category', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'category_id': self.category_id,
            'restaurant_id': self.restaurant_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Product(db.Model):
    __tablename__ = 'products'
    
    product_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id = db.Column(db.String(36), db.ForeignKey('categories.category_id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(255))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else 0.0,
            'image_url': self.image_url,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    order_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
    restaurant_id = db.Column(db.String(36), db.ForeignKey('restaurants.restaurant_id'), nullable=False)
    delivery_agent_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=True)
    order_status = db.Column(db.Enum('pending', 'confirmed', 'preparing', 'ready', 'picked_up', 'delivered', 'cancelled', name='order_statuses'), default='pending')
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_latitude = db.Column(db.Numeric(10, 8), nullable=False)
    delivery_longitude = db.Column(db.Numeric(11, 8), nullable=False)
    payment_method = db.Column(db.Enum('cash', 'bankily', 'masrafi', 'sadad', name='payment_methods'), nullable=False)
    payment_status = db.Column(db.Enum('pending', 'paid', 'failed', name='payment_statuses'), default='pending')
    delivery_code = db.Column(db.String(10))
    restaurant_payout_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    delivered_at = db.Column(db.DateTime)

    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='order', lazy=True)

    def to_dict(self):
        return {
            'order_id': self.order_id,
            'user_id': self.user_id,
            'restaurant_id': self.restaurant_id,
            'delivery_agent_id': self.delivery_agent_id,
            'order_status': self.order_status,
            'total_amount': float(self.total_amount) if self.total_amount else 0.0,
            'delivery_address': self.delivery_address,
            'delivery_latitude': float(self.delivery_latitude) if self.delivery_latitude else None,
            'delivery_longitude': float(self.delivery_longitude) if self.delivery_longitude else None,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'delivery_code': self.delivery_code,
            'restaurant_payout_code': self.restaurant_payout_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    order_item_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey('orders.order_id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    def to_dict(self):
        return {
            'order_item_id': self.order_item_id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': float(self.price) if self.price else 0.0,
            'subtotal': float(self.subtotal) if self.subtotal else 0.0
        }

class Payment(db.Model):
    __tablename__ = 'payments'
    
    payment_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey('orders.order_id'), nullable=False)
    transaction_id = db.Column(db.String(255))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.Enum('cash', 'bankily', 'masrafi', 'sadad', name='payment_methods'), nullable=False)
    payment_status = db.Column(db.Enum('success', 'failed', 'pending', name='payment_statuses'), nullable=False)
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'payment_id': self.payment_id,
            'order_id': self.order_id,
            'transaction_id': self.transaction_id,
            'amount': float(self.amount) if self.amount else 0.0,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class RestaurantReview(db.Model):
    __tablename__ = 'restaurant_reviews'
    
    review_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
    restaurant_id = db.Column(db.String(36), db.ForeignKey('restaurants.restaurant_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'review_id': self.review_id,
            'user_id': self.user_id,
            'restaurant_id': self.restaurant_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class LocationLog(db.Model):
    __tablename__ = 'location_logs'
    
    log_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    delivery_agent_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'log_id': self.log_id,
            'delivery_agent_id': self.delivery_agent_id,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class FinancialTransaction(db.Model):
    __tablename__ = 'financial_transactions'
    
    transaction_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    from_entity_type = db.Column(db.Enum('restaurant', 'delivery_agent', 'customer', name='entity_types'), nullable=False)
    from_entity_id = db.Column(db.String(36), nullable=False)
    to_entity_type = db.Column(db.Enum('restaurant', 'delivery_agent', 'customer', name='entity_types'), nullable=False)
    to_entity_id = db.Column(db.String(36), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.Enum('payment', 'transfer', 'withdrawal', 'commission', name='transaction_types'), nullable=False)
    payment_method = db.Column(db.Enum('cash', 'bankily', 'masrafi', 'sadad', name='payment_methods'), nullable=False)
    status = db.Column(db.Enum('success', 'failed', 'pending', name='transaction_statuses'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
            'from_entity_type': self.from_entity_type,
            'from_entity_id': self.from_entity_id,
            'to_entity_type': self.to_entity_type,
            'to_entity_id': self.to_entity_id,
            'amount': float(self.amount) if self.amount else 0.0,
            'transaction_type': self.transaction_type,
            'payment_method': self.payment_method,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

