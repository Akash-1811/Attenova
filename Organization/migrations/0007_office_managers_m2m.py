# Generated manually for Office.manager -> Office.managers (ManyToMany)

from django.conf import settings
from django.db import migrations, models


def migrate_manager_to_managers(apps, schema_editor):
    """Copy existing manager to managers M2M before removing manager FK."""
    Office = apps.get_model("Organization", "Office")
    for office in Office.objects.all():
        if hasattr(office, "manager_id") and office.manager_id:
            office.managers.add(office.manager_id)


def reverse_migrate(apps, schema_editor):
    """Reverse: set first manager as manager_id (not fully reversible for multiple)."""
    pass  # No-op; we cannot restore single manager from multiple


class Migration(migrations.Migration):

    dependencies = [
        ("Organization", "0006_organization_pincode"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="office",
            name="managers",
            field=models.ManyToManyField(
                blank=True,
                related_name="managed_offices",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(migrate_manager_to_managers, reverse_migrate),
        migrations.RemoveField(
            model_name="office",
            name="manager",
        ),
    ]
