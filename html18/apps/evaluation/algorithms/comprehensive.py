"""
综合权重计算算法
"""

import numpy as np


def calculate_combined_weight(ahp_weight, entropy_weight, ahp_weights, entropy_weights):
    """
    计算局部组合权重
    
    Args:
        ahp_weight (float): AHP权重系数 (α)
        entropy_weight (float): 信息熵权重系数 (1-α)
        ahp_weights (dict): AHP权重数据
        entropy_weights (dict): 信息熵权重数据
    
    Returns:
        dict: 局部组合权重
    """
    combined_weights = {}
    
    # 从四级对三级中获取二级指标
    ahp_level4 = ahp_weights.get('四级对三级', {})
    
    for secondary in ahp_level4:
        combined_weights[secondary] = {}
        for tertiary in ahp_level4[secondary]:
            ahp_w = ahp_level4[secondary][tertiary]
            entropy_w = entropy_weights.get(secondary, {}).get(tertiary, [])
            
            # 确保权重数组长度一致
            min_len = min(len(ahp_w), len(entropy_w))
            combined = []
            
            # 检查该组内是否存在信息熵权重为零的指标
            zero_entropy_indices = [i for i in range(min_len) if entropy_w[i] == 0]
            
            if zero_entropy_indices:
                # 当存在信息熵权重为零的指标时，使用特殊计算方式
                # 1. 计算所有信息熵权重为零的指标的AHP权重总和S
                s = sum(ahp_w[i] for i in zero_entropy_indices)
                # 2. 计算调整系数(1-S)
                adjustment_factor = 1 - s
                # 3. 对于信息熵权重不为零的指标，组合权重 = 调整系数 × 信息熵权重
                for i in range(min_len):
                    if i in zero_entropy_indices:
                        # 信息熵权重为零的指标，组合权重直接取AHP权重
                        combined.append(ahp_w[i])
                    else:
                        # 信息熵权重不为零的指标，组合权重 = 调整系数 × 信息熵权重
                        combined.append(adjustment_factor * entropy_w[i])
            else:
                # 当不存在信息熵权重为零的指标时，使用常规加权平均
                for i in range(min_len):
                    combined_val = ahp_weight * ahp_w[i] + entropy_weight * entropy_w[i]
                    combined.append(combined_val)
            
            combined_weights[secondary][tertiary] = combined
    
    # 处理位置精度的六个三级指标（三级对二级）
    # 注意：位置精度的六个三级指标是三级对二级的指标，它们的组合权重计算方式不同
    # 它们的组合权重 = α * AHP权重 + (1-α) * 信息熵权重
    if '位置精度' in entropy_weights and '三级对二级' in ahp_weights and '位置精度' in ahp_weights['三级对二级']:
        combined_weights['位置精度'] = {}
        # 位置精度的六个三级指标名称
        position_tertiary_indices = {
            '重复定位精度': 0,
            '定位精度': 1,
            '平均位置偏移': 2,
            '定位系统偏差': 3,
            '最小分辨率': 4,
            '反向间隙(差值)': 5
        }
        
        # 提取位置精度的AHP权重和信息熵权重
        position_ahp_weights = ahp_weights['三级对二级']['位置精度']
        position_entropy_weights = []
        position_tertiary_names = []
        
        for tertiary in entropy_weights['位置精度']:
            position_tertiary_names.append(tertiary)
            # 获取三级对二级的AHP权重
            ahp_w = 0
            if tertiary in position_tertiary_indices:
                idx = position_tertiary_indices[tertiary]
                if idx < len(position_ahp_weights):
                    ahp_w = position_ahp_weights[idx]
            position_ahp_weights_for_calc = ahp_w
            
            # 获取信息熵权重
            entropy_w = entropy_weights['位置精度'][tertiary][0] if len(entropy_weights['位置精度'][tertiary]) > 0 else 0
            position_entropy_weights.append(entropy_w)
        
        # 检查该组内是否存在信息熵权重为零的指标
        zero_entropy_indices = [i for i in range(len(position_entropy_weights)) if position_entropy_weights[i] == 0]
        
        for i, tertiary in enumerate(position_tertiary_names):
            ahp_w = position_ahp_weights[i] if i < len(position_ahp_weights) else 0
            entropy_w = position_entropy_weights[i]
            
            if zero_entropy_indices:
                # 当存在信息熵权重为零的指标时，使用特殊计算方式
                # 1. 计算所有信息熵权重为零的指标的AHP权重总和S
                s = sum(position_ahp_weights[j] for j in zero_entropy_indices if j < len(position_ahp_weights))
                # 2. 计算调整系数(1-S)
                adjustment_factor = 1 - s
                # 3. 对于信息熵权重不为零的指标，组合权重 = 调整系数 × 信息熵权重
                if i in zero_entropy_indices:
                    # 信息熵权重为零的指标，组合权重直接取AHP权重
                    combined_val = ahp_w
                else:
                    # 信息熵权重不为零的指标，组合权重 = 调整系数 × 信息熵权重
                    combined_val = adjustment_factor * entropy_w
            else:
                # 当不存在信息熵权重为零的指标时，使用常规加权平均
                combined_val = ahp_weight * ahp_w + entropy_weight * entropy_w
            
            combined_weights['位置精度'][tertiary] = [combined_val]
    
    return combined_weights


