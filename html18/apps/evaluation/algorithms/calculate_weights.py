import sys
import os

# 添加模块路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from entropy import calculate_entropy_weight

# 整理数据
data = [
    [0.200, 0.200],
    [0.100, 0.133],
    [0.200, 0.200],
    [0.200, 0.133],
    [0.040, 0.000],
    [0.040, 0.100],
    [0.040, 0.000],
    [0.040, 0.000],
    [0.040, 0.000],
    [0.200, 0.200]
]

# 计算权重
result = calculate_entropy_weight(data)

# 输出结果
print("信息熵：", result['entropy'])
print("权重：", result['weights'])
print("\n各指标权重：")
print(f"圆度(形状)：{result['weights'][0]:.4f}")
print(f"尺寸精度(圆柱度)：{result['weights'][1]:.4f}")