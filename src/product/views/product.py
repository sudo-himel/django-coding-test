import json

from django.views import generic
from django.views.generic.edit import CreateView
from django.db.models import Q
from product.models import Variant, Product
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from product.models import ProductVariantPrice
from django.http import JsonResponse

from product.models import ProductVariant


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

        products = Product.objects.all()
        q_object = Q()
        if title:
            q_object &= Q(title__icontains=title)
        if variant:
            q_object &= Q(productvariant__variant_title=variant)
        if price_from:
            q_object &= Q(productvariantprice__price__gte=price_from)
        if price_to:
            q_object &= Q(productvariantprice__price__lte=price_to)
        if date:
            q_object &= Q(created_at__date=date)
        products = products.filter(q_object)
        products = products.prefetch_related('productvariantprice_set', 'productvariant_set')

        paginator = Paginator(products, 5)
        page_number = self.request.GET.get('page')
        try:
            products = paginator.page(page_number)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        context['products'] = products
        context['product_count'] = paginator.count
        context['variants'] = Variant.objects.all()
        variants_with_titles = []
        for variant in context['variants']:
            # Access related ProductVariants for the current Variant
            variant_titles = variant.productvariant_set.values_list('variant_title', flat=True).distinct()

            # Append the variant id and titles to the list
            variants_with_titles.append({
                'variant_id': variant.id,
                'variant_title': variant.title,
                'product_variant_titles': variant_titles
            })
        context['variants_with_titles'] = variants_with_titles
        # Create variant info dictionary
        variant_info = {}
        for product in products:
            variant_info[product.id] = {
                'product_id': product.id,
                'product_title': product.title,
                'product_description': product.description,
                'created_at': product.created_at,
                'updated_at': product.updated_at,
                'variants': []
            }
            for variant_price in product.productvariantprice_set.all():
                variant_titles = []
                if variant_price.product_variant_one:
                    variant_titles.append(variant_price.product_variant_one.variant_title)
                if variant_price.product_variant_two:
                    variant_titles.append(variant_price.product_variant_two.variant_title)
                if variant_price.product_variant_three:
                    variant_titles.append(variant_price.product_variant_three.variant_title)
                if variant_titles:
                    variant_info[product.id]['variants'].append({
                        'variant_title_one': variant_titles[0] if len(variant_titles) >= 1 else None,
                        'variant_title_two': variant_titles[1] if len(variant_titles) >= 2 else None,
                        'variant_title_three': variant_titles[2] if len(variant_titles) >= 3 else None,
                        'price': variant_price.price,
                        'stock': variant_price.stock
                    })

        context['variant_info'] = variant_info
        return context


class ProductCreate(CreateView):
    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body)

        product = Product.objects.create(
            title=payload['title'],
            sku=payload['sku'],
            description=payload['description']
        )

        product_variants = []
        for variant_data in payload.get('product_variant', []):
            variant = ProductVariant.objects.create(
                variant_title=variant_data['tags'][0],
                variant_id=variant_data['option'],
                product=product
            )
            product_variants.append(variant)

        price_data = payload.get('product_variant_prices', [])[0]
        price = price_data.get('price', 0)
        stock = price_data.get('stock', 0)
        product_variant_price = ProductVariantPrice.objects.create(
            price=price,
            stock=stock,
            product=product
        )
        for idx, product_variant in enumerate(product_variants):
            if idx == 0:
                product_variant_price.product_variant_one = product_variant
            elif idx == 1:
                product_variant_price.product_variant_two = product_variant
            elif idx == 2:
                product_variant_price.product_variant_three = product_variant

        product_variant_price.save()

        return JsonResponse({'success': True})


class UpdateProduct(CreateView):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        product_title = request.POST.get('product_title')
        product_description = request.POST.get('product_description')

        product, _ = Product.objects.update_or_create(
            id=product_id,
            defaults={
                'title': product_title,
                'description': product_description
            }
        )
        variant_prices = ProductVariantPrice.objects.filter(product_id=product_id)

        for i, variant_price in enumerate(variant_prices):
            variant_price.price = float(request.POST.getlist('price')[i])
            variant_price.stock = int(request.POST.getlist('stock')[i])
            variant_price.save()
        return JsonResponse({'success': True})