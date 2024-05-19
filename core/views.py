from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse, reverse_lazy
from django.http import Http404, HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt

# Imports de terceros
import mercadopago
import resend
from mercadopago import SDK
from rest_framework import viewsets

# Imports locales
from .models import *
from .forms import *
from .serializers import *





#Nos permite mostrar la info
class ProductoViewset(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    #queryset = Producto.objects.filter(tipo=1)
    serializer_class = ProductoSerializers

class CategoriaProductoViewset(viewsets.ModelViewSet):
    queryset = CategoriaProducto.objects.all()
    serializer_class = CategoriaProductoSerializers

# CRUD
# Decorador personalizado para verificar si el usuario es administrador o trabajador
def es_admin_o_trabajador(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='Trabajadores').exists())

# Vista protegida por el decorador de usuario
@user_passes_test(es_admin_o_trabajador)
def add(request):
    if request.method == 'POST':
        formulario = ProductoForm(request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Producto almacenado correctamente")
            return redirect('add')  # Redirige a la página deseada después de guardar

    data = {'form': ProductoForm()}
    return render(request, 'core/add-product.html', data)

@user_passes_test(es_admin_o_trabajador)
def update(request, id):
    producto = Producto.objects.get(id=id)
    data = {
        'form' : ProductoForm(instance=producto)
    }

    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST, instance=producto, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Producto actualizado correctamente")
            data['form'] = formulario

            # Redireccionar a la misma página después de 0.7 segundos
            return redirect(reverse_lazy('update', kwargs={'id': id}))  # Cambia 'update' por la URL de tu vista

    return render(request, 'core/update-product.html', data)


@user_passes_test(es_admin_o_trabajador)
def delete(request, id):
    producto = Producto.objects.get(id=id) # OBTIENE UN PRODUCTO POR EL ID
    producto.delete()

    return redirect(to="index")

#LogOut
def logout_view(request):
    if request.method == 'POST' or request.method == 'GET':
        # Perform logout logic here
        # For example, you can clear the session data and redirect to the login page
        request.session.clear()  # Clear session data
        return redirect('login')  # Redirect to the login page
    else:
        return HttpResponseNotAllowed(['POST', 'GET'])  # Return a 405 Method Not Allowed response

#REGISTRO
def registro(request):
    if request.method == 'POST':
        formulario = CustomUserCreationForm(request.POST)
        if formulario.is_valid():
            user = formulario.save()

            # Autenticar al usuario después del registro
            username = formulario.cleaned_data["username"]
            password = formulario.cleaned_data["password1"]
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)  # Autenticar al usuario
                messages.success(request, "Registro Exitoso. Ahora estás logueado.")
                return redirect('account')  # Redirige al usuario a la página de inicio o a donde sea necesario
        else:
            messages.error(request, "Error en el formulario. Por favor, corrige los errores.")

    else:
        formulario = CustomUserCreationForm()

    return render(request, 'registration/registro.html', {'form': formulario})

#Paginas

def testimonial(request):
    return render(request, 'core/testimonial.html')

def why(request):
    return render(request, 'core/why.html')

def account(request):
    return render(request, 'core/account.html')

def index(request):
    productosAll = Producto.objects.all()  # Obtener todos los productos
    page = request.GET.get('page', 1)  
    try:
        paginator = Paginator(productosAll, 4)  # Paginar los productos
        productosAll = paginator.page(page)
    except Exception as e:
        raise Http404("Página no encontrada")

    # Aplicar transformaciones de Cloudinary a las imágenes de los productos
    for producto in productosAll:
        if producto.imagen:
            imagen_url = producto.imagen.url
            # Dividir la URL de la imagen en dos partes
            partes_url = imagen_url.split('upload/')
            # Aplicar las transformaciones específicas de Cloudinary a la parte antes de 'upload/'
            parte_anterior = partes_url[0] + 'upload/c_scale,w_500/f_auto/'
            # Combinar la parte anterior con la parte después de 'upload/' para obtener la URL completa
            producto.imagen_url = parte_anterior + partes_url[1]
        else:
            producto.imagen_url = '/static/core/images/default_product_image.jpg'

    data = {'listado': productosAll, 'paginator': paginator}

    return render(request, 'core/index.html', data)

