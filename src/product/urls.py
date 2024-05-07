from django.urls import path
from django.views.generic import TemplateView

from product.views.product import CreateProductView
from product.views.variant import VariantView, VariantCreateView, VariantEditView

from product.views.product import SeeAllProduct

from product.views.product import ProductCreate

from product import views

from product.views.product import UpdateProduct

app_name = "product"





urlpatterns = [
    # Variants URLs
    path('variants/', VariantView.as_view(), name='variants'),
    path('variant/create', VariantCreateView.as_view(), name='create.variant'),
    path('variant/<int:id>/edit', VariantEditView.as_view(), name='update.variant'),

    # Products URLs
    path('create/', CreateProductView.as_view(), name='create.product'),
    path('list/', SeeAllProduct.as_view(), name='list.product'),
    path('create/product-save/', ProductCreate.as_view(), name='product-save.product'),
    path('list/update/<id>/', UpdateProduct.as_view(), name='update.product')
]
