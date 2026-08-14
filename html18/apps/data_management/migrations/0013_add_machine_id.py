from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0012_add_unique_constraint_report_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='comprehensiveweightresultdameng',
            name='machine_id',
            field=models.IntegerField(verbose_name='机床ID', db_index=True, null=True, default=0),
        ),
    ]
