from flask import Blueprint, request, jsonify
from src.models.user import db, Order, OrderItem, Product, Restaurant, User, FinancialTransaction
from src.routes.auth import token_required, generate_delivery_code
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
import random
import string

orders_bp = Blueprint('orders', __name__)

def generate_order_code():
    """توليد كود طلب فريد"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@orders_bp.route('/orders', methods=['POST'])
@token_required
def create_order(current_user):
    """إنشاء طلب جديد"""
    try:
        if current_user.user_type != 'customer':
            return jsonify({'message': 'Only customers can create orders'}), 403
        
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['restaurant_id', 'items', 'delivery_address', 'delivery_latitude', 'delivery_longitude', 'payment_method']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'{field} is required'}), 400
        
        # التحقق من وجود المطعم
        restaurant = Restaurant.query.filter_by(restaurant_id=data['restaurant_id']).first()
        if not restaurant:
            return jsonify({'message': 'Restaurant not found'}), 404
        
        if not restaurant.is_open:
            return jsonify({'message': 'Restaurant is currently closed'}), 400
        
        # التحقق من العناصر والحصول على المنتجات
        items = data['items']
        if not items:
            return jsonify({'message': 'Order items are required'}), 400
        
        order_items = []
        total_amount = 0
        
        for item in items:
            if 'product_id' not in item or 'quantity' not in item:
                return jsonify({'message': 'Each item must have product_id and quantity'}), 400
            
            product = Product.query.filter_by(product_id=item['product_id']).first()
            if not product:
                return jsonify({'message': f'Product {item["product_id"]} not found'}), 404
            
            if not product.is_available:
                return jsonify({'message': f'Product {product.name} is not available'}), 400
            
            # التحقق من أن المنتج ينتمي للمطعم المحدد
            if product.category.restaurant_id != data['restaurant_id']:
                return jsonify({'message': f'Product {product.name} does not belong to this restaurant'}), 400
            
            quantity = item['quantity']
            if quantity <= 0:
                return jsonify({'message': 'Quantity must be greater than 0'}), 400
            
            subtotal = float(product.price) * quantity
            total_amount += subtotal
            
            order_items.append({
                'product': product,
                'quantity': quantity,
                'price': float(product.price),
                'subtotal': subtotal
            })
        
        # إضافة رسوم التوصيل
        delivery_fee = float(restaurant.delivery_fee)
        total_amount += delivery_fee
        
        # التحقق من الحد الأدنى للطلب
        if total_amount - delivery_fee < float(restaurant.min_order_value):
            return jsonify({
                'message': f'Minimum order value is {restaurant.min_order_value} (excluding delivery fee)'
            }), 400
        
        # إنشاء الطلب
        new_order = Order(
            user_id=current_user.user_id,
            restaurant_id=data['restaurant_id'],
            total_amount=total_amount,
            delivery_address=data['delivery_address'],
            delivery_latitude=data['delivery_latitude'],
            delivery_longitude=data['delivery_longitude'],
            payment_method=data['payment_method'],
            delivery_code=generate_delivery_code(),
            restaurant_payout_code=generate_delivery_code()
        )
        
        db.session.add(new_order)
        db.session.flush()  # للحصول على order_id
        
        # إضافة عناصر الطلب
        for item_data in order_items:
            order_item = OrderItem(
                order_id=new_order.order_id,
                product_id=item_data['product'].product_id,
                quantity=item_data['quantity'],
                price=item_data['price'],
                subtotal=item_data['subtotal']
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        # إرجاع تفاصيل الطلب
        order_dict = new_order.to_dict()
        order_dict['restaurant'] = restaurant.to_dict()
        order_dict['items'] = []
        
        for item_data in order_items:
            item_dict = {
                'product_id': item_data['product'].product_id,
                'product_name': item_data['product'].name,
                'quantity': item_data['quantity'],
                'price': item_data['price'],
                'subtotal': item_data['subtotal']
            }
            order_dict['items'].append(item_dict)
        
        return jsonify({
            'message': 'Order created successfully',
            'order': order_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to create order: {str(e)}'}), 500

@orders_bp.route('/orders', methods=['GET'])
@token_required
def get_orders(current_user):
    """الحصول على طلبات المستخدم"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        # بناء الاستعلام حسب نوع المستخدم
        if current_user.user_type == 'customer':
            query = Order.query.filter_by(user_id=current_user.user_id)
        elif current_user.user_type == 'restaurant':
            restaurant = Restaurant.query.filter_by(user_id=current_user.user_id).first()
            if not restaurant:
                return jsonify({'message': 'Restaurant not found'}), 404
            query = Order.query.filter_by(restaurant_id=restaurant.restaurant_id)
        elif current_user.user_type == 'delivery_agent':
            query = Order.query.filter_by(delivery_agent_id=current_user.user_id)
        elif current_user.user_type == 'admin':
            query = Order.query
        else:
            return jsonify({'message': 'Invalid user type'}), 403
        
        # تطبيق فلتر الحالة
        if status:
            query = query.filter_by(order_status=status)
        
        # ترتيب وتقسيم الصفحات
        orders = query.order_by(desc(Order.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # تحضير البيانات
        orders_data = []
        for order in orders.items:
            order_dict = order.to_dict()
            
            # إضافة معلومات إضافية
            order_dict['customer'] = order.customer.to_dict() if order.customer else None
            order_dict['restaurant'] = order.restaurant.to_dict() if order.restaurant else None
            order_dict['delivery_agent'] = order.delivery_agent.to_dict() if order.delivery_agent else None
            
            # إضافة عناصر الطلب
            order_dict['items'] = []
            for item in order.order_items:
                item_dict = item.to_dict()
                item_dict['product_name'] = item.product.name if item.product else 'منتج محذوف'
                order_dict['items'].append(item_dict)
            
            orders_data.append(order_dict)
        
        return jsonify({
            'orders': orders_data,
            'pagination': {
                'page': orders.page,
                'pages': orders.pages,
                'per_page': orders.per_page,
                'total': orders.total,
                'has_next': orders.has_next,
                'has_prev': orders.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get orders: {str(e)}'}), 500

@orders_bp.route('/orders/<order_id>', methods=['GET'])
@token_required
def get_order_details(current_user, order_id):
    """الحصول على تفاصيل طلب محدد"""
    try:
        order = Order.query.filter_by(order_id=order_id).first()
        
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # التحقق من الصلاحيات
        has_access = False
        if current_user.user_type == 'admin':
            has_access = True
        elif current_user.user_type == 'customer' and order.user_id == current_user.user_id:
            has_access = True
        elif current_user.user_type == 'delivery_agent' and order.delivery_agent_id == current_user.user_id:
            has_access = True
        elif current_user.user_type == 'restaurant':
            restaurant = Restaurant.query.filter_by(user_id=current_user.user_id).first()
            if restaurant and order.restaurant_id == restaurant.restaurant_id:
                has_access = True
        
        if not has_access:
            return jsonify({'message': 'Access denied'}), 403
        
        # تحضير البيانات التفصيلية
        order_dict = order.to_dict()
        order_dict['customer'] = order.customer.to_dict() if order.customer else None
        order_dict['restaurant'] = order.restaurant.to_dict() if order.restaurant else None
        order_dict['delivery_agent'] = order.delivery_agent.to_dict() if order.delivery_agent else None
        
        # إضافة عناصر الطلب مع تفاصيل المنتجات
        order_dict['items'] = []
        for item in order.order_items:
            item_dict = item.to_dict()
            if item.product:
                item_dict['product'] = item.product.to_dict()
            order_dict['items'].append(item_dict)
        
        return jsonify({'order': order_dict}), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get order details: {str(e)}'}), 500

@orders_bp.route('/orders/<order_id>/status', methods=['PUT'])
@token_required
def update_order_status(current_user, order_id):
    """تحديث حالة الطلب"""
    try:
        order = Order.query.filter_by(order_id=order_id).first()
        
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'message': 'Status is required'}), 400
        
        # التحقق من الصلاحيات والحالات المسموحة
        allowed_transitions = {
            'restaurant': {
                'pending': ['confirmed', 'cancelled'],
                'confirmed': ['preparing'],
                'preparing': ['ready']
            },
            'delivery_agent': {
                'ready': ['picked_up'],
                'picked_up': ['delivered']
            },
            'admin': {
                'pending': ['confirmed', 'cancelled'],
                'confirmed': ['preparing', 'cancelled'],
                'preparing': ['ready', 'cancelled'],
                'ready': ['picked_up', 'cancelled'],
                'picked_up': ['delivered', 'cancelled']
            }
        }
        
        # التحقق من الصلاحيات
        has_permission = False
        if current_user.user_type == 'admin':
            has_permission = True
        elif current_user.user_type == 'restaurant':
            restaurant = Restaurant.query.filter_by(user_id=current_user.user_id).first()
            if restaurant and order.restaurant_id == restaurant.restaurant_id:
                has_permission = True
        elif current_user.user_type == 'delivery_agent' and order.delivery_agent_id == current_user.user_id:
            has_permission = True
        
        if not has_permission:
            return jsonify({'message': 'Access denied'}), 403
        
        # التحقق من صحة الانتقال
        user_type = current_user.user_type
        current_status = order.order_status
        
        if user_type in allowed_transitions:
            if current_status in allowed_transitions[user_type]:
                if new_status not in allowed_transitions[user_type][current_status]:
                    return jsonify({'message': f'Cannot change status from {current_status} to {new_status}'}), 400
            else:
                return jsonify({'message': f'Cannot modify order in {current_status} status'}), 400
        
        # تحديث الحالة
        order.order_status = new_status
        order.updated_at = datetime.utcnow()
        
        # إضافة طوابع زمنية خاصة
        if new_status == 'delivered':
            order.delivered_at = datetime.utcnow()
            
            # إنشاء معاملة مالية للدفع النقدي
            if order.payment_method == 'cash':
                # معاملة من العميل للمندوب
                customer_to_agent = FinancialTransaction(
                    from_entity_type='customer',
                    from_entity_id=order.user_id,
                    to_entity_type='delivery_agent',
                    to_entity_id=order.delivery_agent_id,
                    amount=order.total_amount,
                    transaction_type='payment',
                    payment_method='cash',
                    status='success'
                )
                db.session.add(customer_to_agent)
                
                # حساب عمولة المنصة (10%)
                platform_commission = float(order.total_amount) * 0.10
                restaurant_amount = float(order.total_amount) - platform_commission - float(order.restaurant.delivery_fee)
                
                # معاملة من المندوب للمطعم
                agent_to_restaurant = FinancialTransaction(
                    from_entity_type='delivery_agent',
                    from_entity_id=order.delivery_agent_id,
                    to_entity_type='restaurant',
                    to_entity_id=order.restaurant_id,
                    amount=restaurant_amount,
                    transaction_type='transfer',
                    payment_method='cash',
                    status='pending'  # في انتظار تأكيد المطعم
                )
                db.session.add(agent_to_restaurant)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order status updated successfully',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update order status: {str(e)}'}), 500

@orders_bp.route('/orders/<order_id>/assign-delivery', methods=['PUT'])
@token_required
def assign_delivery_agent(current_user, order_id):
    """تخصيص مندوب للطلب"""
    try:
        if current_user.user_type not in ['admin', 'delivery_agent']:
            return jsonify({'message': 'Access denied'}), 403
        
        order = Order.query.filter_by(order_id=order_id).first()
        
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        if order.order_status != 'ready':
            return jsonify({'message': 'Order must be ready for pickup'}), 400
        
        if order.delivery_agent_id:
            return jsonify({'message': 'Order already has a delivery agent'}), 400
        
        # تخصيص المندوب
        if current_user.user_type == 'delivery_agent':
            # المندوب يخصص نفسه
            order.delivery_agent_id = current_user.user_id
        else:
            # المسؤول يخصص مندوب محدد
            data = request.get_json()
            agent_id = data.get('delivery_agent_id')
            
            if not agent_id:
                return jsonify({'message': 'delivery_agent_id is required'}), 400
            
            agent = User.query.filter_by(user_id=agent_id, user_type='delivery_agent').first()
            if not agent:
                return jsonify({'message': 'Delivery agent not found'}), 404
            
            order.delivery_agent_id = agent_id
        
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Delivery agent assigned successfully',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to assign delivery agent: {str(e)}'}), 500

