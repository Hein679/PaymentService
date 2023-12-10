from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.views.generic import RedirectView

app_name = 'payment_service'

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='payment_service/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='payment_service/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='payment_service:login'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('send_payment/', views.send_payment, name='send_payment'),
    path('check_email/', views.check_email, name='check_email'),
    path('accept_request/<int:transaction_id>/', views.accept_request, name='accept_request'),
    path('reject_request/<int:transaction_id>/', views.reject_request, name='reject_request'),
    path('notifications/', views.notifications, name='notifications'),
    path('admin_page/', views.admin_page, name='admin_page'),
    path('user_transactions/<int:user_id>/', views.user_transactions, name='user_transactions'),
    path('register_admin/', views.register_admin, name='register_admin'),
]