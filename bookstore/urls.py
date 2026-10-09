"""bookstore URL Configuration"""
import debug_toolbar
from django.contrib import admin
from django.urls import include, path
from . import views
urlpatterns = [
    path("__debug__/", include(debug_toolbar.urls)),
    path("admin/", admin.site.urls),
    path("update_server/", views.update, name="update"),
    path("hello/", views.hello_world, name="hello_world"),
]