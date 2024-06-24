# capa de vista/presentación
# si se necesita algún dato (lista, valor, etc), esta capa SIEMPRE se comunica con services_nasa_image_gallery.py
from nasa_image_gallery.models import Favourite
from django.shortcuts import redirect, render
from .layers.services import services_nasa_image_gallery
from .layers.dao import repositories
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login,authenticate
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.http import JsonResponse
from .layers.generic.mapper import fromTemplateIntoNASACard
from django.http import HttpResponseBadRequest
from django.core.mail import send_mail  #envia el mail a la casilla de la persona registrada
from .forms import CustomUserCreationForm


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
    images, favourite_list = getAllImagesAndFavouriteList(request) # llama a la función auxiliar getAllImagesAndFavouriteList() y obtiene 2 listados: 
    #uno de las imágenes de la API y otro de favoritos por usuario.Este último, solo si se desarrolló el opcional de favoritos; caso contrario, será un listado vacío [].
    

    page_number = request.GET.get('page', 1) #btiene el número de la página actual desde los parámetros de la URL (GET request).
    # Si no se proporciona, usa 1 por defecto.
    items_per_page = request.GET.get('items_per_page', 5) #Obtiene la cantidad de elementos por página, si no se determina, usa 5 por defecto.
    

    try:
        items_per_page = int(items_per_page) #convierte al items_per_page en un entero
        if items_per_page < 1: #Si el número es menor que 1, lo ajusta a 5 
            items_per_page = 5
    except ValueError:
        items_per_page = 5 #Si `items_per_page` no es un número válido, lo ajusta a 5

    paginator = Paginator(images, items_per_page) #Crea una instancia de `Paginator` con la lista de imágenes y la cantidad de elementos por página.
    #Paginator es una clase de Django que facilita la división de listas largas en páginas más manejables.
    page_obj = paginator.get_page(page_number) #Obtiene el objeto de la página actual usando el número de la página.

    return render(request, 'home.html', {
        'page_obj': page_obj,'images': images,
        'favourite_list': favourite_list,
        'items_per_page': items_per_page,
    }) # # Renderiza la plantilla `home.html`y pasa el contexto a la plantilla:
    # `page_obj`: objeto de la página actual, que incluye las imágenes para la página y la información de paginación.
    # `images`: la lista completa de imágenes.
    # `favourite_list`: la lista de imágenes favoritas del usuar

# función utilizada en el buscador.
def search(request):
   
    images, favourite_list = getAllImagesAndFavouriteList(request)
    search_msg = request.POST.get('query', '') or request.GET.get('query', '') #Obtiene el término de búsqueda desde los parámetros POST o GET
    if search_msg=='':     #Si search_msg está vacío, llama a la función getAllImages sin parámetros para obtener todas las imágenes.  
        images = services_nasa_image_gallery.getAllImages(None)
    else:                  #Si hay un término de búsqueda, lo pasa a getAllImages y obtiene solo las imágenes de busqueda.
        images = services_nasa_image_gallery.getAllImages(search_msg)

    page_number = request.GET.get('page', 1) #Obtiene el valor de la pagina actual, si no se proporciona toma por defecto 1
    items_per_page = request.GET.get('items_per_page', 5)  # Obtiene la cantidad de elementos por pagina, sino se proporciona usa por defecto 5.
    try: #captura el error
        items_per_page = int(items_per_page)
        if items_per_page < 1:
            items_per_page = 5
    except ValueError:
        items_per_page = 5  #si el numero no es valido coloca por defecto 5
    paginator = Paginator(images, items_per_page)
    page_obj = paginator.get_page(page_number)

    return render(request, 'home.html', { #Renderiza la plantilla home.html y pasa el contexto a la plantilla:
        'page_obj': page_obj,
        'images': images,
        'favourite_list': favourite_list,
        'search_msg': search_msg,  # Pasa el término de búsqueda a la plantilla
        'items_per_page': items_per_page, #La cantidad de elementos por página que se está utilizando actualmente
    }) 

# función que maneja la carga de imágenes y devuelve los datos en formato JSON
def load_images(request):
    images, favourite_list = getAllImagesAndFavouriteList(request)
    image_data = [{'url': image.url} for image in images]
    return JsonResponse({'images': image_data})

# las siguientes funciones se utilizan para implementar la sección de favoritos: traer los favoritos de un usuario, guardarlos, eliminarlos y desloguearse de la app.
@login_required
def getAllFavouritesByUser(request):
    
    favourite_list = services_nasa_image_gallery.getAllFavouritesByUser(request)
    
    return render(request, 'favourites.html', {'favourite_list': favourite_list})


@login_required
def saveFavourite(request):
    if request.method == 'POST':
        nasa_card = fromTemplateIntoNASACard(request)  # Crea la instancia de NASACard desde los datos del formulario
        comment = request.POST.get('comment', '')  # Obtiene el comentario del formulario
        nasa_card.comment = comment
    

        services_nasa_image_gallery.saveFavourite(request)
        favourite_list = services_nasa_image_gallery.getAllFavouritesByUser(request)
    
        return render(request, 'favourites.html', {'favourite_list': favourite_list})
    else:
        return HttpResponseBadRequest('Invalid request method')


@login_required
def deleteFavourite(request):
    favId = request.POST.get('id')
    success = services_nasa_image_gallery.deleteFavourite(request, favId)
    if success:
        # Recuperar la lista actualizada de favoritos
        favourite_list = services_nasa_image_gallery.getAllFavouritesByUser(request)
        return render(request, 'favourites.html', {'favourite_list': favourite_list})
    else:
        # Manejar el caso de error o redirigir según sea necesario
        return redirect('home')  # Redirigir a la página principal o manejar el error de otra manera
    


@login_required
def exit(request):
    logout(request)
    return redirect('home') # cuando cierro sesion me redirige al login automaticamente

@login_required
def login_views(request):
    login(request)
    return redirect(request,'login.html')  #me redirige a la planilla de login

def registration(request):
    data = {
        'form': CustomUserCreationForm()
    }
    if request.method=='POST':
        user_creation_form = CustomUserCreationForm(data=request.POST)
        
        if user_creation_form.is_valid():
            user_creation_form.save()
            user = authenticate(username=user_creation_form.cleaned_data['username'], password=user_creation_form.cleaned_data['password1'], email=user_creation_form.cleaned_data['email'])
            login(request, user)
            return redirect('home')
    return render (request, 'registration/registration.html',data)

"""
def contacto_mail(request):
    if request.method=="POST":   #detecta que se toca el boton en viar y vamos a trabajar para enviar a un mail la libreria de django .mail.
        
        mail=request.POST["asunto"]
        
        password=request.POST["password"]
        
        email_from=settings.EMAIL_HOST_USER
        
        recipient_list=["Nicolasfalzetta@outlook.com"]
        
        send_mail(subject, email_from, recipient_list) 
        
        return render(request,"gracias.html") #nos re dirige a una plantilla de mensaje al apretar el boton enviar es previo antes de las lineas de codigo importantes..
    
    return render(request, "registration.html")
 """