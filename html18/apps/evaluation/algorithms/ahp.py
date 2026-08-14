import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime


class AHPCalculator:
    """
    AHP层次分析法计算器类
    用于执行AHP算法的核心功能，包括权重计算和一致性检验
    """
    
    def __init__(self):
        """
        初始化AHP计算器
        """
        self.name = "层次分析法"
        self.description = "基于专家判断的层次分析法"
    
    def calculate_weights(self, matrix):
        """
        计算权重并进行一致性检验
        
        参数:
            matrix: np.ndarray, n×n的判断矩阵
            
        返回:
            dict: 包含权重计算结果和一致性检验结果的字典
        """
        # 调用现有的权重计算函数
        geometric_means, normalized_weights, consistency = calculate_weights_from_matrix(matrix)
        
        return {
            'geometric_means': geometric_means,
            'normalized_weights': normalized_weights,
            'consistency': consistency
        }
    
    def calculate_consistency(self, matrix, weights):
        """
        计算判断矩阵的一致性检验指标
        
        参数:
            matrix: np.ndarray, n×n的判断矩阵
            weights: np.ndarray, 归一化权重向量
            
        返回:
            dict: 包含一致性检验结果的字典
        """
        n = matrix.shape[0]
        return calculate_consistency(matrix, weights, n)
    
    def get_random_index(self, n):
        """
        获取平均随机一致性指标RI
        
        参数:
            n: int, 矩阵阶数
            
        返回:
            float: 对应阶数的RI值
        """
        return get_random_index(n)
    
    def process_matrix(self, matrix, indicator_names=None):
        """
        处理判断矩阵，计算权重并返回结果
        
        参数:
            matrix: np.ndarray, n×n的判断矩阵
            indicator_names: list, 指标名称列表
            
        返回:
            dict: 包含完整处理结果的字典
        """
        n = matrix.shape[0]
        
        # 如果没有提供指标名称，生成默认名称
        if indicator_names is None:
            indicator_names = [f"指标{i + 1}" for i in range(n)]
        
        # 计算权重
        result = self.calculate_weights(matrix)
        
        # 添加指标名称到结果中
        result['indicator_names'] = indicator_names
        
        return result
    
    def validate_matrix(self, matrix):
        """
        验证判断矩阵是否有效
        
        参数:
            matrix: np.ndarray, 要验证的矩阵
            
        返回:
            bool: 矩阵是否有效
            str: 错误信息（如果矩阵无效）
        """
        # 检查是否为方阵
        if matrix.shape[0] != matrix.shape[1]:
            return False, "矩阵必须是方阵"
        
        # 检查是否为正数矩阵
        if np.any(matrix <= 0):
            return False, "矩阵元素必须为正数"
        
        # 检查是否满足正互反性
        n = matrix.shape[0]
        for i in range(n):
            for j in range(n):
                if abs(matrix[i, j] * matrix[j, i] - 1) > 1e-6:
                    return False, "矩阵必须满足正互反性 (a_ij = 1/a_ji)"
        
        return True, "矩阵有效"


def calculate_weights_from_matrix(matrix):
    """
    从判断矩阵计算权重，并计算一致性检验指标


    参数:
        matrix: np.ndarray, n×n的判断矩阵

    返回:
        tuple: (几何平均数, 归一化权重, 一致性检验结果字典)
    """
    n = matrix.shape[0]

    # 1. 计算每行的几何平均数（开n次方根）
    geometric_means = np.ones(n)

    for i in range(n):
        # 计算第i行所有元素的乘积
        product = 1.0
        for j in range(n):
            product *= matrix[i, j]

        # 开n次方根
        geometric_means[i] = product ** (1 / n)

    # 2. 计算几何平均数的总和
    sum_means = np.sum(geometric_means)

    # 3. 计算归一化权重
    normalized_weights = geometric_means / sum_means

    # 4. 计算一致性检验指标
    consistency_results = calculate_consistency(matrix, normalized_weights, n)

    return geometric_means, normalized_weights, consistency_results


