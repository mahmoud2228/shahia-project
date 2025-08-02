from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import uuid
import random
import string
import hashlib
import hmac
import json
import requests

payments_enhanced_bp = Blueprint('payments_enhanced', __name__)

# محاكاة قاعدة بيانات المدفوعات المحسنة
payments_db = {}
transactions_db = {}
wallets_db = {}

# أنظمة الدفع المدعومة في موريتانيا مع التفاصيل الكاملة
MAURITANIAN_PAYMENT_SYSTEMS = {
    'cash_on_delivery': {
        'name': 'الدفع عند التسليم',
        'name_en': 'Cash on Delivery',
        'enabled': True,
        'fee': 0,
        'description': 'دفع نقدي عند استلام الطلب مع رمز تحقق',
        'supports_verification': True,
        'instant': True
    },
    'bankily': {
        'name': 'بنكيلي',
        'name_en': 'Bankily',
        'enabled': True,
        'fee': 0.02,  # 2% رسوم
        'description': 'الدفع عبر محفظة بنكيلي الإلكترونية - البنك الشعبي الموريتاني',
        'api_endpoint': 'https://api.bankily.mr/v1/payments',
        'merchant_code': 'SHAHIA_001',
        'ussd_code': '*888#',
        'supports_qr': True,
        'supports_phone_transfer': True,
        'instant': True
    },
    'masrafi': {
        'name': 'مصرفي',
        'name_en': 'Masrafi',
        'enabled': True,
        'fee': 0.025,  # 2.5% رسوم
        'description': 'الدفع عبر نظام مصرفي للخدمات المصرفية الرقمية',
        'api_endpoint': 'https://api.masrafi.mr/payments',
        'merchant_code': 'SHAHIA_002',
        'supports_bank_transfer': True,
        'instant': False,
        'processing_time': '1-3 أيام عمل'
    },
    'sadad': {
        'name': 'سداد',
        'name_en': 'Sadad',
        'enabled': True,
        'fee': 0.02,  # 2% رسوم
        'description': 'نظام سداد لاستقبال الأموال من جميع البنوك المحلية',
        'api_endpoint': 'https://api.sadad.mr/pay',
        'merchant_code': 'SHAHIA_003',
        'supports_multi_bank': True,
        'instant': True
    }
}

