from django.urls import path
from . import views

app_name = "post"

urlpatterns = [
    path('', views.HomePageView.as_view(), name='homepage'),
    path('<slug:title>/', views.ThreadListView.as_view(), name='thread_list'),
    path('<slug:title>/thread/<slug:comment_slug>/', views.ThreadDetailView.as_view(), name='thread_detail'),
    path('comment/reply-to/<uuid:pk>/', views.CommentCreateView.as_view(), name='comment_create'),
    path('comment/edit/<uuid:pk>/', views.CommentEditView.as_view(), name='comment_edit'),
    path('thread/create/', views.ThreadCreateView.as_view(), name='thread_create'),
    path('test/test/', views.TestTemplate.as_view(), name='test_template'),
    path('user/<str:username>/', views.UserProfileView.as_view(), name='user_profile'),
    path('categories/all', views.CatListView.as_view(), name='category_list'),
]