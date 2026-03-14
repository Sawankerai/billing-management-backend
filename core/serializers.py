from rest_framework import serializers
from .models import Customer, Vendor, Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    is_low_stock    = serializers.ReadOnlyField()
    is_out_of_stock = serializers.ReadOnlyField()
    category_name   = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model  = Product
        fields = '__all__'