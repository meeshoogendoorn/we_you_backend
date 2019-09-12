"""Company related url patterns."""

from rest_framework.routers import SimpleRouter

from companies.views import CompanyViewSet


router = SimpleRouter()
router.register("company", CompanyViewSet, basename="company")

urlpatterns = router.urls
