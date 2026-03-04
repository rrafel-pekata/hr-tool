from django.db import migrations


def copy_to_es_fields(apps, schema_editor):
    """Copy existing field values to the _es translation columns."""
    Position = apps.get_model('positions', 'Position')
    for pos in Position.objects.all():
        pos.title_es = pos.title
        pos.description_es = pos.description
        pos.requirements_es = pos.requirements
        pos.about_company_snippet_es = pos.about_company_snippet
        pos.benefits_es = pos.benefits
        pos.salary_range_es = pos.salary_range
        pos.save(update_fields=[
            'title_es', 'description_es', 'requirements_es',
            'about_company_snippet_es', 'benefits_es', 'salary_range_es',
        ])


class Migration(migrations.Migration):

    dependencies = [
        ('positions', '0007_position_about_company_snippet_ca_and_more'),
    ]

    operations = [
        migrations.RunPython(copy_to_es_fields, migrations.RunPython.noop),
    ]
