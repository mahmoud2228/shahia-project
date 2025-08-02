from flask import Blueprint, request, jsonify
from src.models.user import db, Restaurant, Category, Product, User, RestaurantReview
from src.routes.auth import token_required, admin_required
from sqlalchemy import func, and_, or_
from datetime import datetime, time
import math

restaurants_bp = Blueprint('restaurants', __name__)

def calculate_distance(lat1, lon1, lat2, lon2):
    """حساب المسافة بين نقطتين بالكيلومتر"""
    if not all([lat1, lon1, lat2, lon2]):
        return float('inf')
    
    # تحويل إلى راديان
    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    
    # معادلة هافرساين
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # نصف قطر الأرض بالكيلومتر
    return c * r

@restaurants_bp.route('/restaurants', methods=['GET'])
def get_restaurants():
    """الحصول على قائمة المطاعم مع إمكانية البحث والتصفية"""
    try:
        # معاملات البحث والتصفية
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        min_rating = request.args.get('min_rating', type=float)
        max_delivery_fee = request.args.get('max_delivery_fee', type=float)
        is_open = request.args.get('is_open', type=bool)
        user_lat = request.args.get('lat', type=float)
        user_lon = request.args.get('lon', type=float)
        max_distance = request.args.get('max_distance', 10, type=float)  # بالكيلومتر
        
        # بناء الاستعلام
        query = Restaurant.query.filter(Restaurant.is_open == True)
        
        if search:
            query = query.filter(
                or_(
                    Restaurant.name.ilike(f'%{search}%'),
                    Restaurant.description.ilike(f'%{search}%')
                )
            )
        
        if min_rating:
            query = query.filter(Restaurant.rating >= min_rating)
        
        if max_delivery_fee:
            query = query.filter(Restaurant.delivery_fee <= max_delivery_fee)
        
        if is_open is not None:
            current_time = datetime.now().time()
            if is_open:
                query = query.filter(
                    and_(
                        Restaurant.opening_time <= current_time,
                        Restaurant.closing_time >= current_time
                    )
                )
        
        restaurants = query.all()
        
        # تطبيق فلتر المسافة وإضافة المسافة للنتائج
        result = []
        for restaurant in restaurants:
            restaurant_dict = restaurant.to_dict()
            
            if user_lat and user_lon:
                distance = calculate_distance(
                    user_lat, user_lon,
                    restaurant.latitude, restaurant.longitude
                )
                restaurant_dict['distance'] = round(distance, 2)
                
                if distance <= max_distance:
                    result.append(restaurant_dict)
            else:
                restaurant_dict['distance'] = None
                result.append(restaurant_dict)
        
        # ترتيب حسب المسافة إذا كان الموقع متوفراً
        if user_lat and user_lon:
            result.sort(key=lambda x: x['distance'] if x['distance'] is not None else float('inf'))
        
        return jsonify({
            'restaurants': result,
            'total': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get restaurants: {str(e)}'}), 500

@restaurants_bp.route('/restaurants/<restaurant_id>', methods=['GET'])
def get_restaurant_details(restaurant_id):
    """الحصول على تفاصيل مطعم محدد مع قائمة الطعام"""
    try:
        restaurant = Restaurant.query.filter_by(restaurant_id=restaurant_id).first()
        
        if not restaurant:
            return jsonify({'message': 'Restaurant not found'}), 404
        
        # الحصول على الفئات والمنتجات
        categories = Category.query.filter_by(restaurant_id=restaurant_id).all()
        
        restaurant_data = restaurant.to_dict()
        restaurant_data['categories'] = []
        
        for category in categories:
            category_data = category.to_dict()
            products = Product.query.filter_by(category_id=category.category_id).all()
            category_data['products'] = [product.to_dict() for product in products]
            restaurant_data['categories'].append(category_data)
        
        # الحصول على التقييمات الأخيرة
        reviews = RestaurantReview.query.filter_by(restaurant_id=restaurant_id)\
                    .order_by(RestaurantReview.created_at.desc())\
                    .limit(10).all()
        
        restaurant_data['recent_reviews'] = []
        for review in reviews:
            review_data = review.to_dict()
            reviewer = User.query.filter_by(user_id=review.user_id).first()
            review_data['reviewer_name'] = reviewer.name if reviewer else 'مستخدم محذوف'
            restaurant_data['recent_reviews'].append(review_data)
        
        return jsonify({'restaurant': restaurant_data}), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get restaurant details: {str(e)}'}), 500

@restaurants_bp.route('/restaurants', methods=['POST'])
@token_required
def create_restaurant(current_user):
    """إنشاء مطعم جديد (للمطاعم فقط)"""
    try:
        if current_user.user_type not in ['restaurant', 'admin']:
            return jsonify({'message': 'Only restaurant owners can create restaurants'}), 403
        
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['name', 'address', 'latitude', 'longitude']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'{field} is required'}), 400
        
        # التحقق من عدم وجود مطعم للمستخدم مسبقاً (إلا للمسؤولين)
        if current_user.user_type == 'restaurant':
            existing_restaurant = Restaurant.query.filter_by(user_id=current_user.user_id).first()
            if existing_restaurant:
                return jsonify({'message': 'User already has a restaurant'}), 400
        
        # إنشاء المطعم الجديد
        new_restaurant = Restaurant(
            user_id=current_user.user_id,
            name=data['name'],
            description=data.get('description'),
            address=data['address'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            phone_number=data.get('phone_number'),
            email=data.get('email'),
            opening_time=time.fromisoformat(data['opening_time']) if data.get('opening_time') else None,
            closing_time=time.fromisoformat(data['closing_time']) if data.get('closing_time') else None,
            logo_url=data.get('logo_url'),
            cover_image_url=data.get('cover_image_url'),
            delivery_fee=data.get('delivery_fee', 0),
            min_order_value=data.get('min_order_value', 0)
        )
        
        db.session.add(new_restaurant)
        db.session.commit()
        
        return jsonify({
            'message': 'Restaurant created successfully',
            'restaurant': new_restaurant.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to create restaurant: {str(e)}'}), 500

@restaurants_bp.route('/restaurants/<restaurant_id>', methods=['PUT'])
@token_required
def update_restaurant(current_user, restaurant_id):
    """تحديث بيانات المطعم"""
    try:
        restaurant = Restaurant.query.filter_by(restaurant_id=restaurant_id).first()
        
        if not restaurant:
            return jsonify({'message': 'Restaurant not found'}), 404
        
        # التحقق من الصلاحيات
        if current_user.user_type != 'admin' and restaurant.user_id != current_user.user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        data = request.get_json()
        
        # تحديث البيانات
        if 'name' in data:
            restaurant.name = data['name']
        if 'description' in data:
            restaurant.description = data['description']
        if 'address' in data:
            restaurant.address = data['address']
        if 'latitude' in data:
            restaurant.latitude = data['latitude']
        if 'longitude' in data:
            restaurant.longitude = data['longitude']
        if 'phone_number' in data:
            restaurant.phone_number = data['phone_number']
        if 'email' in data:
            restaurant.email = data['email']
        if 'opening_time' in data:
            restaurant.opening_time = time.fromisoformat(data['opening_time']) if data['opening_time'] else None
        if 'closing_time' in data:
            restaurant.closing_time = time.fromisoformat(data['closing_time']) if data['closing_time'] else None
        if 'is_open' in data:
            restaurant.is_open = data['is_open']
        if 'logo_url' in data:
            restaurant.logo_url = data['logo_url']
        if 'cover_image_url' in data:
            restaurant.cover_image_url = data['cover_image_url']
        if 'delivery_fee' in data:
            restaurant.delivery_fee = data['delivery_fee']
        if 'min_order_value' in data:
            restaurant.min_order_value = data['min_order_value']
        
        restaurant.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Restaurant updated successfully',
            'restaurant': restaurant.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update restaurant: {str(e)}'}), 500

@restaurants_bp.route('/restaurants/<restaurant_id>/categories', methods=['POST'])
@token_required
def create_category(current_user, restaurant_id):
    """إنشاء فئة جديدة للمطعم"""
    try:
        restaurant = Restaurant.query.filter_by(restaurant_id=restaurant_id).first()
        
        if not restaurant:
            return jsonify({'message': 'Restaurant not found'}), 404
        
        # التحقق من الصلاحيات
        if current_user.user_type != 'admin' and restaurant.user_id != current_user.user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'message': 'Category name is required'}), 400
        
        new_category = Category(
            restaurant_id=restaurant_id,
            name=data['name'],
            description=data.get('description')
        )
        
        db.session.add(new_category)
        db.session.commit()
        
        return jsonify({
            'message': 'Category created successfully',
            'category': new_category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to create category: {str(e)}'}), 500

@restaurants_bp.route('/restaurants/<restaurant_id>/categories/<category_id>/products', methods=['POST'])
@token_required
def create_product(current_user, restaurant_id, category_id):
    """إنشاء منتج جديد في فئة محددة"""
    try:
        restaurant = Restaurant.query.filter_by(restaurant_id=restaurant_id).first()
        category = Category.query.filter_by(category_id=category_id, restaurant_id=restaurant_id).first()
        
        if not restaurant or not category:
            return jsonify({'message': 'Restaurant or category not found'}), 404
        
        # التحقق من الصلاحيات
        if current_user.user_type != 'admin' and restaurant.user_id != current_user.user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['name', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'{field} is required'}), 400
        
        new_product = Product(
            category_id=category_id,
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            image_url=data.get('image_url'),
            is_available=data.get('is_available', True)
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify({
            'message': 'Product created successfully',
            'product': new_product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to create product: {str(e)}'}), 500

@restaurants_bp.route('/restaurants/<restaurant_id>/reviews', methods=['POST'])
@token_required
def create_review(current_user, restaurant_id):
    """إنشاء تقييم للمطعم"""
    try:
        if current_user.user_type != 'customer':
            return jsonify({'message': 'Only customers can review restaurants'}), 403
        
        restaurant = Restaurant.query.filter_by(restaurant_id=restaurant_id).first()
        
        if not restaurant:
            return jsonify({'message': 'Restaurant not found'}), 404
        
        data = request.get_json()
        
        if not data.get('rating') or data['rating'] < 1 or data['rating'] > 5:
            return jsonify({'message': 'Rating must be between 1 and 5'}), 400
        
        # التحقق من عدم وجود تقييم سابق من نفس المستخدم
        existing_review = RestaurantReview.query.filter_by(
            user_id=current_user.user_id,
            restaurant_id=restaurant_id
        ).first()
        
        if existing_review:
            return jsonify({'message': 'You have already reviewed this restaurant'}), 400
        
        new_review = RestaurantReview(
            user_id=current_user.user_id,
            restaurant_id=restaurant_id,
            rating=data['rating'],
            comment=data.get('comment')
        )
        
        db.session.add(new_review)
        
        # تحديث متوسط تقييم المطعم
        avg_rating = db.session.query(func.avg(RestaurantReview.rating))\
                      .filter_by(restaurant_id=restaurant_id).scalar()
        restaurant.rating = round(avg_rating, 1) if avg_rating else 0
        
        db.session.commit()
        
        return jsonify({
            'message': 'Review created successfully',
            'review': new_review.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to create review: {str(e)}'}), 500

@restaurants_bp.route('/my-restaurant', methods=['GET'])
@token_required
def get_my_restaurant(current_user):
    """الحصول على مطعم المستخدم الحالي"""
    try:
        if current_user.user_type != 'restaurant':
            return jsonify({'message': 'Only restaurant owners can access this endpoint'}), 403
        
        restaurant = Restaurant.query.filter_by(user_id=current_user.user_id).first()
        
        if not restaurant:
            return jsonify({'message': 'No restaurant found for this user'}), 404
        
        # الحصول على الفئات والمنتجات
        categories = Category.query.filter_by(restaurant_id=restaurant.restaurant_id).all()
        
        restaurant_data = restaurant.to_dict()
        restaurant_data['categories'] = []
        
        for category in categories:
            category_data = category.to_dict()
            products = Product.query.filter_by(category_id=category.category_id).all()
            category_data['products'] = [product.to_dict() for product in products]
            restaurant_data['categories'].append(category_data)
        
        return jsonify({'restaurant': restaurant_data}), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get restaurant: {str(e)}'}), 500

