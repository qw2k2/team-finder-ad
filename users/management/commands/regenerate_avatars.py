from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        for user in User.objects.all():
            if user.avatar:
                user.avatar.delete(save=False)
            user.avatar = ""
            user.save()

        self.stdout.write(self.style.SUCCESS("Avatars regenerated"))
