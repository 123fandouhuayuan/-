"""
信息熵权重计算算法

本模块实现了基于信息熵理论的客观权重计算方法，用于反映指标数据的离散程度。

主要功能：
- calculate_e: 计算信息熵
- process_data_to_weight: 处理数据列，计算其权重
- process_report: 处理 Excel 文件，计算各列的信息熵权重
- calculate_entropy_weight: 使用极差标准化方法计算信息熵权重

算法原理：
1. 数据标准化：T = (max - value) / (max - min) 或 T = value / Σ(value)
2. 概率计算：P = T / Σ(T)
3. 信息熵计算：E = -k * Σ(Pi * ln(Pi))，其中 k = 1/ln(n)
4. 权重计算：D = 1 - E
5. 归一化权重：W = D / Σ(D)

应用场景：
- 当指标数据存在较大差异时，使用信息熵权重
- 需要客观反映数据离散程度时使用
- 与AHP权重结合，形成组合权重
"""

import pandas as pd
import numpy as np
import os
import math


def calculate_e(X,num):
    """
    计算信息熵

    参数:
        X: list, 概率分布列表
        num: int, 样本数量

    返回:
        float: 信息熵值

    计算公式:
        E = -k * Σ(Pi * ln(Pi))
        其中 k = 1/ln(n)
    """
    k = 1 / math.log(num)
    #print("k=",k)
    E = 0
    for index, value in enumerate(X):
        if value == 0:
            continue
        else:
            LN=value * math.log(value)
            #print("LN=",LN)
            E = E + LN
            #print("E_sum=",E)
    Ek = E*(-k)
    #print("Ek=",Ek)
    return Ek

def process_data_to_weight(ms):
    """
    处理数据列，计算其权重

    参数:
        ms: pandas Series, 数据列

    返回:
        float: 该列的权重

    计算步骤:
        1. 获取非空值
        2. 计算最大值和最小值
        3. 标准化：T = (max - value) / (max - min)
        4. 计算概率：P = T / Σ(T)
        5. 计算信息熵：E
        6. 计算权重：D = 1 - E
    """
    # 获取特性数量
    m = ms.count()
    #m = len(ms)
    #print("m=",m)
    # 将数据转为数组
    measure = ms.astype(float).values


    # 遍历每个值
    T = [None] * m
    P = [None] * m
    non_nan_values = [x for x in measure if pd.notna(x)]
    mmax=max(non_nan_values)
    mmin=min(non_nan_values)


    for index, value in enumerate(non_nan_values):
        T[index]=(mmax-value)/(mmax-mmin)
    for index, value in enumerate(T):
        #print("sum(T)=",sum(T))
        P[index] = T[index]/sum(T)
        #print("p=",P[index])
    shang_e = calculate_e(P,m)
    d = 1-shang_e
    print("D=",d)
    return d


