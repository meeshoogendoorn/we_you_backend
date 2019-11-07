"""URL patterns for the analytics app."""

from rest_framework.routers import SimpleRouter

from analytics.views import CompanyChartsViewSet

router = SimpleRouter()

router.register("company", CompanyChartsViewSet, "company-charts")

urlpatterns = router.urls
