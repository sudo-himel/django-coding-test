from django.views import generic
from django.db.models import Q
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
        title = self.request.GET.get('title')
        variant = self.request.GET.get('variant')
        price_from = self.request.GET.get('price_from')
        price_to = self.request.GET.get('price_to')
        date = self.request.GET.get('date')
        print(title, variant, price_to, price_from, date)

        # Filter products queryset based on parameters
        products = Product.objects.all()
        if title:
            products = products.filter(title__icontains=title)
        if variant:
            products = products.filter(productvariant__variant__title__icontains=variant)
        if price_from:
            q_price_from = Q(productvariantprice__price__gte=price_from)
            products = products.filter(q_price_from)
        if price_to:
            q_price_to = Q(productvariantprice__price__lte=price_to)
            products = products.filter(q_price_to)
        if date:
            products = products.filter(created_at__date=date)

        # Prefetch related variant prices and variants
        products = products.prefetch_related('productvariantprice_set', 'productvariant_set')

        context['products'] = products
        context['product_count'] = products.count()
        context['variants'] = Variant.objects.all()

        # Create variant info dictionary
        variant_info = {}
        for product in context['products']:
            variant_info[product.id] = {
                'product_id': product.id,
                'product_title': product.title,
                'product_description': product.description,
                'created_at': product.created_at,
                'updated_at': product.updated_at,
                'variants': []
            }
            for variant_price in product.productvariantprice_set.all():
                variant = None
                if variant_price.product_variant_one:
                    variant = variant_price.product_variant_one
                elif variant_price.product_variant_two:
                    variant = variant_price.product_variant_two
                elif variant_price.product_variant_three:
                    variant = variant_price.product_variant_three
                if variant:
                    variant_info[product.id]['variants'].append({
                        'variant_title': variant.variant_title,
                        'price': variant_price.price,
                        'stock': variant_price.stock
                    })

        context['variant_info'] = variant_info
        return context

