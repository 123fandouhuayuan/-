from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0007_unify_axis_fields_to_travel'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComprehensiveWeightResultDameng',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_type', models.CharField(choices=[('horizontal_machining_center', '卧式加工中心'), ('five_axis_machining_center', '五轴加工中心')], db_index=True, max_length=50, verbose_name='机床类型')),
                ('report_number', models.CharField(db_index=True, max_length=100, verbose_name='报告编号')),
                ('machine_model', models.CharField(max_length=100, verbose_name='机床型号')),
                ('comprehensive_score', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='综合得分')),
                ('total_weight', models.DecimalField(decimal_places=4, max_digits=10, verbose_name='总权重')),
                ('evaluator', models.CharField(blank=True, max_length=50, null=True, verbose_name='计算人')),
                ('calculated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='计算时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('version', models.IntegerField(default=0, verbose_name='版本号')),
            ],
            options={
                'verbose_name': '综合权重计算结果',
                'verbose_name_plural': '综合权重计算结果',
                'db_table': 'comprehensive_weight_result_dameng',
                'ordering': ['-calculated_at'],
            },
        ),
    ]