from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0011_comprehensiveweightresultdameng'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comprehensiveweightresultdameng',
            name='report_number',
            field=models.CharField(db_index=True, max_length=100, unique=True, verbose_name='报告编号'),
        ),
    ]
