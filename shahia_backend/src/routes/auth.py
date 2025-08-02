from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import db, User
import jwt
from datetime import datetime, timedelta
import random
import string
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def generate_verification_code():
    """توليد كود تحقق من 6 أرقام"""
    return ''.join(random.choices(string.digits, k=6))

def generate_delivery_code():
    """توليد كود توصيل من 4 أرقام"""
    return ''.join(random.choices(string.digits, k=4))

def token_required(f):
    """ديكوريتر للتحقق من صحة التوكن"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(user_id=data['user_id']).first()
            if not current_user:
                return jsonify({'message': 'Token is invalid!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """ديكوريتر للتحقق من صلاحيات المسؤول"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.user_type != 'admin':
            return jsonify({'message': 'Admin access required!'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    """تسجيل مستخدم جديد"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['name', 'email', 'phone_number', 'password', 'user_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'{field} is required'}), 400
        
        # التحقق من صحة نوع المستخدم
        valid_user_types = ['customer', 'restaurant', 'delivery_agent']
        if data['user_type'] not in valid_user_types:
            return jsonify({'message': 'Invalid user type'}), 400
        
        # التحقق من عدم وجود المستخدم مسبقاً
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 400
        
        if User.query.filter_by(phone_number=data['phone_number']).first():
            return jsonify({'message': 'Phone number already exists'}), 400
        
        # إنشاء المستخدم الجديد
        new_user = User(
            name=data['name'],
            email=data['email'],
            phone_number=data['phone_number'],
            user_type=data['user_type'],
            address=data.get('address'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        # إنشاء توكن للمستخدم الجديد
        token = jwt.encode({
            'user_id': new_user.user_id,
            'user_type': new_user.user_type,
            'exp': datetime.utcnow() + timedelta(days=30)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'User registered successfully',
            'user': new_user.to_dict(),
            'token': token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """تسجيل الدخول"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'message': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'message': 'Account is deactivated'}), 401
        
        # إنشاء توكن
        token = jwt.encode({
            'user_id': user.user_id,
            'user_type': user.user_type,
            'exp': datetime.utcnow() + timedelta(days=30)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'token': token
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """الحصول على ملف المستخدم الشخصي"""
    return jsonify({
        'user': current_user.to_dict()
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """تحديث ملف المستخدم الشخصي"""
    try:
        data = request.get_json()
        
        # تحديث البيانات المسموح بتعديلها
        if 'name' in data:
            current_user.name = data['name']
        if 'address' in data:
            current_user.address = data['address']
        if 'latitude' in data:
            current_user.latitude = data['latitude']
        if 'longitude' in data:
            current_user.longitude = data['longitude']
        
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Profile update failed: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """تغيير كلمة المرور"""
    try:
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'message': 'Current password and new password are required'}), 400
        
        if not current_user.check_password(data['current_password']):
            return jsonify({'message': 'Current password is incorrect'}), 400
        
        if len(data['new_password']) < 6:
            return jsonify({'message': 'New password must be at least 6 characters long'}), 400
        
        current_user.set_password(data['new_password'])
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Password change failed: {str(e)}'}), 500

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """التحقق من صحة التوكن"""
    try:
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'valid': False, 'message': 'Token is missing'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user = User.query.filter_by(user_id=data['user_id']).first()
        
        if not user or not user.is_active:
            return jsonify({'valid': False, 'message': 'User not found or inactive'}), 401
        
        return jsonify({
            'valid': True,
            'user': user.to_dict()
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'valid': False, 'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'valid': False, 'message': 'Token is invalid'}), 401
    except Exception as e:
        return jsonify({'valid': False, 'message': f'Token verification failed: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """تسجيل الخروج"""
    # في التطبيق الحقيقي، يمكن إضافة التوكن إلى قائمة سوداء
    return jsonify({'message': 'Logged out successfully'}), 200

