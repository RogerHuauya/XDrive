from django.db import models


class MasterFile(models.Model):
    file = models.FileField(upload_to='master_files/', null=True, blank=True)
    file_name = models.CharField(max_length=255)
    md5_checksum = models.CharField(max_length=32)
    number_of_chunks = models.PositiveIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def is_complete(self):
        return self.chunkedfile_set.count() == self.number_of_chunks


class ChunkedFile(models.Model):
    master_file = models.ForeignKey(MasterFile, on_delete=models.CASCADE)
    file = models.FileField(upload_to='chunked_files/')
    chunk_number = models.PositiveIntegerField()
    md5_checksum = models.CharField(max_length=32)
    uploaded_at = models.DateTimeField(auto_now_add=True)
