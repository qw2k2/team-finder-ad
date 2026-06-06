import json

from django.core.paginator import Paginator

from projects.models import Skill
from .constants import SKILLS_SUGGEST_LIMIT


def paginate(request, queryset, per_page):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


def request_data(request):
    if request.content_type == "application/json":
        try:
            return json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return {}
    return request.POST


def get_skill_suggestions(query):
    if not query:
        return Skill.objects.none()
    return Skill.objects.filter(name__istartswith=query).order_by("name")[:SKILLS_SUGGEST_LIMIT]
