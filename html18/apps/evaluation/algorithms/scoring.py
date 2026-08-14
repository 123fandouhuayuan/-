"""
指标得分计算算法

本模块实现了指标得分的计算功能，基于误差值和标准允差计算指标的性能得分。

主要功能：
- calculate_indicator_score: 计算单个指标的得分
- calculate_multiple_scores: 计算多个指标的得分
- calculate_weighted_score: 计算加权得分
- calculate_overall_score: 计算总体得分

算法原理：
1. 单指标得分计算：得分 = (标准允差 - 误差值) / 标准允差 × 100
2. 得分范围：[0, 100]
3. 偏差越小，得分越高
4. 加权得分：得分 × 权重 / 总权重
5. 总体得分：所有加权得分的平均值

应用场景：
- 机床性能评价
- 质量指标评估
- 多指标综合评价
"""


def calculate_indicator_score(error_value, standard_tolerance):
    """
    计算单个指标的得分

    参数:
        error_value (float): 误差值
        standard_tolerance (float): 标准允差

    返回:
        float: 指标得分（0-100）

    计算公式:
        得分 = (标准允差 - |误差值|) / 标准允差 × 100
        得分范围：[0, 100]
    """
    if standard_tolerance <= 0:
        return 0.0

    # 计算得分：误差值越小，得分越高
    score = (standard_tolerance - abs(error_value)) / standard_tolerance * 100

    # 确保得分在0-100之间
    return max(0, min(100, score))


def calculate_multiple_scores(error_values, standard_tolerances):
    """
    计算多个指标的得分

    参数:
        error_values (dict): 误差值数据
        standard_tolerances (dict): 标准允差数据

    返回:
        dict: 各指标的得分

    数据结构:
        {
            '二级指标': {
                '三级指标': [得分1, 得分2, ...]
            }
        }
    """
    scores = {}

    # 遍历所有二级指标
    for secondary in error_values:
        scores[secondary] = {}

        # 遍历所有三级指标
        for tertiary in error_values[secondary]:
            scores[secondary][tertiary] = []

            # 遍历所有四级指标
            error_list = error_values[secondary][tertiary]
            tolerance_list = standard_tolerances[secondary][tertiary]
            
            for i in range(len(error_list)):
                # 获取对应的值
                error_value = error_list[i]
                standard_tolerance = tolerance_list[i]

                # 计算得分
                score = calculate_indicator_score(error_value, standard_tolerance)
                scores[secondary][tertiary].append(score)

    return scores


def calculate_weighted_score(scores, weights):
    """
    计算加权得分

    参数:
        scores (dict): 指标得分
        weights (dict): 指标权重

    返回:
        dict: 加权得分

    计算公式:
        加权得分 = Σ(得分 × 权重) / Σ(权重)
    """
    weighted_scores = {}

    for secondary in scores:
        weighted_scores[secondary] = {}

        for tertiary in scores[secondary]:
            total_weight = sum(weights.get(secondary, {}).get(tertiary, []))
            weighted_score = 0

            if total_weight > 0:
                for i, score in enumerate(scores[secondary][tertiary]):
                    weight = weights.get(secondary, {}).get(tertiary, [1])[i]
                    weighted_score += score * weight / total_weight

            weighted_scores[secondary][tertiary] = weighted_score

    return weighted_scores


def calculate_overall_score(weighted_scores, level_weights):
    """
    计算总体得分

    参数:
        weighted_scores (dict): 加权得分
        level_weights (dict): 各级指标的权重

    返回:
        float: 总体得分

    计算公式:
        总体得分 = Σ(加权得分 × 权重) / Σ(权重)
    """
    total_score = 0
    total_weight = 0

    for secondary in weighted_scores:
        weight = level_weights.get(secondary, 1.0)

        for tertiary in weighted_scores[secondary]:
            tertiary_score = weighted_scores[secondary][tertiary]
            total_score += tertiary_score * weight
            total_weight += weight

    if total_weight > 0:
        return total_score / total_weight
    return 0.0
