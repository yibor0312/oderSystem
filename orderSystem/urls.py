
from django.contrib import admin # 這是 Django 內建的後台管理
from django.urls import path
from myapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 1. 系統管理後台 (給老闆用)
    path('admin/', admin.site.urls), 

    # 2. 會員相關 (給客戶用)
    path('login/', views.login, name='login'),#登入頁面
    path('password_forget/', views.password_forget, name='password_forget'),#忘記密碼頁面
    path('password_change/', views.password_change_view, name='password_change_view'),#修改密碼頁面
    path('password_reset/', views.password_reset, name='password_reset'),#重置密碼頁面
    path('register/', views.register, name='register'),#註冊會員
    path('logout/', views.logout, name='logout'),#登出會員
    path('member/', views.member_center, name='member_center'), # 個人中心首頁
    path('customer/edit/', views.customer_edit, name='customer_edit'),#會員資料修改
    path('password/update/', views.password_update, name='password_update'),#密碼修改
    path('orders/history/', views.order_history, name='order_history'),#訂單歷史紀錄
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),#訂單詳細內容

    # 3. 點餐功能
    path('menu/', views.food_list, name='menu'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),    # 加入購物車
    path('update_cart/', views.update_cart, name='update_cart'),      # 更新購物車
    path('cart/', views.cart_detail, name='cart_detail'),          # 查看頁面
    path('create_order/', views.create_order, name='create_order'),# 下單
    path('kitchen/', views.kitchen_dashboard, name='kitchen_dashboard'),#廚房看板
    path('kitchen/complete/<int:order_id>/', views.complete_order, name='complete_order'),#廚房完成訂單
    path('checkout-all/', views.checkout_all_orders, name='checkout_all_orders'),#結帳所有訂單
    path('bill/', views.bill_detail, name='bill_detail'),  # 顯示當前帳單
    path('checkout_confirm/', views.checkout_confirm, name='checkout_confirm'),#結帳確認
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)