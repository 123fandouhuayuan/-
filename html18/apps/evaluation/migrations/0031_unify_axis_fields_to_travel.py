"""
机床模型字段统一迁移：将measured_x/y/z的值复制到x/y/z_axis_travel，然后删除measured_x/y/z字段
"""
from django.db import migrations, models


def copy_measured_to_travel(apps, schema_editor):
    """将measured_x/y/z的值复制到x/y/z_axis_travel"""
    Machine = apps.get_model('evaluation', 'Machine')
    
    for obj in Machine.objects.all():
        if obj.measured_x is not None and obj.x_axis_travel is None:
            obj.x_axis_travel = obj.measured_x
        if obj.measured_y is not None and obj.y_axis_travel is None:
            obj.y_axis_travel = obj.measured_y
        if obj.measured_z is not None and obj.z_axis_travel is None:
            obj.z_axis_travel = obj.measured_z
        obj.save(update_fields=['x_axis_travel', 'y_axis_travel', 'z_axis_travel'])


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0030_alter_machine_workpiece_size_and_more'),
    ]

    operations = [
        migrations.RunPython(copy_measured_to_travel, reverse_code=migrations.RunPython.noop),
        
        migrations.RemoveField(
            model_name='machine',
            name='measured_x',
        ),
        migrations.RemoveField(
            model_name='machine',
            name='measured_y',
        ),
        migrations.RemoveField(
            model_name='machine',
            name='measured_z',
        ),
    ]
