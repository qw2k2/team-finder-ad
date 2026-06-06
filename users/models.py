import random
import uuid
from io import BytesIO
from pathlib import Path

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from PIL import Image, ImageDraw, ImageFont

from team_finder.constants import AVATAR_COLORS, AVATAR_FONT_SIZE, AVATAR_SIZE
from team_finder.constants import AVATAR_VERTICAL_OFFSET, USER_ABOUT_MAX_LENGTH
from team_finder.constants import USER_NAME_MAX_LENGTH, USER_PHONE_MAX_LENGTH
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email", unique=True)
    name = models.CharField("Имя", max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField("Фамилия", max_length=USER_NAME_MAX_LENGTH)
    avatar = models.ImageField("Аватар", upload_to="avatars/")
    phone = models.CharField("Телефон", max_length=USER_PHONE_MAX_LENGTH, unique=True, null=True)
    github_url = models.URLField("Ссылка на GitHub", blank=True)
    about = models.TextField("О себе", max_length=USER_ABOUT_MAX_LENGTH, blank=True)
    skills = models.ManyToManyField(
        "projects.Skill",
        verbose_name="Навыки",
        blank=True,
        related_name="users",
    )
    is_active = models.BooleanField("Активен", default=True)
    is_staff = models.BooleanField("Администратор", default=False)
    date_joined = models.DateTimeField("Дата регистрации", auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        ordering = ["name", "surname"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.name} {self.surname}"

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        if not self.avatar and self.name:
            self.avatar.save(self._avatar_name(), self._make_avatar(), save=False)
        super().save(*args, **kwargs)

    def _avatar_name(self):
        return f"avatar_{uuid.uuid4()}.png"

    def _make_avatar(self):
        image = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), random.choice(AVATAR_COLORS))
        draw = ImageDraw.Draw(image)
        letter = self.name[:1].upper()
        font_path = Path("C:/Windows/Fonts/arial.ttf")
        font = (
            ImageFont.truetype(str(font_path), AVATAR_FONT_SIZE)
            if font_path.exists()
            else ImageFont.load_default(size=AVATAR_FONT_SIZE)
        )
        box = draw.textbbox((0, 0), letter, font=font)
        x = (AVATAR_SIZE - (box[2] - box[0])) / 2
        y = (AVATAR_SIZE - (box[3] - box[1])) / 2 - AVATAR_VERTICAL_OFFSET
        draw.text((x, y), letter, fill="#111827", font=font)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return ContentFile(buffer.getvalue())
