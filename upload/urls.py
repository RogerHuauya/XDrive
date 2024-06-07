from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'masterfile', views.MasterFileModelViewSet,
                basename='masterfile')
router.register(r'chunkedfile', views.ChunkedFileModelViewSet,
                basename='chunkedfile')

urlpatterns = router.urls
