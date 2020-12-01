from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static

# Mapeo entre endpoints de la web / direcciones url y las vistas en el archivo views.py
urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('productos', views.ProductListView.as_view(), name='product-list'),
    path('productos/<int:pk>', views.ProductDetailView.as_view(), name='product-detail'),
    path('add_to_cart/<int:product_pk>', views.AddToCartView.as_view(), name='add-to-cart'),
    path('remove_from_cart/<int:product_pk>', views.RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('carrito/', views.PedidoDetailView.as_view(), name='pedido-detail'),
    path('pedido/<int:pedido_pk>', views.PedidoDetailView.as_view(), name='paid-pedido-detail'),
    path('checkout/<int:pk>', views.PedidoUpdateView.as_view(), name='pedido-update'),
    path('payment/', views.PaymentView.as_view(), name='payment'),
    path('complete_payment/', views.CompletePaymentView.as_view(), name='complete-payment'),
    path('registro/', views.RegistrationView.as_view(), name='register'),
    path('empty_car/', views.empty_car, name='empty-car'),
    path('no_client/', views.no_client, name='no-client'),
    path('invalid_age/', views.invalid_age, name='invalid-age'),
    path('invalid_dni/', views.invalid_dni, name='invalid-dni'),
    path('invalid_ruc/', views.invalid_ruc, name='invalid-ruc'),
    path('invalid_phone/', views.invalid_phone, name='invalid-phone'),
    path('invalid_price/', views.invalid_price, name='invalid-price'),
    path('invalid_discount/', views.invalid_discount, name='invalid-discount'),
    path('register_commerce/', views.RegisterCommerceView.as_view(),name='registar-comercio'),
    path('register_product/', views.RegisterProductView.as_view(), name='registar-producto'),
    path('edit_product/<int:pk>', views.EditProductView.as_view(), name='editar-producto'),
    path('pedidos', views.PedidoListView.as_view(), name='pedido-list'),
    path('cancel_pedido/<int:pedido_pk>', views.DeletePedido.as_view(), name='cancelar-pedido'),
    path('register_comment/<int:pedido_pk>', views.RegisterCommentView.as_view(), name='registrar-comentario'),
    path('deliver_pedido/<int:pedido_pk>', views.PedidoDeliveredView.as_view(), name='pedido-delivered')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
