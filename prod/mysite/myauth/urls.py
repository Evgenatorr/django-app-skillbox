from django.urls import path
from django.contrib.auth.views import LoginView
from .views import (
    get_cookie_view,
    set_cookie_view,
    AuthIndexView,
    set_session_view,
    get_session_view,
    MyLogoutView,
    AboutMeView,
    RegisterView,
    ProfileUpdateView,
    ProfileDetailsView,
    ProfileListView,
    HelloView,
)

app_name = "myauth"

urlpatterns = [
    path("", AuthIndexView.as_view(), name="index"),
    path("hello/", HelloView.as_view(), name="hello"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "login/",
        LoginView.as_view(
            template_name="myauth/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("cookie/get", get_cookie_view, name="cookie-get"),
    path("cookie/set", set_cookie_view, name="cookie-set"),
    path("session/get", get_session_view, name="session-get"),
    path("session/set", set_session_view, name="session-set"),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("profiles/", ProfileListView.as_view(), name="profiles_list"),
    path("profiles/<int:pk>/", ProfileDetailsView.as_view(), name="profiles_details"),
    path(
        "profiles/<int:pk>/update/", ProfileUpdateView.as_view(), name="profile_update"
    ),
]
