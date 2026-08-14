from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = '创建 DataOperationLog 表'

    def handle(self, *args, **options):
        self.stdout.write('开始创建 DataOperationLog 表...')

        sql_statements = [
            'DROP TABLE IF EXISTS "EVALUATION_DATAOPERATIONLOG"',
            '''CREATE TABLE "EVALUATION_DATAOPERATIONLOG" (
                "id" INT IDENTITY(1,1) PRIMARY KEY,
                "operator_id" INT NOT NULL,
                "action" VARCHAR(10) NOT NULL,
                "table_name" VARCHAR(100) NOT NULL,
                "record_id" VARCHAR(100) NOT NULL,
                "machine_id" INT NOT NULL,
                "old_data" TEXT,
                "new_data" TEXT,
                "ip_address" VARCHAR(50),
                "user_agent" VARCHAR(200),
                "operation_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                "notes" TEXT
            )''',
            'CREATE INDEX "evaluation_dataoperationlog_machine_id" ON "EVALUATION_DATAOPERATIONLOG"("machine_id")',
            'CREATE INDEX "evaluation_dataoperationlog_operation_time" ON "EVALUATION_DATAOPERATIONLOG"("operation_time")',
            'CREATE INDEX "evaluation_dataoperationlog_operator_id" ON "EVALUATION_DATAOPERATIONLOG"("operator_id")',
            'CREATE INDEX "evaluation_dataoperationlog_action" ON "EVALUATION_DATAOPERATIONLOG"("action")',
        ]

        try:
            with connection.cursor() as cursor:
                for sql in sql_statements:
                    if sql.strip():
                        self.stdout.write(f'执行: {sql[:60]}...')
                        cursor.execute(sql)
            
            self.stdout.write(self.style.SUCCESS('✅ DataOperationLog 表创建成功！'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 执行出错: {e}'))