class MauritanianPaymentGateway:
    """فئة متخصصة لإدارة أنظمة الدفع الموريتانية"""
    
    def __init__(self):
        self.bankily_config = {
            'api_url': 'https://api.bankily.mr/v1',
            'merchant_id': 'SHAHIA_MERCHANT_001',
            'api_key': 'bankily_api_key_here',
            'secret_key': 'bankily_secret_key_here',
            'ussd_code': '*888#'
        }
        
        self.masrafi_config = {
            'api_url': 'https://api.masrafi.mr/v2',
            'merchant_id': 'SHAHIA_MERCHANT_002',
            'api_key': 'masrafi_api_key_here',
            'secret_key': 'masrafi_secret_key_here'
        }
        
        self.sadad_config = {
            'api_url': 'https://api.sadad.mr/v1',
            'merchant_id': 'SHAHIA_MERCHANT_003',
            'api_key': 'sadad_api_key_here',
            'secret_key': 'sadad_secret_key_here'
        }
    
    def generate_signature(self, data, secret_key):
        """توليد التوقيع الرقمي للأمان"""
        message = json.dumps(data, sort_keys=True)
        signature = hmac.new(
            secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def process_bankily_payment(self, payment_data):
        """معالجة الدفع عبر بنكيلي"""
        try:
            # إعداد بيانات الطلب لبنكيلي
            bankily_request = {
                'merchant_id': self.bankily_config['merchant_id'],
                'transaction_id': payment_data['transaction_id'],
                'amount': payment_data['total'],
                'currency': 'MRU',
                'customer_phone': payment_data['customer_phone'],
                'description': f"طلب شهية #{payment_data['order_id']}",
                'callback_url': 'https://shahia.mr/api/payments/bankily/callback',
                'return_url': 'https://shahia.mr/payment/success'
            }
            
            # إضافة التوقيع الرقمي
            bankily_request['signature'] = self.generate_signature(
                bankily_request, 
                self.bankily_config['secret_key']
            )
            
            # محاكاة استجابة بنكيلي
            return {
                'success': True,
                'payment_url': f"https://pay.bankily.mr/checkout/{payment_data['transaction_id']}",
                'qr_code': f"bankily://pay?merchant={self.bankily_config['merchant_id']}&amount={payment_data['total']}&ref={payment_data['transaction_id']}",
                'ussd_instructions': f"اتصل بـ {self.bankily_config['ussd_code']} واتبع التعليمات",
                'phone_transfer_code': f"#{payment_data['transaction_id'][:8]}"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def process_masrafi_payment(self, payment_data):
        """معالجة الدفع عبر مصرفي"""
        try:
            masrafi_request = {
                'merchant_id': self.masrafi_config['merchant_id'],
                'reference': payment_data['transaction_id'],
                'amount': payment_data['total'],
                'currency': 'MRU',
                'customer_info': {
                    'phone': payment_data['customer_phone']
                },
                'order_details': {
                    'order_id': payment_data['order_id'],
                    'description': f"طلب من تطبيق شهية"
                }
            }
            
            # محاكاة استجابة مصرفي
            return {
                'success': True,
                'payment_reference': f"MSR_{payment_data['transaction_id'][:10]}",
                'bank_transfer_details': {
                    'account_number': '1234567890',
                    'bank_name': 'البنك الموريتاني',
                    'reference': payment_data['transaction_id']
                },
                'estimated_processing': '1-3 أيام عمل'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def process_sadad_payment(self, payment_data):
        """معالجة الدفع عبر سداد"""
        try:
            sadad_request = {
                'merchant_code': self.sadad_config['merchant_id'],
                'transaction_ref': payment_data['transaction_id'],
                'amount': payment_data['total'],
                'currency': 'MRU',
                'customer_mobile': payment_data['customer_phone'],
                'description': f"دفع طلب شهية #{payment_data['order_id']}"
            }
            
            # محاكاة استجابة سداد
            return {
                'success': True,
                'sadad_reference': f"SAD_{payment_data['transaction_id'][:8]}",
                'payment_code': f"*{random.randint(1000, 9999)}#",
                'instructions': "استخدم الرمز المرسل لإكمال الدفع عبر أي بنك محلي"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

# إنشاء مثيل من بوابة الدفع
payment_gateway = MauritanianPaymentGateway()

def generate_transaction_id():
    """توليد رقم معاملة فريد مع بادئة موريتانية"""
    prefix = "MR"
    date_part = datetime.now().strftime('%Y%m%d')
    random_part = uuid.uuid4().hex[:8].upper()
    return f"{prefix}_{date_part}_{random_part}"

def generate_verification_code():
    """توليد رمز تحقق من 6 أرقام"""
    return ''.join(random.choices(string.digits, k=6))

def generate_transfer_code():
    """توليد رمز تحويل للمطاعم والمندوبين"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@payments_enhanced_bp.route('/methods', methods=['GET'])
def get_payment_methods():
    """الحصول على طرق الدفع المتاحة مع التفاصيل الكاملة"""
    try:
        methods = []
        for method_id, method_info in MAURITANIAN_PAYMENT_SYSTEMS.items():
            if method_info['enabled']:
                method_data = {
                    'method_id': method_id,
                    'name': method_info['name'],
                    'name_en': method_info['name_en'],
                    'fee_percentage': method_info['fee'] * 100,
                    'description': method_info['description'],
                    'instant': method_info['instant']
                }
                
                # إضافة معلومات خاصة بكل نظام
                if method_id == 'bankily':
                    method_data.update({
                        'ussd_code': method_info['ussd_code'],
                        'supports_qr': method_info['supports_qr'],
                        'supports_phone_transfer': method_info['supports_phone_transfer']
                    })
                elif method_id == 'masrafi':
                    method_data.update({
                        'processing_time': method_info['processing_time'],
                        'supports_bank_transfer': method_info['supports_bank_transfer']
                    })
                elif method_id == 'sadad':
                    method_data.update({
                        'supports_multi_bank': method_info['supports_multi_bank']
                    })
                
                methods.append(method_data)
        
        return jsonify({
            'success': True,
            'payment_methods': methods,
            'currency': 'MRU',
            'currency_name': 'الأوقية الموريتانية'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@payments_enhanced_bp.route('/calculate-fee', methods=['POST'])
def calculate_payment_fee():
    """حساب رسوم الدفع مع تفاصيل إضافية"""
    try:
        data = request.get_json()
        amount = data.get('amount', 0)
        payment_method = data.get('payment_method', 'cash_on_delivery')
        
        if payment_method not in MAURITANIAN_PAYMENT_SYSTEMS:
            return jsonify({'success': False, 'error': 'طريقة دفع غير مدعومة'}), 400
        
        method_info = MAURITANIAN_PAYMENT_SYSTEMS[payment_method]
        fee = amount * method_info['fee']
        total = amount + fee
        
        # حساب توزيع الرسوم
        platform_fee = fee * 0.7  # 70% للمنصة
        gateway_fee = fee * 0.3   # 30% لبوابة الدفع
        
        return jsonify({
            'success': True,
            'calculation': {
                'subtotal': amount,
                'payment_fee': fee,
                'total': total,
                'currency': 'MRU',
                'fee_breakdown': {
                    'platform_fee': platform_fee,
                    'gateway_fee': gateway_fee
                }
            },
            'payment_method': {
                'id': payment_method,
                'name': method_info['name'],
                'instant': method_info['instant']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@payments_enhanced_bp.route('/initiate', methods=['POST'])
def initiate_payment():
    """بدء عملية الدفع مع دعم شامل للأنظمة المحلية"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        amount = data.get('amount')
        payment_method = data.get('payment_method')
        customer_phone = data.get('customer_phone')
        customer_name = data.get('customer_name', 'عميل')
        
        if not all([order_id, amount, payment_method, customer_phone]):
            return jsonify({'success': False, 'error': 'بيانات مفقودة'}), 400
        
        if payment_method not in MAURITANIAN_PAYMENT_SYSTEMS:
            return jsonify({'success': False, 'error': 'طريقة دفع غير مدعومة'}), 400
        
        transaction_id = generate_transaction_id()
        method_info = MAURITANIAN_PAYMENT_SYSTEMS[payment_method]
        fee = amount * method_info['fee']
        total = amount + fee
        
        payment_data = {
            'transaction_id': transaction_id,
            'order_id': order_id,
            'amount': amount,
            'fee': fee,
            'total': total,
            'currency': 'MRU',
            'payment_method': payment_method,
            'customer_phone': customer_phone,
            'customer_name': customer_name,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(minutes=30)).isoformat(),
            'method_info': method_info
        }
        
        # معالجة حسب نوع الدفع
        if payment_method == 'cash_on_delivery':
            verification_code = generate_verification_code()
            payment_data.update({
                'verification_code': verification_code,
                'status': 'confirmed',
                'payment_instructions': {
                    'type': 'cash_verification',
                    'verification_code': verification_code,
                    'message': f'رمز التحقق للدفع النقدي: {verification_code}',
                    'instructions': [
                        'احتفظ برمز التحقق',
                        'أعطِ الرمز للمندوب عند التسليم',
                        'تأكد من استلام طلبك كاملاً قبل الدفع'
                    ]
                }
            })
        
        elif payment_method == 'bankily':
            bankily_response = payment_gateway.process_bankily_payment(payment_data)
            if bankily_response['success']:
                payment_data.update({
                    'payment_instructions': {
                        'type': 'bankily_payment',
                        'payment_url': bankily_response['payment_url'],
                        'qr_code': bankily_response['qr_code'],
                        'ussd_instructions': bankily_response['ussd_instructions'],
                        'phone_transfer_code': bankily_response['phone_transfer_code'],
                        'instructions': [
                            'اضغط على رابط الدفع',
                            'أو امسح رمز QR بتطبيق بنكيلي',
                            f'أو اتصل بـ {method_info["ussd_code"]} واتبع التعليمات'
                        ]
                    }
                })
            else:
                return jsonify({'success': False, 'error': 'فشل في إعداد دفع بنكيلي'}), 500
        
        elif payment_method == 'masrafi':
            masrafi_response = payment_gateway.process_masrafi_payment(payment_data)
            if masrafi_response['success']:
                payment_data.update({
                    'payment_instructions': {
                        'type': 'masrafi_payment',
                        'payment_reference': masrafi_response['payment_reference'],
                        'bank_transfer_details': masrafi_response['bank_transfer_details'],
                        'estimated_processing': masrafi_response['estimated_processing'],
                        'instructions': [
                            'قم بالتحويل المصرفي باستخدام التفاصيل المرفقة',
                            'استخدم رقم المرجع في التحويل',
                            'سيتم تأكيد الدفع خلال 1-3 أيام عمل'
                        ]
                    }
                })
        
        elif payment_method == 'sadad':
            sadad_response = payment_gateway.process_sadad_payment(payment_data)
            if sadad_response['success']:
                payment_data.update({
                    'payment_instructions': {
                        'type': 'sadad_payment',
                        'sadad_reference': sadad_response['sadad_reference'],
                        'payment_code': sadad_response['payment_code'],
                        'instructions': [
                            'استخدم رمز الدفع في أي بنك محلي',
                            'أو ادفع عبر تطبيق البنك الخاص بك',
                            'الدفع فوري ومؤمن'
                        ]
                    }
                })
        
        payments_db[transaction_id] = payment_data
        
        return jsonify({
            'success': True,
            'transaction_id': transaction_id,
            'payment_data': payment_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@payments_enhanced_bp.route('/status/<transaction_id>', methods=['GET'])
def get_payment_status(transaction_id):
    """الحصول على حالة الدفع مع تفاصيل محدثة"""
    try:
        if transaction_id not in payments_db:
            return jsonify({'success': False, 'error': 'معاملة غير موجودة'}), 404
        
        payment_data = payments_db[transaction_id]
        
        # محاكاة تحديث حالة الدفع الإلكتروني
        if (payment_data['payment_method'] != 'cash_on_delivery' and 
            payment_data['status'] == 'pending'):
            
            # محاكاة نجاح الدفع بنسبة 85%
            if random.random() < 0.85:
                payment_data['status'] = 'completed'
                payment_data['completed_at'] = datetime.now().isoformat()
                payment_data['gateway_reference'] = f"GW_{uuid.uuid4().hex[:8].upper()}"
        
        # إضافة معلومات إضافية عن الحالة
        status_info = {
            'pending': 'في انتظار الدفع',
            'confirmed': 'مؤكد - في انتظار التسليم',
            'completed': 'مكتمل',
            'failed': 'فشل',
            'refunded': 'مسترد'
        }
        
        payment_data['status_description'] = status_info.get(payment_data['status'], 'غير معروف')
        
        return jsonify({
            'success': True,
            'payment_status': payment_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@payments_enhanced_bp.route('/confirm-delivery', methods=['POST'])
def confirm_delivery_payment():
    """تأكيد الدفع عند التسليم"""
    try:
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        verification_code = data.get('verification_code')
        driver_id = data.get('driver_id')
        delivery_location = data.get('delivery_location')
        
        if not all([transaction_id, verification_code, driver_id]):
            return jsonify({'success': False, 'error': 'بيانات مفقودة'}), 400
        
        if transaction_id not in payments_db:
            return jsonify({'success': False, 'error': 'معاملة غير موجودة'}), 404
        
        payment_data = payments_db[transaction_id]
        
        if payment_data['payment_method'] != 'cash_on_delivery':
            return jsonify({'success': False, 'error': 'هذه المعاملة ليست دفع عند التسليم'}), 400
        
        if payment_data.get('verification_code') != verification_code:
            return jsonify({'success': False, 'error': 'رمز التحقق غير صحيح'}), 400
        
        # تأكيد التسليم والدفع
        payment_data.update({
            'status': 'completed',
            'completed_at': datetime.now().isoformat(),
            'delivered_by': driver_id,
            'delivery_location': delivery_location,
            'delivery_confirmed': True
        })
        
        # إنشاء رمز تسليم الأموال للمطعم
        money_transfer_code = generate_transfer_code()
        payment_data['money_transfer_code'] = money_transfer_code
        
        return jsonify({
            'success': True,
            'message': 'تم تأكيد التسليم والدفع بنجاح',
            'money_transfer_code': money_transfer_code,
            'payment_status': payment_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@payments_enhanced_bp.route('/transfer-to-restaurant', methods=['POST'])
def transfer_money_to_restaurant():
    """تحويل الأموال من المندوب للمطعم"""
    try:
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        money_transfer_code = data.get('money_transfer_code')
        driver_id = data.get('driver_id')
        restaurant_id = data.get('restaurant_id')
        
        if not all([transaction_id, money_transfer_code, driver_id, restaurant_id]):
            return jsonify({'success': False, 'error': 'بيانات مفقودة'}), 400
        
        if transaction_id not in payments_db:
            return jsonify({'success': False, 'error': 'معاملة غير موجودة'}), 404
        
        payment_data = payments_db[transaction_id]
        
        if payment_data.get('money_transfer_code') != money_transfer_code:
            return jsonify({'success': False, 'error': 'رمز تحويل الأموال غير صحيح'}), 400
        
        # حساب المبالغ
        restaurant_amount = payment_data['amount'] * 0.85  # 85% للمطعم
        platform_commission = payment_data['amount'] * 0.10  # 10% للمنصة
        driver_commission = payment_data['amount'] * 0.05   # 5% للمندوب
        
        transfer_id = generate_transaction_id()
        transfer_data = {
            'transfer_id': transfer_id,
            'original_transaction_id': transaction_id,
            'from_driver': driver_id,
            'to_restaurant': restaurant_id,
            'restaurant_amount': restaurant_amount,
            'platform_commission': platform_commission,
            'driver_commission': driver_commission,
            'status': 'completed',
            'created_at': datetime.now().isoformat(),
            'transfer_method': 'cash_handover'
        }
        
        transactions_db[transfer_id] = transfer_data
        payment_data['money_transferred'] = True
        payment_data['transfer_id'] = transfer_id
        
        return jsonify({
            'success': True,
            'message': 'تم تحويل الأموال بنجاح',
            'transfer_data': transfer_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@payments_enhanced_bp.route('/wallet/balance/<user_id>', methods=['GET'])
def get_wallet_balance(user_id):
    """الحصول على رصيد المحفظة مع تفاصيل شاملة"""
    try:
        # محاكاة أرصدة المحافظ مع تفاصيل إضافية
        mock_wallets = {
            'restaurant_1': {
                'balance': 25000,
                'pending_amount': 3500,
                'total_earned': 125000,
                'last_transaction': datetime.now().isoformat()
            },
            'restaurant_2': {
                'balance': 18500,
                'pending_amount': 2200,
                'total_earned': 89000,
                'last_transaction': datetime.now().isoformat()
            },
            'driver_1': {
                'balance': 12500,
                'pending_amount': 800,
                'total_earned': 45000,
                'last_transaction': datetime.now().isoformat()
            },
            'driver_2': {
                'balance': 8900,
                'pending_amount': 600,
                'total_earned': 32000,
                'last_transaction': datetime.now().isoformat()
            }
        }
        
        wallet_data = mock_wallets.get(user_id, {
            'balance': 0,
            'pending_amount': 0,
            'total_earned': 0,
            'last_transaction': None
        })
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'wallet': {
                'available_balance': wallet_data['balance'],
                'pending_amount': wallet_data['pending_amount'],
                'total_balance': wallet_data['balance'] + wallet_data['pending_amount'],
                'total_earned': wallet_data['total_earned'],
                'currency': 'MRU',
                'currency_name': 'الأوقية الموريتانية',
                'last_transaction': wallet_data['last_transaction']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@payments_enhanced_bp.route('/analytics/dashboard', methods=['GET'])
def get_payment_analytics():
    """تحليلات شاملة للمدفوعات"""
    try:
        analytics_data = {
            'overview': {
                'total_revenue': 125000,
                'monthly_revenue': 45000,
                'weekly_revenue': 12000,
                'daily_revenue': 2800,
                'total_transactions': 1250,
                'successful_rate': 94.5
            },
            'payment_methods_stats': {
                'cash_on_delivery': {
                    'percentage': 65,
                    'amount': 81250,
                    'transactions': 812
                },
                'bankily': {
                    'percentage': 25,
                    'amount': 31250,
                    'transactions': 312
                },
                'masrafi': {
                    'percentage': 7,
                    'amount': 8750,
                    'transactions': 87
                },
                'sadad': {
                    'percentage': 3,
                    'amount': 3750,
                    'transactions': 39
                }
            },
            'revenue_trends': [
                {'month': 'يناير', 'revenue': 85000, 'transactions': 950},
                {'month': 'فبراير', 'revenue': 92000, 'transactions': 1020},
                {'month': 'مارس', 'revenue': 98000, 'transactions': 1100},
                {'month': 'أبريل', 'revenue': 105000, 'transactions': 1180},
                {'month': 'مايو', 'revenue': 112000, 'transactions': 1220},
                {'month': 'يونيو', 'revenue': 118000, 'transactions': 1250},
                {'month': 'يوليو', 'revenue': 125000, 'transactions': 1250}
            ],
            'fees_collected': {
                'total_fees': 2500,
                'platform_fees': 1750,
                'gateway_fees': 750
            },
            'regional_stats': {
                'نواكشوط': {'revenue': 75000, 'percentage': 60},
                'نواذيبو': {'revenue': 25000, 'percentage': 20},
                'روصو': {'revenue': 12500, 'percentage': 10},
                'أخرى': {'revenue': 12500, 'percentage': 10}
            }
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics_data,
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

