"""
判断矩阵生成算法

本模块实现了根据行和数据生成判断矩阵的功能，用于AHP层次分析法。

主要功能：
- generate_judgment_matrix_from_sums: 根据行和数据生成判断矩阵
- process_sum_excel_file: 批量处理Excel文件中的多个sheet
- display_matrix_info: 显示判断矩阵信息

算法原理：
1. 判断矩阵元素计算：a_ij = row_sum_i / row_sum_j
2. 对角线元素：a_ii = 1
3. 互反性：a_ij = 1/a_ji

判断矩阵性质：
1. 方阵：矩阵必须是n×n的方阵
2. 正互反性：a_ij = 1/a_ji
3. 对角线为1：a_ii = 1
4. 正值矩阵：所有元素大于0

应用场景：
- 从行和数据自动生成判断矩阵
- AHP层次分析法的预处理
- 批量处理多个判断矩阵
"""

import pandas as pd
import numpy as np
import os


def generate_judgment_matrix_from_sums(row_sums_series):
    """
    根据行和数据生成判断矩阵

    参数:
        row_sums_series: pandas Series, 每行的和

    返回:
        np.ndarray: n×n的判断矩阵，其中n为行数

    计算公式:
        a_ij = row_sum_i / row_sum_j
        a_ii = 1
    """
    # 获取行数
    n = len(row_sums_series)

    # 初始化n×n的判断矩阵
    matrix = np.ones((n, n))

    # 将Series转换为数组
    sums = row_sums_series.values.astype(float)

    # 填充矩阵
    for i in range(n):
        for j in range(n):
            if i != j:
                # a_ij = ni / nj
                if sums[j] != 0:
                    matrix[i, j] = sums[i] / sums[j]
                else:
                    # 如果nj为0，设为0（实际中不应出现）
                    matrix[i, j] = 0

    return matrix


def process_sum_excel_file(input_path, output_path):
    """
    处理行和Excel文件，为每个sheet生成判断矩阵

    参数:
        input_path: str, 输入Excel文件路径（行和数据）
        output_path: str, 输出Excel文件路径（判断矩阵）

    返回:
        dict: 包含所有sheet判断矩阵的字典

    处理流程:
        1. 读取Excel文件的所有sheet
        2. 对每个sheet的第一列（行和）生成判断矩阵
        3. 验证判断矩阵的性质
        4. 保存结果到输出文件
    """
    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    print(f"读取文件: {input_path}")

    # 1. 读取所有sheet，设置header=None确保第一行作为数据读取
    excel_data = pd.read_excel(input_path, sheet_name=None, header=None)

    # 2. 存储所有判断矩阵
    judgment_matrices = {}

    print("\n开始生成判断矩阵...")
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:

        # 3. 遍历每个sheet
        for sheet_name, df in excel_data.items():
            print(f"处理sheet: {sheet_name}")

            # 检查是否为空sheet
            if df.empty:
                print(f"  -> sheet为空，跳过")
                pd.DataFrame().to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                judgment_matrices[sheet_name] = pd.DataFrame()
                continue

            # 4. 获取行和数据（第一列）
            if df.shape[1] >= 1:
                row_sums = df[0]  # 第一列是行和

                # 5. 生成判断矩阵
                matrix = generate_judgment_matrix_from_sums(row_sums)

                # 6. 将矩阵保存到DataFrame
                matrix_df = pd.DataFrame(matrix)

                # 7. 写入Excel
                matrix_df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                judgment_matrices[sheet_name] = matrix_df

                print(f"  -> 生成 {matrix.shape[0]}×{matrix.shape[1]} 判断矩阵")

                # 8. 验证判断矩阵性质
                n = matrix.shape[0]
                is_valid = True

                # 检查对角线是否为1
                for i in range(n):
                    if not np.isclose(matrix[i, i], 1.0):
                        is_valid = False
                        break

                # 检查互反性 a_ij = 1/a_ji
                for i in range(n):
                    for j in range(n):
                        if i != j:
                            if not np.isclose(matrix[i, j], 1.0 / matrix[j, i]):
                                is_valid = False
                                break
                    if not is_valid:
                        break

                if is_valid:
                    print(f"  -> 判断矩阵验证通过")
                else:
                    print(f"  -> 警告：判断矩阵验证失败")
            else:
                print(f"  -> sheet没有数据列，跳过")
                pd.DataFrame().to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                judgment_matrices[sheet_name] = pd.DataFrame()

    print(f"\n处理完成！判断矩阵已保存到: {output_path}")
    return judgment_matrices


