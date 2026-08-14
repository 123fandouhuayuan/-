from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0036_machine_worktable_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='userevaluationresult',
            name='worktable_parallelism_min_score',
            field=models.FloatField(default=0, verbose_name='平行度(镗铣床)'),
        ),
    ]
