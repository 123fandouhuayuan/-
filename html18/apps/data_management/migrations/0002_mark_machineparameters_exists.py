# 手动创建的迁移文件，标记machineparameters表已经存在

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0001_initial'),
    ]

    operations = [
        # 这个迁移文件只是为了标记machineparameters表已经存在
        # 不执行任何操作
    ]
