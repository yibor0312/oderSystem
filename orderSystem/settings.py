"""
Django settings for orderSystem orderSystem.
"""

from pathlib import Path
import os

# 1. 基礎目錄設定
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. 安全與開發設定
SECRET_KEY = 'django-insecure-xu!py)+@yxurk#z%#3!gxi_v1z0r7al5dfvo)(56n@y10g633r'
DEBUG = True
ALLOWED_HOSTS = ['*']

# 3. 應用程式定義
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',             
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'orderSystem.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media', # 確保 HTML 能抓到 MEDIA_URL
            ],
        },
    },
]

WSGI_APPLICATION = 'orderSystem.wsgi.application'

# 4. 資料庫設定 (MySQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        # 'ENGINE': 'django.db.backends.mysql', 
        # 'NAME': 'project', 
        # 'USER': 'root', 
        # 'PASSWORD': '1234', 
        # 'HOST': 'localhost', 
        # 'PORT': '8888', 
        # 'OPTIONS': {
        #     'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        #     'charset': 'utf8mb4',
        # }
    }
}

# 5. 密碼驗證
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 6. 語系與時區 (繁體中文 / 台北時間)
LANGUAGE_CODE = 'zh-Hant' 
TIME_ZONE = 'Asia/Taipei' 
USE_I18N = True
USE_TZ = True

# 7. 靜態檔案設定 (CSS, JS)
STATIC_URL = '/static/' 
STATICFILES_DIRS = [
    BASE_DIR / "static"
]

# 8. 媒體檔案設定 (上傳的圖片)
# 網址顯示會是 /media/food/xxx.jpg
MEDIA_URL = '/media/' 
# 實際存放路徑為 C:\dvds\orderSystem\picture
MEDIA_ROOT = BASE_DIR / 'picture'

# 9. 預設主鍵類型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/login/'