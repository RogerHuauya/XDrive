from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import (MasterFile, ChunkedFile)
import hashlib
from django.conf import settings
from math import ceil


def get_number_of_chunks(file_size, chunk_size):
    return ceil(file_size / chunk_size)


class FileUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.master_file_url = reverse('masterfile-list')
        self.chunked_file_url = reverse('chunkedfile-list')
        self.test_file_name = 'big_file.txt'
        self.chunk_size = settings.CHUNK_SIZE
        self.test_file_content = b"Master file content" * self.chunk_size * 2
        self.md5_checksum = hashlib.md5(self.test_file_content).hexdigest()

    def test_can_create_empty_masterfile(self):
        number_of_chunks = get_number_of_chunks(len(self.test_file_content), self.chunk_size)
        response = self.client.post(self.master_file_url, {
            'file_name': self.test_file_name,
            'md5_checksum': self.md5_checksum,
            'number_of_chunks': number_of_chunks
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MasterFile.objects.count(), 1)
        master_file = MasterFile.objects.first()
        self.assertEqual(master_file.file_name, self.test_file_name)
        self.assertEqual(master_file.md5_checksum, self.md5_checksum)
        self.assertEqual(master_file.number_of_chunks, number_of_chunks)
        self.assertEqual(master_file.is_complete(), False)

    def tearDown(self):
        MasterFile.objects.all().delete()