def display_matrix_info(matrices_dict):
    """
    显示判断矩阵信息

    参数:
        matrices_dict: dict, 包含所有sheet判断矩阵的字典

    显示内容:
        - 矩阵维度
        - 矩阵内容（前4×4部分）
        - 矩阵性质检查结果
    """
    print("\n" + "=" * 60)
    print("判断矩阵信息:")
    print("=" * 60)

    for sheet_name, matrix_df in matrices_dict.items():
        if not matrix_df.empty:
            matrix = matrix_df.values
            n = matrix.shape[0]

            print(f"\n{sheet_name}:")
            print(f"  矩阵维度: {n}×{n}")

            # 显示矩阵的一部分（如果太大，只显示前4×4）
            if n <= 6:
                print(f"  判断矩阵:")
                for i in range(min(n, 4)):
                    row_str = "  ["
                    for j in range(min(n, 4)):
                        row_str += f"{matrix[i, j]:.3f}, "
                    row_str = row_str.rstrip(", ") + "]"
                    print(row_str)
                if n > 4:
                    print(f"  ... (只显示前4×4)")
            else:
                # 只显示左上角4×4
                print(f"  判断矩阵前4×4部分:")
                for i in range(4):
                    row_str = "  ["
                    for j in range(4):
                        row_str += f"{matrix[i, j]:.3f}, "
                    row_str = row_str.rstrip(", ") + "]"
                    print(row_str)
                print(f"  ... (矩阵过大，只显示前4×4)")

            # 检查矩阵性质
            print(f"  矩阵性质检查:")

            # 检查对角线是否为1
            diag_check = all(np.isclose(matrix[i, i], 1.0) for i in range(n))
            print(f"    - 对角线元素全为1: {'✓' if diag_check else '✗'}")

            # 检查互反性
            reciprocal_check = True
            for i in range(n):
                for j in range(i + 1, n):
                    if not np.isclose(matrix[i, j], 1.0 / matrix[j, i]):
                        reciprocal_check = False
                        break
                if not reciprocal_check:
                    break
            print(f"    - 满足互反性 a_ij = 1/a_ji: {'✓' if reciprocal_check else '✗'}")

            # 检查是否为正值矩阵
            positive_check = np.all(matrix > 0)
            print(f"    - 所有元素大于0: {'✓' if positive_check else '✗'}")
        else:
            print(f"\n{sheet_name}: 空sheet")


def main():
    """
    主函数：根据行和Excel文件生成判断矩阵
    """
    # 设置文件路径
    input_file = '统计表_合并行和.xlsx'  # 上一步生成的行和文件
    output_file = '统计表_判断矩阵.xlsx'  # 判断矩阵输出文件名

    try:
        # 1. 处理行和文件，生成判断矩阵
        judgment_matrices = process_sum_excel_file(input_file, output_file)

        # 2. 显示判断矩阵信息
        display_matrix_info(judgment_matrices)

        # 3. 提供进一步处理的建议
        print("\n" + "=" * 60)
        print("下一步建议:")
        print("=" * 60)
        print("判断矩阵已生成，可以进行以下操作:")
        print("1. 使用AHP方法计算每个矩阵的特征向量（权重）")
        print("2. 进行一致性检验（CR < 0.1）")
        print("3. 如果有多个专家的判断矩阵，可以聚合后再计算权重")
        print("4. 如果有多个层级的指标，可以进行层次总排序")
        print("\n注意：")
        print("- 生成的判断矩阵基于行和的比例关系")
        print("- 如果矩阵不满足一致性要求，可能需要调整原始数据")
        print("- 建议检查每个矩阵是否合理")

    except FileNotFoundError as e:
        print(f"错误: {e}")
        print(f"请确保文件 '{input_file}' 在当前目录中")
        print(f"需要先运行第一步代码生成行和文件")
    except Exception as e:
        print(f"处理过程中发生错误: {e}")


# 执行主函数
if __name__ == "__main__":
    main()
