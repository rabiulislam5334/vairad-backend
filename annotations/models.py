from django.db import models
from django.conf import settings


class AnnotationImage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='annotations/%Y/%m/%d/')
    original_filename = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.original_filename or f"Image {self.id}"


class Polygon(models.Model):
    image = models.ForeignKey(AnnotationImage, on_delete=models.CASCADE, related_name='polygons')
    label = models.CharField(max_length=100, blank=True, default='')
    color = models.CharField(max_length=20, default='#EF4444')
    points = models.JSONField()   # e.g. [{"x": 10, "y": 20}, {"x": 50, "y": 60}, ...]
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Polygon {self.id} on Image {self.image_id}"