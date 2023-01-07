from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from itertools import chain
import random

from .models import Profile, Post, LikePost, FollowersCount


@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)  # 当前用户
    user_profile = Profile.objects.get(user=user_object)
    user_following_list = []
    user_following = FollowersCount.objects.filter(follower=request.user.username)  # 筛选出该用户的正在关注的人
    for users in user_following:
        user_following_list.append(users.user)
    post = []
    for usernames in user_following_list:  # 筛选出所有正在关注的人的所有帖子
        feed_lists = Post.objects.filter(user=usernames)
        post.append(feed_lists)

    post_list = list(chain(*post))
    all_users = User.objects.all()  # 所有人
    user_following_all = []  # 筛选出所有正在关注的人
    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]  # 除掉已经关注的人
    current_user = User.objects.filter(username=request.user.username)  # 除掉自己
    final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
    random.shuffle(final_suggestions_list)
    username_profile = []  # 获取id
    username_profile_list = []
    for users in final_suggestions_list:
        username_profile.append(users.id)
    for ids in username_profile:  # 获取信息
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))
    return render(request, 'index.html', {'user_profile': user_profile, 'posts': post_list,
                                          'suggestions_username_profile_list': suggestions_username_profile_list[:4]})


def signin(request):  # 登录
    if request.method == "POST":  # 是post请求
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)  # 校验
        if user is not None:  # 用户存在
            # messages.info(request, '登录成功')
            # return redirect('signin')
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, '登录失败')  # 用户不存在
            return redirect('signin')
    else:  # 不是post请求
        return render(request, 'signin.html')


def signup(request):  # 注册
    if request.method == 'POST':  # 是post请求
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:  # 密码相同
            if User.objects.filter(email=email).exists():  # 如果邮箱已存在
                messages.info(request, "Email Taken")
                return redirect('signup')
            elif User.objects.filter(username=username).exists():  # 用户名已存在
                messages.info(request, "Username Taken")
                return redirect('signup')
            else:  # 都不存在
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                user_login = auth.authenticate(username=username, password=password)  # 登录
                auth.login(request, user_login)
                user_model = User.objects.get(username=username)  # 设置个人信息
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')  # 跳转到个人信息设置
        else:  # 如果密码不等
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
    else:  # 请求不是post
        return render(request, 'signup.html')


@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        if not request.FILES.get('image'):
            user_profile.bio = request.POST['bio']
            user_profile.location = request.POST['location']
            user_profile.save()
        if request.FILES.get('image'):
            user_profile.profileimg = request.FILES.get('image')
            user_profile.bio = request.POST['bio']
            user_profile.location = request.POST['location']
            user_profile.save()
        return redirect('settings')
    return render(request, 'setting.html', {'user_profile': user_profile})


@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)  # 忽略大小写
        username_profile = []
        username_profile_list = []  # 搜索到的人
        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html',
                  {'user_profile': user_profile, 'username_profile_list': username_profile_list})


@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return redirect('/')
    else:
        return redirect('/')


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')


@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)  # 用户帖子
    user_post_length = len(user_posts)  # 用户帖子数
    follower = request.user.username  # 当前用户
    user = pk  # 查询的用户
    if FollowersCount.objects.filter(follower=follower, user=user).first():  # 如果有查到的
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'
    user_followers = len(FollowersCount.objects.filter(user=pk))  # 查询的用户的关注者
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)


@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']  # 当前用户
        user = request.POST['user']  # 查看的人
        if FollowersCount.objects.filter(follower=follower, user=user).first():  # 删除
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/' + user)
        else:  # 新增
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/' + user)
    else:
        return redirect('/')


@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
    if not like_filter:  # 点赞
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    else:  # 未点赞
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')
