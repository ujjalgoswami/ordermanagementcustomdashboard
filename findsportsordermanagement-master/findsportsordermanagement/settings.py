"""
Django settings for findsportsordermanagement project.

Generated by 'django-admin startproject' using Django 2.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# CREDENTIALS HAVE BEEN REMOVED FOR SECURITY PURPOSES
SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
is_Production = True
LOGIN_URL = '/login'
SESSION_COOKIE_AGE = 604800

if (is_Production):
    DEBUG = False
    ALLOWED_HOSTS = ['*']
else:
    DEBUG = True
    ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home.apps.HomeConfig',
    'netoapihook.apps.NetoapihookConfig',
    'stocklevel.apps.StocklevelConfig',
    'products.apps.ProductsConfig',
    'automation.apps.AutomationConfig',
    'marketplace.apps.MarketplaceConfig',
    'customers.apps.CustomersConfig',
    'refunds.apps.RefundsConfig',
    'suppliers.apps.SuppliersConfig',
    'purchaseorder.apps.PurchaseorderConfig',
    'trackingid.apps.TrackingidConfig',
    'orders.apps.OrdersConfig',
    'timebomb.apps.TimebombConfig',
    'zendesk.apps.ZendeskConfig',
    'warehouse.apps.WarehouseConfig',
    'newsletter.apps.NewsletterConfig',
    'usermanual.apps.UsermanualConfig',
    'testfeatures.apps.TestfeaturesConfig',
    'login.apps.LoginConfig',
    'escalatedorders.apps.EscalatedordersConfig',
    'accounts.apps.AccountsConfig',
    'stockupdate.apps.StockupdateConfig',
    'customerservice.apps.CustomerserviceConfig',
'categorization.apps.CategorizationConfig',
'tasklist.apps.TasklistConfig',
    'mathfilters',
    'fusioncharts',
    'django_cron',
    'django_crontab',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'global_login_required.GlobalLoginRequiredMiddleware',
]

# SECURE_BROWSER_XSS_FILTER=True
# SECURE_CONTENT_TYPE_NOSNIFF=True
# SESSION_COOKIE_SECURE=True
# CSRF_COOKIE_SECURE=True
# X_FRAME_OPTIONS='DENY'

ROOT_URLCONF = 'findsportsordermanagement.urls'
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]

WSGI_APPLICATION = 'findsportsordermanagement.wsgi.application'



# CREDENTIALS HAVE BEEN REMOVED FOR SECURITY PURPOSES
DATABASES = {
    'default': {
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Australia/Melbourne'

USE_I18N = True

USE_L10N = True

USE_TZ = False



STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
if (is_Production):
    STATIC_ROOT = os.path.join(BASE_DIR, 'assets')
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'assets')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CRON_CLASSES = [
    "findsportsordermanagement.cron.MyCronJob"
]

Q_CLUSTER = {
    'name': 'myproject',
    'workers': 8,
    'recycle': 500,
    'timeout': 60,
    'compress': True,
    'cpu_affinity': 1,
    'save_limit': 250,
    'queue_limit': 500,
    'label': 'Django Q',
    'redis': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 0, }
}