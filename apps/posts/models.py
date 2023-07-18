from django.db import models
from django.core.validators import FileExtensionValidator, MaxLengthValidator

from apps.shared.models import BaseModel
from apps.users.models import User


class Post(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='posts_photos',validators=[FileExtensionValidator(
                                allowed_extensions=['png', 'jpeg', 'jpg']
                            )])
    caption = models.TextField(validators=[MaxLengthValidator(1700)])

    class Meta:
        db_table = 'posts'
        verbose_name = 'post'
        verbose_name_plural = 'posts'

    def __str__(self):
        return f"{self.author} | {self.caption}"
    

class PostLike(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='postlikes')

    class Meta:
        constraints  = [
            models.UniqueConstraint(
                fields=['author', 'post'],
                name='postlikeunique'
            )
        ]

class PostComment(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name='child', blank=True, null=True)
    
    def __str__(self):
        return f"{self.author} | {self.comment}"
    

class CommentLike(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='commentlikes')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'comment'],
                name='commentlikeunique'
            )
        ]