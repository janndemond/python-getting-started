from django.conf.urls import url
from django.urls import path, include

from django.contrib import admin
from django.contrib.auth import views as auth_views
admin.autodiscover()

import hello.views
from   users import views as user_views

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("", hello.views.index, name="index"),
    path("register/",user_views.register,name="register"),
    path("register/",user_views.profile,name="profile"),
    path("login/",auth_views.LoginView.as_view(template_name="users/login.html"),name="login"),
    path("logout/",auth_views.LogoutView.as_view(),name="logout"),
    path("admin/", admin.site.urls),
    path("accounts/", include('allauth.urls')),
    url(r'^cookies/', include('cookie_consent.urls'))
]
