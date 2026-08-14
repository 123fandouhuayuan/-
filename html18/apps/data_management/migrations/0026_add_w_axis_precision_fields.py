# Generated migration for adding W-axis precision fields for boring milling machine

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0025_add_z_axis_measurement_range'),
    ]

    operations = [
        migrations.AddField(
            model_name='machineparameters',
            name='linear_axis_repeatability_w',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=10, null=True, verbose_name='线性轴W轴双向重复定位精度'),
        ),
        migrations.AddField(
            model_name='machineparameters',
            name='linear_axis_positioning_accuracy_w',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=10, null=True, verbose_name='线性轴W轴双向定位精度'),
        ),
        migrations.AddField(
            model_name='machineparameters',
            name='linear_axis_mean_deviation_w',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=10, null=True, verbose_name='线性轴W轴平均双向位置偏差范围'),
        ),
        migrations.AddField(
            model_name='machineparameters',
            name='linear_axis_system_deviation_w',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=10, null=True, verbose_name='线性轴W轴双向定位系统偏差E'),
        ),
        migrations.AddField(
            model_name='machineparameters',
            name='linear_axis_backlash_w',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=10, null=True, verbose_name='线性轴W轴反向差值'),
        ),
    ]
