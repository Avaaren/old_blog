from django.urls import path
from . import views
from django.contrib.auth import views as login_views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name = 'post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('search/', views.post_search, name='post_search'),
    # path('login/', views.user_login, name='login'),
    path('login/', login_views.LoginView.as_view(), name='login'),
    path('logout/', login_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('register/', views.register, name='registration'),
    path('ajax_search/', views.ajax_search, name='ajax_search'),
]