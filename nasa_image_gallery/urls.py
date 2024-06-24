from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    
    path('', views.index_page, name='index-page'),
    path('login/', views.login_views, name='login'),
    path('home/', views.home, name='home'),
    path('buscar/', views.search, name='buscar'),
   
    path('favourites/', views.getAllFavouritesByUser, name='favoritos'),
    path('favourites/add/', views.saveFavourite, name='agregar-favorito'),
    path('favourites/delete/', views.deleteFavourite, name='borrar-favorito'),
    path('save-favourite/', views.saveFavourite, name='guardar-favoritos'),

    path('load-images/', views.load_images, name='cargar-imagenes'),

    path('exit/', views.exit, name='exit'),
    
]