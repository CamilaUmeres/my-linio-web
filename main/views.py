from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, FormView, TemplateView, View, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.db.models import F
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.db.models import Q
from random import randint
from django.forms import ImageField

from .models import *
from .forms import *

# Create your views here.
# Vista principal (default)
class HomePageView(TemplateView):
    # Ubicacion del template dentro del proyecto (./main/templates/main/home.html)
    template_name = "main/home.html"
    puede_registrar_comercio = False
    puede_registrar_producto = False
    tiene_pedido = False

    # Carga la pagina
    def get(self, request, *args, **kwargs):
        # Es el perfil comerciante?
        user = request.user
        # Se consulta si el comerciante ha registrado su comercio
        try:
            perfil = Profile.objects.get(user=user)
            comerciante = Comerciante.objects.get(user_profile=perfil)
            print(Proveedor.objects.filter(
                comerciante=comerciante))
            self.puede_registrar_comercio = Proveedor.objects.filter(
                comerciante=comerciante).count() == 0
            self.puede_registrar_producto = not self.puede_registrar_comercio
        except Exception as e:
            self.puede_registrar_comercio = False
            self.puede_registrar_producto = False

        # Se consulta si el cliente tiene pedido
        try:
            cliente = Cliente.objects.get(user_profile=perfil)
            self.tiene_pedido = Pedido.objects.filter(
                cliente=cliente).count() >= 1
        except Exception as e:
            self.tiene_pedido = False

        # Se consulta si el colaborador tiene pedidos por enviar
        try:
            colaborador = Colaborador.objects.get(user_profile=perfil)
            self.tiene_por_entregar = Pedido.objects.filter(
                repartidor=colaborador).count() >= 1
        except Exception as e:
            self.tiene_por_entregar = False

        return super().get(self,request,*args,**kwargs)


    # Carga los elementos de la pagina
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Carga los ultimos 5 productos añadidos
        context['latest_products'] = Producto.objects.all().order_by('-id')[:5]
        context['puede_registrar_comercio'] = self.puede_registrar_comercio
        context['puede_registrar_producto'] = self.puede_registrar_producto
        context['tiene_pedido'] = self.tiene_pedido
        context['tiene_por_entregar'] = self.tiene_por_entregar

        return context



# Vista de pedidos (vista tipo lista)
class PedidoListView(ListView):
    # La lista se basa en el modelo producto
    model = Pedido

    # Filtro de productos
    def get_queryset(self):
        perfil = Profile.objects.filter(user=self.request.user)[0]
        try:
            cliente = Cliente.objects.filter(user_profile=perfil)[0]
        except Exception as e:
            cliente = None

        try:
            self.colaborador = Colaborador.objects.filter(user_profile=perfil)[0]
        except Exception as e:
            self.colaborador = None

        object_list = Pedido.objects.filter(
            Q(cliente=cliente) | Q(repartidor=self.colaborador),
            Q(estado='PAG') | Q(estado='ENT'))
        return object_list

    def get_context_data(self, **kwargs):
        context = super(PedidoListView, self).get_context_data(**kwargs)
        if(self.colaborador is None):
            context['colaborador'] = ""
        else:
            context['colaborador'] = self.colaborador
        return context


# Vista de productos (vista tipo lista)
class ProductListView(ListView):
    # La lista se basa en el modelo producto
    model = Producto
    selectedCategory = ""

    # Filtro de productos
    def get_queryset(self):
        # Obtiene filtro
        query = self.request.GET.get('q')
        # Filtrado
        if query is not None:
            # Por categoria
            if(query=="buscar_por_categoria"):
                query = self.request.GET.get('categoria')
                self.selectedCategory = query
                categoria_id = Categoria.objects.filter(nombre=query)[0]
                object_list = Producto.objects.filter(categoria=categoria_id)
            # Por key word
            else:
                object_list = Producto.objects.filter(nombre__icontains=query)
            return object_list
        else:
            return Producto.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context['categoria_list'] = Categoria.objects.all()
        context['categoria_selected'] = self.selectedCategory
        return context


# Detalle del producto (vista tipo detalle)
class ProductDetailView(DetailView):
    # El detalle se basa en el modelo producto
    model = Producto

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        # Extraemos el modelo proveedor del usuario
        try:
            perfil = Profile.objects.get(user=self.request.user)
            comerciante = Comerciante.objects.get(user_profile=perfil)
            proveedor = Proveedor.objects.get(comerciante=comerciante)
            # Extreamos el modelo proveedor del producto
            prov_producto = Proveedor.objects.get(producto=self.object)
            # Si son el mismo, se puede editar este producto
            context['puede_editar_producto'] = proveedor == prov_producto
        except Exception as e:
            context['puede_editar_producto'] = False
        return context



