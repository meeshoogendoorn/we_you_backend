"""URL patterns for the analytics app."""

from rest_framework.routers import SimpleRouter

from analytics.views import CompanyChartsViewSet
from analytics.views import SessionChartsViewSet

router = SimpleRouter()

router.register("company", CompanyChartsViewSet, "company-charts")
router.register("session", SessionChartsViewSet, "session-charts")

urlpatterns = router.urls
