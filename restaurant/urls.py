from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()
router.register('tables', views.BookingViewSet, basename='booking')
urlpatterns = [path('', views.home, name='restaurant-home'),
    path('menu/', views.MenuItemsView.as_view(), name='menu-list'),
    path('menu/<int:pk>/', views.SingleMenuItemView.as_view(), name='menu-detail'),
    path('booking/', include(router.urls)),
    path('auth/users/', views.RegistrationView.as_view(), name='register'),
    path('auth/token/login/', views.LoginView.as_view(), name='token-login'),
    path('auth/token/logout/', views.LogoutView.as_view(), name='token-logout')]
