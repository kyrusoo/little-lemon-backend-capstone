from django.contrib import admin
from django.urls import path, include
from restaurant.views import home
urlpatterns = [path('', home, name='home'), path('admin/', admin.site.urls),
    path('restaurant/', include('restaurant.urls')), path('auth/', include('rest_framework.urls'))]
