from django.utils import timezone
from rest_framework import serializers
from app.features.product.models import Product
from main.settings import IMAGE_PATH_CLOUDINARY



class GetSingleProductSerializer(serializers.ModelSerializer):
    image_file = serializers.SerializerMethodField('get_image_file')

    class Meta:
        model = Product
        fields = [
            'id',
            'code',
            'name',
            'description',
            'image_file',
            # 'supplier_id',
            'brand',
            'measure_unit',
            'weight',
            'length',
            'width',
            'height',
            'color',
            'size',
            'dimension_unit',
            'weight_unit',
        ]

    @staticmethod
    def get_image_file(obj):
        if obj.image:
            return IMAGE_PATH_CLOUDINARY + obj.image


class ProductGetAllSerializer(serializers.ModelSerializer):
    # supplier = serializers.SerializerMethodField('get_supplier_name')

    class Meta:
        model = Product
        fields = [
            'id',
            'code',
            'name',
            'description',
            # 'supplier',
            'brand',
            'measure_unit',
            'weight',
            'length',
            'width',
            'height',
            'color',
            'size',
            'dimension_unit',
            'weight_unit',
        ]

    # @staticmethod
    # def get_supplier_name(obj):
        # return obj.supplier and obj.supplier.name


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    # supplier_id = serializers.CharField(max_length=10)

    class Meta:
        model = Product
        fields = [
            'code',
            'name',
            'description',
            # 'supplier_id',
            'brand',
            'measure_unit',
            'weight',
            'length',
            'width',
            'height',
            'color',
            'size',
            'dimension_unit',
            'weight_unit',
            'image', # stores the filename of the image
        ]