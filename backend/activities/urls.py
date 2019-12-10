"""Activity related urlpatterns."""

__all__ = (
    "urlpatterns",
)

from rest_framework.routers import SimpleRouter

from activities.views import AnswerViewSet
from activities.views import AnswersViewSet
from activities.views import AnswerStylesViewSet

router = SimpleRouter()

router.register("answer", AnswerViewSet, "answer")
router.register("answers", AnswersViewSet, "answers")
router.register("answer-styles", AnswerStylesViewSet, "answer-styles")

urlpatterns = router.urls
