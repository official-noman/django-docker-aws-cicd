from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer

# ListCreateAPIView: এটা একাই GET এবং POST হ্যান্ডেল করে!
class ProductListCreate(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer