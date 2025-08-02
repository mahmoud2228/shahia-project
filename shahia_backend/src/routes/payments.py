from flask import Blueprint, request, jsonify
from src.models.user import db, Payment, Order, FinancialTransaction, User, Restaurant
from src.routes.auth import token_required
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
import requests
import hashlib
import hmac
import json

payments_bp = Blueprint('payments', __name__)

class PaymentGateway:
    """فئة لإدارة بوابات الدفع المحلية"""
    
    def __init__(self):
        # إعدادات بوابات الدفع (يجب تخزينها في متغيرات البيئة)
        self.bankily_config = {
            'api_url': 'https://api.bankily.mr',
            'merchant_id': 'SHAHIA_MERCHANT',
            'api_key': 'your_bankily_api_key',
            'secret_key': 'your_bankily_secret_key'
        }
        
        self.masrafi_config = {
            'api_url': 'https://api.masrafi.mr',
            'merchant_id': 'SHAHIA_MERCHANT',
            'api_key': 'your_masrafi_api_key',
            'secret_key': 'your_masrafi_secret_key'
        }
        
        self.sadad_config = {
            'api_url': 'https://api.sadad.mr',
            'merchant_id': 'SHAHIA_MERCHANT',
            'api_key': 'your_sadad_api_key',
            'secret_key': 'your_sadad_secret_key'
        }
    
    def process_bankily_payment(self, order, phone_number):
        """معالجة الدفع عبر بنكيلي"""
        try:
            # إعداد بيانات الطلب
            payment_data = {
                'merchant_id': self.bankily_config['merchant_id'],
                'order_id': order.order_id,
                'amount': float(order.total_amount),
                'currency': 'MRU',  # الأوقية الموريتانية
                'customer_phone': phone_number,
                'description': f'طلب من تطبيق شهية - {order.restaurant.name}',
                'callback_url': 'https://your-domain.com/api/payments/bankily/callback',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # إنشاء التوقيع
            signature_string = f"{payment_data['merchant_id']}{payment_data['order_id']}{payment_data['amount']}{payment_data['timestamp']}"
            signature = hmac.new(
                self.bankily_config['secret_key'].encode(),
                signature_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            payment_data['signature'] = signature
            
            # إرسال الطلب لبنكيلي
            headers = {
                'Authorization': f"Bearer {self.bankily_config['api_key']}",
                'Content-Type': 'application/json'
            }
            
            # في التطبيق الحقيقي، استخدم الـ API الفعلي
            # response = requests.post(
            #     f"{self.bankily_config['api_url']}/payments/initiate",
            #     json=payment_data,
            #     headers=headers,
            #     timeout=30
            # )
            
            # محاكاة استجابة ناجحة للاختبار
            mock_response = {
                'status': 'success',
                'transaction_id': f'BKL_{order.order_id}_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}',
                'payment_url': f'bankily://pay?order_id={order.order_id}&amount={order.total_amount}',
                'expires_at': (datetime.utcnow() + timedelta(minutes=15)).isoformat()
            }
            
            return {
                'success': True,
                'transaction_id': mock_response['transaction_id'],
                'payment_url': mock_response['payment_url'],
                'expires_at': mock_response['expires_at']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_masrafi_payment(self, order, phone_number):
        """معالجة الدفع عبر مصرفي"""
        try:
            # محاكاة معالجة مصرفي
            mock_response = {
                'status': 'success',
                'transaction_id': f'MSR_{order.order_id}_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}',
                'payment_url': f'masrafi://pay?order_id={order.order_id}&amount={order.total_amount}',
                'expires_at': (datetime.utcnow() + timedelta(minutes=15)).isoformat()
            }
            
            return {
                'success': True,
                'transaction_id': mock_response['transaction_id'],
                'payment_url': mock_response['payment_url'],
                'expires_at': mock_response['expires_at']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_sadad_payment(self, order, phone_number):
        """معالجة الدفع عبر سداد"""
        try:
            # محاكاة معالجة سداد
            mock_response = {
                'status': 'success',
                'transaction_id': f'SDD_{order.order_id}_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}',
                'payment_url': f'sadad://pay?order_id={order.order_id}&amount={order.total_amount}',
                'expires_at': (datetime.utcnow() + timedelta(minutes=15)).isoformat()
            }
            
            return {
                'success': True,
                'transaction_id': mock_response['transaction_id'],
                'payment_url': mock_response['payment_url'],
                'expires_at': mock_response['expires_at']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# إنشاء مثيل من بوابة الدفع
payment_gateway = PaymentGateway()

@payments_bp.route('/payments/initiate', methods=['POST'])
@token_required
def initiate_payment(current_user):
    """بدء عملية الدفع"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['order_id', 'payment_method']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'{field} is required'}), 400
        
        # الحصول على الطلب
        order = Order.query.filter_by(order_id=data['order_id']).first()
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # التحقق من الصلاحيات
        if current_user.user_type != 'customer' or order.user_id != current_user.user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        # التحقق من حالة الطلب
        if order.payment_status == 'paid':
            return jsonify({'message': 'Order is already paid'}), 400
        
        if order.order_status == 'cancelled':
            return jsonify({'message': 'Cannot pay for cancelled order'}), 400
        
        payment_method = data['payment_method']
        
        # معالجة الدفع النقدي
        if payment_method == 'cash':
            # تحديث طريقة الدفع فقط
            order.payment_method = 'cash'
            order.payment_status = 'pending'
            db.session.commit()
            
            return jsonify({
                'message': 'Cash payment method set successfully',
                'payment_method': 'cash',
                'status': 'pending'
            }), 200
        
        # معالجة الدفع الإلكتروني
        phone_number = data.get('phone_number')
        if not phone_number:
            return jsonify({'message': 'Phone number is required for electronic payment'}), 400
        
        # معالجة حسب نوع بوابة الدفع
        payment_result = None
        
        if payment_method == 'bankily':
            payment_result = payment_gateway.process_bankily_payment(order, phone_number)
        elif payment_method == 'masrafi':
            payment_result = payment_gateway.process_masrafi_payment(order, phone_number)
        elif payment_method == 'sadad':
            payment_result = payment_gateway.process_sadad_payment(order, phone_number)
        else:
            return jsonify({'message': 'Unsupported payment method'}), 400
        
        if not payment_result['success']:
            return jsonify({'message': f'Payment initiation failed: {payment_result["error"]}'}), 500
        
        # إنشاء سجل دفع
        new_payment = Payment(
            order_id=order.order_id,
            transaction_id=payment_result['transaction_id'],
            amount=order.total_amount,
            payment_method=payment_method,
            payment_status='pending'
        )
        
        db.session.add(new_payment)
        
        # تحديث الطلب
        order.payment_method = payment_method
        order.payment_status = 'pending'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment initiated successfully',
            'payment_id': new_payment.payment_id,
            'transaction_id': payment_result['transaction_id'],
            'payment_url': payment_result['payment_url'],
            'expires_at': payment_result['expires_at']
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Payment initiation failed: {str(e)}'}), 500

@payments_bp.route('/payments/<payment_id>/status', methods=['GET'])
@token_required
def get_payment_status(current_user, payment_id):
    """الحصول على حالة الدفع"""
    try:
        payment = Payment.query.filter_by(payment_id=payment_id).first()
        
        if not payment:
            return jsonify({'message': 'Payment not found'}), 404
        
        # التحقق من الصلاحيات
        order = payment.order
        if current_user.user_type != 'admin' and order.user_id != current_user.user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        return jsonify({
            'payment': payment.to_dict(),
            'order_status': order.order_status
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get payment status: {str(e)}'}), 500

@payments_bp.route('/payments/bankily/callback', methods=['POST'])
def bankily_callback():
    """استقبال إشعارات بنكيلي"""
    try:
        data = request.get_json()
        
        # التحقق من التوقيع
        received_signature = request.headers.get('X-Bankily-Signature')
        if not received_signature:
            return jsonify({'message': 'Missing signature'}), 400
        
        # التحقق من صحة التوقيع (في التطبيق الحقيقي)
        # expected_signature = hmac.new(
        #     payment_gateway.bankily_config['secret_key'].encode(),
        #     json.dumps(data, sort_keys=True).encode(),
        #     hashlib.sha256
        # ).hexdigest()
        
        # if not hmac.compare_digest(received_signature, expected_signature):
        #     return jsonify({'message': 'Invalid signature'}), 400
        
        # معالجة الإشعار
        transaction_id = data.get('transaction_id')
        status = data.get('status')
        order_id = data.get('order_id')
        
        if not all([transaction_id, status, order_id]):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # العثور على الدفع
        payment = Payment.query.filter_by(transaction_id=transaction_id).first()
        if not payment:
            return jsonify({'message': 'Payment not found'}), 404
        
        # تحديث حالة الدفع
        if status == 'success':
            payment.payment_status = 'success'
            payment.paid_at = datetime.utcnow()
            payment.order.payment_status = 'paid'
            
            # إنشاء معاملة مالية
            financial_transaction = FinancialTransaction(
                from_entity_type='customer',
                from_entity_id=payment.order.user_id,
                to_entity_type='restaurant',
                to_entity_id=payment.order.restaurant_id,
                amount=payment.amount,
                transaction_type='payment',
                payment_method=payment.payment_method,
                status='success'
            )
            db.session.add(financial_transaction)
            
        elif status == 'failed':
            payment.payment_status = 'failed'
            payment.order.payment_status = 'failed'
        
        db.session.commit()
        
        return jsonify({'message': 'Callback processed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Callback processing failed: {str(e)}'}), 500

@payments_bp.route('/payments/financial-transactions', methods=['GET'])
@token_required
def get_financial_transactions(current_user):
    """الحصول على المعاملات المالية"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        transaction_type = request.args.get('type')
        
        # بناء الاستعلام حسب نوع المستخدم
        query = FinancialTransaction.query
        
        if current_user.user_type == 'customer':
            query = query.filter(
                or_(
                    and_(
                        FinancialTransaction.from_entity_type == 'customer',
                        FinancialTransaction.from_entity_id == current_user.user_id
                    ),
                    and_(
                        FinancialTransaction.to_entity_type == 'customer',
                        FinancialTransaction.to_entity_id == current_user.user_id
                    )
                )
            )
        elif current_user.user_type == 'restaurant':
            restaurant = Restaurant.query.filter_by(user_id=current_user.user_id).first()
            if restaurant:
                query = query.filter(
                    or_(
                        and_(
                            FinancialTransaction.from_entity_type == 'restaurant',
                            FinancialTransaction.from_entity_id == restaurant.restaurant_id
                        ),
                        and_(
                            FinancialTransaction.to_entity_type == 'restaurant',
                            FinancialTransaction.to_entity_id == restaurant.restaurant_id
                        )
                    )
                )
        elif current_user.user_type == 'delivery_agent':
            query = query.filter(
                or_(
                    and_(
                        FinancialTransaction.from_entity_type == 'delivery_agent',
                        FinancialTransaction.from_entity_id == current_user.user_id
                    ),
                    and_(
                        FinancialTransaction.to_entity_type == 'delivery_agent',
                        FinancialTransaction.to_entity_id == current_user.user_id
                    )
                )
            )
        elif current_user.user_type != 'admin':
            return jsonify({'message': 'Access denied'}), 403
        
        # تطبيق فلتر نوع المعاملة
        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)
        
        # ترتيب وتقسيم الصفحات
        transactions = query.order_by(desc(FinancialTransaction.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'transactions': [t.to_dict() for t in transactions.items],
            'pagination': {
                'page': transactions.page,
                'pages': transactions.pages,
                'per_page': transactions.per_page,
                'total': transactions.total,
                'has_next': transactions.has_next,
                'has_prev': transactions.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get financial transactions: {str(e)}'}), 500

@payments_bp.route('/payments/balance', methods=['GET'])
@token_required
def get_balance(current_user):
    """الحصول على الرصيد الحالي"""
    try:
        balance = 0
        pending_balance = 0
        
        if current_user.user_type == 'restaurant':
            restaurant = Restaurant.query.filter_by(user_id=current_user.user_id).first()
            if restaurant:
                # حساب الرصيد من المعاملات الواردة
                incoming = db.session.query(func.sum(FinancialTransaction.amount))\
                    .filter(
                        and_(
                            FinancialTransaction.to_entity_type == 'restaurant',
                            FinancialTransaction.to_entity_id == restaurant.restaurant_id,
                            FinancialTransaction.status == 'success'
                        )
                    ).scalar() or 0
                
                # حساب المعاملات الصادرة
                outgoing = db.session.query(func.sum(FinancialTransaction.amount))\
                    .filter(
                        and_(
                            FinancialTransaction.from_entity_type == 'restaurant',
                            FinancialTransaction.from_entity_id == restaurant.restaurant_id,
                            FinancialTransaction.status == 'success'
                        )
                    ).scalar() or 0
                
                balance = float(incoming) - float(outgoing)
                
                # حساب الرصيد المعلق
                pending_balance = db.session.query(func.sum(FinancialTransaction.amount))\
                    .filter(
                        and_(
                            FinancialTransaction.to_entity_type == 'restaurant',
                            FinancialTransaction.to_entity_id == restaurant.restaurant_id,
                            FinancialTransaction.status == 'pending'
                        )
                    ).scalar() or 0
        
        elif current_user.user_type == 'delivery_agent':
            # حساب رصيد المندوب
            incoming = db.session.query(func.sum(FinancialTransaction.amount))\
                .filter(
                    and_(
                        FinancialTransaction.to_entity_type == 'delivery_agent',
                        FinancialTransaction.to_entity_id == current_user.user_id,
                        FinancialTransaction.status == 'success'
                    )
                ).scalar() or 0
            
            outgoing = db.session.query(func.sum(FinancialTransaction.amount))\
                .filter(
                    and_(
                        FinancialTransaction.from_entity_type == 'delivery_agent',
                        FinancialTransaction.from_entity_id == current_user.user_id,
                        FinancialTransaction.status == 'success'
                    )
                ).scalar() or 0
            
            balance = float(incoming) - float(outgoing)
            
            pending_balance = db.session.query(func.sum(FinancialTransaction.amount))\
                .filter(
                    and_(
                        FinancialTransaction.to_entity_type == 'delivery_agent',
                        FinancialTransaction.to_entity_id == current_user.user_id,
                        FinancialTransaction.status == 'pending'
                    )
                ).scalar() or 0
        
        return jsonify({
            'current_balance': balance,
            'pending_balance': float(pending_balance),
            'currency': 'MRU'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get balance: {str(e)}'}), 500

@payments_bp.route('/payments/payout-codes/<order_id>', methods=['POST'])
@token_required
def confirm_payout(current_user, order_id):
    """تأكيد تسليم الأموال بكود التحقق"""
    try:
        order = Order.query.filter_by(order_id=order_id).first()
        
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        data = request.get_json()
        payout_code = data.get('payout_code')
        
        if not payout_code:
            return jsonify({'message': 'Payout code is required'}), 400
        
        # التحقق من الصلاحيات والكود
        if current_user.user_type == 'restaurant':
            restaurant = Restaurant.query.filter_by(user_id=current_user.user_id).first()
            if not restaurant or order.restaurant_id != restaurant.restaurant_id:
                return jsonify({'message': 'Access denied'}), 403
            
            if payout_code != order.restaurant_payout_code:
                return jsonify({'message': 'Invalid payout code'}), 400
        else:
            return jsonify({'message': 'Only restaurant owners can confirm payout'}), 403
        
        # البحث عن المعاملة المعلقة
        pending_transaction = FinancialTransaction.query.filter(
            and_(
                FinancialTransaction.to_entity_type == 'restaurant',
                FinancialTransaction.to_entity_id == order.restaurant_id,
                FinancialTransaction.status == 'pending'
            )
        ).first()
        
        if pending_transaction:
            pending_transaction.status = 'success'
            db.session.commit()
            
            return jsonify({
                'message': 'Payout confirmed successfully',
                'amount': float(pending_transaction.amount)
            }), 200
        else:
            return jsonify({'message': 'No pending payout found'}), 404
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to confirm payout: {str(e)}'}), 500