def calculate_consistency(matrix, weights, n):
    """
    计算判断矩阵的一致性检验指标（论文公式(3)-(4)）

    参数:
        matrix: np.ndarray, n×n的判断矩阵
        weights: np.ndarray, 归一化权重向量
        n: int, 矩阵阶数

    返回:
        dict: 包含一致性检验结果的字典
    """
    # 计算加权和向量
    weighted_sum = np.dot(matrix, weights)

    # 计算最大特征值 λ_max（论文公式(3)的λ_max）
    # λ_max = 平均值(加权和向量 / 权重向量)
    lambda_max = np.mean(weighted_sum / weights)

    # 计算一致性指标CI（论文公式(3)）
    CI = (lambda_max - n) / (n - 1) if n > 1 else 0

    # 获取平均随机一致性指标RI（论文表1）
    RI = get_random_index(n)

    # 计算一致性比例CR（论文公式(4)）
    CR = CI / RI if RI != 0 else 0

    # 判断一致性是否可接受（CR < 0.1）
    is_consistent = CR < 0.1 if n > 1 else True

    return {
        'lambda_max': lambda_max,
        'CI': CI,
        'RI': RI,
        'CR': CR,
        'is_consistent': is_consistent
    }


def get_random_index(n):
    """
    获取平均随机一致性指标RI（论文表1）

    参数:
        n: int, 矩阵阶数

    返回:
        float: 对应阶数的RI值
    """
    # 论文表1：平均随机一致性指标RI表
    ri_table = {
        1: 0.0, 2: 0.0, 3: 0.52, 4: 0.89, 5: 1.12,
        6: 1.26, 7: 1.36, 8: 1.41, 9: 1.46, 10: 1.49,
        11: 1.52, 12: 1.54, 13: 1.56, 14: 1.58, 15: 1.59
    }

    # 如果n大于表中的最大值，使用插值法估算
    if n in ri_table:
        return ri_table[n]
    elif n <= 0:
        return 0.0
    else:
        # 对于更大的n，使用近似公式：RI = 1.98 * (n - 2) / n
        return 1.98 * (n - 2) / n


def input_matrix_manually():
    """
    手动输入判断矩阵

    返回:
        tuple: (矩阵, 指标名称列表)
    """
    print("\n" + "=" * 60)
    print("手动输入判断矩阵")
    print("=" * 60)

    # 输入指标数量
    while True:
        try:
            n = int(input("请输入指标数量 (矩阵阶数): "))
            if n <= 0:
                print("指标数量必须为正整数，请重新输入！")
                continue
            if n > 15:
                print("注意：指标数量较多，计算时间可能较长")
                confirm = input("是否继续？(y/n): ").lower()
                if confirm != 'y':
                    continue
            break
        except ValueError:
            print("请输入有效的整数！")

    # 输入指标名称
    indicator_names = []
    print(f"\n请输入 {n} 个指标的名称:")
    for i in range(n):
        name = input(f"指标{i + 1}的名称: ").strip()
        if not name:
            name = f"指标{i + 1}"
        indicator_names.append(name)

    print(f"\n将创建一个 {n}×{n} 的判断矩阵")
    print("请根据各指标之间的相对重要性输入矩阵元素")
    print("重要程度标度: 1-同等重要, 3-稍微重要, 5-明显重要, 7-强烈重要, 9-极端重要")
    print("              2,4,6,8-中间值, 倒数-表示相反重要性")

    # 创建空矩阵
    matrix = np.eye(n)  # 对角线初始化为1

    # 只输入上三角部分，下三角自动取倒数
    for i in range(n):
        for j in range(i + 1, n):
            while True:
                try:
                    prompt = f"{indicator_names[i]} 相对于 {indicator_names[j]} 的重要性 (1-9或其倒数): "
                    value = input(prompt).strip()

                    # 处理分数输入
                    if '/' in value:
                        numerator, denominator = value.split('/')
                        value = float(numerator) / float(denominator)
                    else:
                        value = float(value)

                    # 验证输入值
                    if value <= 0:
                        print("重要性必须为正数，请重新输入！")
                        continue

                    matrix[i, j] = value
                    matrix[j, i] = 1.0 / value
                    break

                except (ValueError, ZeroDivisionError):
                    print("输入无效，请输入数字或分数！")

    return matrix, indicator_names


def display_matrix(matrix, indicator_names, title="判断矩阵"):
    """
    显示矩阵

    参数:
        matrix: np.ndarray, 要显示的矩阵
        indicator_names: list, 指标名称列表
        title: str, 标题
    """
    n = matrix.shape[0]

    print(f"\n{title}:")
    print("-" * (n * 10 + 10))

    # 打印列标题
    header = " " * 12
    for name in indicator_names:
        header += f"{name[:8]:>10}"  # 限制名称长度
    print(header)

    # 打印矩阵
    for i in range(n):
        row_str = f"{indicator_names[i][:10]:<12}"  # 行标题
        for j in range(n):
            row_str += f"{matrix[i, j]:>10.4f}"
        print(row_str)

    print("-" * (n * 10 + 10))


