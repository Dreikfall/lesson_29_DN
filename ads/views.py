import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from rest_framework.generics import ListAPIView

from ads.models import Category, Ad
from ads.serializers import AdSerializer
from users.models import User


def root(request):
    return JsonResponse({
        "status": "ok"
    })


class AdListView(ListAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer

    def get(self, request, *args, **kwargs):
        cat = request.GET.get('cat')
        if cat:
            self.queryset = Ad.objects.filter(category=cat)
        text = request.GET.get('text')
        if text:
            self.queryset = Ad.objects.filter(name__contains=text)
        location = request.GET.get('location')
        if location:
            self.queryset = Ad.objects.filter(author__locations__name__icontains=location)
        price_from = request.GET.get('price_from')
        price_to = request.GET.get('price_to')
        if price_from:
            self.queryset = Ad.objects.filter(price__gte=price_from)
        if price_to:
            self.queryset = Ad.objects.filter(price__lte=price_to)
        return super().get(self, request, *args, **kwargs)


class AdDetailView(DetailView):
    model = Ad

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        ad = self.get_object()
        return JsonResponse(
            {
                "id": ad.id,
                "name": ad.name,
                "author": ad.author.username,
                "price": ad.price,
                "description": ad.description,
                "is_published": ad.is_published,
                "image": ad.image.url,
                "category": ad.category.name
            }
        )


@method_decorator(csrf_exempt, name='dispatch')
class AdImageView(UpdateView):
    model = Ad
    fields = ['image']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.object.image = request.FILES['image']
        self.object.save()

        return JsonResponse({
            "id": self.object.id,
            "name": self.object.name,
            "author": self.object.author.username,
            "price": self.object.price,
            "description": self.object.description,
            "is_published": self.object.is_published,
            "image": self.object.image.url,
            "category": self.object.category.name
        })


@method_decorator(csrf_exempt, name='dispatch')
class AdCreateView(CreateView):
    model = Ad
    fields = ["author", "name", "price", "description", "is_published", "category"]

    def post(self, request, *args, **kwargs):
        ad_data = json.loads(request.body)

        author = get_object_or_404(User, id=ad_data['author'])
        category = get_object_or_404(Category, id=ad_data['category'])

        ad = Ad.objects.create(
            name=ad_data['name'],
            author=author,
            category=category,
            price=ad_data['price'],
            description=ad_data['description'],
            is_published=ad_data['is_published'],
        )
        ad.save()
        return JsonResponse(
            {
                "id": ad.id,
                "name": ad.name,
                "author": ad.author.username,
                "price": ad.price,
                "description": ad.description,
                "is_published": ad.is_published,
                "image": ad.image.url if ad.image else 'Картинки нет',
                "category": ad.category.id
            }
        )


@method_decorator(csrf_exempt, name='dispatch')
class AdUpdateView(UpdateView):
    model = Ad
    fields = ["author", "name", "price", "description", "is_published", "category"]

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        ad_data = json.loads(request.body)

        author = get_object_or_404(User, id=ad_data['author'])
        category = get_object_or_404(Category, id=ad_data['category'])

        self.object.name = ad_data['name']
        self.object.author = author
        self.object.category = category
        self.object.price = ad_data['price']
        self.object.description = ad_data['description']
        self.object.is_published = ad_data['is_published']
        self.object.save()
        return JsonResponse(
            {
                "id": self.object.id,
                "name": self.object.name,
                "author": self.object.author.username,
                "price": self.object.price,
                "description": self.object.description,
                "is_published": self.object.is_published,
                "image": self.object.image.url if self.object.image else 'Картинки нет',
                "category": self.object.category.id
            }
         )


@method_decorator(csrf_exempt, name='dispatch')
class AdDeleteView(DeleteView):
    model = Ad
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({'status': 'ok'}, status=200)


class CategoryListView(ListView):
    model = Category
    queryset = Category.objects.all()

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)

        self.object_list = self.object_list.order_by('name')

        categories = []
        for category in self.object_list:
            categories.append(
                {
                    "id": category.id,
                    "name": category.name,
                }
            )
        return JsonResponse(categories, safe=False)


class CategoryDetailView(DetailView):
    model = Category

    def get(self, request, *args, **kwargs):
        category = self.get_object()

        return JsonResponse({
            "id": category.id,
            "name": category.name,
        })


@method_decorator(csrf_exempt, name="dispatch")
class CategoryCreateView(CreateView):
    model = Category
    fields = ["name"]

    def post(self, request, *args, **kwargs):
        category_data = json.loads(request.body)

        category = Category()
        category.name = category_data["name"]

        category.save()

        return JsonResponse(
            {
                "id": category.id,
                "name": category.name,

            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class CategoryUpdateView(UpdateView):
    model = Category
    fields = ["name"]

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        category_data = json.loads(request.body)
        self.object.name = category_data["name"]
        self.object.save()
        return JsonResponse(
            {
                "id": self.object.id,
                "name": self.object.name,
            }
        )


@method_decorator(csrf_exempt, name='dispatch')
class CategoryDeleteView(DeleteView):
    model = Category
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({'status': 'ok'}, status=200)
