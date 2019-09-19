"""Url patterns for communication related view sets."""

__all__ = (
    "urlpatterns",
)

from rest_framework.routers import SimpleRouter

from communications.views import EmailViewSet
from communications.views import VariableViewSet
from communications.views import EnvironmentViewSet


router = SimpleRouter()
router.register("emails", EmailViewSet, "email")
router.register("variables", VariableViewSet, "variable")
router.register("environments", EnvironmentViewSet, "environments")

urlpatterns = router.urls
