from django.db import migrations


def copy_to_es_fields(apps, schema_editor):
    """Copy existing CaseStudy field values to the _es translation columns."""
    CaseStudy = apps.get_model('casestudies', 'CaseStudy')
    for obj in CaseStudy.objects.all():
        obj.title_es = obj.title
        obj.brief_description_es = obj.brief_description
        obj.full_content_es = obj.full_content
        obj.evaluation_criteria_es = obj.evaluation_criteria
        obj.save(update_fields=[
            'title_es', 'brief_description_es',
            'full_content_es', 'evaluation_criteria_es',
        ])


class Migration(migrations.Migration):

    dependencies = [
        ('casestudies', '0002_casestudy_brief_description_ca_and_more'),
    ]

    operations = [
        migrations.RunPython(copy_to_es_fields, migrations.RunPython.noop),
    ]
