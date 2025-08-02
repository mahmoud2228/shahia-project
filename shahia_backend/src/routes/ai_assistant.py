from flask import Blueprint, request, jsonify, current_app
from src.models.user import db, User, Restaurant, Order, Product, OrderItem, FinancialTransaction
from src.routes.auth import token_required
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
import openai
import json
from collections import defaultdict

ai_assistant_bp = Blueprint("ai_assistant", __name__)

class AIAssistant:
    def __init__(self):
        pass
    
    def _get_openai_client(self):
        """يحصل على عميل OpenAI مع مفتاح API من إعدادات التطبيق"""
        if not current_app.config.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is not configured in the application.")
        return openai.OpenAI(api_key=current_app.config["OPENAI_API_KEY"])

    def get_customer_insights(self, user_id):
        """تحليل بيانات العميل وتقديم رؤى ذكية"""
        try:
            user = User.query.filter_by(user_id=user_id).first()
            orders = Order.query.filter_by(user_id=user_id).order_by(desc(Order.created_at)).limit(50).all()
            
            if not orders:
                return {
                    "insights": [],
                    "recommendations": ["مرحباً بك في شهية! ابدأ بتصفح المطاعم القريبة منك واكتشف أشهى الأطباق."],
                    "spending_analysis": {"total_spent": 0, "average_order": 0, "order_count": 0}
                }
            
            total_spent = sum(float(order.total_amount) for order in orders)
            avg_order_value = total_spent / len(orders)
            
            restaurant_orders = defaultdict(int)
            for order in orders:
                restaurant_orders[order.restaurant_id] += 1
            
            favorite_restaurants = sorted(restaurant_orders.items(), key=lambda x: x[1], reverse=True)[:3]
            
            order_hours = [order.created_at.hour for order in orders]
            peak_hour = max(set(order_hours), key=order_hours.count) if order_hours else 12
            
            order_weekdays = [order.created_at.weekday() for order in orders]
            peak_weekday = max(set(order_weekdays), key=order_weekdays.count) if order_weekdays else 0
            
            weekday_names = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "السبت", "الأحد"]
            
            insights = []
            recommendations = []
            
            if len(orders) >= 5:
                insights.append(f"لديك {len(orders)} طلب في آخر فترة بمتوسط {avg_order_value:.0f} أوقية للطلب الواحد")
                insights.append(f"وقتك المفضل للطلب هو الساعة {peak_hour}:00")
                insights.append(f"يومك المفضل للطلب هو {weekday_names[peak_weekday]}")
            
            if avg_order_value < 500:
                recommendations.append("💡 جرب العروض المجمعة لتوفير أكثر على طلباتك")
            
            if len(favorite_restaurants) > 0:
                fav_restaurant = Restaurant.query.filter_by(restaurant_id=favorite_restaurants[0][0]).first()
                if fav_restaurant:
                    recommendations.append(f"🍽️ مطعمك المفضل {fav_restaurant.name} لديه عروض جديدة!")
            
            current_hour = datetime.now().hour
            if 6 <= current_hour <= 10:
                recommendations.append("🌅 وقت الإفطار! اكتشف أفضل خيارات الإفطار القريبة منك")
            elif 12 <= current_hour <= 14:
                recommendations.append("🍽️ وقت الغداء! جرب أطباق اليوم المميزة")
            elif 19 <= current_hour <= 22:
                recommendations.append("🌙 وقت العشاء! استمتع بوجبة مسائية لذيذة")
            
            return {
                "insights": insights,
                "recommendations": recommendations,
                "spending_analysis": {
                    "total_spent": total_spent,
                    "average_order": avg_order_value,
                    "order_count": len(orders),
                    "favorite_restaurants": len(favorite_restaurants)
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_restaurant_insights(self, restaurant_id):
        """تحليل بيانات المطعم وتقديم رؤى تجارية ذكية"""
        try:
            restaurant = Restaurant.query.filter_by(restaurant_id=restaurant_id).first()
            if not restaurant:
                return {"error": "Restaurant not found"}
            
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            orders = Order.query.filter(
                and_(
                    Order.restaurant_id == restaurant_id,
                    Order.created_at >= thirty_days_ago
                )
            ).all()
            
            if not orders:
                return {
                    "insights": ["لا توجد طلبات في آخر 30 يوم"],
                    "recommendations": [
                        "📈 ابدأ بإضافة منتجات جذابة لقائمتك",
                        "📸 أضف صور عالية الجودة لأطباقك",
                        "💰 قدم عروض ترحيبية للعملاء الجدد"
                    ],
                    "performance_metrics": {}
                }
            
            total_revenue = sum(float(order.total_amount) for order in orders)
            avg_order_value = total_revenue / len(orders)
            
            product_sales = defaultdict(int)
            for order in orders:
                for item in order.order_items:
                    product_sales[item.product_id] += item.quantity
            
            top_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]
            
            order_hours = [order.created_at.hour for order in orders]
            peak_hours = {}
            for hour in order_hours:
                peak_hours[hour] = peak_hours.get(hour, 0) + 1
            
            busiest_hour = max(peak_hours.items(), key=lambda x: x[1])[0] if peak_hours else 12
            
            cancelled_orders = [o for o in orders if o.order_status == "cancelled"]
            cancellation_rate = len(cancelled_orders) / len(orders) * 100
            
            insights = []
            recommendations = []
            
            insights.append(f"💰 إجمالي المبيعات: {total_revenue:.0f} أوقية في آخر 30 يوم")
            insights.append(f"📊 متوسط قيمة الطلب: {avg_order_value:.0f} أوقية")
            insights.append(f"🕐 ساعة الذروة: {busiest_hour}:00")
            insights.append(f"📈 عدد الطلبات: {len(orders)} طلب")
            
            if cancellation_rate > 0:
                insights.append(f"⚠️ معدل الإلغاء: {cancellation_rate:.1f}%")
            
            if avg_order_value < 300:
                recommendations.append("💡 اقترح منتجات إضافية لزيادة قيمة الطلب")
                recommendations.append("🎁 قدم عروض مجمعة جذابة")
            
            if cancellation_rate > 10:
                recommendations.append("⚡ راجع أوقات التحضير لتقليل الإلغاءات")
                recommendations.append("📞 تواصل مع العملاء عند التأخير")
            
            if len(orders) < 50:
                recommendations.append("📢 زد من التسويق لمطعمك")
                recommendations.append("⭐ اطلب من العملاء تقييم مطعمك")
            
            current_hour = datetime.now().hour
            if 10 <= current_hour <= 14:
                recommendations.append("🍽️ قدم عروض غداء مميزة الآن")
            elif 17 <= current_hour <= 21:
                recommendations.append("🌙 وقت مثالي لعروض العشاء")
            
            return {
                "insights": insights,
                "recommendations": recommendations,
                "performance_metrics": {
                    "total_revenue": total_revenue,
                    "order_count": len(orders),
                    "avg_order_value": avg_order_value,
                    "cancellation_rate": cancellation_rate,
                    "busiest_hour": busiest_hour
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_delivery_agent_insights(self, agent_id):
        """تحليل بيانات المندوب وتقديم رؤى لتحسين الأداء"""
        try:
            agent = User.query.filter_by(user_id=agent_id).first()
            if not agent or agent.user_type != "delivery_agent":
                return {"error": "Delivery agent not found"}
            
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            deliveries = Order.query.filter(
                and_(
                    Order.delivery_agent_id == agent_id,
                    Order.created_at >= thirty_days_ago,
                    Order.order_status.in_(["delivered", "picked_up"])
                )
            ).all()
            
            if not deliveries:
                return {
                    "insights": ["لا توجد توصيلات في آخر 30 يوم"],
                    "recommendations": [
                        "🚀 ابدأ بقبول المزيد من طلبات التوصيل",
                        "📍 تأكد من تحديث موقعك باستمرار",
                        "⏰ كن متاحاً في أوقات الذروة"
                    ],
                    "performance_metrics": {}
                }
            
            total_earnings = 0
            for delivery in deliveries:
                commission = float(delivery.total_amount) * 0.15
                delivery_fee = float(delivery.restaurant.delivery_fee) if delivery.restaurant else 0
                total_earnings += commission + delivery_fee
            
            avg_earnings_per_delivery = total_earnings / len(deliveries)
            
            delivery_hours = [d.created_at.hour for d in deliveries]
            peak_hours = {}
            for hour in delivery_hours:
                peak_hours[hour] = peak_hours.get(hour, 0) + 1
            
            busiest_hour = max(peak_hours.items(), key=lambda x: x[1])[0] if peak_hours else 12
            
            delivery_areas = defaultdict(int)
            for delivery in deliveries:
                area = f"{delivery.delivery_latitude:.2f},{delivery.delivery_longitude:.2f}"
                delivery_areas[area] += 1
            
            insights = []
            recommendations = []
            
            insights.append(f"💰 إجمالي الأرباح: {total_earnings:.0f} أوقية في آخر 30 يوم")
            insights.append(f"📊 متوسط الربح للتوصيل: {avg_earnings_per_delivery:.0f} أوقية")
            insights.append(f"🚚 عدد التوصيلات: {len(deliveries)} توصيل")
            insights.append(f"🕐 ساعة الذروة: {busiest_hour}:00")
            
            # توصيات ذكية
            if len(deliveries) < 30:
                recommendations.append("📈 اقبل المزيد من الطلبات لزيادة دخلك")
                recommendations.append("⏰ كن متاحاً في أوقات الذروة (12-14 و 19-21)")
            
            if avg_earnings_per_delivery < 50:
                recommendations.append("🎯 ركز على الطلبات ذات القيمة العالية")
                recommendations.append("📍 اختر المناطق القريبة لتوفير الوقت والوقود")
            
            current_hour = datetime.now().hour
            if 11 <= current_hour <= 14:
                recommendations.append("🍽️ وقت ذروة الغداء - فرصة ذهبية للتوصيلات!")
            elif 18 <= current_hour <= 21:
                recommendations.append("🌙 وقت ذروة العشاء - استعد لطلبات كثيرة!")
            elif 22 <= current_hour or current_hour <= 6:
                recommendations.append("😴 وقت راحة - استعد لليوم التالي")
            
            return {
                "insights": insights,
                "recommendations": recommendations,
                "performance_metrics": {
                    "total_earnings": total_earnings,
                    "delivery_count": len(deliveries),
                    "avg_earnings_per_delivery": avg_earnings_per_delivery,
                    "busiest_hour": busiest_hour
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_smart_recommendations(self, user_type, user_id, context=None):
        """الحصول على توصيات ذكية باستخدام OpenAI"""
        try:
            client = self._get_openai_client()

            if user_type == "customer":
                data = self.get_customer_insights(user_id)
            elif user_type == "restaurant":
                restaurant = Restaurant.query.filter_by(user_id=user_id).first()
                if restaurant:
                    data = self.get_restaurant_insights(restaurant.restaurant_id)
                else:
                    return {"recommendations": ["قم بإنشاء مطعمك أولاً"]}
            elif user_type == "delivery_agent":
                data = self.get_delivery_agent_insights(user_id)
            else:
                return {"recommendations": ["نوع مستخدم غير مدعوم"]}
            
            if "error" in data:
                return {"recommendations": [data["error"]]}
            
            prompt = f"""
            أنت مساعد ذكي لتطبيق توصيل الطعام "شهية" في موريتانيا.
            نوع المستخدم: {user_type}
            البيانات: {json.dumps(data, ensure_ascii=False)}
            السياق الإضافي: {context or "لا يوجد"}
            
            قدم 3-5 توصيات ذكية ومفيدة باللغة العربية مع استخدام الرموز التعبيرية المناسبة.
            ركز على تحسين الأداء وزيادة الأرباح والرضا.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "أنت مساعد ذكي متخصص في تطبيقات توصيل الطعام"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_recommendations = response.choices[0].message.content.strip().split("\n")
            ai_recommendations = [rec.strip() for rec in ai_recommendations if rec.strip()]
            
            all_recommendations = data.get("recommendations", []) + ai_recommendations
            
            return {
                "insights": data.get("insights", []),
                "recommendations": all_recommendations[:8],  # أقصى 8 توصيات
                "performance_metrics": data.get("performance_metrics", {})
            }
            
        except Exception as e:
            if user_type == "customer":
                return self.get_customer_insights(user_id)
            elif user_type == "restaurant":
                restaurant = Restaurant.query.filter_by(user_id=user_id).first()
                if restaurant:
                    return self.get_restaurant_insights(restaurant.restaurant_id)
            elif user_type == "delivery_agent":
                return self.get_delivery_agent_insights(user_id)
            
            return {"recommendations": [f"خطأ في النظام: {str(e)}"]}

# إنشاء مثيل من المساعد الذكي
ai_assistant = AIAssistant()

@ai_assistant_bp.route("/ai/insights", methods=["GET"])
@token_required
def get_ai_insights(current_user):
    """الحصول على رؤى وتوصيات ذكية للمستخدم"""
    try:
        context = request.args.get("context")
        insights_data = ai_assistant.get_smart_recommendations(
            current_user.user_type, 
            current_user.user_id, 
            context
        )
        
        return jsonify({
            "user_type": current_user.user_type,
            "timestamp": datetime.utcnow().isoformat(),
            **insights_data
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Failed to get AI insights: {str(e)}"}), 500

@ai_assistant_bp.route("/ai/chat", methods=["POST"])
@token_required
def ai_chat(current_user):
    """محادثة مع المساعد الذكي"""
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        
        if not user_message:
            return jsonify({"message": "الرسالة لا يمكن أن تكون فارغة"}), 400
        
        client = ai_assistant._get_openai_client()

        prompt = f"""
        أنت مساعد ذكي لتطبيق توصيل الطعام "شهية" في موريتانيا.
        أنت تتحدث مع مستخدم من نوع {current_user.user_type} (الاسم: {current_user.name}).
        الرسالة من المستخدم: {user_message}
        
        أجب على الرسالة بأسلوب ودود ومفيد باللغة العربية، مع استخدام الرموز التعبيرية المناسبة.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت مساعد ذكي متخصص في تطبيقات توصيل الطعام"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        ai_response_content = response.choices[0].message.content.strip()
        
        return jsonify({"response": ai_response_content}), 200
        
    except Exception as e:
        return jsonify({"message": f"Failed to chat with AI: {str(e)}"}), 500