# Vista de registro (vista tipo formulario)
class RegistrationView(FormView):
    # Utiliza el template register.html dentro de ./main/templates/registration/register.html
    template_name = 'registration/register.html'
    # Usa el formulario UserForm como base
    form_class = UserForm
    # Carga el template
    success_url = reverse_lazy('home')

    # Validacion del formulario
    def form_valid(self, form):
        # This method is called when valid from data has been POSTed
        # It should return an HttpResponse

        # Create User
        # Cleaned_data valida la informacion (longitudes y campos requeridos)
        username = form.cleaned_data['username']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password1']

        # Se crea el usuario
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
        # Se guarda en la base de datos
        user.save()

        # Create Profile
        documento_identidad = form.cleaned_data['documento_identidad']
        fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
        estado = form.cleaned_data['estado']
        genero = form.cleaned_data['genero']

        user_profile = Profile.objects.create( user=user, documento_identidad=documento_identidad, fecha_nacimiento=fecha_nacimiento, estado=estado, genero=genero)
        try:
            user_profile.validate_data()
        except ValidationError as e:
            print("Error: ", e)
            user_profile.delete()
            if("Must be over 18" in str(e)):
                return redirect('/invalid_age/')
            if("DNI must be 8 characters" in str(e)):
                return redirect('/invalid_dni/')

        # Se guarda en la base de datos
        user_profile.save()

        # Create Colaborador if needed
        # Solo se crea si el usuario es colaborador
        is_colaborador = form.cleaned_data['is_colaborador']
        if is_colaborador:
            reputacion = form.cleaned_data['reputacion']
            colaborador = Colaborador.objects.create(user_profile=user_profile, reputacion=reputacion)

            # Handle special attribute
            cobertura_entrega = form.cleaned_data['cobertura_entrega']
            # La cobertura debe ser valida para la tabla Localizacion
            cobertura_entrega_set = Localizacion.objects.filter(pk=cobertura_entrega.pk)
            colaborador.cobertura_entrega.set(cobertura_entrega_set)

            colaborador.save()

        # Create Cliente if needed
        is_cliente = form.cleaned_data['is_cliente']
        if is_cliente:
            cliente = Cliente.objects.create(user_profile=user_profile)

            # Handle special attribute
            preferencias = form.cleaned_data['preferencias']
            # Las preferencias deben estar en la tabla Categoria
            preferencias_set = Categoria.objects.filter(pk=preferencias.pk)
            cliente.preferencias.set(preferencias_set)

            cliente.save()


        # Create Comerciante if needed
        is_comerciante = form.cleaned_data['is_comerciante']
        if is_comerciante:
            comerciante = Comerciante.objects.create(user_profile=user_profile)
            comerciante.save()

        # Login the user
        login(self.request, user)

        return super().form_valid(form)


# Vista agregar a carrito
class AddToCartView(View):
    def get(self, request, product_pk):
        # Obten el cliente
        try:
            user_profile = Profile.objects.get(user=request.user)
            cliente = Cliente.objects.get(user_profile=user_profile)
        except Exception as e:
            return redirect('/no_client/')
        # Obtén el producto que queremos añadir al carrito
        producto = Producto.objects.get(pk=product_pk)
        # Obtén/Crea un/el pedido en proceso (EP) del usuario
        pedido, _  = Pedido.objects.get_or_create(cliente=cliente, estado='EP')
        # Obtén/Crea un/el detalle de pedido
        detalle_pedido, created = DetallePedido.objects.get_or_create(
            producto=producto,
            pedido=pedido,
        )

        # Si el detalle de pedido es creado la cantidad es 1
        # Si no sumamos 1 a la cantidad actual
        if created:
            detalle_pedido.cantidad = 1
        else:
            detalle_pedido.cantidad = F('cantidad') + 1
        # Guardamos los cambios
        detalle_pedido.save()
        # Recarga la página
        return redirect(request.META['HTTP_REFERER'])


# Vista remover del carrito
class RemoveFromCartView(View):
    def get(self, request, product_pk):
        # Obten el cliente
        user_profile = Profile.objects.get(user=request.user)
        cliente = Cliente.objects.get(user_profile=user_profile)
        # Obtén el producto que queremos añadir al carrito
        producto = Producto.objects.get(pk=product_pk)
        # Obtén/Crea un/el pedido en proceso (EP) del usuario
        pedido, _  = Pedido.objects.get_or_create(cliente=cliente, estado='EP')
        # Obtén/Crea un/el detalle de pedido
        detalle_pedido = DetallePedido.objects.get(
            producto=producto,
            pedido=pedido,
        )
        # Si la cantidad actual menos 1 es 0 elmina el producto del carrito
        # Si no restamos 1 a la cantidad actual
        if detalle_pedido.cantidad - 1 == 0:
            detalle_pedido.delete()
        else:
            detalle_pedido.cantidad = F('cantidad') - 1
            # Guardamos los cambios
            detalle_pedido.save()
        # Recarga la página
        return redirect(request.META['HTTP_REFERER'])


