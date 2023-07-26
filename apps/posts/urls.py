from django.urls import path

from . import views


urlpatterns = [
    path('lists/', views.PostListView.as_view()),
    path('detail/<uuid:pk>/', views.PostDetailView.as_view()),
    path('update/<uuid:pk>/', views.PostUpdateView.as_view()),
    path('delete/<uuid:pk>/', views.PostDestroyView.as_view()),
    path('create/', views.PostCreateView.as_view()),

    #   Izohlar uchun.
    path('comments/', views.CommentListCreateView.as_view()),
    path('comment/<uuid:pk>/', views.CommentDetailView.as_view()),
    path('comment/liked/<uuid:pk>/', views.CommentLikeView.as_view()),

    #   likelar uchun
    path('likes/<uuid:pk>/', views.PostLikeListView.as_view()),
    path('liked/<uuid:pk>/', views.PostLikeView.as_view()),
]
