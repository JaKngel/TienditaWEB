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
from django.contrib.auth.decorators import login_required

# Imports de terceros
import mercadopago
import requests
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
def addCategory(request):
    if request.method == 'POST':
        formulario = CategoryForm(request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Producto almacenado correctamente")
            return redirect('addCategory')  # Redirige a la página deseada después de guardar

    data = {'form': CategoryForm()}
    return render(request, 'core/add-category.html', data)



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


# FUNCION QUNERICA QUE VALIDA EL GRUPO DEL USUARIO
def grupo_requerido(nombre_grupo):
    def decorator(view_fuc):
        @user_passes_test(lambda user: user.groups.filter(name=nombre_grupo).exists())
        def wrapper(request, *arg, **kwargs):
            return view_fuc(request,  *arg, **kwargs)
        return wrapper
    return decorator


#REGISTRO
def registro(request):
    if request.method == 'POST':
        formulario = CustomUserCreationForm(request.POST)
        if formulario.is_valid():
            user = formulario.save()
            # Comprobar si el grupo 'Cliente' existe, si no existe, crearlo
            grupo_cliente, creado = Group.objects.get_or_create(name='Cliente')
            # Asignar el usuario al grupo 'Cliente'
            user.groups.add(grupo_cliente)

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



def registroAdminVen(request):
    if request.method == 'POST':
        formulario = CustomUserCreationForm(request.POST)
        if formulario.is_valid():
            user = formulario.save()
            # Comprobar si el grupo 'Vendedor' existe, si no existe, crearlo
            grupo_vendedor, creado = Group.objects.get_or_create(name='Vendedor')
            # Asignar el usuario al grupo 'Vendedor'
            user.groups.clear()  # Limpiar los grupos para evitar duplicados
            user.groups.add(grupo_vendedor)

            messages.success(request, "Usuario Vendedor creado exitosamente.")
            return redirect('account')  # Redirige al usuario a la página de inicio o a donde sea necesario
        else:
            messages.error(request, "Error en el formulario. Por favor, corrige los errores.")

    else:
        formulario = CustomUserCreationForm()

    return render(request, 'registration/registroAdminVen.html', {'form': formulario})


def registroAdminBod(request):
    if request.method == 'POST':
        formulario = CustomUserCreationForm(request.POST)
        if formulario.is_valid():
            user = formulario.save()
            # Comprobar si el grupo 'Bodeguero' existe, si no existe, crearlo
            grupo_bodeguero, creado = Group.objects.get_or_create(name='Bodeguero')
            # Asignar el usuario al grupo 'Bodeguero'
            user.groups.clear()  # Limpiar los grupos para evitar duplicados
            user.groups.add(grupo_bodeguero)

            messages.success(request, "Usuario Bodeguero creado exitosamente.")
            return redirect('account')  # Redirige al usuario a la página de inicio o a donde sea necesario
        else:
            messages.error(request, "Error en el formulario. Por favor, corrige los errores.")

    else:
        formulario = CustomUserCreationForm()

    return render(request, 'registration/registroAdminBod.html', {'form': formulario})






#Paginas

def testimonial(request):
    # Obtener el usuario actualmente logueado
    usuario = request.user

    # Obtener todos los pedidos asociados a ese usuario
    pedidos = Pedido.objects.filter(usuario=usuario)

    # Obtener todos los detalles de pedidos asociados a esos pedidos
    detalles_pedido = DetallePedido.objects.filter(pedido__in=pedidos)

    context = {
        'detalles_pedido': detalles_pedido
    }

    return render(request, 'core/testimonial.html', context)

def why(request):
    return render(request, 'core/why.html')


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

def ver_carrito(request):
    if request.user.is_authenticated:
        carrito_items = Carrito.objects.filter(usuario=request.user)
        carrito_subtotales = [(item, item.producto.precio * item.cantidad) for item in carrito_items]
        total = sum(subtotal for _, subtotal in carrito_subtotales)
        
        # Obtener el valor del dólar desde la API de Mindicador
        productos_all = requests.get('https://mindicador.cl/api/dolar').json()
        valor_usd = productos_all['serie'][0]['valor']
        
        # Calcular el valor total del carrito en dólares
        valor_carrito = total  # Puedes usar el total que ya calculaste o modificarlo según tus necesidades
        valor_total = valor_carrito / valor_usd 

        context = {
            'carrito_subtotales': carrito_subtotales,
            'total': total,
            'valor_total_usd': round(valor_total, 2),  # Redondear el valor a dos decimales
            'total_productos': sum(item.cantidad for item in carrito_items),  # Calcular la cantidad total de productos en el carrito
        }
        return render(request, 'core/ver_carrito.html', context)
    else:
        # Manejar el caso de usuario no autenticado
        return redirect('login')



    
def realizar_pedido(request):
    if request.method == 'POST':
        # Procesar el pedido
        pedido = Pedido(usuario=request.user)
        pedido.save()

        # Asociar productos del carrito al pedido
        carrito_items = Carrito.objects.filter(usuario=request.user)
        total_pedido = 0
        for item in carrito_items:
            DetallePedido.objects.create(pedido=pedido, producto=item.producto, cantidad=item.cantidad)
            
            # Calcular subtotal y sumarlo al total del pedido
            subtotal = item.producto.precio * item.cantidad
            total_pedido += subtotal

            # Eliminar el producto del carrito
            item.delete()

        # Obtener la dirección de entrega del formulario
        shipping_user = ShippingAddress.objects.get(user=request.user)
        shipping_form = ShippingForm(request.POST, instance=shipping_user)
        if shipping_form.is_valid():
            shipping_form.save()
        else:
            messages.error(request, "Por favor, corrija los errores en el formulario de dirección de entrega.")

        # Redirigir al usuario a pagar en Mercado Pago
        return HttpResponseRedirect(reverse('comprar') + f'?pedido_id={pedido.id}&total_pedido={total_pedido}&costo_total={total_pedido}')
    
    if request.user.is_authenticated:
        # Obtener los productos del carrito para mostrar en la plantilla y calcular el costo total
        carrito_items = Carrito.objects.filter(usuario=request.user)
        costo_total = sum(item.producto.precio * item.cantidad for item in carrito_items)

        # Obtener la dirección de entrega del usuario
        shipping_user = ShippingAddress.objects.get(user=request.user)
        shipping_form = ShippingForm(instance=shipping_user)

        context = {'carrito_items': carrito_items, 'costo_total': costo_total, 'shipping_form': shipping_form}
        return render(request, 'core/realizar_pedido.html', context)
    else:
        # Manejar el caso de usuario no autenticado
        return redirect('login')
    

    


def comprar(request):
    # Configurar las credenciales de Mercado Pago
    access_token = settings.MERCADO_PAGO_ACCESS_TOKEN

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
    # Verificar si el usuario es el cliente que realizó el pedido o es un administrador
    if request.user == pedido.usuario or request.user.is_staff:
        detalles_pedido = pedido.detallepedido_set.all()
        context = {'pedido': pedido, 'detalles_pedido': detalles_pedido}
        return render(request, 'core/detalle_pedido.html', context)
    else:
        # Redirigir a una página de acceso denegado o mostrar un mensaje de error
        return redirect('login')


#Correo
resend.api_key = settings.RESEND_API_KEY


@login_required
def enviar_correo(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            sender = "Ferramas <onboarding@resend.dev>"
            recipient = "ang.rojasc@duocuc.cl"
            subject = "Contacto"
            Formulario_contacto = form.cleaned_data['Formulario_contacto']

            params = {
                "from": sender,
                "to": [recipient],
                "subject": subject,
                "html": Formulario_contacto,
            }

            try:
                email = resend.Emails.send(params)
                messages.success(request, 'Correo enviado exitosamente.')
                return redirect('enviar_correo')  
            except Exception as e:
                messages.error(request, f'Error al enviar el correo: {e}')
                return redirect('enviar_correo')  
        else:
            messages.error(request, 'Por favor, completa correctamente el CAPTCHA.')
            return redirect('enviar_correo')  
    else:
        form = ContactForm()

    return render(request, 'core/enviar_correo.html', {'form': form})

##Info user
@login_required
def account(request):
	if request.user.is_authenticated:
		# Get Current User
		current_user = Profile.objects.get(user__id=request.user.id)
		# Get Current User's Shipping Info
		shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
		
		# Get original User Form
		form = UserInfoForm(request.POST or None, instance=current_user)
		# Get User's Shipping Form
		shipping_form = ShippingForm(request.POST or None, instance=shipping_user)		
		if form.is_valid() or shipping_form.is_valid():
			# Save original form
			form.save()
			# Save shipping form
			shipping_form.save()

			messages.success(request, "¡Tu información ha sido actualizada!")
			return redirect('account')
		return render(request, "core/account.html", {'form':form, 'shipping_form':shipping_form})
	else:
		messages.success(request, "¡Debes iniciar sesión para acceder a esta página!")
		return redirect('account')
