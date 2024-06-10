from rest_framework import serializers
from .models import ChunkedFile, MasterFile


class MasterFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterFile
        fields = ['id', 'file_name', 'md5_checksum',
                  'number_of_chunks']


class ChunkedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChunkedFile
        fields = '__all__'
