"""Activity related urlpatterns."""

__all__ = (
    "urlpatterns",
)

from rest_framework.routers import SimpleRouter

from activities.views import ColourThemeViewSet


router = SimpleRouter()
router.register("colour-theme/", ColourThemeViewSet, basename="color-theme")


urlpatterns = router.urls
