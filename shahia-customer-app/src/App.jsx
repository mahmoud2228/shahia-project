import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { 
  Search, 
  MapPin, 
  Star, 
  Clock, 
  ShoppingCart, 
  User, 
  Heart,
  Plus,
  Minus,
  MessageCircle,
  Bot,
  Truck,
  CreditCard,
  Phone,
  Home,
  Menu,
  Bell,
  Gift
} from 'lucide-react'
import './App.css'

// مكونات التطبيق
const API_BASE = 'https://shahia-project.onrender.com/api';


function App() {
  const [user, setUser] = useState(null)
  const [currentPage, setCurrentPage] = useState('home')
  const [restaurants, setRestaurants] = useState([])
  const [cart, setCart] = useState([])
  const [orders, setOrders] = useState([])
  const [aiInsights, setAiInsights] = useState(null)
  const [showAiChat, setShowAiChat] = useState(false)
  const [chatMessages, setChatMessages] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [userLocation, setUserLocation] = useState(null)

  // تحميل البيانات الأولية
  useEffect(() => {
    // محاكاة تسجيل دخول المستخدم
    const mockUser = {
      user_id: 'customer_1',
      name: 'أحمد محمد',
      email: 'ahmed@example.com',
      phone_number: '+22200000001',
      user_type: 'customer',
      address: 'حي النصر، نواكشوط'
    }
    setUser(mockUser)
    
    // تحميل المطاعم
    loadRestaurants()
    
    // تحميل رؤى المساعد الذكي
    loadAiInsights()
    
    // محاولة الحصول على الموقع
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          })
        },
        (error) => {
          console.log('خطأ في الحصول على الموقع:', error)
          // استخدام موقع افتراضي (نواكشوط)
          setUserLocation({
            latitude: 18.0735,
            longitude: -15.9582
          })
        }
      )
    }
  }, [])

  const loadRestaurants = async () => {
    // محاكاة بيانات المطاعم
    const mockRestaurants = [
      {
        restaurant_id: 'rest_1',
        name: 'مطعم الأصالة',
        description: 'أشهى الأطباق الموريتانية التقليدية',
        address: 'شارع جمال عبد الناصر، نواكشوط',
        rating: 4.8,
        delivery_fee: 50,
        min_order_value: 200,
        logo_url: '/api/placeholder/100/100',
        cover_image_url: '/api/placeholder/400/200',
        is_open: true,
        distance: 2.3,
        categories: [
          {
            category_id: 'cat_1',
            name: 'الأطباق الرئيسية',
            products: [
              {
                product_id: 'prod_1',
                name: 'لحم مشوي مع الأرز',
                description: 'لحم طازج مشوي مع أرز بسمتي وخضار',
                price: 450,
                image_url: '/api/placeholder/200/150',
                is_available: true
              },
              {
                product_id: 'prod_2',
                name: 'دجاج مقلي',
                description: 'دجاج مقرمش مع البطاطس المقلية',
                price: 350,
                image_url: '/api/placeholder/200/150',
                is_available: true
              }
            ]
          }
        ]
      },
      {
        restaurant_id: 'rest_2',
        name: 'مطعم البحر',
        description: 'أطباق السمك الطازج والمأكولات البحرية',
        address: 'ميناء نواكشوط',
        rating: 4.5,
        delivery_fee: 75,
        min_order_value: 300,
        logo_url: '/api/placeholder/100/100',
        cover_image_url: '/api/placeholder/400/200',
        is_open: true,
        distance: 3.7,
        categories: [
          {
            category_id: 'cat_2',
            name: 'المأكولات البحرية',
            products: [
              {
                product_id: 'prod_3',
                name: 'سمك مشوي',
                description: 'سمك طازج مشوي مع الخضار',
                price: 500,
                image_url: '/api/placeholder/200/150',
                is_available: true
              }
            ]
          }
        ]
      }
    ]
    setRestaurants(mockRestaurants)
  }

  const loadAiInsights = async () => {
    // محاكاة رؤى المساعد الذكي
    const mockInsights = {
      insights: [
        'لديك 12 طلب في آخر شهر بمتوسط 380 أوقية للطلب الواحد',
        'وقتك المفضل للطلب هو الساعة 19:00',
        'يومك المفضل للطلب هو الجمعة'
      ],
      recommendations: [
        '🍽️ مطعمك المفضل "الأصالة" لديه عروض جديدة!',
        '🌙 وقت العشاء! استمتع بوجبة مسائية لذيذة',
        '💡 جرب العروض المجمعة لتوفير أكثر على طلباتك',
        '⭐ لا تنس تقييم طلبك الأخير'
      ]
    }
    setAiInsights(mockInsights)
  }

  const addToCart = (product, restaurant) => {
    const existingItem = cart.find(item => item.product_id === product.product_id)
    if (existingItem) {
      setCart(cart.map(item => 
        item.product_id === product.product_id 
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ))
    } else {
      setCart([...cart, { 
        ...product, 
        quantity: 1, 
        restaurant_name: restaurant.name,
        restaurant_id: restaurant.restaurant_id 
      }])
    }
  }

  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.product_id !== productId))
  }

  const updateCartQuantity = (productId, newQuantity) => {
    if (newQuantity === 0) {
      removeFromCart(productId)
    } else {
      setCart(cart.map(item => 
        item.product_id === productId 
          ? { ...item, quantity: newQuantity }
          : item
      ))
    }
  }

  const getTotalPrice = () => {
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0)
  }

  const sendAiMessage = async (message) => {
    const newMessage = { type: 'user', content: message, timestamp: new Date() }
    setChatMessages(prev => [...prev, newMessage])

    // محاكاة رد المساعد الذكي
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
      'مرحباً! كيف يمكنني مساعدتك اليوم؟ 😊',
      'بناءً على تاريخ طلباتك، أنصحك بتجربة مطعم الأصالة - لديهم عروض رائعة اليوم! 🍽️',
      'يمكنني مساعدتك في العثور على أفضل المطاعم القريبة منك أو تتبع طلبك الحالي 📍',
      'هل تريد اقتراحات لوجبة عشاء لذيذة؟ لدي بعض التوصيات الرائعة! 🌙',
      'لاحظت أنك تحب الأطباق الموريتانية التقليدية، جرب الطبق الجديد في مطعم الأصالة! 🇲🇷'
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
              <AvatarFallback className="bg-orange-500 text-white">
                {user?.name?.charAt(0)}
              </AvatarFallback>
            </Avatar>
            <div>
              <h2 className="font-semibold text-gray-900">مرحباً {user?.name}</h2>
              <p className="text-sm text-gray-500 flex items-center">
                <MapPin className="w-3 h-3 ml-1" />
                {user?.address}
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
            </Button>
          </div>
        </div>
      </div>
    </div>
  )

  const SearchBar = () => (
    <div className="max-w-md mx-auto px-4 py-3">
      <div className="relative">
        <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
        <Input
          placeholder="ابحث عن مطعم أو طبق..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pr-10 text-right"
        />
      </div>
    </div>
  )

  const AiInsightsCard = () => (
    aiInsights && (
      <div className="max-w-md mx-auto px-4 mb-4">
        <Card className="bg-gradient-to-r from-orange-50 to-red-50 border-orange-200">
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

  const RestaurantCard = ({ restaurant }) => (
    <Card className="mb-4 cursor-pointer hover:shadow-md transition-shadow">
      <div className="relative">
        <img
          src={restaurant.cover_image_url}
          alt={restaurant.name}
          className="w-full h-32 object-cover rounded-t-lg"
        />
        <Badge className="absolute top-2 right-2 bg-green-500">
          {restaurant.is_open ? 'مفتوح' : 'مغلق'}
        </Badge>
      </div>
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <div className="flex-1">
            <h3 className="font-semibold text-lg">{restaurant.name}</h3>
            <p className="text-gray-600 text-sm mb-2">{restaurant.description}</p>
            <div className="flex items-center space-x-4 space-x-reverse text-sm text-gray-500">
              <div className="flex items-center">
                <Star className="w-4 h-4 text-yellow-400 ml-1" />
                {restaurant.rating}
              </div>
              <div className="flex items-center">
                <MapPin className="w-4 h-4 ml-1" />
                {restaurant.distance} كم
              </div>
              <div className="flex items-center">
                <Truck className="w-4 h-4 ml-1" />
                {restaurant.delivery_fee} أوقية
              </div>
            </div>
          </div>
          <Avatar className="w-12 h-12">
            <AvatarImage src={restaurant.logo_url} />
            <AvatarFallback>{restaurant.name.charAt(0)}</AvatarFallback>
          </Avatar>
        </div>
        <Button
          className="w-full"
          onClick={() => setCurrentPage(`restaurant-${restaurant.restaurant_id}`)}
        >
          عرض القائمة
        </Button>
      </CardContent>
    </Card>
  )

  const RestaurantMenu = ({ restaurant }) => (
    <div className="max-w-md mx-auto">
      <div className="relative mb-4">
        <img
          src={restaurant.cover_image_url}
          alt={restaurant.name}
          className="w-full h-48 object-cover"
        />
        <Button
          variant="ghost"
          className="absolute top-4 right-4 bg-white/80"
          onClick={() => setCurrentPage('home')}
        >
          ← العودة
        </Button>
      </div>
      
      <div className="px-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold">{restaurant.name}</h1>
            <p className="text-gray-600">{restaurant.description}</p>
            <div className="flex items-center space-x-4 space-x-reverse mt-2 text-sm">
              <div className="flex items-center">
                <Star className="w-4 h-4 text-yellow-400 ml-1" />
                {restaurant.rating}
              </div>
              <div className="flex items-center">
                <Clock className="w-4 h-4 ml-1" />
                30-45 دقيقة
              </div>
            </div>
          </div>
          <Avatar className="w-16 h-16">
            <AvatarImage src={restaurant.logo_url} />
            <AvatarFallback>{restaurant.name.charAt(0)}</AvatarFallback>
          </Avatar>
        </div>

        {restaurant.categories.map(category => (
          <div key={category.category_id} className="mb-6">
            <h2 className="text-xl font-semibold mb-3">{category.name}</h2>
            {category.products.map(product => (
              <Card key={product.product_id} className="mb-3">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold">{product.name}</h3>
                      <p className="text-gray-600 text-sm mb-2">{product.description}</p>
                      <p className="text-lg font-bold text-orange-600">{product.price} أوقية</p>
                    </div>
                    <div className="flex flex-col items-center space-y-2">
                      <img
                        src={product.image_url}
                        alt={product.name}
                        className="w-20 h-20 object-cover rounded-lg"
                      />
                      <Button
                        size="sm"
                        onClick={() => addToCart(product, restaurant)}
                        disabled={!product.is_available}
                      >
                        <Plus className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ))}
      </div>
    </div>
  )

  const CartPage = () => (
    <div className="max-w-md mx-auto px-4">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">سلة التسوق</h1>
        <Button variant="ghost" onClick={() => setCurrentPage('home')}>
          ← العودة
        </Button>
      </div>

      {cart.length === 0 ? (
        <div className="text-center py-12">
          <ShoppingCart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">سلة التسوق فارغة</p>
          <Button className="mt-4" onClick={() => setCurrentPage('home')}>
            تصفح المطاعم
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          {cart.map(item => (
            <Card key={item.product_id}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold">{item.name}</h3>
                    <p className="text-sm text-gray-600">{item.restaurant_name}</p>
                    <p className="text-orange-600 font-bold">{item.price} أوقية</p>
                  </div>
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => updateCartQuantity(item.product_id, item.quantity - 1)}
                    >
                      <Minus className="w-4 h-4" />
                    </Button>
                    <span className="w-8 text-center">{item.quantity}</span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => updateCartQuantity(item.product_id, item.quantity + 1)}
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}

          <Card className="bg-gray-50">
            <CardContent className="p-4">
              <div className="flex justify-between items-center mb-2">
                <span>المجموع الفرعي:</span>
                <span className="font-bold">{getTotalPrice()} أوقية</span>
              </div>
              <div className="flex justify-between items-center mb-2">
                <span>رسوم التوصيل:</span>
                <span>50 أوقية</span>
              </div>
              <hr className="my-2" />
              <div className="flex justify-between items-center text-lg font-bold">
                <span>المجموع الكلي:</span>
                <span className="text-orange-600">{getTotalPrice() + 50} أوقية</span>
              </div>
            </CardContent>
          </Card>

          <Button className="w-full" size="lg">
            <CreditCard className="w-5 h-5 ml-2" />
            إتمام الطلب
          </Button>
        </div>
      )}
    </div>
  )

  const AiChatDialog = () => (
    <Dialog open={showAiChat} onOpenChange={setShowAiChat}>
      <DialogContent className="max-w-md mx-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <Bot className="w-5 h-5 ml-2 text-orange-500" />
            مساعدك الذكي
          </DialogTitle>
          <DialogDescription>
            اسأل أي شيء عن المطاعم والطلبات
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="h-64 overflow-y-auto space-y-2 p-2 bg-gray-50 rounded">
            {chatMessages.length === 0 && (
              <div className="text-center text-gray-500 py-8">
                <Bot className="w-12 h-12 mx-auto mb-2 text-orange-500" />
                <p>مرحباً! كيف يمكنني مساعدتك اليوم؟</p>
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
            variant={currentPage === 'search' ? 'default' : 'ghost'}
            className="flex-1 flex flex-col items-center py-2"
            onClick={() => setCurrentPage('search')}
          >
            <Search className="w-5 h-5" />
            <span className="text-xs mt-1">البحث</span>
          </Button>
          <Button
            variant={currentPage === 'cart' ? 'default' : 'ghost'}
            className="flex-1 flex flex-col items-center py-2 relative"
            onClick={() => setCurrentPage('cart')}
          >
            <ShoppingCart className="w-5 h-5" />
            {cart.length > 0 && (
              <Badge className="absolute -top-1 -right-1 w-5 h-5 text-xs">
                {cart.length}
              </Badge>
            )}
            <span className="text-xs mt-1">السلة</span>
          </Button>
          <Button
            variant={currentPage === 'orders' ? 'default' : 'ghost'}
            className="flex-1 flex flex-col items-center py-2"
            onClick={() => setCurrentPage('orders')}
          >
            <Truck className="w-5 h-5" />
            <span className="text-xs mt-1">طلباتي</span>
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

  // عرض الصفحات
  const renderPage = () => {
    if (currentPage === 'home') {
      return (
        <div className="pb-20">
          <Header />
          <SearchBar />
          <AiInsightsCard />
          <div className="max-w-md mx-auto px-4">
            <h2 className="text-xl font-bold mb-4">المطاعم القريبة منك</h2>
            {restaurants.map(restaurant => (
              <RestaurantCard key={restaurant.restaurant_id} restaurant={restaurant} />
            ))}
          </div>
        </div>
      )
    }

    if (currentPage.startsWith('restaurant-')) {
      const restaurantId = currentPage.split('-')[1]
      const restaurant = restaurants.find(r => r.restaurant_id === restaurantId)
      return restaurant ? <RestaurantMenu restaurant={restaurant} /> : <div>مطعم غير موجود</div>
    }

    if (currentPage === 'cart') {
      return (
        <div className="pb-20">
          <CartPage />
        </div>
      )
    }

    if (currentPage === 'search') {
      return (
        <div className="pb-20">
          <Header />
          <SearchBar />
          <div className="max-w-md mx-auto px-4">
            <h2 className="text-xl font-bold mb-4">نتائج البحث</h2>
            {restaurants
              .filter(r => r.name.includes(searchQuery) || r.description.includes(searchQuery))
              .map(restaurant => (
                <RestaurantCard key={restaurant.restaurant_id} restaurant={restaurant} />
              ))}
          </div>
        </div>
      )
    }

    if (currentPage === 'orders') {
      return (
        <div className="pb-20">
          <Header />
          <div className="max-w-md mx-auto px-4">
            <h2 className="text-xl font-bold mb-4">طلباتي</h2>
            <div className="text-center py-12">
              <Truck className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">لا توجد طلبات حالياً</p>
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
                    <AvatarFallback className="bg-orange-500 text-white text-2xl">
                      {user?.name?.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  <h3 className="text-xl font-semibold">{user?.name}</h3>
                  <p className="text-gray-600">{user?.email}</p>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <span>رقم الهاتف</span>
                    <span>{user?.phone_number}</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <span>العنوان</span>
                    <span>{user?.address}</span>
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

