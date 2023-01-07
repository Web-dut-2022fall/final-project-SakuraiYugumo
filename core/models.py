from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime
import uuid

User = get_user_model()


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 当前操作的用户
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)  # 个人介绍
    profileimg = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')  # 头像
    location = models.CharField(max_length=100, blank=True)  # 地区


class Post(models.Model):  # 帖子
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)   # 用户
    image = models.ImageField(upload_to='post_images')  # 帖子图片
    caption = models.TextField()  # 标题
    created_at = models.DateTimeField(default=datetime.now)  # 时间
    no_of_likes = models.IntegerField(default=0)  # 点赞


class LikePost(models.Model):
    post_id = models.CharField(max_length=500)  # 帖子id
    username = models.CharField(max_length=100)  # 用户名


class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)  # 关注
    user = models.CharField(max_length=100)  # 用户
