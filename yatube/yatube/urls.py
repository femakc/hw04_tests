from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('posts.urls', namespace='posts')),
    path('admin/', admin.site.urls),
    path('group/<slug>/', include('posts.urls', namespace='group')),
    path('auth/', include('users.urls', namespace='users')),
    path('auth/', include('django.contrib.auth.urls')),
    path('about/', include('about.urls', namespace='about')),
    path('profile/', include('posts.urls', namespace='profile')),
    path('posts/', include('posts.urls', namespace='post_detail')),
]
