from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        # 這些是你在 views.py 中提到的欄位
        fields = ['cName', 'cBirthday', 'cEmail', 'cPhone']
        
        # 加上 widgets 可以讓 HTML 生成時更漂亮（例如日期選擇器）
        widgets = {
            'cName': forms.TextInput(attrs={'class': 'form-control'}),
            'cBirthday': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cEmail': forms.EmailInput(attrs={'class': 'form-control'}),
            'cPhone': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'cName': '姓名',
            'cBirthday': '生日',
            'cEmail': '電子郵件',
            'cPhone': '電話',
        }