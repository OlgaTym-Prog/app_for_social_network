"""
URL configuration for my_diplom project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from backend.views import PostViewSet, CommentViewSet


# Настраиваем маршруты
router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='posts')
router.register(r'comments', CommentViewSet, basename='comments')


# Кастомный API Root
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def custom_api_root(request, format=None):
    return Response({
        "posts": request.build_absolute_uri('posts/'),
        "comments": request.build_absolute_uri('comments/')
    })


# Маршруты
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', custom_api_root),  # Кастомный API Root
] + router.urls + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
