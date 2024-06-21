# capa de vista/presentación
# si se necesita algún dato (lista, valor, etc), esta capa SIEMPRE se comunica con services_nasa_image_gallery.py
from nasa_image_gallery.models import Favourite
from django.shortcuts import redirect, render
from .layers.services import services_nasa_image_gallery
from .layers.dao import repositories
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login

# función que invoca al template del índice de la aplicación.
def index_page(request):
    return render(request, 'index.html')

# auxiliar: retorna 2 listados -> uno de las imágenes de la API y otro de los favoritos del usuario.
def getAllImagesAndFavouriteList(request):
  
    images = services_nasa_image_gallery.getAllImages(None)
    favourite_list = services_nasa_image_gallery.getAllFavouritesByUser(request)

    return images, favourite_list

# función principal de la galería.
def home(request):
    # llama a la función auxiliar getAllImagesAndFavouriteList() y obtiene 2 listados: uno de las imágenes de la API y otro de favoritos por usuario*.
    # (*) este último, solo si se desarrolló el opcional de favoritos; caso contrario, será un listado vacío [].

    
    images, favourite_list = getAllImagesAndFavouriteList(request)
    return render(request, 'home.html', {'images': images, 'favourite_list': favourite_list} )


# función utilizada en el buscador.
def search(request):
   
    images, favourite_list = getAllImagesAndFavouriteList(request) 
    search_msg = request.POST.get('query', '')
    if search_msg=='':      
        images = services_nasa_image_gallery.getAllImages(None)
    else:
        images = services_nasa_image_gallery.getAllImages(search_msg)

    return render(request, 'home.html', {'images': images, 'favourite_list': favourite_list} )



# las siguientes funciones se utilizan para implementar la sección de favoritos: traer los favoritos de un usuario, guardarlos, eliminarlos y desloguearse de la app.
@login_required
def getAllFavouritesByUser(request):
    
    favourite_list = services_nasa_image_gallery.getAllFavouritesByUser(request)
    
    return render(request, 'favourites.html', {'favourite_list': favourite_list})


@login_required
def saveFavourite(request):
    
    favourite_list = services_nasa_image_gallery.saveFavourite(request)
        
    return render(request, 'favourites.html',{'favourite_list': favourite_list} )



@login_required
def deleteFavourite(request):
   services_nasa_image_gallery.deleteFavourite(request)
   return redirect('home')
    


@login_required
def exit(request):
    logout(request)
    return redirect('home') # cuando cierro sesion me redirige al login automaticamente

@login_required
def login_views(request):
    login(request)
    return redirect(request,'login.html')  #me redirige a la planilla de login
