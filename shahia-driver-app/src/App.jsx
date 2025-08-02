import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar.jsx'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx'
import { 
  Truck, 
  MapPin, 
  Clock, 
  DollarSign,
  Phone,
  Navigation,
  CheckCircle,
  Package,
  Star,
  TrendingUp,
  Bot,
  MessageCircle,
  Bell,
  User,
  Home,
  List,
  Wallet,
  Settings,
  Play,
  Pause,
  AlertCircle,
  Route
} from 'lucide-react'
import './App.css'

const API_BASE = 'https://g8h3ilcvjzd3.manus.space/api'

function App() {
  const [user, setUser] = useState(null)
  const [currentPage, setCurrentPage] = useState('home')
  const [availableOrders, setAvailableOrders] = useState([])
  const [myOrders, setMyOrders] = useState([])
  const [isOnline, setIsOnline] = useState(false)
  const [currentLocation, setCurrentLocation] = useState(null)
  const [aiInsights, setAiInsights] = useState(null)
  const [showAiChat, setShowAiChat] = useState(false)
  const [chatMessages, setChatMessages] = useState([])
  const [stats, setStats] = useState({})

  // تحميل البيانات الأولية
  useEffect(() => {
    // محاكاة تسجيل دخول المندوب
    const mockUser = {
      user_id: 'driver_1',
      name: 'عبد الرحمن أحمد',
      email: 'driver@shahia.mr',
      phone_number: '+22200000006',
      user_type: 'driver',
      vehicle_type: 'motorcycle',
      license_plate: 'NKC-123',
      rating: 4.9,
      total_deliveries: 245
    }
    setUser(mockUser)
    
    loadAvailableOrders()
    loadMyOrders()
    loadAiInsights()
    loadStats()
    
    // محاولة الحصول على الموقع
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setCurrentLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          })
        },
        (error) => {
          console.log('خطأ في الحصول على الموقع:', error)
          // استخدام موقع افتراضي (نواكشوط)
          setCurrentLocation({
            latitude: 18.0735,
            longitude: -15.9582
          })
        }
      )
    }
  }, [])

  const loadAvailableOrders = () => {
    // محاكاة الطلبات المتاحة للاستلام
    const mockOrders = [
      {
        order_id: 'order_3',
        restaurant_name: 'مطعم الأصالة',
        restaurant_address: 'شارع جمال عبد الناصر، نواكشوط',
        customer_name: 'عبد الله حسن',
        customer_phone: '+22200000005',
        delivery_address: 'حي السبخة، نواكشوط',
        total_amount: 800,
        delivery_fee: 50,
        distance: 3.2,
        estimated_time: 25,
        order_status: 'ready',
        created_at: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
        items: [
          { product_name: 'لحم مشوي مع الأرز', quantity: 1 },
          { product_name: 'دجاج مقلي', quantity: 1 }
        ]
      },
      {
        order_id: 'order_4',
        restaurant_name: 'مطعم البحر',
        restaurant_address: 'ميناء نواكشوط',
        customer_name: 'مريم محمد',
        customer_phone: '+22200000007',
        delivery_address: 'حي تفرغ زينة، نواكشوط',
        total_amount: 500,
        delivery_fee: 75,
        distance: 4.8,
        estimated_time: 35,
        order_status: 'ready',
        created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        items: [
          { product_name: 'سمك مشوي', quantity: 1 }
        ]
      }
    ]
    setAvailableOrders(mockOrders)
  }

  const loadMyOrders = () => {
    // محاكاة طلبات المندوب الحالية
    const mockMyOrders = [
      {
        order_id: 'order_5',
        restaurant_name: 'مطعم الأصالة',
        restaurant_address: 'شارع جمال عبد الناصر، نواكشوط',
        customer_name: 'خديجة علي',
        customer_phone: '+22200000008',
        delivery_address: 'حي النصر، نواكشوط',
        total_amount: 650,
        delivery_fee: 50,
        distance: 2.1,
        order_status: 'picked_up',
        pickup_time: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
        verification_code: '1234',
        items: [
          { product_name: 'لحم مشوي مع الأرز', quantity: 1 },
          { product_name: 'عصير طبيعي', quantity: 2 }
        ]
      }
    ]
    setMyOrders(mockMyOrders)
  }

  const loadAiInsights = () => {
    // محاكاة رؤى المساعد الذكي للمندوبين
    const mockInsights = {
      insights: [
        'أرباحك اليوم: 450 أوقية من 9 توصيلات',
        'متوسط وقت التوصيل: 22 دقيقة',
        'تقييمك: 4.9/5 نجوم',
        'المنطقة الأكثر ربحية: حي النصر'
      ],
      recommendations: [
        '🚀 ساعة الذروة قادمة! استعد لطلبات أكثر',
        '💰 توجه لحي النصر - طلبات عالية القيمة',
        '⚡ قلل أوقات الانتظار لزيادة التقييم',
        '🎯 اقبل الطلبات القريبة لتوفير الوقود',
        '📈 هدفك اليوم: 15 توصيلة لمكافأة إضافية'
      ]
    }
    setAiInsights(mockInsights)
  }

  const loadStats = () => {
    // محاكاة إحصائيات المندوب
    const mockStats = {
      todayDeliveries: 9,
      todayEarnings: 450,
      weeklyEarnings: 2800,
      monthlyEarnings: 12500,
      averageRating: 4.9,
      completionRate: 98
    }
    setStats(mockStats)
  }

  const acceptOrder = (orderId) => {
    const order = availableOrders.find(o => o.order_id === orderId)
    if (order) {
      setMyOrders([...myOrders, { ...order, order_status: 'accepted' }])
      setAvailableOrders(availableOrders.filter(o => o.order_id !== orderId))
    }
  }

  const updateOrderStatus = (orderId, newStatus) => {
    setMyOrders(myOrders.map(order => 
      order.order_id === orderId 
        ? { ...order, order_status: newStatus }
        : order
    ))
  }

  const sendAiMessage = async (message) => {
    const newMessage = { type: 'user', content: message, timestamp: new Date() }
    setChatMessages(prev => [...prev, newMessage])

    setTimeout(() => {
      const aiResponse = {
        type: 'ai',
        content: getAiResponse(message),
        timestamp: new Date()
      }
      setChatMessages(prev => [...prev, aiResponse])
    }, 1000)
  }

  const getAiResponse = (message) => {
    const responses = [
      'مرحباً! كيف يمكنني مساعدتك في تحسين أرباحك اليوم؟ 🚗',
      'بناءً على تحليل حركة الطلبات، أنصحك بالتوجه لحي النصر الآن 📍',
      'لديك فرصة لزيادة أرباحك بـ 200 أوقية إضافية اليوم! 💰',
      'تذكر: العملاء يقدرون السرعة والأدب في التعامل ⭐',
      'نصيحة: تجنب ساعات الذروة المرورية لتوفير الوقت ⏰'
    ]
    return responses[Math.floor(Math.random() * responses.length)]
  }

  // مكونات الواجهة
  const Header = () => (
    <div className="bg-white shadow-sm border-b sticky top-0 z-50">
      <div className="max-w-md mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3 space-x-reverse">
            <Avatar>
              <AvatarFallback className="bg-blue-500 text-white">
                {user?.name?.charAt(0)}
              </AvatarFallback>
            </Avatar>
            <div>
              <h2 className="font-semibold text-gray-900">{user?.name}</h2>
              <p className="text-sm text-gray-500 flex items-center">
                <Truck className="w-3 h-3 ml-1" />
                {user?.vehicle_type === 'motorcycle' ? 'دراجة نارية' : 'سيارة'} - {user?.license_plate}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2 space-x-reverse">
            <Button
              variant={isOnline ? "default" : "outline"}
              size="sm"
              onClick={() => setIsOnline(!isOnline)}
              className={isOnline ? "bg-green-500 hover:bg-green-600" : ""}
            >
              {isOnline ? <Play className="w-4 h-4 ml-1" /> : <Pause className="w-4 h-4 ml-1" />}
              {isOnline ? 'متصل' : 'غير متصل'}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAiChat(true)}
              className="relative"
            >
              <Bot className="w-5 h-5 text-blue-500" />
              <Badge className="absolute -top-1 -right-1 w-2 h-2 p-0 bg-green-500"></Badge>
            </Button>
          </div>
        </div>
      </div>
    </div>
  )

  const StatsCards = () => (
    <div className="max-w-md mx-auto px-4 mb-4">
      <div className="grid grid-cols-2 gap-3">
        <Card>
          <CardContent className="p-3">
            <div className="text-center">
              <p className="text-sm text-gray-600">توصيلات اليوم</p>
              <p className="text-xl font-bold text-blue-600">{stats.todayDeliveries}</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-3">
            <div className="text-center">
              <p className="text-sm text-gray-600">أرباح اليوم</p>
              <p className="text-xl font-bold text-green-600">{stats.todayEarnings}</p>
              <p className="text-xs text-gray-500">أوقية</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-3">
            <div className="text-center">
              <p className="text-sm text-gray-600">التقييم</p>
              <p className="text-xl font-bold text-yellow-600">{stats.averageRating}</p>
              <div className="flex justify-center">
                <Star className="w-4 h-4 text-yellow-400 fill-current" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-3">
            <div className="text-center">
              <p className="text-sm text-gray-600">معدل الإنجاز</p>
              <p className="text-xl font-bold text-purple-600">{stats.completionRate}%</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  const AiInsightsCard = () => (
    aiInsights && (
      <div className="max-w-md mx-auto px-4 mb-4">
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg flex items-center">
                <Bot className="w-5 h-5 ml-2 text-blue-500" />
                مساعدك الذكي
              </CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAiChat(true)}
              >
                <MessageCircle className="w-4 h-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {aiInsights.recommendations.slice(0, 2).map((rec, index) => (
                <p key={index} className="text-sm text-gray-700 bg-white/50 p-2 rounded">
                  {rec}
                </p>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    )
  )

  const AvailableOrderCard = ({ order }) => (
    <Card className="mb-3">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h3 className="font-semibold text-lg">{order.restaurant_name}</h3>
            <p className="text-sm text-gray-600 flex items-center">
              <MapPin className="w-3 h-3 ml-1" />
              {order.restaurant_address}
            </p>
            <p className="text-sm text-gray-600">إلى: {order.delivery_address}</p>
          </div>
          <div className="text-left">
            <p className="text-lg font-bold text-green-600">{order.delivery_fee} أوقية</p>
            <Badge variant="secondary">{order.distance} كم</Badge>
          </div>
        </div>
        
        <div className="flex items-center justify-between mb-3 text-sm text-gray-500">
          <div className="flex items-center">
            <Clock className="w-4 h-4 ml-1" />
            {order.estimated_time} دقيقة
          </div>
          <div className="flex items-center">
            <Package className="w-4 h-4 ml-1" />
            {order.items.length} عنصر
          </div>
          <div className="flex items-center">
            <DollarSign className="w-4 h-4 ml-1" />
            {order.total_amount} أوقية
          </div>
        </div>
        
        <div className="flex space-x-2 space-x-reverse">
          <Button 
            className="flex-1"
            onClick={() => acceptOrder(order.order_id)}
            disabled={!isOnline}
          >
            <CheckCircle className="w-4 h-4 ml-1" />
            قبول الطلب
          </Button>
          <Button variant="outline" size="sm">
            <Navigation className="w-4 h-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )

  const MyOrderCard = ({ order }) => (
    <Card className="mb-3">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h3 className="font-semibold">طلب #{order.order_id}</h3>
            <p className="text-sm text-gray-600">{order.customer_name}</p>
            <p className="text-sm text-gray-500 flex items-center">
              <Phone className="w-3 h-3 ml-1" />
              {order.customer_phone}
            </p>
            <p className="text-sm text-gray-500 flex items-center">
              <MapPin className="w-3 h-3 ml-1" />
              {order.delivery_address}
            </p>
          </div>
          <div className="text-left">
            <p className="text-lg font-bold text-green-600">{order.delivery_fee} أوقية</p>
            <Badge 
              variant={
                order.order_status === 'accepted' ? 'default' :
                order.order_status === 'picked_up' ? 'secondary' :
                order.order_status === 'delivered' ? 'outline' : 'destructive'
              }
            >
              {order.order_status === 'accepted' && 'مقبول'}
              {order.order_status === 'picked_up' && 'تم الاستلام'}
              {order.order_status === 'delivered' && 'تم التوصيل'}
            </Badge>
          </div>
        </div>
        
        {order.verification_code && (
          <div className="bg-yellow-50 border border-yellow-200 rounded p-2 mb-3">
            <p className="text-sm font-medium text-yellow-800">
              كود التحقق: <span className="font-bold text-lg">{order.verification_code}</span>
            </p>
          </div>
        )}
        
        <div className="flex space-x-2 space-x-reverse">
          {order.order_status === 'accepted' && (
            <Button 
              className="flex-1"
              onClick={() => updateOrderStatus(order.order_id, 'picked_up')}
            >
              <Package className="w-4 h-4 ml-1" />
              تم الاستلام
            </Button>
          )}
          {order.order_status === 'picked_up' && (
            <Button 
              className="flex-1"
              onClick={() => updateOrderStatus(order.order_id, 'delivered')}
            >
              <CheckCircle className="w-4 h-4 ml-1" />
              تم التوصيل
            </Button>
          )}
          <Button variant="outline" size="sm">
            <Phone className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="sm">
            <Navigation className="w-4 h-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )

  const AiChatDialog = () => (
    <Dialog open={showAiChat} onOpenChange={setShowAiChat}>
      <DialogContent className="max-w-md mx-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <Bot className="w-5 h-5 ml-2 text-blue-500" />
            مساعدك الذكي للتوصيل
          </DialogTitle>
          <DialogDescription>
            احصل على نصائح لزيادة أرباحك وتحسين أدائك
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="h-64 overflow-y-auto space-y-2 p-2 bg-gray-50 rounded">
            {chatMessages.length === 0 && (
              <div className="text-center text-gray-500 py-8">
                <Bot className="w-12 h-12 mx-auto mb-2 text-blue-500" />
                <p>مرحباً! كيف يمكنني مساعدتك في تحسين أرباحك؟</p>
              </div>
            )}
            {chatMessages.map((message, index) => (
              <div
                key={index}
                className={`p-2 rounded max-w-xs ${
                  message.type === 'user'
                    ? 'bg-blue-500 text-white mr-auto'
                    : 'bg-white text-gray-800 ml-auto'
                }`}
              >
                {message.content}
              </div>
            ))}
          </div>
          
          <div className="flex space-x-2 space-x-reverse">
            <Input
              placeholder="اكتب رسالتك..."
              onKeyPress={(e) => {
                if (e.key === 'Enter' && e.target.value.trim()) {
                  sendAiMessage(e.target.value)
                  e.target.value = ''
                }
              }}
              className="text-right"
            />
            <Button
              onClick={() => {
                const input = document.querySelector('input[placeholder="اكتب رسالتك..."]')
                if (input.value.trim()) {
                  sendAiMessage(input.value)
                  input.value = ''
                }
              }}
            >
              إرسال
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )

  const BottomNavigation = () => (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg">
      <div className="max-w-md mx-auto px-4 py-2">
        <div className="flex justify-around">
          <Button
            variant={currentPage === 'home' ? 'default' : 'ghost'}
            className="flex-1 flex flex-col items-center py-2"
            onClick={() => setCurrentPage('home')}
          >
            <Home className="w-5 h-5" />
            <span className="text-xs mt-1">الرئيسية</span>
          </Button>
          <Button
            variant={currentPage === 'available' ? 'default' : 'ghost'}
            className="flex-1 flex flex-col items-center py-2"
            onClick={() => setCurrentPage('available')}
          >
            <List className="w-5 h-5" />
            <span className="text-xs mt-1">الطلبات المتاحة</span>
            {availableOrders.length > 0 && (
              <Badge className="absolute -top-1 -right-1 w-5 h-5 text-xs">
                {availableOrders.length}
              </Badge>
            )}
          </Button>
          <Button
            variant={currentPage === 'my-orders' ? 'default' : 'ghost'}
            className="flex-1 flex flex-col items-center py-2"
            onClick={() => setCurrentPage('my-orders')}
          >
            <Truck className="w-5 h-5" />
            <span className="text-xs mt-1">طلباتي</span>
            {myOrders.length > 0 && (
              <Badge className="absolute -top-1 -right-1 w-5 h-5 text-xs">
                {myOrders.length}
              </Badge>
            )}
          </Button>
          <Button
            variant={currentPage === 'earnings' ? 'default' : 'ghost'}
            className="flex-1 flex flex-col items-center py-2"
            onClick={() => setCurrentPage('earnings')}
          >
            <Wallet className="w-5 h-5" />
            <span className="text-xs mt-1">الأرباح</span>
          </Button>
          <Button
            variant={currentPage === 'profile' ? 'default' : 'ghost'}
            className="flex-1 flex flex-col items-center py-2"
            onClick={() => setCurrentPage('profile')}
          >
            <User className="w-5 h-5" />
            <span className="text-xs mt-1">حسابي</span>
          </Button>
        </div>
      </div>
    </div>
  )

  const renderPage = () => {
    if (currentPage === 'home') {
      return (
        <div className="pb-20">
          <Header />
          <StatsCards />
          <AiInsightsCard />
          
          {!isOnline && (
            <div className="max-w-md mx-auto px-4 mb-4">
              <Card className="border-orange-200 bg-orange-50">
                <CardContent className="p-4">
                  <div className="flex items-center">
                    <AlertCircle className="w-5 h-5 text-orange-500 ml-2" />
                    <p className="text-orange-700">اضغط على "متصل" لبدء استقبال الطلبات</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
          
          <div className="max-w-md mx-auto px-4">
            <h2 className="text-xl font-bold mb-4">آخر الطلبات</h2>
            {myOrders.slice(0, 2).map(order => (
              <MyOrderCard key={order.order_id} order={order} />
            ))}
            {availableOrders.slice(0, 1).map(order => (
              <AvailableOrderCard key={order.order_id} order={order} />
            ))}
          </div>
        </div>
      )
    }

    if (currentPage === 'available') {
      return (
        <div className="pb-20">
          <Header />
          <div className="max-w-md mx-auto px-4">
            <h2 className="text-xl font-bold mb-4">الطلبات المتاحة</h2>
            {!isOnline ? (
              <div className="text-center py-12">
                <Pause className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">اضغط على "متصل" لرؤية الطلبات المتاحة</p>
              </div>
            ) : availableOrders.length === 0 ? (
              <div className="text-center py-12">
                <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">لا توجد طلبات متاحة حالياً</p>
              </div>
            ) : (
              availableOrders.map(order => (
                <AvailableOrderCard key={order.order_id} order={order} />
              ))
            )}
          </div>
        </div>
      )
    }

    if (currentPage === 'my-orders') {
      return (
        <div className="pb-20">
          <Header />
          <div className="max-w-md mx-auto px-4">
            <h2 className="text-xl font-bold mb-4">طلباتي الحالية</h2>
            {myOrders.length === 0 ? (
              <div className="text-center py-12">
                <Truck className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">لا توجد طلبات حالياً</p>
              </div>
            ) : (
              myOrders.map(order => (
                <MyOrderCard key={order.order_id} order={order} />
              ))
            )}
          </div>
        </div>
      )
    }

    if (currentPage === 'earnings') {
      return (
        <div className="pb-20">
          <Header />
          <div className="max-w-md mx-auto px-4">
            <h2 className="text-xl font-bold mb-4">الأرباح والإحصائيات</h2>
            
            <div className="space-y-4">
              <Card>
                <CardContent className="p-4">
                  <h3 className="font-semibold mb-3">ملخص الأرباح</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>اليوم:</span>
                      <span className="font-bold text-green-600">{stats.todayEarnings} أوقية</span>
                    </div>
                    <div className="flex justify-between">
                      <span>هذا الأسبوع:</span>
                      <span className="font-bold">{stats.weeklyEarnings} أوقية</span>
                    </div>
                    <div className="flex justify-between">
                      <span>هذا الشهر:</span>
                      <span className="font-bold">{stats.monthlyEarnings} أوقية</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <h3 className="font-semibold mb-3">إحصائيات الأداء</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>إجمالي التوصيلات:</span>
                      <span className="font-bold">{user?.total_deliveries}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>التقييم:</span>
                      <span className="font-bold flex items-center">
                        {stats.averageRating}
                        <Star className="w-4 h-4 text-yellow-400 fill-current mr-1" />
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>معدل الإنجاز:</span>
                      <span className="font-bold">{stats.completionRate}%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      )
    }

    if (currentPage === 'profile') {
      return (
        <div className="pb-20">
          <Header />
          <div className="max-w-md mx-auto px-4">
            <h2 className="text-xl font-bold mb-4">حسابي</h2>
            <Card>
              <CardContent className="p-6">
                <div className="text-center mb-6">
                  <Avatar className="w-20 h-20 mx-auto mb-4">
                    <AvatarFallback className="bg-blue-500 text-white text-2xl">
                      {user?.name?.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  <h3 className="text-xl font-semibold">{user?.name}</h3>
                  <p className="text-gray-600">{user?.email}</p>
                  <div className="flex items-center justify-center mt-2">
                    <Star className="w-4 h-4 text-yellow-400 fill-current ml-1" />
                    <span className="font-bold">{user?.rating}</span>
                    <span className="text-gray-500 mr-2">({user?.total_deliveries} توصيلة)</span>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <span>رقم الهاتف</span>
                    <span>{user?.phone_number}</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <span>نوع المركبة</span>
                    <span>{user?.vehicle_type === 'motorcycle' ? 'دراجة نارية' : 'سيارة'}</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <span>رقم اللوحة</span>
                    <span>{user?.license_plate}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )
    }

    return <div>صفحة غير موجودة</div>
  }

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      {renderPage()}
      <BottomNavigation />
      <AiChatDialog />
    </div>
  )
}

export default App