# Vista detalle del pedido
class PedidoDetailView(DetailView):
    model = Pedido

    def get(self, request, pedido_pk=-1, *args, **kwargs):
        try:
            self.pedido_pk = pedido_pk
            self.es_carrito = self.pedido_pk == -1
            return super().get(self,request,*args,**kwargs)
        except Exception as e:
            print("Error: ", e)
            return redirect('../empty_car/')

    def get_object(self):
        if(not self.es_carrito):
            # Obtén pedido
            pedido  = Pedido.objects.get(pk=self.pedido_pk)
            self.comentario = Comment.objects.filter(
            usuario=self.request.user,pedido=pedido).order_by('-id')
            return pedido
        else:
            # Obten el cliente
            user_profile = Profile.objects.get(user=self.request.user)
            cliente = Cliente.objects.get(user_profile=user_profile)
            # Obtén/Crea un/el pedido en proceso (EP) del usuario
            pedido  = Pedido.objects.get(cliente=cliente, estado='EP')
            return pedido

    # Cargar pagina
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener el detalle de los objetos
        context['detalles'] = context['object'].detallepedido_set.all()
        context['es_carrito'] = self.es_carrito
        if(not self.es_carrito):
            context['comments'] =self.comentario
        return context



# Vista actualizar pedido
class PedidoUpdateView(UpdateView):
    model = Pedido
    # Campos para actualizar
    fields = ['ubicacion', 'direccion_entrega','comprobante']
    success_url = reverse_lazy('payment')

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        self.object = form.save(commit=False)
        # Calculo de tarifa
        self.object.tarifa = randint(5, 20)
        return super().form_valid(form)

# Vista para pago
class PaymentView(TemplateView):
    # Se utiliza el template payment.html
    template_name = "main/payment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obten el cliente
        user_profile = Profile.objects.get(user=self.request.user)
        cliente = Cliente.objects.get(user_profile=user_profile)
        context['pedido'] = Pedido.objects.get(cliente=cliente, estado='EP')

        return context

# Vista para completar pago
class CompletePaymentView(View):
    def get(self, request):
        # Obten el cliente
        user_profile = Profile.objects.get(user=request.user)

        cliente = Cliente.objects.get(user_profile=user_profile)

        # Obtén/Crea un/el pedido en proceso (EP) del usuario
        pedido = Pedido.objects.get(cliente=cliente, estado='EP')

        # Cambia el estado del pedido
        pedido.estado = 'PAG'
        # Asignacion de repartidor
        pedido.repartidor = Colaborador.objects.filter(~Q(user_profile=user_profile)).order_by('?').first()
        # Guardamos los cambios
        pedido.save()
        messages.success(request, 'Gracias por tu compra! Un repartidor ha sido asignado a tu pedido.')
        return redirect('home')