def get_indicator_name(tertiary, indicator_idx):
    """
    根据三级指标和索引获取对应的四级指标名称
    
    Args:
        tertiary (str): 三级指标名称
        indicator_idx (int): 指标索引
    
    Returns:
        str: 四级指标名称
    """
    indicator_mapping = {
        '进给轴精度': ['直线度', '平行度', '角度误差', '垂直度'],
        '工作台精度': ['平面度', '直线度', 'T型槽平行度'],
        '主轴精度': ['圆度', '同轴度', '主轴径向跳动', '主轴端面跳动', '主轴轴向窜动'],
        '刀库精度': ['刀库定位精度', '刀库重复定位精度'],
        '微观几何形状误差': ['表面粗糙度'],
        '加工分散性': ['加工工序能力'],
        '工件几何精度': ['尺寸精度', '形状精度'],
        '主轴运动精度': ['主轴径向误差', '主轴轴向误差', '主轴角度误差', '主轴启停响应时间', '主轴高速旋转时的动平衡精度'],
        '多轴联动精度': ['平面圆度误差', '多轴联动同步误差', '轮廓精度', '空间精度', '动态RTCP精度'],
        '传动精度': ['直线圆弧插补轨迹误差', '伺服跟随误差', '高速移动过冲滞后', '低速移动爬行'],
        '热误差': ['进给轴热误差', '主轴径向误差', '主轴轴向误差'],
        '磨损精度': ['刀具磨损', '砂轮磨损']
    }
    if tertiary in indicator_mapping and indicator_idx < len(indicator_mapping[tertiary]):
        return indicator_mapping[tertiary][indicator_idx]
    return tertiary if indicator_idx == 0 else f'{tertiary}{indicator_idx + 1}'


