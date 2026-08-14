# -*- coding: utf-8 -*-
"""
管理命令：使用 Django ORM 为 comprehensive_weight_result_dameng 表添加五维度评分字段
"""
from django.core.management.base import BaseCommand
from django.db import connection, transaction

class Command(BaseCommand):
    help = '使用 Django ORM 为 comprehensive_weight_result_dameng 表添加五维度评分字段'

    def handle(self, *args, **kwargs):
        self.stdout.write('开始为 comprehensive_weight_result_dameng 表添加五维度评分字段...')
        
        fields_sql = [
            ('precision_score', 'DECIMAL(10,2) DEFAULT 0'),
            ('performance_score', 'DECIMAL(10,2) DEFAULT 0'),
            ('reliability_score', 'DECIMAL(10,2) DEFAULT 0'),
            ('intelligence_score', 'DECIMAL(10,2) DEFAULT 0'),
            ('green_score', 'DECIMAL(10,2) DEFAULT 0'),
        ]
        
        with connection.cursor() as cursor:
            # 直接尝试添加字段，如果已存在则忽略错误
            for field_name, field_type in fields_sql:
                try:
                    sql = f"ALTER TABLE comprehensive_weight_result_dameng ADD {field_name} {field_type}"
                    cursor.execute(sql)
                    self.stdout.write(self.style.SUCCESS(f'✓ 成功添加字段 {field_name}'))
                except Exception as e:
                    error_msg = str(e)
                    if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                        self.stdout.write(self.style.SUCCESS(f'✓ 字段 {field_name} 已存在'))
                    else:
                        self.stdout.write(self.style.WARNING(f'⚠ 添加字段 {field_name} 时出错：{e}'))
        
        self.stdout.write(self.style.SUCCESS('\n迁移完成！'))
