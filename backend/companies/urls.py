"""Company related url patterns."""

from rest_framework.routers import SimpleRouter

from companies.views import CompanyViewSet
from companies.views import CompanyLogoViewSet
from companies.views import ColourThemeViewSet


router = SimpleRouter()
router.register("company", CompanyViewSet, basename="company")
router.register("colour-theme/", ColourThemeViewSet, basename="colour-theme")
router.register("company-logo/", CompanyLogoViewSet, basename="company-logo")

urlpatterns = router.urls
