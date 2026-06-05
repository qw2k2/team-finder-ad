from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0002_initial"),
        ("users", "0002_alter_user_avatar_alter_user_phone"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="skills",
            field=models.ManyToManyField(blank=True, related_name="users", to="projects.skill"),
        ),
    ]