def calculate_global_weight(secondary_to_primary, tertiary_to_secondary, combined_weights, entropy_weights):
    """
    计算全局原始权重
    
    Args:
        secondary_to_primary (dict): 二级对一级的权重
        tertiary_to_secondary (dict): 三级对二级的权重
        combined_weights (dict): 局部组合权重
        entropy_weights (dict): 信息熵权重
    
    Returns:
        list: 全局权重和得分数据
    """
    global_weights_and_scores = []
    
    for secondary, secondary_weight in secondary_to_primary.items():
        if secondary in tertiary_to_secondary:
            for tertiary_idx, (tertiary, tertiary_weight) in enumerate(tertiary_to_secondary[secondary].items()):
                # 检查combined_weights中是否有该三级指标的权重
                if secondary in combined_weights and tertiary in combined_weights[secondary]:
                    local_weights = combined_weights[secondary][tertiary]
                    
                    # 对于位置精度的六个三级指标，它们没有四级指标
                    if secondary == '位置精度':
                        # 位置精度的六个三级指标使用组合权重作为三级对二级的权重
                        # global_original = secondary_weight * combined_weight
                        local_weight = local_weights[0] if len(local_weights) > 0 else 0
                        global_original = secondary_weight * local_weight
                        # 计算全局AHP权重
                        globalAHP = secondary_weight * local_weight
                        # 获取信息熵权重
                        entropy_weight = 0
                        if secondary in entropy_weights and tertiary in entropy_weights[secondary]:
                            entropy_w_list = entropy_weights[secondary][tertiary]
                            entropy_weight = entropy_w_list[0] if len(entropy_w_list) > 0 else 0
                        global_weights_and_scores.append({
                            'secondary': secondary,
                            'tertiary': tertiary,
                            'indicator': tertiary,
                            'indicator_idx': 0,
                            'combined': local_weight,
                            'globalAHP': globalAHP,
                            'global_original': global_original,
                            'entropy_weight': entropy_weight,
                            'weight_chain': f'{secondary_weight:.2f} × {local_weight:.2f}'
                        })
                    else:
                        # 其他三级指标对应多个四级指标
                        for indicator_idx, local_weight in enumerate(local_weights):
                            global_original = secondary_weight * tertiary_weight * local_weight
                            # 计算全局AHP权重（与全局原始权重相同，因为组合权重已经包含了AHP权重）
                            globalAHP = secondary_weight * tertiary_weight * local_weight
                            # 获取信息熵权重
                            entropy_weight = 0
                            if secondary in entropy_weights and tertiary in entropy_weights[secondary]:
                                entropy_w_list = entropy_weights[secondary][tertiary]
                                if indicator_idx < len(entropy_w_list):
                                    entropy_weight = entropy_w_list[indicator_idx]
                            global_weights_and_scores.append({
                                'secondary': secondary,
                                'tertiary': tertiary,
                                'indicator': get_indicator_name(tertiary, indicator_idx),
                                'indicator_idx': indicator_idx,
                                'combined': local_weight,
                                'globalAHP': globalAHP,
                                'global_original': global_original,
                                'entropy_weight': entropy_weight,
                                'weight_chain': f'{secondary_weight:.2f} × {tertiary_weight:.2f}'
                            })
                else:
                    # 如果combined_weights中没有该三级指标的权重，检查entropy_weights中是否有
                    if secondary in entropy_weights and tertiary in entropy_weights[secondary]:
                        entropy_w = entropy_weights[secondary][tertiary]
                        for indicator_idx, entropy_weight in enumerate(entropy_w):
                            global_original = secondary_weight * tertiary_weight * entropy_weight
                            # 计算全局AHP权重（与全局原始权重相同，因为这里使用的是信息熵权重）
                            globalAHP = secondary_weight * tertiary_weight * entropy_weight
                            global_weights_and_scores.append({
                                'secondary': secondary,
                                'tertiary': tertiary,
                                'indicator': get_indicator_name(tertiary, indicator_idx),
                                'indicator_idx': indicator_idx,
                                'combined': entropy_weight,
                                'globalAHP': globalAHP,
                                'global_original': global_original,
                                'entropy_weight': entropy_weight,
                                'weight_chain': f'{secondary_weight:.2f} × {tertiary_weight:.2f}'
                            })
                    else:
                        # 如果entropy_weights中也没有该三级指标的权重，使用默认值
                        local_weight = 1.0
                        global_original = secondary_weight * tertiary_weight * local_weight
                        # 计算全局AHP权重（与全局原始权重相同，因为使用的是默认权重）
                        globalAHP = secondary_weight * tertiary_weight * local_weight
                        global_weights_and_scores.append({
                            'secondary': secondary,
                            'tertiary': tertiary,
                            'indicator': tertiary,
                            'indicator_idx': 0,
                            'combined': local_weight,
                            'globalAHP': globalAHP,
                            'global_original': global_original,
                            'entropy_weight': 0,
                            'weight_chain': f'{secondary_weight:.2f} × {tertiary_weight:.2f}'
                        })
    
    return global_weights_and_scores


def filter_key_indicators(global_weights_and_scores):
    """
    筛选关键指标 - 仅保留信息熵权重不为零的指标
    如果所有指标的信息熵权重都为0，则将所有指标作为关键指标处理

    Args:
        global_weights_and_scores (list): 全局权重和得分数据

    Returns:
        dict: 包含关键指标和计算结果的数据
    """
    key_indicators = []
    non_key_indicators = []
    total_weight_original = 0

    print(f"[DEBUG] filter_key_indicators: 收到 {len(global_weights_and_scores)} 个指标")

    for item in global_weights_and_scores:
        entropy_w = item.get('entropy_weight', 0)
        indicator_name = item.get('indicator', 'unknown')
        print(f"[DEBUG] 指标: {indicator_name}, entropy_weight: {entropy_w}, global_original: {item.get('global_original', 0)}")
        if entropy_w > 0:
            key_indicators.append(item)
            total_weight_original += item['global_original']
        else:
            non_key_indicators.append(item)

    print(f"[DEBUG] filter_key_indicators: 关键指标数量 = {len(key_indicators)}, 非关键指标数量 = {len(non_key_indicators)}")
    print(f"[DEBUG] filter_key_indicators: 关键指标列表 = {[item.get('indicator', 'unknown') for item in key_indicators]}")
    
    # 如果所有指标的信息熵权重都为0，则将所有指标作为关键指标处理
    if not key_indicators and non_key_indicators:
        print(f"[DEBUG] 所有指标的信息熵权重都为0，将所有指标作为关键指标处理")
        key_indicators = non_key_indicators
        non_key_indicators = []
        total_weight_original = sum(item['global_original'] for item in key_indicators)
    
    if not key_indicators:
        return {
            'all_indicators': global_weights_and_scores,
            'key_indicators': [],
            'non_key_indicators': non_key_indicators,
            'total_weight_original': 0,
            'key_indicator_count': 0,
            'total_indicator_count': len(global_weights_and_scores)
        }
    
    for item in key_indicators:
        item['is_key'] = True
        item['normalized_weight'] = item['global_original'] / total_weight_original
    
    for item in non_key_indicators:
        item['is_key'] = False
        item['normalized_weight'] = 0
    
    all_indicators = key_indicators + non_key_indicators
    
    return {
        'all_indicators': all_indicators,
        'key_indicators': key_indicators,
        'non_key_indicators': non_key_indicators,
        'total_weight_original': total_weight_original,
        'key_indicator_count': len(key_indicators),
        'total_indicator_count': len(global_weights_and_scores)
    }


