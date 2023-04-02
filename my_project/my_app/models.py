from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13)
    registration_date = models.DateTimeField(auto_now_add=True)
    cover_image_url = models.URLField()