@orders_bp.route('/orders/<order_id>/confirm-delivery', methods=['POST'])
@token_required
def confirm_delivery(current_user, order_id):
    """تأكيد التوصيل بكود التحقق"""
    try:
        order = Order.query.filter_by(order_id=order_id).first()
        
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        data = request.get_json()
        confirmation_code = data.get('confirmation_code')
        
        if not confirmation_code:
            return jsonify({'message': 'Confirmation code is required'}), 400
        
        # التحقق من الصلاحيات والكود
        if current_user.user_type == 'delivery_agent':
            if order.delivery_agent_id != current_user.user_id:
                return jsonify({'message': 'Access denied'}), 403
            
            if confirmation_code != order.delivery_code:
                return jsonify({'message': 'Invalid confirmation code'}), 400
        
        elif current_user.user_type == 'customer':
            if order.user_id != current_user.user_id:
                return jsonify({'message': 'Access denied'}), 403
            
            if confirmation_code != order.delivery_code:
                return jsonify({'message': 'Invalid confirmation code'}), 400
        
        else:
            return jsonify({'message': 'Only customers and delivery agents can confirm delivery'}), 403
        
        if order.order_status != 'picked_up':
            return jsonify({'message': 'Order must be picked up before confirmation'}), 400
        
        # تأكيد التوصيل
        order.order_status = 'delivered'
        order.delivered_at = datetime.utcnow()
        order.payment_status = 'paid' if order.payment_method == 'cash' else order.payment_status
        
        db.session.commit()
        
        return jsonify({
            'message': 'Delivery confirmed successfully',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to confirm delivery: {str(e)}'}), 500

@orders_bp.route('/orders/available', methods=['GET'])
@token_required
def get_available_orders(current_user):
    """الحصول على الطلبات المتاحة للتوصيل"""
    try:
        if current_user.user_type != 'delivery_agent':
            return jsonify({'message': 'Only delivery agents can access this endpoint'}), 403
        
        # الحصول على الطلبات الجاهزة للتوصيل
        available_orders = Order.query.filter(
            and_(
                Order.order_status == 'ready',
                Order.delivery_agent_id == None
            )
        ).order_by(Order.created_at).all()
        
        orders_data = []
        for order in available_orders:
            order_dict = order.to_dict()
            order_dict['restaurant'] = order.restaurant.to_dict() if order.restaurant else None
            
            # حساب المسافة التقريبية (يمكن تحسينها)
            if current_user.latitude and current_user.longitude:
                # هنا يمكن إضافة حساب المسافة الفعلية
                order_dict['estimated_distance'] = 'غير محدد'
            
            # حساب الأجر المتوقع
            commission = float(order.total_amount) * 0.15  # 15% عمولة
            delivery_fee = float(order.restaurant.delivery_fee) if order.restaurant else 0
            order_dict['estimated_earnings'] = commission + delivery_fee
            
            orders_data.append(order_dict)
        
        return jsonify({
            'available_orders': orders_data,
            'count': len(orders_data)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get available orders: {str(e)}'}), 500

@orders_bp.route('/orders/statistics', methods=['GET'])
@token_required
def get_order_statistics(current_user):
    """الحصول على إحصائيات الطلبات"""
    try:
        # تحديد الفترة الزمنية
        period = request.args.get('period', 'week')  # day, week, month, year
        
        if period == 'day':
            start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = datetime.utcnow() - timedelta(days=7)
        elif period == 'month':
            start_date = datetime.utcnow() - timedelta(days=30)
        elif period == 'year':
            start_date = datetime.utcnow() - timedelta(days=365)
        else:
            start_date = datetime.utcnow() - timedelta(days=7)
        
        # بناء الاستعلام حسب نوع المستخدم
        base_query = Order.query.filter(Order.created_at >= start_date)
        
        if current_user.user_type == 'customer':
            base_query = base_query.filter_by(user_id=current_user.user_id)
        elif current_user.user_type == 'restaurant':
            restaurant = Restaurant.query.filter_by(user_id=current_user.user_id).first()
            if not restaurant:
                return jsonify({'message': 'Restaurant not found'}), 404
            base_query = base_query.filter_by(restaurant_id=restaurant.restaurant_id)
        elif current_user.user_type == 'delivery_agent':
            base_query = base_query.filter_by(delivery_agent_id=current_user.user_id)
        elif current_user.user_type != 'admin':
            return jsonify({'message': 'Access denied'}), 403
        
        # حساب الإحصائيات
        total_orders = base_query.count()
        completed_orders = base_query.filter_by(order_status='delivered').count()
        cancelled_orders = base_query.filter_by(order_status='cancelled').count()
        
        # حساب إجمالي المبيعات
        total_revenue = db.session.query(func.sum(Order.total_amount))\
                        .filter(Order.order_id.in_([o.order_id for o in base_query.all()]))\
                        .scalar() or 0
        
        # حساب متوسط قيمة الطلب
        avg_order_value = float(total_revenue) / total_orders if total_orders > 0 else 0
        
        # إحصائيات حسب الحالة
        status_stats = {}
        for status in ['pending', 'confirmed', 'preparing', 'ready', 'picked_up', 'delivered', 'cancelled']:
            count = base_query.filter_by(order_status=status).count()
            status_stats[status] = count
        
        return jsonify({
            'period': period,
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'cancelled_orders': cancelled_orders,
            'completion_rate': (completed_orders / total_orders * 100) if total_orders > 0 else 0,
            'total_revenue': float(total_revenue),
            'avg_order_value': avg_order_value,
            'status_breakdown': status_stats
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get statistics: {str(e)}'}), 500

