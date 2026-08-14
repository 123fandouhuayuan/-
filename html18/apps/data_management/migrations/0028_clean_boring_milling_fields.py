# Clean up boring milling fields - remove unnecessary fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0027_create_boring_milling_parameters'),
    ]

    operations = [
        # 删除基础参数字段
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='x_axis_travel',
        ),
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='y_axis_travel',
        ),
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='z_axis_travel',
        ),
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='worktable_length',
        ),
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='workpiece_size',
        ),
        
        # 删除垂直度字段
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='bm_y_axis_perpendicularity_z',
        ),
        
        # 删除主轴精度字段
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='bm_spindle_axial_runout',
        ),
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='bm_spindle_radial_runout_near',
        ),
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='bm_spindle_radial_runout_300mm',
        ),
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='bm_spindle_parallelism_yz',
        ),
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='bm_spindle_parallelism_zx',
        ),
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='bm_spindle_perpendicularity_x',
        ),
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='bm_spindle_perpendicularity_y',
        ),
        
        # 删除工作台精度字段
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='bm_worktable_flatness',
        ),
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='bm_worktable_parallelism_x',
        ),
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='bm_worktable_parallelism_z',
        ),
        
        # 删除加工精度字段
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='bm_cylindricity',
        ),
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='bm_hole_perpendicularity_a',
        ),
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='bm_concentricity_c',
        ),
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='bm_slope_linearity',
        ),
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='bm_slope_inclination_b',
        ),
        migrations.RemoveField(
            model_name='boringmillingparameters',
            name='bm_concentricity_d',
        ),
    ]
