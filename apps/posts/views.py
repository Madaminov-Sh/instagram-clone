from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView, ListCreateAPIView
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response

from .models import Post, CommentLike, PostComment, PostLike
from . import serializers
from apps.shared.custom_pagination import CustomPagination


class PostListView(ListAPIView):
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = serializers.PostSerializer
    pagination_class = CustomPagination


class PostCreateView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = serializers.PostSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)
    

class PostDetailView(RetrieveAPIView):
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = serializers.PostSerializer


class PostUpdateView(UpdateAPIView):
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = serializers.PostSerializer

    def put(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.serializer_class(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "success": True,
                "message": "post muvafaqiyatli o'zgartirildi",
                "data": serializer.data
            }
        )


class PostDestroyView(DestroyAPIView):
    queryset = Post.objects.all()
    pagination_class = [permissions.IsAuthenticated,]
    serializer_class = serializers.PostLikeSerializer
    
    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        post.delete()
        return Response(
            {
                "success": True,
                "message": "post muvafaqiyatli o'chirildi"
            }
        )
    

class CommentListCreateView(ListCreateAPIView):
    queryset = PostComment.objects.all()
    permission_classes = [permissions.IsAuthenticated,]
    pagination_class = CustomPagination
    serializer_class = serializers.CommentSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentDetailView(RetrieveAPIView):
    queryset = PostComment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = [permissions.IsAuthenticated,]


class PostLikeListView(ListAPIView):
    serializer_class = serializers.PostLikeSerializer
    permission_classes = [permissions.IsAuthenticated,]
    pagination_class = CustomPagination

    def get_queryset(self):
        post_id = self.kwargs['pk']
        return PostLike.objects.filter(post_id=post_id)
    

class CommentLikeListView(ListAPIView):
    serializer_class = serializers.CommentLikeSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        comment_id = self.kwargs['pk']
        return CommentLike.objects.filter(comment_id=comment_id)
    

class PostLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request, pk):
        try:
            post_like = PostLike.objects.get(
                author = request.user,
                post_id = pk
            )
            post_like.delete()
            return Response(
                {
                    "success": True,
                    "message": "Like deleted"
                }, status=204
            )
        except PostLike.DoesNotExist:
            post_like = PostLike.objects.create(
                author = request.user,
                post_id = pk
            )
            serializer = serializers.PostLikeSerializer(post_like)
            return Response(
                {
                    "success": True,
                    "message": "Liked",
                    "data": serializer.data
                }, status=201
            )
        

class CommentLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request, pk):
        try:
            comment_like = CommentLike.objects.get(
                author = request.user,
                comment_id = pk
            )
            comment_like.delete()
            return Response(
                {
                    "success": True,
                    "message": "Like deleted"
                }, status=204
            )
        except CommentLike.DoesNotExist:
            comment_like = CommentLike.objects.create(
                author = request.user,
                comment_id = pk
            )
            serializer = serializers.CommentLikeSerializer(comment_like)
            return Response(
                {
                    "success": True,
                    "message": "Liked",
                    "data": serializer.data
                }, status=201
            )
 
 

