from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import (MasterFile, ChunkedFile)
from .utils import get_number_of_chunks
import hashlib
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone


class Creator:
    @staticmethod
    def post_master_file(api_client, master_file_url,
                         file_name, md5_checksum, number_of_chunks):
        response = api_client.post(master_file_url, {
            'file_name': file_name,
            'md5_checksum': md5_checksum,
            'number_of_chunks': number_of_chunks
        }, format='json')
        return response

    @staticmethod
    def post_chunked_file(api_client, chunked_file_url, master_file_id,
                          chunk_file_name, chunk, chunk_number,
                          chunk_md5_checksum, upload_time):
        response = api_client.post(chunked_file_url, {
            'master_file': master_file_id,
            'file': SimpleUploadedFile(chunk_file_name, chunk),
            'chunk_number': chunk_number,
            'md5_checksum': chunk_md5_checksum,
            'uploaded_at': upload_time
        }, format='multipart')
        return response

    @staticmethod
    def get_merge_chunks(api_client, merge_chunks_url, master_file_id):
        url = f'{merge_chunks_url}?master_file_id={master_file_id}'
        response = api_client.get(url)
        return response


class FileUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.master_file_url = reverse('masterfile-list')
        self.chunked_file_url = reverse('chunkedfile-list')
        self.merge_chunks_url = reverse('chunkedfile-merge-chunks')
        self.test_file_name = 'big_file.txt'
        self.chunk_size = settings.CHUNK_SIZE
        self.test_file_content = b"Master file content" * self.chunk_size * 2
        self.md5_checksum = hashlib.md5(self.test_file_content).hexdigest()

    def test_get_number_of_chunks_is_correct_for_full_chunks_only(self):
        """
        Test if the number of chunks is correctly calculated
        for files with only full chunks.
        This test ensures that when the file size is perfectly
         divisible by the chunk size,
        the number of chunks is calculated correctly.

        Number of chunks: 38 => [#####][#####]....[#####]
        """
        number_of_chunks = get_number_of_chunks(len(self.test_file_content),
                                                self.chunk_size)
        expected_number_of_chunks = 38
        self.assertEqual(number_of_chunks, expected_number_of_chunks)

    def test_get_number_of_chunks_is_correct_for_1_non_full_chunk(self):
        """
        Test if the number of chunks is correctly calculated
        for files with one non-full chunk.
        This test verifies that when there is a remaining
        portion of the file after dividing
        it into chunks, an additional chunk is accounted for.

        Number of chunks: 39 => [#####][#####]....[#####][#    ]
        """
        self.test_file_content += b"a"
        number_of_chunks = get_number_of_chunks(
            len(self.test_file_content), self.chunk_size)
        expected_number_of_chunks = 39
        self.assertEqual(number_of_chunks, expected_number_of_chunks)

    def test_can_create_empty_masterfile(self):
        """
        Test if an empty master file can be successfully created.
        This test verifies that an empty master file can be
        created in the system with the
        correct metadata and initial state.
        """
        number_of_chunks = get_number_of_chunks(
            len(self.test_file_content), self.chunk_size)
        response = Creator.post_master_file(
                self.client,
                self.master_file_url,
                self.test_file_name,
                self.md5_checksum,
                number_of_chunks
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MasterFile.objects.count(), 1)
        master_file = MasterFile.objects.first()
        self.assertEqual(master_file.file_name, self.test_file_name)
        self.assertEqual(master_file.md5_checksum, self.md5_checksum)
        self.assertEqual(master_file.number_of_chunks, number_of_chunks)
        self.assertEqual(master_file.is_complete(), False)

    def test_can_create_one_chunk_for_masterfile(self):
        """
        Test if a single chunk can be successfully
        created and associated
        with a master file.

        This test verifies that a single chunk of a
        file can be successfully uploaded and
        associated with its corresponding master file
        in the system.
        """
        number_of_chunks = get_number_of_chunks(
            len(self.test_file_content), self.chunk_size)
        response = Creator.post_master_file(
                self.client,
                self.master_file_url,
                self.test_file_name,
                self.md5_checksum,
                number_of_chunks
            )

        master_file = MasterFile.objects.first()
        chunk = self.test_file_content[0: self.chunk_size]

        upload_time = timezone.now()
        chunk_md5_checksum = hashlib.md5(chunk).hexdigest()
        chunk_file_name = f"test-chunk-{master_file.id}-0.txt"
        response = Creator.post_chunked_file(
                self.client,
                self.chunked_file_url,
                master_file.id,
                chunk_file_name,
                chunk,
                0,
                chunk_md5_checksum,
                upload_time
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ChunkedFile.objects.count(), 1)

        chunked_file = ChunkedFile.objects.filter(
            master_file=master_file.id,
            chunk_number=0).first()

        self.assertIsNotNone(chunked_file)
        self.assertEqual(chunked_file.master_file.id, master_file.id)
        self.assertEqual(chunked_file.file.read(), chunk)
        self.assertEqual(chunked_file.chunk_number, 0)
        self.assertEqual(chunked_file.md5_checksum, chunk_md5_checksum)

    def test_can_create_all_chunks_for_masterfile(self):
        """
        Test if all chunks can be successfully created and associated
        with a master file.

        This test verifies that all chunks of a file can be
        successfully uploaded and
        associated with their corresponding master file in the system.
        """
        number_of_chunks = get_number_of_chunks(
            len(self.test_file_content),
            self.chunk_size)

        Creator.post_master_file(
            self.client,
            self.master_file_url,
            self.test_file_name,
            self.md5_checksum,
            number_of_chunks
        )

        master_file = MasterFile.objects.first()
        chunks = [self.test_file_content[
                i * self.chunk_size: (i+1) * self.chunk_size
            ] for i in range(number_of_chunks)]

        current_number_of_posted_chunks = 0
        chunk_file_prefix = "test-chunk-{}-{}.txt"

        for chunk in chunks:
            upload_time = timezone.now()
            chunk_md5_checksum = hashlib.md5(chunk).hexdigest()
            chunk_file_name = chunk_file_prefix.format(
                master_file.id,
                current_number_of_posted_chunks
            )

            response = Creator.post_chunked_file(
                self.client,
                self.chunked_file_url,
                master_file.id,
                chunk_file_name,
                chunk,
                current_number_of_posted_chunks,
                chunk_md5_checksum,
                upload_time
            )

            current_number_of_posted_chunks += 1

            self.assertEqual(response.status_code,
                             status.HTTP_201_CREATED)
            self.assertEqual(ChunkedFile.objects.count(),
                             current_number_of_posted_chunks)

            chunked_file = ChunkedFile.objects.filter(
                master_file=master_file.id,
                chunk_number=current_number_of_posted_chunks-1).first()

            self.assertIsNotNone(chunked_file)
            self.assertEqual(chunked_file.master_file.id,
                             master_file.id)
            self.assertEqual(chunked_file.file.read(),
                             chunk)
            self.assertEqual(chunked_file.chunk_number,
                             current_number_of_posted_chunks-1)
            self.assertEqual(chunked_file.md5_checksum,
                             chunk_md5_checksum)

    def test_can_merge_chunked_files(self):
        """
        Test if chunked files can be successfully uploaded,
        merged, and the merged content matches the original
        content with the correct MD5 checksum.

        Setup:
        - Calculate the number of chunks based on the size of
          `test_file_content` and `chunk_size`.
        - Create a MasterFile instance by posting metadata
          using `post_master_file`.
        - Divide `test_file_content` into chunks based
          on `chunk_size`.

        Execution:
        - Upload each chunk using `post_chunked_file`, associating
          them with the created MasterFile.
        - Call `get_merge_chunks` to initiate the merging process
          for uploaded chunks.

        Assertions:
        - Verify that the HTTP response status code from
         `get_merge_chunks` is `200 OK`.
        - Retrieve and compare the merged content (`merged_content`)
          with `test_file_content`.
        - Compute the MD5 checksum of `merged_content` and compare
          it with the expected checksum (`md5_checksum`) of the MasterFile.
        """
        number_of_chunks = get_number_of_chunks(
            len(self.test_file_content),
            self.chunk_size)

        # Create a MasterFile instance
        response = Creator.post_master_file(
            self.client,
            self.master_file_url,
            self.test_file_name,
            self.md5_checksum,
            number_of_chunks
        )

        master_file = MasterFile.objects.first()
        chunks = [self.test_file_content[
                  i * self.chunk_size: (i + 1) * self.chunk_size
                  ] for i in range(number_of_chunks)]

        for i, chunk in enumerate(chunks):
            upload_time = timezone.now()
            chunk_md5_checksum = hashlib.md5(chunk).hexdigest()
            chunk_file_name = f"test-chunk-{master_file.id}-{i}.txt"

            response = Creator.post_chunked_file(
                self.client,
                self.chunked_file_url,
                master_file.id,
                chunk_file_name,
                chunk,
                i,
                chunk_md5_checksum,
                upload_time
            )

        response = Creator.get_merge_chunks(
            self.client,
            self.merge_chunks_url,
            master_file.id
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        master_file.refresh_from_db()

        self.assertTrue(master_file.file)
        with master_file.file.open('rb') as f:
            merged_content = f.read()

        self.assertEqual(merged_content, self.test_file_content)

        obtained_md5 = hashlib.md5(merged_content).hexdigest()
        expected_md5 = master_file.md5_checksum
        self.assertEqual(obtained_md5, expected_md5)

    def tearDown(self):
        self.test_file_content = b"Master file content" * self.chunk_size * 2
        MasterFile.objects.all().delete()
        ChunkedFile.objects.all().delete()
