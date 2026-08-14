"""
帕累托定律应用算法
"""


def apply_pareto_law(indicators, threshold=80):
    """
    应用帕累托定律筛选关键指标
    
    Args:
        indicators (list): 指标数据列表，每个元素包含'global_original'和其他属性
        threshold (float): 帕累托阈值 (默认80%)
    
    Returns:
        dict: 包含筛选结果的字典
    """
    # 1. 按全局原始权重排序（从大到小）
    sorted_indicators = sorted(
        indicators, 
        key=lambda x: x.get('global_original', 0), 
        reverse=True
    )
    
    # 2. 计算总权重
    total_global = sum(item.get('global_original', 0) for item in sorted_indicators)
    
    if total_global == 0:
        return {
            'key_indicators': [],
            'non_key_indicators': [],
            'total_global': 0,
            'cumulative_percentage': 0,
            'threshold': threshold,
            'key_indicator_count': 0,
            'total_indicator_count': 0,
            'key_indicator_ratio': 0
        }
    
    # 3. 筛选关键指标
    cumulative = 0
    key_indicators = []
    non_key_indicators = []
    total_weight_original = 0
    
    for item in sorted_indicators:
        weight = item.get('global_original', 0)
        weight_percentage = (weight / total_global) * 100
        cumulative += weight_percentage
        
        if cumulative <= threshold:
            # 关键指标
            key_indicators.append({
                **item,
                'is_key': True,
                'weight_percentage': weight_percentage,
                'cumulative_percentage': cumulative
            })
            total_weight_original += weight
        else:
            # 非关键指标
            non_key_indicators.append({
                **item,
                'is_key': False,
                'weight_percentage': weight_percentage,
                'cumulative_percentage': cumulative
            })
    
    # 4. 计算关键指标的累计权重和
    total_key_weight = sum(item.get('global_original', 0) for item in key_indicators)
    
    # 5. 为关键指标计算归一化权重
    for item in key_indicators:
        if total_key_weight > 0:
            item['normalized_weight'] = item.get('global_original', 0) / total_key_weight
        else:
            item['normalized_weight'] = 0
    
    # 6. 为非关键指标设置归一化权重为0
    for item in non_key_indicators:
        item['normalized_weight'] = 0
    
    return {
        'key_indicators': key_indicators,
        'non_key_indicators': non_key_indicators,
        'total_global': total_global,
        'total_weight_original': total_weight_original,
        'total_key_weight': total_key_weight,
        'cumulative_percentage': cumulative,
        'threshold': threshold,
        'key_indicator_count': len(key_indicators),
        'total_indicator_count': len(sorted_indicators),
        'key_indicator_ratio': len(key_indicators) / len(sorted_indicators) if sorted_indicators else 0
    }


def calculate_pareto_effectiveness(key_indicators, total_indicators):
    """
    计算帕累托效应
    
    Args:
        key_indicators (list): 关键指标列表
        total_indicators (list): 所有指标列表
    
    Returns:
        dict: 帕累托效应分析结果
    """
    # 计算关键指标的权重和
    key_weight_sum = sum(item.get('global_original', 0) for item in key_indicators)
    
    # 计算所有指标的权重和
    total_weight_sum = sum(item.get('global_original', 0) for item in total_indicators)
    
    # 计算效应比
    effectiveness_ratio = (key_weight_sum / total_weight_sum) * 100 if total_weight_sum > 0 else 0
    
    # 计算指标占比
    indicator_ratio = (len(key_indicators) / len(total_indicators)) * 100 if total_indicators else 0
    
    # 计算帕累托系数
    pareto_coefficient = effectiveness_ratio / indicator_ratio if indicator_ratio > 0 else 0
    
    return {
        'effectiveness_ratio': effectiveness_ratio,
        'indicator_ratio': indicator_ratio,
        'pareto_coefficient': pareto_coefficient,
        'key_indicator_count': len(key_indicators),
        'total_indicator_count': len(total_indicators),
        'key_weight_sum': key_weight_sum,
        'total_weight_sum': total_weight_sum
    }


def generate_pareto_analysis(indicators, threshold=80):
    """
    生成帕累托分析报告
    
    Args:
        indicators (list): 指标数据列表
        threshold (float): 帕累托阈值
    
    Returns:
        dict: 完整的帕累托分析报告
    """
    # 应用帕累托定律
    pareto_result = apply_pareto_law(indicators, threshold)
    
    # 计算帕累托效应
    effectiveness = calculate_pareto_effectiveness(
        pareto_result['key_indicators'],
        pareto_result['key_indicators'] + pareto_result['non_key_indicators']
    )
    
    # 生成分析报告
    report = {
        **pareto_result,
        **effectiveness,
        'analysis': {
            'threshold': threshold,
            'key_indicators_summary': f"{pareto_result['key_indicator_count']}个关键指标，占总指标数的{effectiveness['indicator_ratio']:.1f}%",
            'weight_contribution': f"关键指标贡献了{effectiveness['effectiveness_ratio']:.1f}%的权重",
            'pareto_coefficient': f"帕累托系数: {effectiveness['pareto_coefficient']:.2f}",
            'interpretation': _interpret_pareto_result(effectiveness['pareto_coefficient'])
        }
    }
    
    return report


def _interpret_pareto_result(pareto_coefficient):
    """
    解释帕累托系数
    
    Args:
        pareto_coefficient (float): 帕累托系数
    
    Returns:
        str: 解释结果
    """
    if pareto_coefficient >= 4:
        return "强帕累托效应：少数指标对结果有显著影响，应重点关注这些关键指标"
    elif pareto_coefficient >= 2:
        return "中等帕累托效应：部分指标对结果有较大影响，建议关注这些指标"
    elif pareto_coefficient >= 1:
        return "弱帕累托效应：指标间的重要性较为平均，需要综合考虑所有指标"
    else:
        return "无明显帕累托效应：指标分布均匀，建议全面评估"


def optimize_threshold(indicators, min_threshold=50, max_threshold=90, step=5):
    """
    优化帕累托阈值
    
    Args:
        indicators (list): 指标数据列表
        min_threshold (float): 最小阈值
        max_threshold (float): 最大阈值
        step (float): 步长
    
    Returns:
        dict: 最优阈值分析结果
    """
    results = []
    
    for threshold in range(int(min_threshold), int(max_threshold) + 1, int(step)):
        result = generate_pareto_analysis(indicators, threshold)
        results.append({
            'threshold': threshold,
            'key_indicator_count': result['key_indicator_count'],
            'effectiveness_ratio': result['effectiveness_ratio'],
            'pareto_coefficient': result['pareto_coefficient'],
            'key_indicator_ratio': result['indicator_ratio']
        })
    
    # 找到最优阈值（帕累托系数最大的）
    optimal_result = max(results, key=lambda x: x['pareto_coefficient'])
    
    return {
        'optimal_threshold': optimal_result['threshold'],
        'analysis_results': results,
        'optimal_pareto_coefficient': optimal_result['pareto_coefficient'],
        'optimal_key_indicator_count': optimal_result['key_indicator_count'],
        'optimal_effectiveness_ratio': optimal_result['effectiveness_ratio']
    }
