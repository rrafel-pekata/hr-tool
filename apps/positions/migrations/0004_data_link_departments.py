# Data migration: link positions to Department model via FK

from django.db import migrations


def link_departments(apps, schema_editor):
    """For each Position with department_old text, find the matching Department and set the FK."""
    Position = apps.get_model('positions', 'Position')
    Department = apps.get_model('tenants', 'Department')

    for position in Position.objects.exclude(department_old=''):
        dept_name = position.department_old.strip()
        if dept_name:
            dept = Department.objects.filter(
                company_id=position.company_id,
                name=dept_name,
            ).first()
            if dept:
                position.department = dept
                position.save(update_fields=['department'])


class Migration(migrations.Migration):

    dependencies = [
        ('positions', '0003_add_department_fk'),
        ('tenants', '0004_data_migrate_profiles_departments'),
    ]

    operations = [
        migrations.RunPython(
            link_departments,
            migrations.RunPython.noop,
        ),
    ]
