import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.restaurants import restaurants_bp
from src.routes.orders import orders_bp
from src.routes.payments import payments_bp
from src.routes.ai_assistant import ai_assistant_bp
from src.config import Config

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# إعداد CORS للسماح بالطلبات من جميع المصادر
CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])

app.config["OPENAI_API_KEY"] = Config.OPENAI_API_KEY
app.config["SECRET_KEY"] = "shahia_super_secret_key_2024_mauritania"

# تسجيل المسارات
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(restaurants_bp, url_prefix='/api')
app.register_blueprint(orders_bp, url_prefix='/api')
app.register_blueprint(payments_bp, url_prefix='/api')
app.register_blueprint(ai_assistant_bp, url_prefix='/api')

# إعداد قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    
    # إنشاء مستخدم مسؤول افتراضي
    from src.models.user import User
    admin_user = User.query.filter_by(email='admin@shahia.mr').first()
    if not admin_user:
        admin_user = User(
            name='مسؤول شهية',
            email='admin@shahia.mr',
            phone_number='+22200000000',
            user_type='admin',
            address='نواكشوط، موريتانيا'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print("تم إنشاء حساب المسؤول الافتراضي:")
        print("البريد الإلكتروني: admin@shahia.mr")
        print("كلمة المرور: admin123")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "مرحباً بك في API تطبيق شهية - منصة توصيل الطعام الذكية في موريتانيا", 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """فحص صحة النظام"""
    return {
        'status': 'healthy',
        'message': 'Shahia API is running successfully',
        'version': '1.0.0',
        'features': [
            'Smart AI Assistant',
            'Real-time Order Tracking',
            'Local Payment Gateways',
            'Advanced Analytics',
            'Multi-user Support'
        ]
    }, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