def calculate_indicator_score(error_value, standard_tolerance):
    """
    计算指标得分
    
    Args:
        error_value (float): 误差值（不是测量值与标准值的差，而是独立的误差变量）
        standard_tolerance (float): 标准允差
    
    Returns:
        float: 指标得分
    """
    if standard_tolerance <= 0:
        return 0.0
    
    # 计算得分：(标准允差-|误差值|)/标准允差 × 100（转换为百分制）
    score = (standard_tolerance - abs(error_value)) / standard_tolerance * 100
    return max(0, score)  # 确保得分不为负


def calculate_final_score(key_indicators):
    """
    计算最终综合得分
    
    Args:
        key_indicators (list): 关键指标数据
    
    Returns:
        float: 最终综合得分
    """
    if not key_indicators:
        return 0.0
    
    total_weighted_score = 0
    total_weight = 0
    
    for item in key_indicators:
        if 'score' in item and 'normalized_weight' in item:
            total_weighted_score += item['score'] * item['normalized_weight']
            total_weight += item['normalized_weight']
    
    if total_weight > 0:
        weighted_average = total_weighted_score / total_weight
        return (0.6 + weighted_average * 0.4) * 100
    return 0.0


def comprehensive_weight_calculation(data):
    """
    综合权重计算主函数
    
    Args:
        data (dict): 包含所有必要数据的字典
    
    Returns:
        dict: 计算结果
    """
    # 提取数据
    ahp_weight = data.get('ahp_weight', 0.5)
    entropy_weight = 1 - ahp_weight
    ahp_weights = data.get('ahp_weights', {})
    entropy_weights = data.get('entropy_weights', {})
    secondary_to_primary = data.get('secondary_to_primary', {})
    tertiary_to_secondary = data.get('tertiary_to_secondary', {})
    indicator_scores = data.get('indicator_scores', {})  # 新增：用户评价指标得分
    error_values = data.get('error_values', {})  # 兼容：误差值数据（可选）
    standard_tolerances = data.get('standard_tolerances', {})  # 兼容：标准允差数据（可选）
    pareto_threshold = data.get('pareto_threshold', 80)
    
    # 计算局部组合权重
    combined_weights = calculate_combined_weight(
        ahp_weight, entropy_weight, ahp_weights, entropy_weights
    )
    
    # 计算全局权重
    global_weights = calculate_global_weight(
        secondary_to_primary, tertiary_to_secondary, combined_weights, entropy_weights
    )
    
    # 添加得分信息
    for item in global_weights:
        secondary = item['secondary']
        tertiary = item['tertiary']
        indicator_idx = item.get('indicator_idx', 0)
        
        # 优先使用用户评价指标得分
        score = 0.0
        
        if indicator_scores and secondary in indicator_scores and tertiary in indicator_scores[secondary]:
            score_list = indicator_scores[secondary][tertiary]
            if isinstance(score_list, list) and indicator_idx < len(score_list):
                score = score_list[indicator_idx]
            elif isinstance(score_list, list) and len(score_list) > 0:
                score = score_list[0]
            elif isinstance(score_list, (int, float)):
                score = float(score_list)
        
        # 如果没有用户评价指标得分，则使用误差值和允差值计算（兼容旧逻辑）
        if score == 0.0 and error_values and standard_tolerances:
            error_list = error_values.get(secondary, {}).get(tertiary, [0])
            error_value = error_list[indicator_idx] if indicator_idx < len(error_list) else error_list[0]
            
            tolerance_list = standard_tolerances.get(secondary, {}).get(tertiary, [1])
            standard_tolerance = tolerance_list[indicator_idx] if indicator_idx < len(tolerance_list) else tolerance_list[0]
            
            # 计算得分
            score = calculate_indicator_score(error_value, standard_tolerance)
            
            # 保存误差值和标准允差
            item['error_value'] = error_value
            item['standard_tolerance'] = standard_tolerance
        
        # 更新项目数据
        item['score'] = score
        item['weighted_score_original'] = item['global_original'] * score
    
    # 筛选关键指标 - 仅保留信息熵权重不为零的指标
    filter_result = filter_key_indicators(global_weights)
    
    # 计算最终得分
    final_score = calculate_final_score(filter_result['key_indicators'])
    
    return {
        'combined_weights': combined_weights,
        'global_weights': global_weights,
        'filter_result': filter_result,
        'final_score': final_score,
        'parameters': {
            'ahp_weight': ahp_weight,
            'entropy_weight': entropy_weight
        }
    }