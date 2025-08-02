import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Switch } from '@/components/ui/switch.jsx'
import { 
  Store, 
  Package, 
  ShoppingBag, 
  TrendingUp, 
  Clock, 
  DollarSign,
  Users,
  Star,
  Plus,
  Edit,
  Eye,
  CheckCircle,
  XCircle,
  Truck,
  Bot,
  MessageCircle,
  Bell,
  Settings,
  BarChart3,
  Calendar,
  MapPin,
  Phone
} from 'lucide-react'
import './App.css'

const API_BASE = 'https://g8h3ilcvjzd3.manus.space/api'

function App() {
  const [user, setUser] = useState(null)
  const [restaurant, setRestaurant] = useState(null)
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [orders, setOrders] = useState([])
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [aiInsights, setAiInsights] = useState(null)
  const [showAiChat, setShowAiChat] = useState(false)
  const [chatMessages, setChatMessages] = useState([])
  const [stats, setStats] = useState({})

  // تحميل البيانات الأولية
  useEffect(() => {
    // محاكاة تسجيل دخول صاحب المطعم
    const mockUser = {
      user_id: 'restaurant_1',
      name: 'محمد الأمين',
      email: 'restaurant@shahia.mr',
      phone_number: '+22200000002',
      user_type: 'restaurant'
    }
    setUser(mockUser)
    
    // محاكاة بيانات المطعم
    const mockRestaurant = {
      restaurant_id: 'rest_1',
      name: 'مطعم الأصالة',
      description: 'أشهى الأطباق الموريتانية التقليدية',
      address: 'شارع جمال عبد الناصر، نواكشوط',
      phone_number: '+22200000003',
      email: 'info@asala-restaurant.mr',
      rating: 4.8,
      delivery_fee: 50,
      min_order_value: 200,
      is_open: true,
      opening_time: '08:00',
      closing_time: '23:00'
    }
    setRestaurant(mockRestaurant)
    
    loadOrders()
    loadProducts()
    loadAiInsights()
    loadStats()
  }, [])

  const loadOrders = () => {
    // محاكاة الطلبات
    const mockOrders = [
      {
        order_id: 'order_1',
        customer_name: 'أحمد محمد',
        customer_phone: '+22200000001',
        total_amount: 450,
        order_status: 'pending',
        created_at: new Date().toISOString(),
        delivery_address: 'حي النصر، نواكشوط',
        items: [
          { product_name: 'لحم مشوي مع الأرز', quantity: 1, price: 450 }
        ]
      },
      {
        order_id: 'order_2',
        customer_name: 'فاطمة علي',
        customer_phone: '+22200000004',
        total_amount: 350,
        order_status: 'preparing',
        created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        delivery_address: 'حي الرياض، نواكشوط',
        items: [
          { product_name: 'دجاج مقلي', quantity: 1, price: 350 }
        ]
      },
      {
        order_id: 'order_3',
        customer_name: 'عبد الله حسن',
        customer_phone: '+22200000005',
        total_amount: 800,
        order_status: 'ready',
        created_at: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
        delivery_address: 'حي السبخة، نواكشوط',
        items: [
          { product_name: 'لحم مشوي مع الأرز', quantity: 1, price: 450 },
          { product_name: 'دجاج مقلي', quantity: 1, price: 350 }
        ]
      }
    ]
    setOrders(mockOrders)
  }

  const loadProducts = () => {
    // محاكاة المنتجات والفئات
    const mockCategories = [
      {
        category_id: 'cat_1',
        name: 'الأطباق الرئيسية',
        products: [
          {
            product_id: 'prod_1',
            name: 'لحم مشوي مع الأرز',
            description: 'لحم طازج مشوي مع أرز بسمتي وخضار',
            price: 450,
            is_available: true,
            image_url: '/api/placeholder/200/150'
          },
          {
            product_id: 'prod_2',
            name: 'دجاج مقلي',
            description: 'دجاج مقرمش مع البطاطس المقلية',
            price: 350,
            is_available: true,
            image_url: '/api/placeholder/200/150'
          }
        ]
      },
      {
        category_id: 'cat_2',
        name: 'المشروبات',
        products: [
          {
            product_id: 'prod_3',
            name: 'عصير طبيعي',
            description: 'عصير فواكه طازج',
            price: 80,
            is_available: true,
            image_url: '/api/placeholder/200/150'
          }
        ]
      }
    ]
    setCategories(mockCategories)
    
    // استخراج جميع المنتجات
    const allProducts = mockCategories.flatMap(cat => cat.products)
    setProducts(allProducts)
  }

  const loadAiInsights = () => {
    // محاكاة رؤى المساعد الذكي للمطاعم
    const mockInsights = {
      insights: [
        'إجمالي المبيعات: 12,500 أوقية في آخر 30 يوم',
        'متوسط قيمة الطلب: 420 أوقية',
        'ساعة الذروة: 19:00',
        'عدد الطلبات: 30 طلب'
      ],
      recommendations: [
        '📈 اقترح منتجات إضافية لزيادة قيمة الطلب',
        '🎁 قدم عروض مجمعة جذابة',
        '⚡ راجع أوقات التحضير لتقليل الإلغاءات',
        '🍽️ قدم عروض غداء مميزة الآن',
        '📢 زد من التسويق لمطعمك'
      ]
    }
    setAiInsights(mockInsights)
  }

  const loadStats = () => {
    // محاكاة الإحصائيات
    const mockStats = {
      todayOrders: 8,
      todayRevenue: 3200,
      pendingOrders: 3,
      monthlyRevenue: 45000,
      averageRating: 4.8,
      totalCustomers: 156
    }
    setStats(mockStats)
  }

  const updateOrderStatus = (orderId, newStatus) => {
    setOrders(orders.map(order => 
      order.order_id === orderId 
        ? { ...order, order_status: newStatus }
        : order
    ))
  }

  const toggleProductAvailability = (productId) => {
    setProducts(products.map(product => 
      product.product_id === productId 
        ? { ...product, is_available: !product.is_available }
        : product
    ))
    
    // تحديث الفئات أيضاً
    setCategories(categories.map(category => ({
      ...category,
      products: category.products.map(product => 
        product.product_id === productId 
          ? { ...product, is_available: !product.is_available }
          : product
      )
    })))
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
      'مرحباً! كيف يمكنني مساعدتك في إدارة مطعمك؟ 🍽️',
      'بناءً على تحليل مبيعاتك، أنصحك بإضافة عروض مسائية لزيادة الطلبات 📈',
      'لاحظت زيادة في الطلبات مؤخراً، تأكد من توفر المكونات الأساسية 📦',
      'يمكنك تحسين أوقات التحضير لتقليل انتظار العملاء ⏰',
      'اقترح إضافة منتجات موسمية لجذب المزيد من العملاء 🌟'
    ]
    return responses[Math.floor(Math.random() * responses.length)]
  }

  // مكونات الواجهة
  const Header = () => (
    <div className="bg-white shadow-sm border-b sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3 space-x-reverse">
            <Avatar>
              <AvatarFallback className="bg-orange-500 text-white">
                {restaurant?.name?.charAt(0)}
              </AvatarFallback>
            </Avatar>
            <div>
              <h2 className="font-semibold text-gray-900">{restaurant?.name}</h2>
              <p className="text-sm text-gray-500 flex items-center">
                <Store className="w-3 h-3 ml-1" />
                لوحة تحكم المطعم
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2 space-x-reverse">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAiChat(true)}
              className="relative"
            >
              <Bot className="w-5 h-5 text-orange-500" />
              <Badge className="absolute -top-1 -right-1 w-2 h-2 p-0 bg-green-500"></Badge>
            </Button>
            <Button variant="ghost" size="sm">
              <Bell className="w-5 h-5" />
              {stats.pendingOrders > 0 && (
                <Badge className="absolute -top-1 -right-1 w-5 h-5 text-xs">
                  {stats.pendingOrders}
                </Badge>
              )}
            </Button>
            <Button variant="ghost" size="sm">
              <Settings className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )

  const StatsCards = () => (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">طلبات اليوم</p>
              <p className="text-2xl font-bold text-orange-600">{stats.todayOrders}</p>
            </div>
            <ShoppingBag className="w-8 h-8 text-orange-500" />
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">مبيعات اليوم</p>
              <p className="text-2xl font-bold text-green-600">{stats.todayRevenue}</p>
              <p className="text-xs text-gray-500">أوقية</p>
            </div>
            <DollarSign className="w-8 h-8 text-green-500" />
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">طلبات معلقة</p>
              <p className="text-2xl font-bold text-red-600">{stats.pendingOrders}</p>
            </div>
            <Clock className="w-8 h-8 text-red-500" />
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">التقييم</p>
              <p className="text-2xl font-bold text-yellow-600">{stats.averageRating}</p>
            </div>
            <Star className="w-8 h-8 text-yellow-500" />
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const AiInsightsCard = () => (
    aiInsights && (
      <Card className="mb-6 bg-gradient-to-r from-orange-50 to-red-50 border-orange-200">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg flex items-center">
              <Bot className="w-5 h-5 ml-2 text-orange-500" />
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
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-semibold mb-2">رؤى الأداء</h4>
              <div className="space-y-1">
                {aiInsights.insights.slice(0, 2).map((insight, index) => (
                  <p key={index} className="text-sm text-gray-700">• {insight}</p>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-2">توصيات ذكية</h4>
              <div className="space-y-1">
                {aiInsights.recommendations.slice(0, 2).map((rec, index) => (
                  <p key={index} className="text-sm text-gray-700">{rec}</p>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  )

  const OrdersTable = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <ShoppingBag className="w-5 h-5 ml-2" />
          الطلبات الحالية
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {orders.map(order => (
            <div key={order.order_id} className="border rounded-lg p-4">
              <div className="flex items-start justify-between mb-3">
                <div>
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
                  <p className="text-lg font-bold text-orange-600">{order.total_amount} أوقية</p>
                  <Badge 
                    variant={
                      order.order_status === 'pending' ? 'destructive' :
                      order.order_status === 'preparing' ? 'default' :
                      order.order_status === 'ready' ? 'secondary' : 'outline'
                    }
                  >
                    {order.order_status === 'pending' && 'جديد'}
                    {order.order_status === 'preparing' && 'قيد التحضير'}
                    {order.order_status === 'ready' && 'جاهز'}
                    {order.order_status === 'picked_up' && 'تم الاستلام'}
                    {order.order_status === 'delivered' && 'تم التوصيل'}
                  </Badge>
                </div>
              </div>
              
              <div className="mb-3">
                <h4 className="font-medium mb-1">العناصر:</h4>
                {order.items.map((item, index) => (
                  <p key={index} className="text-sm text-gray-600">
                    {item.quantity}x {item.product_name} - {item.price} أوقية
                  </p>
                ))}
              </div>
              
              <div className="flex space-x-2 space-x-reverse">
                {order.order_status === 'pending' && (
                  <>
                    <Button 
                      size="sm" 
                      onClick={() => updateOrderStatus(order.order_id, 'preparing')}
                    >
                      <CheckCircle className="w-4 h-4 ml-1" />
                      قبول
                    </Button>
                    <Button 
                      variant="destructive" 
                      size="sm"
                      onClick={() => updateOrderStatus(order.order_id, 'cancelled')}
                    >
                      <XCircle className="w-4 h-4 ml-1" />
                      رفض
                    </Button>
                  </>
                )}
                {order.order_status === 'preparing' && (
                  <Button 
                    size="sm" 
                    onClick={() => updateOrderStatus(order.order_id, 'ready')}
                  >
                    <CheckCircle className="w-4 h-4 ml-1" />
                    جاهز للتوصيل
                  </Button>
                )}
                {order.order_status === 'ready' && (
                  <Badge variant="secondary" className="flex items-center">
                    <Truck className="w-4 h-4 ml-1" />
                    في انتظار المندوب
                  </Badge>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )

  const ProductsManagement = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">إدارة المنتجات</h2>
        <Button>
          <Plus className="w-4 h-4 ml-1" />
          إضافة منتج جديد
        </Button>
      </div>
      
      {categories.map(category => (
        <Card key={category.category_id}>
          <CardHeader>
            <CardTitle>{category.name}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {category.products.map(product => (
                <Card key={product.product_id} className="relative">
                  <CardContent className="p-4">
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className="w-full h-32 object-cover rounded-lg mb-3"
                    />
                    <h3 className="font-semibold mb-1">{product.name}</h3>
                    <p className="text-sm text-gray-600 mb-2">{product.description}</p>
                    <p className="text-lg font-bold text-orange-600 mb-3">{product.price} أوقية</p>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2 space-x-reverse">
                        <Switch
                          checked={product.is_available}
                          onCheckedChange={() => toggleProductAvailability(product.product_id)}
                        />
                        <Label className="text-sm">
                          {product.is_available ? 'متوفر' : 'غير متوفر'}
                        </Label>
                      </div>
                      <Button variant="ghost" size="sm">
                        <Edit className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )

  const AiChatDialog = () => (
    <Dialog open={showAiChat} onOpenChange={setShowAiChat}>
      <DialogContent className="max-w-md mx-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <Bot className="w-5 h-5 ml-2 text-orange-500" />
            مساعدك الذكي للمطعم
          </DialogTitle>
          <DialogDescription>
            احصل على رؤى وتوصيات لتحسين أداء مطعمك
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="h-64 overflow-y-auto space-y-2 p-2 bg-gray-50 rounded">
            {chatMessages.length === 0 && (
              <div className="text-center text-gray-500 py-8">
                <Bot className="w-12 h-12 mx-auto mb-2 text-orange-500" />
                <p>مرحباً! كيف يمكنني مساعدتك في إدارة مطعمك؟</p>
              </div>
            )}
            {chatMessages.map((message, index) => (
              <div
                key={index}
                className={`p-2 rounded max-w-xs ${
                  message.type === 'user'
                    ? 'bg-orange-500 text-white mr-auto'
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

  const Sidebar = () => (
    <div className="w-64 bg-white shadow-lg h-screen fixed right-0 top-0 z-40">
      <div className="p-4 border-b">
        <h1 className="text-xl font-bold text-orange-600">شهية للمطاعم</h1>
      </div>
      <nav className="p-4">
        <div className="space-y-2">
          <Button
            variant={currentPage === 'dashboard' ? 'default' : 'ghost'}
            className="w-full justify-start"
            onClick={() => setCurrentPage('dashboard')}
          >
            <BarChart3 className="w-4 h-4 ml-2" />
            لوحة التحكم
          </Button>
          <Button
            variant={currentPage === 'orders' ? 'default' : 'ghost'}
            className="w-full justify-start"
            onClick={() => setCurrentPage('orders')}
          >
            <ShoppingBag className="w-4 h-4 ml-2" />
            الطلبات
            {stats.pendingOrders > 0 && (
              <Badge className="mr-auto">{stats.pendingOrders}</Badge>
            )}
          </Button>
          <Button
            variant={currentPage === 'products' ? 'default' : 'ghost'}
            className="w-full justify-start"
            onClick={() => setCurrentPage('products')}
          >
            <Package className="w-4 h-4 ml-2" />
            المنتجات
          </Button>
          <Button
            variant={currentPage === 'analytics' ? 'default' : 'ghost'}
            className="w-full justify-start"
            onClick={() => setCurrentPage('analytics')}
          >
            <TrendingUp className="w-4 h-4 ml-2" />
            التحليلات
          </Button>
          <Button
            variant={currentPage === 'settings' ? 'default' : 'ghost'}
            className="w-full justify-start"
            onClick={() => setCurrentPage('settings')}
          >
            <Settings className="w-4 h-4 ml-2" />
            الإعدادات
          </Button>
        </div>
      </nav>
    </div>
  )

  const renderPage = () => {
    if (currentPage === 'dashboard') {
      return (
        <div className="space-y-6">
          <StatsCards />
          <AiInsightsCard />
          <OrdersTable />
        </div>
      )
    }

    if (currentPage === 'orders') {
      return <OrdersTable />
    }

    if (currentPage === 'products') {
      return <ProductsManagement />
    }

    if (currentPage === 'analytics') {
      return (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="w-5 h-5 ml-2" />
              تحليلات المبيعات
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-12">
              <BarChart3 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">قريباً - تحليلات مفصلة للمبيعات والأداء</p>
            </div>
          </CardContent>
        </Card>
      )
    }

    if (currentPage === 'settings') {
      return (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Settings className="w-5 h-5 ml-2" />
              إعدادات المطعم
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <Label htmlFor="restaurant-name">اسم المطعم</Label>
                <Input id="restaurant-name" value={restaurant?.name} className="text-right" />
              </div>
              <div>
                <Label htmlFor="restaurant-desc">وصف المطعم</Label>
                <Textarea id="restaurant-desc" value={restaurant?.description} className="text-right" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="opening-time">وقت الفتح</Label>
                  <Input id="opening-time" type="time" value={restaurant?.opening_time} />
                </div>
                <div>
                  <Label htmlFor="closing-time">وقت الإغلاق</Label>
                  <Input id="closing-time" type="time" value={restaurant?.closing_time} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="delivery-fee">رسوم التوصيل</Label>
                  <Input id="delivery-fee" type="number" value={restaurant?.delivery_fee} />
                </div>
                <div>
                  <Label htmlFor="min-order">الحد الأدنى للطلب</Label>
                  <Input id="min-order" type="number" value={restaurant?.min_order_value} />
                </div>
              </div>
              <Button>حفظ التغييرات</Button>
            </div>
          </CardContent>
        </Card>
      )
    }

    return <div>صفحة غير موجودة</div>
  }

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      <Sidebar />
      <div className="mr-64">
        <Header />
        <main className="max-w-6xl mx-auto p-6">
          {renderPage()}
        </main>
      </div>
      <AiChatDialog />
    </div>
  )
}

export default App

