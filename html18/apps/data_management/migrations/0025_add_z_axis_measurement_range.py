# Generated migration for adding z_axis_measurement_range field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0024_tolerancevalue_machine_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='machineparameters',
            name='z_axis_measurement_range',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=10, null=True, verbose_name='数控镗轴或滑枕(Z轴)测量范围(mm)'),
        ),
    ]
