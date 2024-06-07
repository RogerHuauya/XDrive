from django.db import models


class MasterFile(models.Model):
    file = models.FileField(upload_to='master_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class ChunkedFile(models.Model):
    master_file = models.ForeignKey(MasterFile, on_delete=models.CASCADE)
    file = models.FileField(upload_to='chunked_files/')
    chunk_number = models.PositiveIntegerField()
    md5_checksum = models.CharField(max_length=32)
    uploaded_at = models.DateTimeField(auto_now_add=True)
