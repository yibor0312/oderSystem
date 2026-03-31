from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django import forms
from .models import Category, Food, Customer, Order, OrderItem, StockLog
from django.utils import timezone
from django.db.models import Sum

# --- 全域設定：標題與廚房看板連結 ---
admin.site.site_header = format_html('點餐管理系統 <a href="/kitchen/" target="_blank" style="font-size: 14px; margin-left: 20px; color: #ffc107;">👨‍🍳 開啟廚房看板</a>')
admin.site.site_title = "店長後台"
admin.site.index_title = "餐廳營運管理"
admin.site.site_url = None

# --- 共通邏輯：讓所有頁面都能顯示營收看板 ---
class BaseAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        from django.db.models import Sum
        from django.utils import timezone
        import datetime
        
        # 取得本地時區的「今天」起始與結束時間，這比直接用 .date() 更精準
        now = timezone.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        extra_context = extra_context or {}
        
        #  今日營收：使用 range 篩選一整天，並嚴格比對 '已結帳'
        # 注意：這裡的 '已結帳' 必須與 views.py 裡 update 的字串完全一模一樣
        extra_context['today_sales'] = Order.objects.filter(
            oTime__range=(start_of_day, end_of_day),
            oStatus='已結帳'
        ).aggregate(Sum('oTotal'))['oTotal__sum'] or 0
        
        #  本月營營：使用 year 和 month 篩選
        first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        extra_context['month_sales'] = Order.objects.filter(
            oTime__gte=first_day_of_month,
            oStatus='已結帳'
        ).aggregate(Sum('oTotal'))['oTotal__sum'] or 0
        
        # 額外小技巧：在終端機印出數據，方便你檢查
        print(f"--- 營收偵錯 ---")
        print(f"時間範圍: {start_of_day} ~ {end_of_day}")
        print(f"今日營收結果: {extra_context['today_sales']}")
        
        return super().changelist_view(request, extra_context=extra_context)

# ---  訂單明細內嵌 (用於訂單詳情頁) ---
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('food', 'quantity', 'get_price')
    
    def get_price(self, obj):
        return f"${obj.food.fPrice}"
    get_price.short_description = '單價'

# ---  餐點管理 ---
@admin.register(Food)
class FoodAdmin(BaseAdmin): # 繼承 BaseAdmin 以顯示看板
    list_display = ('fImage_tag', 'fName', 'category', 'fPrice', 'fStock', 'add_qty', 'stock_status', 'is_active')
    list_editable = ('fPrice', 'add_qty', 'is_active') 
    readonly_fields = ('fStock',)

    def fImage_tag(self, obj):
        if obj.fImage:
            return format_html('<img src="{}" style="width: 45px; height: 45px; border-radius: 5px; object-fit: cover;" />', obj.fImage.url)
        return "無圖片"
    fImage_tag.short_description = "預覽"

    def stock_status(self, obj):
        if obj.fStock <= 0:
            return format_html('<b style="color: red;">已售罄</b>')
        elif obj.fStock <= 10:
            return format_html('<b style="color: orange;">庫存緊張</b>')
        return format_html('<b style="color: green;">充足</b>')
    stock_status.short_description = "庫存狀態"

    def save_model(self, request, obj, form, change):
        add_qty = form.cleaned_data.get('add_qty', 0)

        if add_qty != 0:
            # 直接更新庫存
            obj.fStock += add_qty
            
            # 在建立日誌前先確保物件已儲存（若是新增物件需要 ID）
            super().save_model(request, obj, form, change)

            # 建立日誌
            StockLog.objects.create(
                food=obj,
                amount=add_qty,
                reason='IN' if add_qty > 0 else 'OUT',
                note=f"列表快速補貨 (操作者: {request.user.username})"
            )

            obj.add_qty = 0 
        else:
            super().save_model(request, obj, form, change)

# ---  訂單管理 ---
@admin.register(Order)
class OrderAdmin(BaseAdmin):
    list_display = ('oID', 'customer', 'display_items', 'oTotal', 'oStatus', 'oTime')
    list_filter = ('oStatus', 'oTime')
    inlines = [OrderItemInline]

    def display_items(self, obj):
        items = obj.items.all()
        return ", ".join([f"{item.food.fName} x {item.quantity}" for item in items])
    display_items.short_description = '餐點內容'

# ---  其他註冊 ---
@admin.register(Customer)
class CustomerAdmin(BaseAdmin):
    list_display = ('cId', 'cName', 'cAccount', 'cPhone')

@admin.register(StockLog)
class StockLogAdmin(BaseAdmin):
    list_display = ('created_at', 'food', 'amount', 'reason', 'note')
    readonly_fields = ('created_at', 'food', 'amount', 'reason', 'note')

@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = ('catID', 'catName')