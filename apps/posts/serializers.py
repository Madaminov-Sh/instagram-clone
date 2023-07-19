from apps.users.models import User
from .models import Post, PostComment, PostLike, CommentLike

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'photo', 'username']


class PostSerializer(serializers.ModelSerializer):
        id = serializers.UUIDField(read_only=True)
        author = UserSerializer(read_only=True)

        post_likes_count = serializers.SerializerMethodField("get_likes_count")
        post_comments_count = serializers.SerializerMethodField("getcomment_count")
        me_liked = serializers.SerializerMethodField("get_me_liked")

        class Meta:
            model = Post
            fields = [
                'id', 
                'author', 
                'image', 
                'caption', 
                'created_time', 
                'post_likes_count', 
                'post_comment_count',
                'me_liked'
            ]

        def get_likes_count(self, obj):
             print("this is obk: ", obj)
             return obj.postlikes.count()
        
        def get_comment_count(self, obj):
             return obj.comments.count()
        
        def get_me_liked(self, obj):
            request = self.context('request', None)
             
            if request and request.user.is_authenticated:
                try:
                    PostLike.objects.get(post=obj, author=request.user)
                    return True
                except PostLike.DoesNotExist:
                    return False
            return False
                       

class CommentSerializer(serializers.ModelSerializer):
     id = serializers.UUIDField(read_only=True)
     author = UserSerializer(read_only=True)
     replies = serializers.SerializerMethodField("get_replies")
     me_liked = serializers.SerializerMethodField("get_me_liked")
     likes_count = serializers.SerializerMethodField("get_like_count")

     class Meta:
          model = PostComment
          fields = [
              'id', 
              'author', 
              'post', 
              'created_time', 
              'parent', 
              'replies', 
              'me_liked', 
              'likes_count'
            ]
          
     def get_replies(self, obj):
        if obj.child.exists():
            serializer = self.__class__(obj.child.all(), many=True, context=self.context)
            return serializer.data
        else:
            return None
            
     def get_me_liked(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return obj.comments(author=user).exists()
        else:
            return False

     def get_like_count(self, obj):
        return obj.commentlikes.count()
     

class PostLikeSerializer(serializers.ModelSerializer):
     id = serializers.UUIDField(read_only=True)
     author = UserSerializer(read_only=True)

     class Meta:
         model = PostLike
         fields = ['id', 'author', 'post']


class CommentLikeSerializer(serializers.ModelSerializer):
     id = serializers.UUIDField(read_only=True)
     author = UserSerializer(read_only=True)

     class Meta:
         model = CommentLike
         fields = ['id', 'author']