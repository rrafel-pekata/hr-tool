from django.db import migrations


def copy_company_to_es_fields(apps, schema_editor):
    """Copy existing Company field values to the _es translation columns."""
    Company = apps.get_model('tenants', 'Company')
    for obj in Company.objects.all():
        obj.name_es = obj.name
        obj.description_es = obj.description
        obj.benefits_es = obj.benefits
        obj.work_schedule_es = obj.work_schedule
        obj.remote_policy_es = obj.remote_policy
        obj.office_location_es = obj.office_location
        obj.culture_es = obj.culture
        obj.save(update_fields=[
            'name_es', 'description_es', 'benefits_es', 'work_schedule_es',
            'remote_policy_es', 'office_location_es', 'culture_es',
        ])


def copy_department_to_es_fields(apps, schema_editor):
    """Copy existing Department field values to the _es translation columns."""
    Department = apps.get_model('tenants', 'Department')
    for obj in Department.objects.all():
        obj.name_es = obj.name
        obj.description_es = obj.description
        obj.save(update_fields=['name_es', 'description_es'])


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0006_company_benefits_ca_company_benefits_en_and_more'),
    ]

    operations = [
        migrations.RunPython(copy_company_to_es_fields, migrations.RunPython.noop),
        migrations.RunPython(copy_department_to_es_fields, migrations.RunPython.noop),
    ]
