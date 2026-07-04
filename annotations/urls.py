from rest_framework.routers import DefaultRouter
from .views import AnnotationImageViewSet, PolygonViewSet

router = DefaultRouter()
router.register('images', AnnotationImageViewSet, basename='annotation-image')
router.register('polygons', PolygonViewSet, basename='polygon')

urlpatterns = router.urls