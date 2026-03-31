from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import Customer, Food, Category, Order, OrderItem, StockLog
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# --- 輔助函式：取得今日與本月已結帳總額 ---
def get_sales_context():
    now = timezone.now()
    today_sales = Order.objects.filter(
        oTime__date=now.date(), 
        oStatus='已結帳'
    ).aggregate(Sum('oTotal'))['oTotal__sum'] or 0
    
    month_sales = Order.objects.filter(
        oTime__year=now.year, 
        oTime__month=now.month, 
        oStatus='已結帳'
    ).aggregate(Sum('oTotal'))['oTotal__sum'] or 0
    
    return {
        'today_sales': today_sales,
        'month_sales': month_sales
    }

# 菜單首頁
def food_list(request):
    categories = Category.objects.prefetch_related('foods').all()
    user_id = request.session.get('user_id')
    
    show_checkout_btn = False
    if user_id:
        # 這裡的狀態必須「不包含」已結帳
        show_checkout_btn = Order.objects.filter(
            customer_id=user_id, 
            oStatus__in=['處理中', '已完成'] 
        ).exists()

    return render(request, 'food_list.html', {
        'categories': categories,
        'show_checkout_btn': show_checkout_btn,
    })

#結帳頁面
def bill_detail(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    # 在此頁面才計算訂單明細與總金額
    unpaid_orders = Order.objects.filter(
        customer_id=user_id, 
        oStatus__in=['處理中', '已完成']
    ).prefetch_related('items__food')
    
    current_bill = unpaid_orders.aggregate(Sum('oTotal'))['oTotal__sum'] or 0

    return render(request, 'bill.html', {
        'unpaid_orders': unpaid_orders,
        'current_bill': current_bill,
    })
#  忘記密碼
def password_forget(request):
    if request.method == 'POST':
        account = request.POST.get('account')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        try:
            # 必須精確縮排在 if 內
            # 根據你的 Model 欄位名稱 (cAccount, cEmail, cPhone) 進行比對
            user = Customer.objects.get(cAccount=account, cEmail=email, cPhone=phone)
            
            # 驗證成功：存入 session
            request.session['reset_user_id'] = user.cId 
            return redirect('password_change_view') 
            
        except Customer.DoesNotExist:
            messages.error(request, "驗證失敗：找不到符合的資料，請檢查輸入內容。")
        except Exception as e:
            messages.error(request, f"系統錯誤：{str(e)}")
            
    return render(request, 'password_forget.html')

# 2. 設定新密碼頁面
def password_change_view(request):
    # 安全檢查：若未經第一步驗證則踢回
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('password_forget')

    if request.method == 'POST':
        new_pwd = request.POST.get('new_password')
        confirm_pwd = request.POST.get('confirm_password')

        if new_pwd == confirm_pwd:
            user = Customer.objects.get(cId=user_id)
            user.cPassword = new_pwd
            user.save()
            
            # 清除 session 並跳轉登入頁
            del request.session['reset_user_id']
            messages.success(request, "密碼已重設，請使用新密碼登入。")
            return redirect('login')
        else:
            messages.error(request, "兩次輸入的新密碼不一致。")

    return render(request, 'password_change.html')

# 為了對應你 urls.py 裡的 password_reset，額外加一個指向
def password_reset(request):
    return redirect('password_forget')

# 登入
def login(request):
    if request.method == "POST":
        account = request.POST.get('account')
        password = request.POST.get('password')
        try:
            user = Customer.objects.get(cAccount=account)
            if user.cPassword == password:
                request.session['user_id'] = user.cId
                request.session['user_name'] = user.cName
                messages.success(request, f"歡迎回來，{user.cName}！")
                return redirect('menu')
            else:
                messages.error(request, "密碼錯誤")
        except Customer.DoesNotExist:
            messages.error(request, "帳號不存在")
    return render(request, 'login.html')

# 註冊
def register(request):
    if request.method == "POST":
        data = request.POST
        
        #取得所有欄位值並去除前後空白
        account = data.get('account', '').strip()
        password = data.get('password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        name = data.get('name', '').strip()
        gender = data.get('gender', '').strip()
        birthday = data.get('birthday', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()

        #檢查是否有任何必填欄位是空的 (這裡排除生日，因為生日通常允許 None)
        # 如果你連生日都必填，就把 birthday 加入判斷
        required_fields = [account, password, name, gender, email, phone]
        if not all(required_fields):
            messages.error(request, "所有欄位皆為必填，請勿留空！")
            return render(request, 'register.html', {'old_data': data})

        #檢查密碼是否一致
        if password != confirm_password:
            messages.error(request, "兩次輸入的密碼不一致")
            return render(request, 'register.html', {'old_data': data})
        
        try:
            # 檢查帳號是否已存在 (避免重複註冊)
            if Customer.objects.filter(cAccount=account).exists():
                messages.error(request, "此帳號已被註冊")
                return render(request, 'register.html', {'old_data': data})

            Customer.objects.create(
                cAccount=account,
                cPassword=password,
                cName=name,
                cSex=gender,
                cBirthday=birthday or None, # 如果是空字串就存 NULL
                cEmail=email,
                cPhone=phone
            )
            messages.success(request, "註冊成功，請登入")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"註冊失敗：{str(e)}")
            
    return render(request, 'register.html')

def logout(request):
    request.session.flush()
    return redirect('login')
# 個人中心首頁
def member_center(request):
    # 這裡通常需要檢查使用者是否已登入
    return render(request, 'member_center.html')

# 客戶資料修改
def customer_edit(request):
    # 1. 檢查 Session 是否有登入
    customer_id = request.session.get('user_id')
    if not customer_id:
        return redirect('login')

    # 2. 抓取該會員物件
    customer = Customer.objects.get(cId=customer_id)

    if request.method == "POST":
        # 3. 接收表單傳回的新資料
        customer.cName = request.POST.get('cName')
        customer.cEmail = request.POST.get('cEmail')
        customer.cPhone = request.POST.get('cPhone')
        customer.cBirthday = request.POST.get('cBirthday')
        # 如果你有隱藏的性別欄位或是其他邏輯也可以在這裡處理
        
        customer.save() # 儲存到資料庫
        
        # 4. 加上成功訊息並跳轉
        messages.success(request, '個人資料已成功更新！')
        return redirect('member_center')

    # 5. 將 customer 物件傳給 Template
    return render(request, 'customer_edit.html', {'customer': customer})
# 密碼修改
def password_update(request):
    customer_id = request.session.get('user_id')
    if not customer_id:
        return redirect('login')

    if request.method == "POST":
        old_pwd = request.POST.get('old_password')
        new_pwd = request.POST.get('new_password')
        confirm_pwd = request.POST.get('confirm_password')

        customer = Customer.objects.get(cId=customer_id)

        if customer.cPassword != old_pwd:
            return render(request, 'password_change.html', {'error': '舊密碼輸入錯誤'})

        if new_pwd != confirm_pwd:
            return render(request, 'password_change.html', {'error': '兩次新密碼不一致'})

        # 儲存新密碼
        customer.cPassword = new_pwd
        customer.save()
        
        # 2. 在跳轉前存入成功訊息
        messages.success(request, '密碼修改成功！請牢記您的新密碼。')
        
        return redirect('member_center') # 跳轉回會員中心

    return render(request, 'password_update.html')
# 訂單歷史紀錄
def order_history(request):
    customer_id = request.session.get('user_id')
    if not customer_id:
        return redirect('login')
    
    orders = Order.objects.filter(customer_id=customer_id).order_by('-oTime')
    return render(request, 'order_history.html', {'orders': orders})
# 訂單詳細內容
def order_detail(request, order_id):
    customer_id = request.session.get('user_id')
    if not customer_id:
        return redirect('login')

    # 確保該訂單真的屬於目前登入的客戶（安全檢查）
    order = get_object_or_404(Order, oID=order_id, customer_id=customer_id)
    
    # 抓取該訂單關聯的所有餐點項目
    items = OrderItem.objects.filter(order=order).prefetch_related('food')

    return render(request, 'order_detail.html', {
        'order': order,
        'items': items
    })
# 加入購物車
def add_to_cart(request):
    if request.method == "POST":
        food_id = request.POST.get('food_id')
        qty = int(request.POST.get('quantity', 1))
        food = get_object_or_404(Food, fID=food_id)

        if food.fStock < qty:
            messages.error(request, f"{food.fName} 庫存不足")
            return redirect('menu')

        cart = request.session.get('cart', {})
        cart[str(food_id)] = cart.get(str(food_id), 0) + qty
        request.session['cart'] = cart
        request.session.modified = True 
        messages.success(request, f"已加入 {food.fName}")
    return redirect('menu')
# 更新購物車
def update_cart(request):
    if request.method == "POST":
        food_id = request.POST.get('food_id')
        qty = int(request.POST.get('quantity', 1))
        
        # 獲取購物車
        cart = request.session.get('cart', {})
        
        if str(food_id) in cart:
            if qty > 0:
                # 檢查庫存 (可選，但建議做)
                food = get_object_or_404(Food, fID=food_id)
                if qty <= food.fStock:
                    cart[str(food_id)] = qty
                    messages.success(request, f"已更新 {food.fName} 的數量")
                else:
                    messages.error(request, f"{food.fName} 庫存不足，目前剩餘 {food.fStock}")
            else:
                # 如果數量設為 0，可以直接刪除該項目
                del cart[str(food_id)]
        
        request.session['cart'] = cart
        request.session.modified = True 
        
    return redirect('cart_detail') # 跳轉回購物車頁面

# 送出訂單 (點餐)
def create_order(request):
    user_id = request.session.get('user_id')
    cart = request.session.get('cart', {})
    
    if not user_id:
        messages.error(request, "請先登入")
        return redirect('login')
    if not cart:
        messages.error(request, "購物車是空的")
        return redirect('menu')

    try:
        with transaction.atomic():
            customer = Customer.objects.get(cId=user_id)
            new_order = Order.objects.create(customer=customer, oStatus='處理中', oTotal=0)
            total_amount = 0

            for food_id, quantity in cart.items():
                food = Food.objects.select_for_update().get(fID=food_id)
                if food.fStock < quantity:
                    raise Exception(f"{food.fName} 庫存不足")

                subtotal = food.fPrice * quantity
                total_amount += subtotal
                
                # 扣庫存
                food.fStock -= quantity
                food.save()

                # 庫存日誌 (SALE)
                StockLog.objects.create(
                    food=food, amount=-quantity, reason='SALE', 
                    note=f"訂單 #{new_order.oID} 自動扣除"
                )
                OrderItem.objects.create(order=new_order, food=food, quantity=quantity)

            new_order.oTotal = total_amount
            new_order.save()
            
            request.session['cart'] = {}
            request.session.modified = True 
            messages.success(request, "訂單已送往廚房！")
    except Exception as e:
        messages.error(request, f"下單失敗：{str(e)}")
    
    return redirect('menu')

# 最終確認買單 (正式計入銷售額)
def checkout_all_orders(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    if request.method == "POST":
        # 找出還在「處理中」或「已完成(出餐)」的訂單
        unpaid_orders = Order.objects.filter(
            customer_id=user_id, 
            oStatus__in=['處理中', '已完成']
        )
        
        if unpaid_orders.exists():
            # 【關鍵修改】改成一個代表「付完錢離開了」的狀態
            unpaid_orders.update(oStatus='已結帳') 
            messages.success(request, "訂單已完成，歡迎再次光臨！")
        
        return redirect('menu') 

    return redirect('menu')
# 結帳
def checkout_confirm(request):
    user_id = request.session.get('user_id')
    
    # 這裡的 filter 必須只包含「非最終狀態」的訂單
    unpaid_orders = Order.objects.filter(
        customer_id=user_id, 
        oStatus__in=['處理中', '已完成'] # 確保這裡「不包含」已結帳
    )
    
    # 如果已經沒單了，就直接回首頁，不要顯示空收據
    if not unpaid_orders.exists():
        return redirect('menu')

    current_bill = unpaid_orders.aggregate(Sum('oTotal'))['oTotal__sum'] or 0
    return render(request, 'checkout_confirm.html', {
        'unpaid_orders': unpaid_orders,
        'current_bill': current_bill,
    })

# 購物車詳情
def cart_detail(request):
    cart = request.session.get('cart', {})
    items = []
    total_price = 0
    for food_id, quantity in cart.items():
        food = get_object_or_404(Food, fID=food_id)
        subtotal = food.fPrice * quantity
        total_price += subtotal
        items.append({'food': food, 'quantity': quantity, 'subtotal': subtotal})
    return render(request, 'cart.html', {'items': items, 'total_price': total_price})

# 廚房看板
# def kitchen_dashboard(request):
#     if request.session.get('user_id') != 1:
#         messages.error(request, "權限不足")
#         return redirect('menu')
#     active_orders = Order.objects.filter(oStatus='處理中').order_by('oTime')
#     return render(request, 'kitchen.html', {'orders': active_orders})


# def kitchen_dashboard(request):
#     # 檢查是否為員工，如果不是，就跳轉到 menu
#     if not request.user.is_staff: 
#         return redirect('menu') 
#     context = {
#         'title': '廚房管理看板',
#     }
#     return render(request, 'kitchen.html', context)

def kitchen_dashboard(request):
    # 1. 使用你原本的 Session 檢查邏輯，避開 Django 內建系統的干擾
    user_id = request.session.get('user_id')
    
    # 假設管理員/員工的 ID 是 1 (照你原本的設定)
    if user_id != 1: 
        messages.error(request, "權限不足，請以員工帳號登入")
        return redirect('menu') 

    # 2. 抓取資料
    active_orders = Order.objects.filter(oStatus='處理中').order_by('oTime')

    # 3. 務必定義 context 字典 (解決 NameError)
    context = {
        'title': '廚房管理看板',
        'orders': active_orders,
    }
    
    # 4. 回傳頁面
    return render(request, 'kitchen.html', context)
# 出餐完成
def complete_order(request, order_id):
    if request.session.get('user_id') != 1:
        return HttpResponseForbidden()
    if request.method == "POST":
        order = get_object_or_404(Order, oID=order_id)
        order.oStatus = '已完成'
        order.save()
        messages.success(request, f"訂單 #{order_id} 已出餐")
    return redirect('kitchen_dashboard')

