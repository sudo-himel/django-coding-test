from django.views import generic
from django.db.models import Prefetch
from product.models import Variant, Product

from product.models import ProductVariantPrice


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


class SeeAllProduct(generic.TemplateView):
    template_name = 'products/list.html'

    def get_context_data(self, **kwargs):
        context = super(SeeAllProduct, self).get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        variant_info = {}
        for product in context['products']:
            variant_info[product.id] = {'product_id': product.id, 'product_title': product.title,
                                        'product_description': product.description, 'created_at': product.created_at,
                                        'updated_at': product.updated_at, 'variants': []}
            variant_prices = ProductVariantPrice.objects.filter(product=product)

            for pv_price in variant_prices:
                if pv_price.product_variant_one:
                    variant = pv_price.product_variant_one
                elif pv_price.product_variant_two:
                    variant = pv_price.product_variant_two
                elif pv_price.product_variant_three:
                    variant = pv_price.product_variant_three
                else:
                    variant = None
                if variant:
                    variant_info[product.id]['variants'].append({
                        'variant_title': variant.variant_title,
                        'price': pv_price.price,
                        'stock': pv_price.stock
                    })
        print(variant_info)
        context['variant_info'] = variant_info
        return context
