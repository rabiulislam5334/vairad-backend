from rest_framework import serializers
from .models import AnnotationImage, Polygon


class PolygonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Polygon
        fields = ['id', 'label', 'color', 'points', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_points(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Points must be a list of {x, y} coordinates.")
        if len(value) < 3:
            raise serializers.ValidationError("A polygon must have at least 3 points.")
        for point in value:
            if not isinstance(point, dict) or 'x' not in point or 'y' not in point:
                raise serializers.ValidationError("Each point must be an object with 'x' and 'y' keys.")
        return value


class AnnotationImageSerializer(serializers.ModelSerializer):
    polygons = PolygonSerializer(many=True, read_only=True)

    class Meta:
        model = AnnotationImage
        fields = ['id', 'image', 'original_filename', 'uploaded_at', 'polygons']
        read_only_fields = ['id', 'uploaded_at']

    def validate_image(self, value):
        max_size_mb = 5
        allowed_types = ['image/jpeg', 'image/png', 'image/webp']

        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Only JPEG, PNG, or WEBP images are allowed.")

        if value.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(f"Image size must not exceed {max_size_mb}MB.")

        return value