def display_results(geometric_means, normalized_weights, consistency, indicator_names):
    """
    显示计算结果

    参数:
        geometric_means: np.ndarray, 几何平均数
        normalized_weights: np.ndarray, 归一化权重
        consistency: dict, 一致性检验结果
        indicator_names: list, 指标名称列表
    """
    n = len(geometric_means)

    print(f"\n{'=' * 80}")
    print("AHP权重计算结果")
    print(f"{'=' * 80}")

    # 显示权重结果
    print("\n权重计算结果:")
    print("-" * 80)
    print(f"{'序号':^6} {'指标名称':^20} {'几何平均数':^15} {'归一化权重':^15} {'权重百分比':^15}")
    print("-" * 80)

    for i in range(n):
        weight_percent = normalized_weights[i] * 100
        print(f"{i + 1:^6} {indicator_names[i]:^20} {geometric_means[i]:^15.6f} "
              f"{normalized_weights[i]:^15.6f} {weight_percent:^15.2f}%")

    print("-" * 80)
    print(f"{'合计':^6} {'-':^20} {np.sum(geometric_means):^15.6f} "
          f"{np.sum(normalized_weights):^15.6f} {100:^15.2f}%")

    # 显示一致性检验结果
    print(f"\n一致性检验结果:")
    print("-" * 80)
    print(f"矩阵阶数: {n}")
    print(f"最大特征值 λ_max = {consistency['lambda_max']:.6f}")
    print(f"一致性指标 CI = (λ_max - n)/(n - 1) = {consistency['CI']:.6f}")
    print(f"随机一致性指标 RI (n={n}) = {consistency['RI']:.6f}")
    print(f"一致性比率 CR = CI/RI = {consistency['CR']:.6f}")

    if consistency['is_consistent']:
        print(f"\n结论: CR = {consistency['CR']:.6f} < 0.1，矩阵一致性可接受 ✓")
    else:
        print(f"\n警告: CR = {consistency['CR']:.6f} ≥ 0.1，矩阵一致性不可接受，建议调整判断矩阵！")

    print("-" * 80)


