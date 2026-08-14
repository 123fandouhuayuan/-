# Generated migration for adding z_axis_measurement_range field to Machine model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0037_userevaluationresult_worktable_parallelism_min_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='z_axis_measurement_range',
            field=models.FloatField(blank=True, null=True, verbose_name='数控镗轴或滑枕(Z轴)测量范围(mm)'),
        ),
    ]
