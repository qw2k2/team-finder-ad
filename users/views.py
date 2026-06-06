from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from team_finder.constants import OBJECTS_ON_PAGE
from team_finder.services import get_skill_suggestions, paginate, request_data
from projects.models import Skill
from .forms import LoginForm, ProfileForm, RegisterForm, UserPasswordChangeForm
from .models import User


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("users:login")

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    form = LoginForm(request, request.POST or None)
    if form.is_valid():
        login(request, form.user)
        return redirect("projects:list")

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_list(request):
    participants = User.objects.order_by("-date_joined", "-id")
    page_obj = paginate(request, participants, OBJECTS_ON_PAGE)
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
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect(request.user)

    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    form = UserPasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect(user)

    return render(request, "users/change_password.html", {"form": form})


@require_GET
def skill_search(request):
    q = request.GET.get("q", "").strip()
    skills = get_skill_suggestions(q)
    return JsonResponse(list(skills.values("id", "name")), safe=False)


@login_required
@require_POST
def user_skill_add(request, pk):
    profile_user = get_object_or_404(User, pk=pk)
    if request.user != profile_user:
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
