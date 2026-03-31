from django.db import models

class Category(models.Model):
    catID = models.AutoField(primary_key=True)
    catName = models.CharField(max_length=50, verbose_name="分類名稱")

    class Meta:
        verbose_name = "餐點分類"
        verbose_name_plural = "餐點分類"

    def __str__(self):
        return self.catName

class Food(models.Model):
    fID = models.AutoField(primary_key=True)
    fName = models.CharField(max_length=50, verbose_name="餐點名稱")
    fPrice = models.IntegerField(verbose_name="單價")
    fStock = models.IntegerField(default=0, verbose_name="當前庫存")
    add_qty = models.IntegerField(default=0, verbose_name="補貨")
    fImage = models.ImageField(upload_to='foods/', blank=True, null=True, verbose_name="餐點圖片")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='foods', verbose_name="所屬分類")
    is_active = models.BooleanField(default=True, verbose_name="是否供應")

    class Meta:
        verbose_name = "餐點"
        verbose_name_plural = "餐點"

    def __str__(self):
        return self.fName

class Customer(models.Model):
    cId = models.AutoField(primary_key=True)
    cName = models.CharField(max_length=50, verbose_name="姓名")
    cAccount = models.CharField(max_length=50, unique=True, verbose_name="帳號")
    cPassword = models.CharField(max_length=50, verbose_name="密碼")
    cSex = models.CharField(max_length=1, choices=(('M', '男'), ('F', '女')), verbose_name="性別")
    cBirthday = models.DateField(blank=True, null=True, verbose_name="生日")
    cEmail = models.EmailField(verbose_name="電子郵件")
    cPhone = models.CharField(max_length=20, verbose_name="電話")
    updated_time= models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "客戶管理"
        verbose_name_plural = "客戶管理"
    def __str__(self):
        return self.cName

class Order(models.Model):
    STATUS_CHOICES = (
        ('處理中', '處理中'),
        ('已完成', '已完成'),
        ('已結帳', '已結帳'), # 確保這裡有「已結帳」
    )
    oID = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="客戶")
    oTotal = models.IntegerField(default=0, verbose_name="總金額")
    oStatus = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='處理中', 
        verbose_name="狀態"
    )
    class Meta:
        verbose_name = "訂單"
        verbose_name_plural = "訂單"
    oTime = models.DateTimeField(auto_now_add=True, verbose_name="訂單時間")

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

class StockLog(models.Model):
    LOG_TYPE = (
        ('IN', '進貨/補貨'),
        ('SALE', '銷售扣除'),
    )
    food = models.ForeignKey(Food, on_delete=models.CASCADE, verbose_name="餐點")
    amount = models.IntegerField(verbose_name="變動數量")
    reason = models.CharField(max_length=10, choices=LOG_TYPE, default='SALE', verbose_name="變動類型")
    note = models.CharField(max_length=100, blank=True, verbose_name="備註")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="紀錄時間")

    class Meta:
        verbose_name = "庫存變動紀錄"
        verbose_name_plural = "庫存變動紀錄"
        ordering = ['-created_at']