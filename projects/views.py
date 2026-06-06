from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from team_finder.constants import OBJECTS_ON_PAGE
from team_finder.services import get_skill_suggestions, paginate, request_data
from .forms import ProjectForm
from .models import Project, Skill


def project_list(request):
    active_skill = request.GET.get("skill", "").strip()
    projects = Project.objects.select_related("owner").prefetch_related("participants", "skills")

    if active_skill:
        projects = projects.filter(skills__name=active_skill)

    projects = projects.order_by("-created_at").distinct()
    page_obj = paginate(request, projects, OBJECTS_ON_PAGE)
    query_prefix = f"skill={active_skill}&" if active_skill else ""

    return render(request, "projects/project_list.html", {
        "projects": projects,
        "page_obj": page_obj,
        "all_skills": Skill.objects.order_by("name"),
        "active_skill": active_skill,
        "query_prefix": query_prefix,
    })


def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants", "skills"),
        pk=pk,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def project_create(request):
    form = ProjectForm(
        request.POST or None,
        initial={"status": Project.STATUS_OPEN},
    )
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect(project)

    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.owner and not request.user.is_staff:
        return HttpResponseForbidden("Нет прав на редактирование проекта")

    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect(project)

    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
@require_POST
def project_complete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.owner and not request.user.is_staff:
        return HttpResponseForbidden("Нет прав на завершение проекта")
    if project.status != Project.STATUS_OPEN:
        return HttpResponseBadRequest("Проект уже закрыт")

    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": Project.STATUS_CLOSED})


@login_required
@require_POST
def toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user == project.owner:
        return HttpResponseBadRequest("Автор уже участвует в проекте")

    participant = project.participants.filter(pk=request.user.pk).exists()
    if participant:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)

    return JsonResponse({"status": "ok", "participant": not participant})


@require_GET
def skill_search(request):
    q = request.GET.get("q", "").strip()
    skills = get_skill_suggestions(q)
    return JsonResponse(list(skills.values("id", "name")), safe=False)


@login_required
@require_POST
def project_skill_add(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.owner:
        return HttpResponseForbidden("Нет прав на изменение навыков")

    data = request_data(request)
    skill_id = data.get("skill_id")
    name = str(data.get("name", "")).strip()

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
        created = False
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return HttpResponseBadRequest("Не передан навык")

    already_added = project.skills.filter(pk=skill.pk).exists()
    if not already_added:
        project.skills.add(skill)

    return JsonResponse({
        "id": skill.id,
        "name": skill.name,
        "skill_id": skill.id,
        "created": created,
        "added": not already_added,
    })


@login_required
@require_POST
def project_skill_remove(request, pk, skill_id):
    project = get_object_or_404(Project, pk=pk)
    skill = get_object_or_404(Skill, pk=skill_id)
    if request.user != project.owner:
        return HttpResponseForbidden("Нет прав на изменение навыков")
    if not project.skills.filter(pk=skill.pk).exists():
        return HttpResponseBadRequest("Навык не добавлен к проекту")

    project.skills.remove(skill)
    return JsonResponse({"status": "ok"})