def save_results_to_excel(matrix, indicator_names, geometric_means, normalized_weights,
                          consistency, filename=None):
    """
    将手动输入矩阵的结果保存到Excel文件

    参数:
        matrix: np.ndarray, 判断矩阵
        indicator_names: list, 指标名称列表
        geometric_means: np.ndarray, 几何平均数
        normalized_weights: np.ndarray, 归一化权重
        consistency: dict, 一致性检验结果
        filename: str, 输出文件名

    返回:
        str: 保存的文件名
    """
    n = matrix.shape[0]

    # 生成默认文件名
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"AHP_计算结果_{timestamp}.xlsx"

    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 1. 判断矩阵sheet
            matrix_df = pd.DataFrame(matrix, index=indicator_names, columns=indicator_names)
            matrix_df.to_excel(writer, sheet_name='判断矩阵')

            # 2. 权重结果sheet
            weight_data = []
            for i in range(n):
                weight_data.append([
                    i + 1,
                    indicator_names[i],
                    geometric_means[i],
                    normalized_weights[i],
                    normalized_weights[i] * 100
                ])

            weight_df = pd.DataFrame(weight_data,
                                     columns=['序号', '指标名称', '几何平均数', '归一化权重', '权重百分比(%)'])
            weight_df.to_excel(writer, sheet_name='权重结果', index=False)

            # 添加汇总行
            summary_row = pd.DataFrame([['合计', '-', np.sum(geometric_means),
                                         np.sum(normalized_weights), 100.00]],
                                       columns=['序号', '指标名称', '几何平均数', '归一化权重', '权重百分比(%)'])
            weight_df_with_summary = pd.concat([weight_df, summary_row], ignore_index=True)
            weight_df_with_summary.to_excel(writer, sheet_name='权重结果', index=False)

            # 3. 一致性检验sheet
            consistency_data = [
                ['矩阵阶数', n],
                ['最大特征值 (λ_max)', consistency['lambda_max']],
                ['一致性指标 (CI)', consistency['CI']],
                ['随机一致性指标 (RI)', consistency['RI']],
                ['一致性比率 (CR)', consistency['CR']],
                ['一致性判断', '可接受' if consistency['is_consistent'] else '不可接受'],
                ['判断标准', 'CR < 0.1 可接受']
            ]

            consistency_df = pd.DataFrame(consistency_data, columns=['项目', '值/说明'])
            consistency_df.to_excel(writer, sheet_name='一致性检验', index=False)

            # 4. 计算说明sheet
            notes_data = [
                ['计算时间', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                ['软件版本', 'AHP权重计算器 v2.0'],
                ['矩阵阶数', f'{n}×{n}'],
                ['指标数量', n],
                ['计算方法', '几何平均法（根法）'],
                ['一致性检验', '基于λ_max、CI、RI、CR的完全一致性检验'],
                ['参考文献',
                 '邓雪等. 层次分析法权重计算方法分析及其应用研究[J]. 数学的实践与认识, 2012, 42(7): 93-100.']
            ]

            notes_df = pd.DataFrame(notes_data, columns=['项目', '内容'])
            notes_df.to_excel(writer, sheet_name='计算说明', index=False)

        return filename

    except Exception as e:
        raise Exception(f"保存文件时出错: {e}")


def process_judgment_matrix_file(input_path, output_path):
    """
    处理判断矩阵Excel文件，计算权重和一致性检验

    参数:
        input_path: str, 判断矩阵Excel文件路径
        output_path: str, 权重输出Excel文件路径
    """
    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    print(f"读取判断矩阵文件: {input_path}")

    # 读取所有sheet
    excel_data = pd.read_excel(input_path, sheet_name=None, header=None)

    print("\n开始计算权重和一致性检验...")

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # 遍历每个sheet
        for sheet_name, df in excel_data.items():
            print(f"\n处理sheet: {sheet_name}")

            # 检查是否为空sheet
            if df.empty:
                print(f"  -> sheet为空，跳过")
                pd.DataFrame().to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                continue

            # 获取判断矩阵
            matrix = df.values.astype(float)
            n = matrix.shape[0]

            # 检查是否为方阵
            if matrix.shape[0] != matrix.shape[1]:
                print(f"  -> 非方阵({matrix.shape})，跳过")
                continue

            print(f"  -> 处理 {n}×{n} 判断矩阵")

            # 生成指标名称
            indicator_names = [f"指标{i + 1}" for i in range(n)]

            # 计算权重和一致性检验
            geometric_means, normalized_weights, consistency = calculate_weights_from_matrix(matrix)

            # 创建结果数组
            result_data = []

            # 添加标题
            result_data.append([f"判断矩阵: {sheet_name}"])
            result_data.append([])

            # 添加表头
            headers = ["序号", "指标", "几何平均数", "归一化权重", "权重百分比(%)"]
            result_data.append(headers)

            # 添加每行数据
            for i in range(n):
                weight_percent = normalized_weights[i] * 100
                row_data = [
                    i + 1,
                    indicator_names[i],
                    geometric_means[i],
                    normalized_weights[i],
                    weight_percent
                ]
                result_data.append(row_data)

            # 添加汇总行
            result_data.append([
                "合计", "-",
                np.sum(geometric_means),
                np.sum(normalized_weights),
                100.00
            ])

            result_data.append([])  # 空行分隔
            result_data.append(["一致性检验"])
            result_data.append(["检验项目", "值", "计算公式", "判断结果"])

            result_data.append([
                "矩阵阶数(n)",
                n,
                "",
                ""
            ])

            result_data.append([
                "最大特征值(λ_max)",
                f"{consistency['lambda_max']:.6f}",
                "λ_max = mean(A·w / w)",
                ""
            ])

            result_data.append([
                "一致性指标(CI)",
                f"{consistency['CI']:.6f}",
                f"CI = (λ_max-{n})/({n}-1)",
                ""
            ])

            result_data.append([
                "随机一致性指标(RI)",
                f"{consistency['RI']:.6f}",
                f"查表得到(n={n})",
                ""
            ])

            result_data.append([
                "一致性比率(CR)",
                f"{consistency['CR']:.6f}",
                "CR = CI/RI",
                ""
            ])

            result_data.append([
                "一致性判断",
                "可接受" if consistency['is_consistent'] else "不可接受",
                "CR < 0.1 可接受",
                "✓" if consistency['is_consistent'] else "✗"
            ])

            # 转换为DataFrame
            result_df = pd.DataFrame(result_data)

            # 写入Excel，不包含索引和列名
            result_df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)

            print(f"  -> 完成权重计算和一致性检验")
            print(f"     归一化权重和: {np.sum(normalized_weights):.6f}")
            print(
                f"     一致性比率CR: {consistency['CR']:.6f} ({'可接受' if consistency['is_consistent'] else '需调整'})")

    print(f"\n处理完成！权重计算结果已保存到: {output_path}")


def show_menu():
    """
    显示主菜单
    """
    print("\n" + "=" * 60)
    print("AHP层次分析法权重计算器")
    print("=" * 60)
    print("1. 从Excel文件读取判断矩阵")
    print("2. 手动输入判断矩阵")
    print("3. 查看使用说明")
    print("4. 退出程序")
    print("=" * 60)


