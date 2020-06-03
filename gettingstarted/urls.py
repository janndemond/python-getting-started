from django.conf.urls import url
from django.urls import path, include
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from hello.views import weatherListView
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
    #path("", weatherListView.as_view(), name="index"),
    path("register/",user_views.register,name="register"),
    path("sentEmail/",hello.views.email,name="SentEmail"),
    path("login/",auth_views.LoginView.as_view(template_name="users/login.html"),name="login"),
    path("logout/",auth_views.LogoutView.as_view(),name="logout"),
    path("admin/", admin.site.urls),
    path("accounts/", include('allauth.urls')),
    url(r'^cookies/', include('cookie_consent.urls')),
    path('profile/', user_views.profile, name='profile'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
