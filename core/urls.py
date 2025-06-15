from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),

 
    path('customer-login/', views.customer_login_view, name='login'),
    path('manager-login/', views.manager_login_view, name='manager_login'),
    # ...other urls...

    path('register/customer/', views.register_customer_view, name='register_customer'),
    path('register/manager/', views.register_manager_view, name='register_manager'),
    # path('login/', views.login_view, name='login'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('transfer/', views.transfer_funds, name='transfer_funds'),

    # Manager URLs
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('account/<int:id>/approve/', views.approve_account, name='approve_account'),
    path('account/<int:id>/deny/', views.deny_account, name='deny_account'),
    path('account/<int:id>/freeze/', views.freeze_account, name='freeze_account'),
    path('account/<int:id>/unfreeze/', views.unfreeze_account, name='unfreeze_account'),

    path('loan/request/', views.request_loan, name='request_loan'),
    path('loan/manage/', views.manage_loans, name='manage_loans'),
    path('loan/<int:id>/approve/', views.approve_loan, name='approve_loan'),
    path('loan/<int:id>/deny/', views.deny_loan, name='deny_loan'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    # path('logout/', views.logout_view, name='logout'),
]
