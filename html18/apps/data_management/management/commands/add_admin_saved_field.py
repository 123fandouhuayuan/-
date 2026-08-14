from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = '添加 admin_saved 字段到 Daeng 数据库'

    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                self.stdout.write("尝试添加 ADMIN_SAVED 字段...")
                
                try:
                    cursor.execute("""
                        ALTER TABLE EVALUATION_MACHINE 
                        ADD ADMIN_SAVED SMALLINT DEFAULT 0
                    """)
                    self.stdout.write(self.style.SUCCESS("成功添加 ADMIN_SAVED 字段"))
                except Exception as e:
                    error_msg = str(e)
                    if 'ADMIN_SAVED' in error_msg or '已存在' in error_msg or 'already exists' in error_msg:
                        self.stdout.write(self.style.WARNING("字段 ADMIN_SAVED 已存在"))
                    else:
                        raise
                
                # 验证字段是否存在
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM ALL_TAB_COLUMNS 
                    WHERE TABLE_NAME = 'EVALUATION_MACHINE' 
                    AND COLUMN_NAME = 'ADMIN_SAVED'
                """)
                result = cursor.fetchone()
                
                if result and result[0] > 0:
                    self.stdout.write(self.style.SUCCESS(f"验证成功: ADMIN_SAVED 字段存在"))
                else:
                    self.stdout.write(self.style.ERROR("验证失败: ADMIN_SAVED 字段不存在"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"操作失败: {str(e)}"))
            import traceback
            traceback.print_exc()