# Vista de registro de comercio (vista tipo formulario)
class RegisterCommerceView(FormView):
    # Utiliza el template register.html dentro de ./main/templates/registration/register.html
    template_name = 'registration/register.html'
    # Usa el formulario UserForm como base
    form_class = CommerceForm
    # Carga el template
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super(RegisterCommerceView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    # Validacion del formulario
    def form_valid(self, form):
        # This method is called when valid from data has been POSTed
        # It should return an HttpResponse
        perfil = Profile.objects.get(user=form.user)
        comerciante = Comerciante.objects.get(user_profile=perfil)

        # Create Commerce (Proveedor)
        # Cleaned_data valida la informacion (longitudes y campos requeridos)
        ruc = form.cleaned_data['ruc']
        razon_social = form.cleaned_data['razon_social']
        telefono = form.cleaned_data['telefono']

        # Se crea el proveedor
        provider = Proveedor.objects.create(ruc=ruc, razon_social=razon_social, telefono=telefono, comerciante=comerciante)

        try:
            provider.validate_data()
        except ValidationError as e:
            print("Error: ", e)
            provider.delete()
            if("Phone must be 9 characters" in str(e)):
                return redirect('/invalid_phone/')
            if("RUC must be 11 characters" in str(e)):
                return redirect('/invalid_ruc/')
        # Se guarda en la base de datos
        provider.save()

        return super().form_valid(form)



# Vista de registro de producto (vista tipo formulario)
class RegisterProductView(FormView):
    # Utiliza el template register.html dentro de ./main/templates/registration/register.html
    template_name = 'registration/register.html'
    # Usa el formulario UserForm como base
    form_class = ProductForm
    # Carga el template
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super(RegisterProductView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    # Validacion del formulario
    def form_valid(self, form):
        # This method is called when valid from data has been POSTed
        # It should return an HttpResponse
        perfil = Profile.objects.get(user=form.user)
        comerciante = Comerciante.objects.get(user_profile=perfil)
        proveedor = Proveedor.objects.get(comerciante=comerciante)

        # Create Producto
        # Cleaned_data valida la informacion (longitudes y campos requeridos)
        categoria = form.cleaned_data['categoria']
        nombre = form.cleaned_data['nombre']
        descripcion = form.cleaned_data['descripcion']
        precio = form.cleaned_data['precio']
        estado = form.cleaned_data['estado']
        descuento = form.cleaned_data['descuento']
        imagen = form.cleaned_data['imagen']

        # Se crea el producto
        try:
            producto = proveedor.register_product(categoria,nombre,descripcion,precio,estado,descuento)
            ProductoImage.objects.create(product=producto, image=imagen)
        except Exception as e:
            print("error2")
            print(e)
            if("Price must be over 0" in str(e)):
                return redirect('/invalid_price/')
            if("Discount must be over 0" in str(e)):
                return redirect('/invalid_discount/')


        return super().form_valid(form)


# Vista de registro de producto (vista tipo formulario)
class EditProductView(UpdateView):
    model = Producto
    # Campos para actualizar
    fields = ['categoria', 'nombre', 'descripcion', 'precio', 'estado', 'descuento']


    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        self.object = form.save(commit=False)
        return super().form_valid(form)


    def get_success_url(self):
      productid=self.kwargs['pk']
      return reverse_lazy('product-detail', kwargs={'pk': productid})


# Vista eliminar pedido
class DeletePedido(View):
    def get(self, request, pedido_pk):
        # Obten el cliente
        user_profile = Profile.objects.get(user=request.user)
        cliente = Cliente.objects.get(user_profile=user_profile)
        # Obtén el pedido que se eliminara
        pedido  = Pedido.objects.get(cliente=cliente, estado='PAG')
        pedido.cancelar_pedido()
        messages.success(request, 'Tu pedido ha sido cancelado correctamente.')

        return redirect('home')


# Vista registrar comentario
class RegisterCommentView(FormView):
    # Utiliza el template register.html dentro de ./main/templates/registration/register.html
    template_name = 'registration/register.html'
    # Usa el formulario UserForm como base
    form_class = CommentForm

    def get_form_kwargs(self):
        kwargs = super(RegisterCommentView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        kwargs.update({'pedido_pk': self.kwargs['pedido_pk']})
        return kwargs

    # Validacion del formulario
    def form_valid(self, form):
        # Informacion de usuario y pedido
        usuario = form.user
        pedido = Pedido.objects.get(pk=form.pedido_pk)[0]
        # Create Comment
        # Cleaned_data valida la informacion (longitudes y campos requeridos)
        body = form.cleaned_data['body']

        # Se crea el producto
        comentario = Comment.objects.create(pedido=pedido,usuario=usuario,body=body)

        return super().form_valid(form)

    def get_success_url(self):
      pedidoid=self.kwargs['pedido_pk']
      return reverse_lazy('paid-pedido-detail', kwargs={'pedido_pk': pedidoid})


# Vista entregar pedido
class PedidoDeliveredView(View):
    def get(self, request, pedido_pk):
        # Obtén/Crea un/el pedido
        pedido = Pedido.objects.get(pk=pedido_pk)
        pedido.estado = 'ENT'
        # Guardamos los cambios
        pedido.save()
        # Recarga la página
        return redirect(request.META['HTTP_REFERER'])


def empty_car(request):
    return render(request, 'main/custom_alert.html',{"mensaje":"Agregue objetos al carrito primero"})


def invalid_age(request):
    return render(request, 'main/custom_alert.html',{"mensaje":"Debe ser mayor de 18 años para registrarse"})

def invalid_dni(request):
    return render(request, 'main/custom_alert.html',{"mensaje":"El DNI debe tener 8 caracteres"})

def invalid_ruc(request):
    return render(request, 'main/custom_alert.html',{"mensaje":"El RUC debe tener 11 caracteres"})

def invalid_phone(request):
    return render(request, 'main/custom_alert.html',{"mensaje":"El numero de telefono debe tener 9 caracteres"})

def invalid_price(request):
    return render(request, 'main/custom_alert.html',{"mensaje":"El precio debe ser mayor a 0"})

def invalid_discount(request):
    return render(request, 'main/custom_alert.html',{"mensaje":"El descuento debe ser mayor a 0 y menor a 1"})

def no_client(request):
    return render(request, 'main/custom_alert.html',{"mensaje":"No tiene usuario tipo cliente"})
