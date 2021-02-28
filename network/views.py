from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

from .models import User, Post, Relationship


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


''' Displays posts by all users in reverse chronologial order '''
def index(request):
    # get posts in reverse chronologial order
    posts = Post.objects.order_by("-timestamp").all()
    paginator = Paginator(posts, 10) # Show 10 posts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        'page_obj': page_obj
    })


''' Displays all posts made by users that the current user follows '''
@login_required
def following(request):
    if request.method == 'GET':
        # current user following list
        following = Relationship.objects.filter(follower=request.user).all()
        if not following:
            return render(request, 'network/following.html', {
                'error': "No post by the people you follow."
            })

        #get all posts
        all_posts = Post.objects.order_by('-timestamp').all()
        posts = []
        for post in all_posts:
            for f in following:
                if f.followed == post.poster:
                    posts.append(post)

        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'network/following.html', {
            'page_obj': page_obj
        })


''' Create a new post'''
@login_required
def new_post(request):
    if request.method == 'POST':
        textarea = request.POST['textarea']
        if not textarea:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        post = Post.objects.create(content=textarea, poster=request.user)
        post.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


''' Modify an existing post '''
@login_required
def edit_post(request, post_id):
    try:
        post = Post.objects.get(poster=request.user, pk=post_id)
    except Post.DoesNotExist:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    if request.method == 'POST':
        content = request.POST['textarea']
        post.content = content
        post.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


''' Delete post'''
@login_required
def delete_post(request, post_id):
    try:
        post = Post.objects.get(poster=request.user, pk=post_id)
    except Post.DoesNotExist:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    if request.method == 'POST':
        post.delete()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


''' Displays user's info and all his post '''
@login_required
def profile(request, username):
    if request.method == 'GET':
        if username == request.user.username:
            userInfo = request.user
        else:
            #get user
            userInfo = get_object_or_404(User, username=username)

        follows = Relationship.objects.filter(follower=request.user, followed=userInfo).exists()
        followerCount = Relationship.objects.filter(followed=userInfo).count()
        followingCount = Relationship.objects.filter(follower=userInfo).count()
        posts = Post.objects.filter(poster=userInfo).order_by('-timestamp').all()

        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, "network/profile.html", {
            'userInfo': userInfo,
            'followerCount': followerCount,
            'followingCount': followingCount,
            'page_obj': page_obj,
            'follows': follows
        })


''' Like or Unlike a Post'''
class PostLikeAPIToggle(APIView):
    authentication_classes = {authentication.SessionAuthentication,}
    permission_classes = {permissions.IsAuthenticated,}

    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        user = self.request.user
        updated = False
        liked = False
        
        if user.is_authenticated:
            if user in post.likes.all():
                liked = False
                post.likes.remove(user)
            else:
                liked = True
                post.likes.add(user)
            updated = True
        data = {
            "updated": updated,
            "liked": liked
        }

        return Response(data)


''' Follow or Unfollow Someone '''
class FollowToggle(APIView):
    authentication_classes = {authentication.SessionAuthentication,}
    permission_classes = {permissions.IsAuthenticated,}

    def get(self, request, user_id):
        following = get_object_or_404(User, pk=user_id)
        follower = self.request.user
        updated = False
        followed = False

        follows = Relationship.objects.filter(follower=follower, followed=following).exists()
        
        if follower.is_authenticated:
            if follows == True:
                # get obj
                obj = Relationship.objects.get(follower=follower, followed=following)
                followed = False
                obj.delete()
            else:
                followed = True
                newFollower = Relationship.objects.create(follower=follower, followed=following)
                newFollower.save()
            updated = True
        data = {
            "updated": updated,
            "followed": followed
        }

        return Response(data)