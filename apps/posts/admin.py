from django.contrib import admin

from . import models


class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'caption', 'created_time']
    search_fields = ['author__username', 'caption']


class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'comment', 'created_time']
    search_fields = ['author__username', 'comment']


class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_time']
    search_fields = ['author__username', 'post']


class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['author', 'comment', 'created_time']
    search_fields = ['author__username', 'comment']


admin.site.register(models.Post, PostAdmin)
admin.site.register(models.PostComment, CommentAdmin)
admin.site.register(models.PostLike, PostLikeAdmin)
admin.site.register(models.CommentLike, CommentLikeAdmin)