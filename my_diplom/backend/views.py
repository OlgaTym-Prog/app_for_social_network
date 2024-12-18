from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .permissios import IsOwnerOrReadOnly
from .serializers import PostSerializer, CommentSerializer
from .models import Post, Comment, Like


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsOwnerOrReadOnly()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Задаём автора публикации как текущего пользователя"""
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        """Позволяет редактировать текст, изображение или оба поля вместе"""
        instanse = self.get_object()

        # Проверяем, что  пользователь - автор публикации
        if instanse.author != request.user:
            raise PermissionDenied("You cannot update this object.")

        # Проверяем, что хотябы одно из полей было передано
        allowed_fields = {'text', 'image'}
        if not any(field in request.data for field in allowed_fields):
            raise ValidationError(
                {"detail": "You must provide at least one field to update."}
            )

        # Обновляем только переданные поля
        if 'text' in request.data:
            instanse.text = request.data['text']
        if 'image' in request.data:
            instanse.image = request.data['image']

        instanse.save()
        serializer = self.get_serializer(instanse)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Добавление/удаление лайка"""
        post = self.get_object()
        like, created = Like.objects.get_or_create(post=post, author=request.user)
        if not created:
            like.delete()
            return Response({"detail": "Like removed.", "liked": False}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Post liked.", "liked": True}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        """Детали публикации"""
        post = self.get_object()
        serializer = PostSerializer(post)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.request.data.get('post')
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise ValidationError({"post": "Post does not exist"})
        serializer.save(author=self.request.user, post=post)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("You cannot delete this object.")
        instance.delete()
