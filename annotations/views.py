from rest_framework import viewsets, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import AnnotationImage, Polygon
from .serializers import AnnotationImageSerializer, PolygonSerializer
from accounts.permissions import IsOwner


class AnnotationImageViewSet(viewsets.ModelViewSet):
    serializer_class = AnnotationImageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return AnnotationImage.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        image_file = self.request.FILES.get('image')
        serializer.save(
            user=self.request.user,
            original_filename=image_file.name if image_file else ''
        )


class PolygonViewSet(viewsets.ModelViewSet):
    serializer_class = PolygonSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Polygon.objects.filter(image__user=self.request.user)

    def perform_create(self, serializer):
        image_id = self.request.data.get('image')
        serializer.save(image_id=image_id)