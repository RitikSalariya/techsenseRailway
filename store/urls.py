from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from . import views

app_name = 'store'

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Projects
    path('projects/', views.project_list, name='project_list'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    path('projects/<slug:slug>/buy/', views.buy_project, name='buy_project'),

    # Blog
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<int:pk>/', views.blog_detail, name='blog_detail'),

    # Contact
    path('contact/', views.contact, name='contact'),

    # Authentication
    path('signup/', views.user_signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Email Verification
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),

    # Orders
    path('my-orders/', views.my_orders, name='my_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),

    # Cart
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:project_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Account
    path('account/', views.account_dashboard, name='account_dashboard'),
    path('account/profile/edit/', views.profile_edit, name='profile_edit'),
    path('account/change-password/', views.account_change_password, name='account_change_password'),

    # Password Reset
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="store/password_reset.html",
            email_template_name="store/password_reset_email.html",
            subject_template_name="store/password_reset_subject.txt",
            success_url=reverse_lazy("store:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="store/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="store/password_reset_confirm.html",
            success_url=reverse_lazy("store:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="store/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