def calculate_entropy_weight(data):
    """
    使用极差标准化方法计算信息熵权重

    参数:
        data: list of lists, 二维数据数组，其中每一行是一个样本，每一列是一个指标

    返回:
        dict: 包含信息熵和权重的字典

    计算步骤:
        1. 数据标准化：使用极差标准化，r_ij = (max - x_ij) / (max - min)
        2. 概率计算：P = T / Σ(T)
        3. 信息熵计算：E = -k * Σ(Pi * ln(Pi))
        4. 权重计算：D = 1 - E，然后归一化
        
    特殊情况处理:
        - 当一列数据全为 0 时，该列的信息熵和权重都为 0
    """
    m = len(data)  # 样本数量
    n = len(data[0])  # 指标数量
    
    # 数据标准化：使用极差标准化（成本型指标）
    normalized_data = []
    for j in range(n):
        # 找出该列的最大值和最小值
        col_values = [data[i][j] for i in range(m)]
        max_val = max(col_values)
        min_val = min(col_values)
        range_val = max_val - min_val
        
        column = []
        for i in range(m):
            if range_val == 0:
                # 如果极差为 0，说明所有值都相同，标准化为 1
                column.append(1)
            else:
                # 极差标准化：r_ij = (max - x_ij) / (max - min)
                column.append((max_val - data[i][j]) / range_val)
        normalized_data.append(column)
    
    # 计算比重 p_ij
    probability_data = []
    for j in range(n):
        column_sum = sum(normalized_data[j])
        column = []
        for i in range(m):
            if column_sum > 0:
                column.append(normalized_data[j][i] / column_sum)
            else:
                column.append(0)
        probability_data.append(column)
    
    # 计算信息熵
    entropy = []
    k = 1 / math.log(m)
    for j in range(n):
        # 检查该列是否全为 0
        col_values = [data[i][j] for i in range(m)]
        if all(v == 0 for v in col_values):
            # 如果一列数据全为 0，信息熵设为 0
            entropy.append(0.0)
        else:
            e = 0
            for i in range(m):
                if probability_data[j][i] > 0:
                    e -= probability_data[j][i] * math.log(probability_data[j][i])
            entropy.append(k * e)
    
    # 计算权重
    d = [1 - e for e in entropy]
    
    # 如果一列数据全为 0，则该列的差异系数也为 0（权重为 0）
    for j in range(n):
        col_values = [data[i][j] for i in range(m)]
        if all(v == 0 for v in col_values):
            d[j] = 0.0
    
    d_sum = sum(d)
    
    # 归一化权重
    if d_sum == 0:
        # 如果所有列的差异系数都为 0，则所有权重都为 0
        weights = [0.0] * n
    else:
        weights = [di / d_sum for di in d]
    
    return {
        'entropy': entropy,
        'weights': weights
    }



def process_report(input_path, output_path):
    """
    处理Excel文件，计算各列的信息熵权重

    参数:
        input_path: str, 输入Excel文件路径
        output_path: str, 输出Excel文件路径

    返回:
        dict: 包含所有sheet权重的字典

    处理流程:
        1. 读取Excel文件的所有sheet
        2. 对每个sheet的每一列计算信息熵权重
        3. 对每列的权重进行归一化
        4. 保存结果到输出文件
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    print(f"读取文件: {input_path}")

    # 1. 读取所有sheet，设置header=None确保第一行作为数据读取
    excel_data = pd.read_excel(input_path, sheet_name=None, header=None)

    # 2. 存储所有权重
    processed_weight = {}

    print("\n开始生成权重...")
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:

        # 3. 遍历每个sheet
        for sheet_name, df in excel_data.items():
            print(f"处理sheet: {sheet_name}")

            # 检查是否为空sheet
            if df.empty:
                print(f"  -> sheet为空，跳过")
                pd.DataFrame().to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                processed_weight[sheet_name] = pd.DataFrame()
                continue

            sum_D = 0
            D_list = [None] * df.shape[1]
            W_list = [None] * df.shape[1]
            # 对每一列进行计算
            for col_idx in range(df.shape[1]):
                # 获取该列数据
                column_data = df[col_idx]

                # 只转换数值型数据
                if pd.api.types.is_numeric_dtype(column_data):
                    # 进行转换
                    D = process_data_to_weight(column_data)
                    sum_D = sum_D + D
                    D_list[col_idx] = D
                    print(f"  -> 第{col_idx + 1}列计算完成")
                else:
                    print(f"  -> 第{col_idx + 1}列不是数值型数据，跳过计算")

            for i in range(len(W_list)):
                W_list[i] = D_list[i] / sum_D
                #print("listW=",W_list[i])
            row_sums_df = pd.DataFrame(W_list)
            row_sums_df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)



        #写入excel
        for sheet_name, df in processed_weight.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)

    print(f"\n处理完成！权重已保存到: {output_path}")
    return processed_weight



def main():
    """
    主函数：根据Excel文件生成信息熵结果
    """
    # 设置文件路径
    input_file = '加工中心性能.xlsx'  # 上一步生成的行和文件
    output_file = '信息熵_加工中心性能.xlsx'  # 信息熵输出文件名


    process_report(input_file, output_file)




if __name__ == "__main__":
    main()
