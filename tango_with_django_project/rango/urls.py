from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^about/', views.about, name='about'),
    re_path(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
    re_path(r'^add_category/$', views.add_category, name='add_category'),
    re_path(r'^category/(?P<category_name_slug>[\w\-]+)/add_page/$', views.add_page, name='add_page'),
    re_path(r'^register/$', views.register, name='register'),
    re_path(r'^login/$', views.user_login, name='login'),
    re_path(r'^restricted/', views.restricted, name='restricted'),
]