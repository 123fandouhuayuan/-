"""
评价系统算法模块

本模块包含机床质量评价系统的核心算法，包括：
- AHP层次分析法
- 信息熵权重计算
- 帕累托定律应用
- 层次化权重计算
- 指标得分计算
- 判断矩阵生成
- 综合权重计算

详细说明请参考 说明.md 文件
"""

__version__ = '1.0.0'
__author__ = '评价系统开发团队'

from . import ahp
from . import entropy
from . import pareto
from . import combined
from . import scoring
from . import matrix
from . import comprehensive

__all__ = [
    'ahp',
    'entropy',
    'pareto',
    'combined',
    'scoring',
    'matrix',
    'comprehensive'
]
