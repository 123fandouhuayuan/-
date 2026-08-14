from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0031_unify_axis_fields_to_travel'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='admin_saved',
            field=models.BooleanField(default=False, verbose_name='管理员已保存'),
        ),
    ]