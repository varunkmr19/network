
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.new_post, name="newPost"),
    path("post/edit/<int:post_id>", views.edit_post, name="editPost"),
    path("post/delete/<int:post_id>", views.delete_post, name="deletePost"),
    path("following", views.following, name="following"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("post/<int:post_id>/like", views.PostLikeAPIToggle.as_view(), name='likeToggle'),
    path("profile/<int:user_id>/follow", views.FollowToggle.as_view(), name='followToggle')
]