def show_instructions():
    """
    显示使用说明
    """
    print("\n" + "=" * 60)
    print("AHP层次分析法使用说明")
    print("=" * 60)
    print("层次分析法(AHP)是一种多准则决策分析方法")
    print("")
    print("判断矩阵要求:")
    print("1. 矩阵必须是方阵 (n×n)")
    print("2. 对角线元素必须为1 (a_ii = 1)")
    print("3. 矩阵应满足正互反性: a_ij = 1/a_ji")
    print("4. 一致性比率CR < 0.1 表示矩阵一致性可接受")
    print("")
    print("重要程度标度 (1-9标度法):")
    print("1  - 同等重要")
    print("3  - 稍微重要")
    print("5  - 明显重要")
    print("7  - 强烈重要")
    print("9  - 极端重要")
    print("2,4,6,8 - 中间值")
    print("倒数   - 表示相反重要性 (如1/3表示j比i稍微重要)")
    print("")
    print("计算步骤:")
    print("1. 输入指标数量")
    print("2. 输入各指标名称")
    print("3. 输入判断矩阵 (只需输入上三角部分)")
    print("4. 系统自动计算权重和一致性")
    print("5. 结果自动保存到Excel文件")
    print("=" * 60)
    input("\n按Enter键返回主菜单...")


def main():
    """
    主函数：AHP权重计算器
    """
    print("=" * 60)
    print("AHP层次分析法权重计算器")
    print("版本: 2.0 (含一致性检验和矩阵输入功能)")
    print("=" * 60)

    while True:
        show_menu()

        try:
            choice = input("\n请选择操作 (1-4): ").strip()

            if choice == '1':
                # 从Excel文件读取
                print("\n" + "=" * 60)
                print("从Excel文件读取判断矩阵")
                print("=" * 60)

                default_input = '统计表_判断矩阵.xlsx'
                default_output = '统计表_权重计算结果.xlsx'

                input_file = input(f"请输入Excel文件路径 (直接回车使用默认: {default_input}): ").strip()
                if not input_file:
                    input_file = default_input

                output_file = input(f"请输入输出文件路径 (直接回车使用默认: {default_output}): ").strip()
                if not output_file:
                    output_file = default_output

                try:
                    process_judgment_matrix_file(input_file, output_file)
                    print(f"\n✓ 结果已保存到: {output_file}")
                    input("\n按Enter键返回主菜单...")

                except FileNotFoundError as e:
                    print(f"\n✗ 错误: {e}")
                    print(f"请确保文件 '{input_file}' 在当前目录中")
                    input("\n按Enter键返回主菜单...")
                except Exception as e:
                    print(f"\n✗ 处理过程中发生错误: {e}")
                    input("\n按Enter键返回主菜单...")

            elif choice == '2':
                # 手动输入矩阵
                try:
                    # 输入矩阵
                    matrix, indicator_names = input_matrix_manually()

                    # 显示输入的矩阵
                    display_matrix(matrix, indicator_names)

                    # 确认矩阵是否正确
                    confirm = input("\n矩阵输入完成，是否开始计算？(y/n): ").lower()
                    if confirm != 'y':
                        print("已取消计算")
                        input("\n按Enter键返回主菜单...")
                        continue

                    # 计算权重和一致性检验
                    print("\n正在进行计算...")
                    geometric_means, normalized_weights, consistency = calculate_weights_from_matrix(matrix)

                    # 显示计算结果
                    display_results(geometric_means, normalized_weights, consistency, indicator_names)

                    # 直接保存结果，不询问
                    try:
                        # 生成文件名
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"AHP_手动输入_{timestamp}.xlsx"

                        # 保存结果
                        saved_filename = save_results_to_excel(
                            matrix, indicator_names, geometric_means,
                            normalized_weights, consistency, filename
                        )

                        print(f"\n✓ 计算结果已自动保存到文件: {saved_filename}")

                    except Exception as save_error:
                        print(f"\n✗ 保存文件时出错: {save_error}")
                        print("但计算已完成，请记录以上显示的结果")

                    input("\n按Enter键返回主菜单...")

                except Exception as e:
                    print(f"\n✗ 计算过程中发生错误: {e}")
                    input("\n按Enter键返回主菜单...")

            elif choice == '3':
                # 显示使用说明
                show_instructions()

            elif choice == '4':
                # 退出程序
                print("\n感谢使用AHP层次分析法权重计算器！")
                print("程序已退出")
                break

            else:
                print("\n无效选择，请输入1-4之间的数字！")
                input("\n按Enter键继续...")

        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")
            input("\n按Enter键继续...")


# 执行主函数
if __name__ == "__main__":
    main()