def filter_products(request):
    # Obtener todas las categorías
    categorias = CategoriaProducto.objects.all()

    # Obtener la categoría seleccionada si está presente en la URL
    categoria_id = request.GET.get('categoria')
    if categoria_id is not None and categoria_id.isdigit():
        try:
            categoria_seleccionada = CategoriaProducto.objects.get(id=categoria_id)
        except CategoriaProducto.DoesNotExist:
            raise Http404
    else:
        categoria_seleccionada = None

    # Obtener todos los productos
    productosAll = Producto.objects.all()

    # Filtrar los productos por categoría si se ha seleccionado una categoría
    if categoria_seleccionada:
        productosAll = productosAll.filter(categoria=categoria_seleccionada)

    # Ordenar los productos según la opción de ordenamiento seleccionada en la URL
    ordenar_por = request.GET.get('ordenar')
    if ordenar_por == 'precio_asc':
        productosAll = productosAll.order_by('precio')
    elif ordenar_por == 'precio_desc':
        productosAll = productosAll.order_by('-precio')

    # Paginar los productos
    page = request.GET.get('page', 1)
    paginator = Paginator(productosAll, 8)
    try:
        productos_paginados = paginator.page(page)
    except EmptyPage:
        raise Http404

    # Pasar los datos al contexto y renderizar el template
    data = {
        'listado': productos_paginados,
        'categorias': categorias,  # Incluir todas las categorías en el contexto
        'paginator': paginator,
        'categoria_seleccionada': categoria_seleccionada,
        'ordenar_por': ordenar_por,
    }
    return render(request, 'core/shop.html', data)

def shop(request):
    categorias = CategoriaProducto.objects.all()
    categoria_seleccionada = None
    productosAll = Producto.objects.all()

    categoria_id = request.GET.get('categoria')
    if categoria_id is not None and categoria_id.isdigit():
        categoria_seleccionada = get_object_or_404(CategoriaProducto, id=categoria_id)
        productosAll = productosAll.filter(categoria=categoria_seleccionada)

    ordenar_por = request.GET.get('ordenar')
    if ordenar_por == 'precio_asc':
        productosAll = productosAll.order_by('precio')
    elif ordenar_por == 'precio_desc':
        productosAll = productosAll.order_by('-precio')
    else:
        productosAll = productosAll.order_by('id')  # Orden predeterminado por ID o algún otro campo

    paginator = Paginator(productosAll, 8)
    page = request.GET.get('page')

    try:
        productos_paginados = paginator.page(page)
    except PageNotAnInteger:
        productos_paginados = paginator.page(1)
    except EmptyPage:
        productos_paginados = paginator.page(paginator.num_pages)

    data = {
        'listado': productos_paginados,
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada,
        'ordenar_por': ordenar_por,
    }
    return render(request, 'core/shop.html', data)


def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST' and 'agregar_al_carrito' in request.POST:
        # Lógica para agregar el producto al carrito
        if request.user.is_authenticated:
            carrito, created = Carrito.objects.get_or_create(usuario=request.user, producto=producto)
            if not created:
                carrito.cantidad += 1
                carrito.save()
        else:
            messages.error(request, 'Debes iniciar sesión para agregar productos al carrito.')
        return redirect('ver_carrito')  # Redirige a la página del carrito
    else:
        return redirect('index')  # Redirige a otra página si no es una solicitud POST válida

def eliminar_del_carrito(request, carrito_id):
    # Lógica para eliminar productos del carrito
    pass

def ver_carrito(request):
    if request.user.is_authenticated:
        carrito_items = Carrito.objects.filter(usuario=request.user)
        carrito_subtotales = [(item, item.producto.precio * item.cantidad) for item in carrito_items]
        total = sum(subtotal for _, subtotal in carrito_subtotales)
        
        # Obtener el stock disponible de cada producto en el carrito
        stocks_disponibles = {item.producto_id: item.producto.stock for item in carrito_items}

        context = {'carrito_subtotales': carrito_subtotales, 'total': total, 'stocks_disponibles': stocks_disponibles}
        return render(request, 'core/ver_carrito.html', context)
    else:
        # Manejar el caso de usuario no autenticado
        return redirect('login')
    

def eliminar_del_carrito(request, carrito_id):
    if request.user.is_authenticated:
        item = Carrito.objects.filter(usuario=request.user, id=carrito_id).first()
        if item:
            item.delete()
    return redirect('ver_carrito')


def actualizar_carrito(request, item_id):
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))  # Obtener la cantidad del formulario
        item = Carrito.objects.filter(usuario=request.user, id=item_id).first()
        if item:
            item.cantidad = cantidad
            item.save()
    return redirect('ver_carrito')
    
