"""
删除动刚度权重配置的Django管理命令

此命令用于：
1. 删除AHPMatrix表中path='性能/机床刚度/动刚度'的记录
2. 更新path='性能/机床刚度'的记录，将weights从[静刚度权重, 动刚度权重]改为[静刚度权重]
"""

from django.core.management.base import BaseCommand
from apps.evaluation.models import AHPMatrix

class Command(BaseCommand):
    help = '删除动刚度权重配置，更新机床刚度板块权重为单项'
    
    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("开始删除动刚度权重配置...")
        self.stdout.write("=" * 60)
        
        # 1. 删除path='性能/机床刚度/动刚度'的记录
        self.stdout.write("\n步骤1: 删除动刚度子项权重配置...")
        dynamic_stiffness_records = AHPMatrix.objects.filter(path='性能/机床刚度/动刚度')
        count = dynamic_stiffness_records.count()
        
        if count > 0:
            self.stdout.write(f"找到 {count} 条动刚度权重配置记录")
            for record in dynamic_stiffness_records:
                self.stdout.write(f"  - ID: {record.id}, Path: {record.path}, Weights: {record.weights}")
            dynamic_stiffness_records.delete()
            self.stdout.write(self.style.SUCCESS(f"已删除 {count} 条记录"))
        else:
            self.stdout.write("未找到动刚度权重配置记录")
        
        # 2. 更新path='性能/机床刚度'的记录
        self.stdout.write("\n步骤2: 更新机床刚度板块权重配置...")
        stiffness_records = AHPMatrix.objects.filter(path='性能/机床刚度')
        
        for record in stiffness_records:
            self.stdout.write(f"\n处理记录 ID: {record.id}")
            self.stdout.write(f"  当前路径: {record.path}")
            self.stdout.write(f"  当前权重: {record.weights}")
            self.stdout.write(f"  当前指标名称: {record.indicator_names}")
            
            # 如果weights长度为2，说明包含静刚度和动刚度权重
            if record.weights and len(record.weights) == 2:
                # 只保留静刚度权重（第一个权重）
                new_weights = [record.weights[0]]
                self.stdout.write(f"  新权重: {new_weights} (仅保留静刚度权重)")
                
                # 更新indicator_names，删除动刚度
                if record.indicator_names and len(record.indicator_names) == 2:
                    new_indicator_names = [record.indicator_names[0]]
                    self.stdout.write(f"  新指标名称: {new_indicator_names} (仅保留静刚度)")
                    record.indicator_names = new_indicator_names
                
                record.weights = new_weights
                record.save()
                self.stdout.write(self.style.SUCCESS(f"  [OK] 已更新记录"))
            elif record.weights and len(record.weights) == 1:
                self.stdout.write(self.style.SUCCESS(f"  [OK] 权重已为单项，无需更新"))
            else:
                self.stdout.write(self.style.WARNING(f"  [WARN] 权重格式异常，跳过更新"))
        
        # 3. 验证结果
        self.stdout.write("\n步骤3: 验证删除结果...")
        
        # 检查是否还有动刚度记录
        remaining_dynamic = AHPMatrix.objects.filter(path='性能/机床刚度/动刚度').count()
        if remaining_dynamic == 0:
            self.stdout.write(self.style.SUCCESS("[OK] 动刚度权重配置记录已全部删除"))
        else:
            self.stdout.write(self.style.WARNING(f"[WARN] 仍有 {remaining_dynamic} 条动刚度权重配置记录残留"))
        
        # 检查机床刚度板块权重
        stiffness_records = AHPMatrix.objects.filter(path='性能/机床刚度')
        for record in stiffness_records:
            if record.weights and len(record.weights) == 1:
                self.stdout.write(self.style.SUCCESS(f"[OK] 机床刚度板块权重已更新为单项: {record.weights}"))
            else:
                self.stdout.write(self.style.WARNING(f"[WARN] 机床刚度板块权重仍为多项: {record.weights}"))
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("动刚度权重配置删除完成！"))
        self.stdout.write("=" * 60)