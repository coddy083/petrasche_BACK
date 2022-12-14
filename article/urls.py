from django.urls import path
from article import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.ArticleView.as_view()),
    path('pet/<pet>/', views.ArticleSelectView.as_view()),
    path('page/<int:page>/', views.ArticleScrollView.as_view()),
    path('top/', views.ArticleTopView.as_view()),
    path('comment/<int:pk>/', views.CommentView.as_view()),
    path('like/<int:pk>/', views.LikeView.as_view()),
    path('myarticle/', views.MyArticleView.as_view()),
    path('myarticle/<int:pk>/', views.MyArticleView.as_view()),
    path('<int:pk>/', views.ArticleDetailView.as_view()),
    path('search/', views.SearchView.as_view()),
    path('hashtagsearch/', views.HashTagSearchView.as_view()),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