def realizar_pedido(request):
    if request.method == 'POST':
        # Lógica para procesar el pedido sin el uso de formulario
        pedido = Pedido(usuario=request.user)
        pedido.save()

        # Asociar productos del carrito al pedido
        carrito_items = Carrito.objects.filter(usuario=request.user)
        total_pedido = 0
        for item in carrito_items:
            detalle_pedido = DetallePedido.objects.create(pedido=pedido, producto=item.producto, cantidad=item.cantidad)
            
            # Calcular subtotal y sumarlo al total del pedido
            subtotal = item.producto.precio * item.cantidad
            total_pedido += subtotal

            # Eliminar el producto del carrito
            item.delete()

        # Redirigir al usuario a pagar en Mercado Pago
        return HttpResponseRedirect(reverse('comprar') + f'?pedido_id={pedido.id}&total_pedido={total_pedido}&costo_total={total_pedido}')
    
    # Obtener los productos del carrito para mostrar en la plantilla y calcular el costo total
    if request.user.is_authenticated:
        carrito_items = Carrito.objects.filter(usuario=request.user)
        costo_total = sum(item.producto.precio * item.cantidad for item in carrito_items)
    else:
        carrito_items = []
        costo_total = 0

    context = {'carrito_items': carrito_items, 'costo_total': costo_total}
    return render(request, 'core/realizar_pedido.html', context)



def comprar(request):
    # Configurar las credenciales de Mercado Pago
    access_token = settings.MERCADO_PAGO_ACCESS_TOKEN

    # Obtener el costo total y los detalles del pedido de la URL de la solicitud
    costo_total = request.GET.get('costo_total', '0')
    pedido_id = request.GET.get('pedido_id', '')

    # Obtener los detalles del pedido para obtener los nombres de los productos
    detalles_pedido = DetallePedido.objects.filter(pedido_id=pedido_id)
    items = []

    for detalle in detalles_pedido:
        producto = detalle.producto
        item = {
            "title": producto.nombre,
            "quantity": detalle.cantidad,
            "currency_id": "CLP",
            "unit_price": producto.precio
        }
        items.append(item)

    # Crear un objeto SDK de Mercado Pago
    sdk = SDK(access_token)

    # URL a la que Mercado Pago redirigirá al usuario después del pago
    back_url = request.build_absolute_uri(reverse('recibir_confirmacion'))

    # Crear la preferencia de pago con back_url y los detalles de los productos
    preference_data = {
        "items": items,  # Usar los detalles obtenidos del pedido
        "external_reference": pedido_id,  # Incluir el external_reference con el ID del pedido
        "back_urls": {
            "success": back_url,
            "failure": back_url,
            "pending": back_url
        },
        "auto_return": "approved",
        
    }
    preference_result = sdk.preference().create(preference_data)

    # Obtener la URL de pago desde la preferencia creada
    checkout_url = preference_result["response"]["init_point"]

    # Redirigir al usuario a la URL de pago en Mercado Pago
    return HttpResponseRedirect(checkout_url)


@csrf_exempt
def recibir_confirmacion(request):
    if request.method == 'GET':
        collection_id = request.GET.get('collection_id')
        collection_status = request.GET.get('collection_status')
        external_reference = request.GET.get('external_reference')

        if collection_status == 'approved' and external_reference != 'null':
            try:
                pedido = get_object_or_404(Pedido, id=external_reference)


                if pedido.estado != 'pagado':
                    pedido.estado = 'pagado'
                    pedido.save()

                    # Obtener los detalles del pedido y actualizar el stock
                    detalles_pedido = DetallePedido.objects.filter(pedido=pedido)
                    for detalle in detalles_pedido:
                        producto = detalle.producto
                        producto.stock -= detalle.cantidad
                        producto.save()

                    # Redirigir a una página de éxito con el número de pedido y total
                    return redirect(reverse('detalle_pedido', args=[pedido.id]))
                else:
                    return HttpResponse("El pedido ya se encuentra pagado.", status=200)
            except Pedido.DoesNotExist:
                return HttpResponse("Pedido no encontrado.", status=404)
        else:
            return HttpResponse("Error en la confirmación de pago.", status=400)
        

def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalles_pedido = pedido.detallepedido_set.all()
    context = {'pedido': pedido, 'detalles_pedido': detalles_pedido}
    return render(request, 'core/detalle_pedido.html', context)


#Correo
resend.api_key = settings.RESEND_API_KEY

def enviar_correo(request):
    if request.method == 'POST':
        sender = "Ferramas <onboarding@resend.dev>"
        recipient = request.POST.get('recipient')
        subject = request.POST.get('subject')
        html_content = request.POST.get('html_content')

        params = {
            "sender": sender,
            "to": [recipient],
            "subject": subject,
            "html": html_content,
        }

        try:
            email = resend.Emails.send(params)
            messages.success(request, 'Correo enviado exitosamente.')
            return redirect('enviar_correo')
        except Exception as e:
            messages.error(request, f'Error al enviar el correo: {e}')

    return render(request, 'core/enviar_correo.html')

