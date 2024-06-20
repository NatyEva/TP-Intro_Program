# capa de servicio/lógica de negocio

from ..transport import transport
from ..dao import repositories
from ..generic import mapper
from django.contrib.auth import get_user

def getAllImages(input=None):
    
    json_collection = transport.getAllImages(input)# obtiene un listado de imágenes desde transport.py y lo guarda en un json_collection.el parámetro 'input' indica si se debe buscar por un valor introducido en el buscador.

    images =  []#lista vacia donde se guardaran las NasaCard

    for object in json_collection: # recorre el listado de objetos del JSON

        nasa_card=mapper.fromRequestIntoNASACard(object)#formatea al abjeto en una Nasa Card
        
        images.append(nasa_card)#agrega a la lista imagenes una nasa_card 
   

    return images#retorna la lista de nasa_card


def getImagesBySearchInputLike(input):
    return getAllImages(input)


# añadir favoritos (usado desde el template 'home.html')
def saveFavourite(request):
    
    fav = '' # transformamos un request del template en una NASACard.
    fav.user = '' # le seteamos el usuario correspondiente.

    return repositories.saveFavourite(fav) # lo guardamos en la base.


# usados en el template 'favourites.html'
def getAllFavouritesByUser(request):
    if not request.user.is_authenticated:
        return []
    else:
        user = get_user(request)

        favourite_list = [] # buscamos desde el repositorio TODOS los favoritos del usuario (variable 'user').
        mapped_favourites = []

        for favourite in favourite_list:
            nasa_card = '' # transformamos cada favorito en una NASACard, y lo almacenamos en nasa_card.
            mapped_favourites.append(nasa_card)

        return mapped_favourites


def deleteFavourite(request):
    favId = request.POST.get('id')
    return repositories.deleteFavourite(favId) # borramos un favorito por su ID.