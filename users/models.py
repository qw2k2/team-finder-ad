import random
import uuid
from io import BytesIO
from pathlib import Path

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to="avatars/")
    phone = models.CharField(max_length=12, unique=True, null=True)
    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=256, blank=True)
    skills = models.ManyToManyField("projects.Skill", blank=True, related_name="users")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        if not self.avatar and self.name:
            self.avatar.save(self._avatar_name(), self._make_avatar(), save=False)
        super().save(*args, **kwargs)

    def _avatar_name(self):
        return f"avatar_{uuid.uuid4()}.png"

    def _make_avatar(self):
        colors = ["#DCEBFF", "#E8F5E9", "#FFF3D6", "#F4E8FF", "#E8F0FE", "#FDEDEC"]
        image = Image.new("RGB", (200, 200), random.choice(colors))
        draw = ImageDraw.Draw(image)
        letter = self.name[:1].upper()
        font_path = Path("C:/Windows/Fonts/arial.ttf")
        font = (
            ImageFont.truetype(str(font_path), 96)
            if font_path.exists()
            else ImageFont.load_default(size=96)
        )
        box = draw.textbbox((0, 0), letter, font=font)
        x = (200 - (box[2] - box[0])) / 2
        y = (200 - (box[3] - box[1])) / 2 - 8
        draw.text((x, y), letter, fill="#111827", font=font)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return ContentFile(buffer.getvalue())
