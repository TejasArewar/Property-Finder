from django.urls import path,include
from . import views



urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name = 'logout'),
    path('forgot_password/', views.forgot_password, name = 'forgot_password'),
    path('signup/', views.signup, name="signup"),
    path('property/', views.property, name="property"),
    path('delete_prop/<int:id>/', views.delete_prop, name = 'delete_prop'),
    path('profile_pic/<int:id>/', views.profile_pic, name = 'profile_pic'),
    path('edit_prop/<int:pk>/', views.edit_prop, name='edit_prop'),
    path('delete_profile_pic/<int:id>/', views.delete_profile_pic, name = 'delete_profile_pic'),
    path('my_adds/', views.my_adds, name="my_adds"),
    path('subscription/', views.subscription, name="subscription"),
    path('subscription_success/<int:payment>/<str:payment_id>/', views.subscription_success, name='subscription_success'),
]