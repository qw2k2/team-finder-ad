import json

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from projects.models import Skill
from .forms import LoginForm, ProfileForm, RegisterForm, UserPasswordChangeForm
from .models import User


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/users/login/")
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, request.POST)
        if form.is_valid():
            login(request, form.user)
            return redirect("/projects/list/")
    else:
        form = LoginForm(request)

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("/projects/list/")


def user_list(request):
    participants = User.objects.order_by("-date_joined", "-id")
    paginator = Paginator(participants, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "users/participants.html", {
        "participants": participants,
        "page_obj": page_obj,
    })


def user_detail(request, pk):
    profile_user = get_object_or_404(
        User.objects.prefetch_related("skills", "owned_projects"),
        pk=pk,
    )
    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(f"/users/{request.user.id}/")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect(f"/users/{request.user.id}/")
    else:
        form = UserPasswordChangeForm(request.user)

    return render(request, "users/change_password.html", {"form": form})


@require_GET
def skill_search(request):
    q = request.GET.get("q", "").strip()
    skills = (
        Skill.objects.filter(name__istartswith=q).order_by("name")[:10]
        if q
        else Skill.objects.none()
    )
    return JsonResponse(list(skills.values("id", "name")), safe=False)


@login_required
@require_POST
def user_skill_add(request, pk):
    profile_user = get_object_or_404(User, pk=pk)
    if request.user != profile_user:
        return HttpResponseForbidden("Нет прав на изменение навыков")

    data = _request_data(request)
    skill_id = data.get("skill_id")
    name = str(data.get("name", "")).strip()

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
        created = False
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return HttpResponseBadRequest("Не передан навык")

    already_added = profile_user.skills.filter(pk=skill.pk).exists()
    if not already_added:
        profile_user.skills.add(skill)

    return JsonResponse({
        "id": skill.id,
        "name": skill.name,
        "skill_id": skill.id,
        "created": created,
        "added": not already_added,
    })


@login_required
@require_POST
def user_skill_remove(request, pk, skill_id):
    profile_user = get_object_or_404(User, pk=pk)
    skill = get_object_or_404(Skill, pk=skill_id)
    if request.user != profile_user:
        return HttpResponseForbidden("Нет прав на изменение навыков")
    if not profile_user.skills.filter(pk=skill.pk).exists():
        return HttpResponseBadRequest("Навык не добавлен к профилю")

    profile_user.skills.remove(skill)
    return JsonResponse({"status": "ok"})


def _request_data(request):
    if request.content_type == "application/json":
        try:
            return json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return {}
    return request.POST
