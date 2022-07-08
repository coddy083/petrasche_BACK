from django.db import models
from user.models import BaseModel, User
# from djangotoolbox.fields import ListField

# Create your models here.
class Article(BaseModel):
    title = models.CharField("제목", max_length=200, null=True)
    user = models.ForeignKey('user.User', verbose_name="작성자", on_delete=models.CASCADE, null=True)
    content = models.TextField("내용")
    like = models.ManyToManyField(User, related_name='좋아요', blank=True)
    is_active = models.BooleanField("공개 여부", default=True)
    # tags = TaggableManager("태그",blank=True)

    def __str__(self):
        return f"Article:{self.title}"

class Image(models.Model):
    article = models.ForeignKey(Article, verbose_name="아티클", on_delete=models.CASCADE, null=True)
    imgurl = models.URLField(max_length=200, null=True)


class Comment(BaseModel):
    user = models.ForeignKey('user.User', verbose_name="작성자", on_delete=models.SET_NULL, null=True)
    article = models.ForeignKey(Article, verbose_name="원글", on_delete=models.CASCADE, null=True)
    comment = models.TextField("댓글 내용")

    def __str__(self):
        return f"{self.user.username} 님 댓글입니다."