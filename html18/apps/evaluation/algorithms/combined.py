"""
层次化权重计算算法

本模块实现了多层次体系中所有末端特性的全局权重计算，支持混合层级（既有末端特性，又有可细分的特性）。

主要功能：
- HierarchicalWeightCalculator: 层次化权重计算器类
  - load_weights: 加载权重Excel文件
  - build_hierarchy_tree: 构建层次结构树
  - find_all_end_features: 找出所有末端特性
  - calculate_all_global_weights: 计算所有末端特性的全局权重
  - create_summary_sheet: 创建汇总sheet

算法原理：
1. 层次结构构建：根据sheet名称构建层次结构树
2. 末端特性识别：没有子sheet的特性为末端特性
3. 全局权重计算：全局权重 = 路径上所有父级权重的乘积 × 当前特性的本地权重
4. 权重验证：所有末端特性的全局权重和应该等于1

应用场景：
- 多层次指标体系的权重计算
- 复杂层次结构的权重分析
- 末端特性的全局权重计算
"""

import pandas as pd
import numpy as np
import os


class HierarchicalWeightCalculator:
    """
    层次化权重计算器

    用于计算多层次体系中所有末端特性的全局权重
    支持混合层级（既有末端特性，又有可细分的特性）
    """

    def __init__(self, weight_file):
        """
        初始化权重计算器

        参数:
            weight_file: str, 权重Excel文件路径
        """
        self.weight_file = weight_file
        self.weights = {}  # 存储各sheet的归一化权重
        self.all_sheets = []  # 所有sheet名称
        self.hierarchy_tree = {}  # 层次结构树
        self.end_features_info = []  # 存储所有末端特性的详细信息

    def load_weights(self):
        """加载权重Excel文件"""
        excel_data = pd.read_excel(self.weight_file, sheet_name=None, header=None)
        self.all_sheets = list(excel_data.keys())

        for sheet_name, df in excel_data.items():
            if not df.empty and df.shape[1] >= 3:
                # 提取第三列（归一化权重）
                self.weights[sheet_name] = df.iloc[:, 2].values
            else:
                self.weights[sheet_name] = np.array([])

        print(f"加载完成，共{len(self.all_sheets)}个sheet")
        return self

    def build_hierarchy_tree(self):
        """构建层次结构树"""
        self.hierarchy_tree = {}

        for sheet_name in self.all_sheets:
            if sheet_name == "0":
                self.hierarchy_tree["0"] = {
                    "children": [],
                    "level": 0,
                    "parent": None
                }
                continue

            # 解析sheet名称获取层级信息
            parts = sheet_name.split('.')
            level = len(parts)
            parent_name = '.'.join(parts[:-1]) if len(parts) > 1 else "0"

            # 记录当前节点
            if sheet_name not in self.hierarchy_tree:
                self.hierarchy_tree[sheet_name] = {
                    "children": [],
                    "level": level,
                    "parent": parent_name
                }

            # 更新父节点的子节点列表
            if parent_name in self.hierarchy_tree:
                if sheet_name not in self.hierarchy_tree[parent_name]["children"]:
                    self.hierarchy_tree[parent_name]["children"].append(sheet_name)
            else:
                self.hierarchy_tree[parent_name] = {
                    "children": [sheet_name],
                    "level": level - 1,
                    "parent": None if parent_name == "0" else '.'.join(parent_name.split('.')[:-1])
                }

        print("层次结构构建完成")
        return self

    def get_children_sheets(self, sheet_name, row_index):
        """
        获取某个特性对应的子sheet

        参数:
            sheet_name: str, 当前sheet名称
            row_index: int, 特性在当前sheet中的行索引（0-based）

        返回:
            list: 子sheet名称列表
        """
        # 行索引转换为特性序号（从1开始）
        feature_num = row_index + 1

        # 构建可能的子sheet名称模式
        child_pattern = f"{sheet_name}.{feature_num}"

        # 查找所有以该模式开头的sheet
        children = []
        for sheet in self.all_sheets:
            if sheet.startswith(child_pattern):
                # 检查是否是直接子节点
                remaining = sheet[len(child_pattern):]
                if not remaining or remaining.startswith('.'):
                    children.append(sheet)

        return children

    def is_end_feature(self, sheet_name, row_index):
        """
        判断某个特性是否为末端特性

        末端特性定义：没有子sheet的特性
        """
        children = self.get_children_sheets(sheet_name, row_index)
        return len(children) == 0

    def calculate_global_weight_for_feature(self, sheet_name, row_index):
        """
        计算单个特性的全局权重

        全局权重 = 路径上所有父级权重的乘积 × 当前特性的本地权重
        """
        if sheet_name not in self.weights:
            return 0.0

        # 获取当前特性的本地权重
        local_weights = self.weights[sheet_name]
        if len(local_weights) <= row_index:
            return 0.0

        local_weight = local_weights[row_index]

        # 如果是根节点，直接返回本地权重
        if sheet_name == "0":
            return local_weight

        # 计算路径权重累积
        cumulative_weight = 1.0
        current_sheet = sheet_name

        # 沿父节点路径向上计算权重累积
        while current_sheet != "0":
            # 获取当前sheet的父节点
            if current_sheet in self.hierarchy_tree:
                parent_sheet = self.hierarchy_tree[current_sheet]["parent"]
            else:
                break

            if not parent_sheet or parent_sheet not in self.weights:
                break

            # 确定当前sheet在父节点中的索引
            # 例如：当前sheet是"2.1"，则它是父节点"2"中的第1个特性
            parent_parts = parent_sheet.split('.') if parent_sheet != "0" else []
            child_parts = current_sheet.split('.')

            # 获取当前sheet在父节点中的序号（从1开始）
            child_index_in_parent = int(child_parts[len(parent_parts)])

            # 转换为行索引（从0开始）
            row_in_parent = child_index_in_parent - 1

            # 获取父节点权重
            parent_weights = self.weights[parent_sheet]
            if len(parent_weights) > row_in_parent:
                parent_weight = parent_weights[row_in_parent]
                cumulative_weight *= parent_weight

            current_sheet = parent_sheet

        # 全局权重 = 路径权重累积 × 本地权重
        return cumulative_weight * local_weight

    def find_all_end_features(self):
        """
        找出所有末端特性

        返回:
            dict: {sheet_name: [行索引列表]}
        """
        end_features = {}

        for sheet_name in self.all_sheets:
            if sheet_name not in self.weights:
                continue

            local_weights = self.weights[sheet_name]
            if len(local_weights) == 0:
                continue

            end_features[sheet_name] = []

            # 检查当前sheet中的每个特性
            for row_index in range(len(local_weights)):
                if self.is_end_feature(sheet_name, row_index):
                    end_features[sheet_name].append(row_index)

        # 统计末端特性数量
        total_end_features = sum(len(indices) for indices in end_features.values())
        print(f"共找到{total_end_features}个末端特性")

        return end_features

    def calculate_all_global_weights(self):
        """
        计算所有末端特性的全局权重

        返回:
            dict: {sheet_name: [全局权重列表]}
        """
        # 找出所有末端特性
        end_features = self.find_all_end_features()

        # 计算全局权重并记录详细信息
        global_weights = {}
        self.end_features_info = []  # 清空信息列表
        total_weight = 0.0

        for sheet_name, row_indices in end_features.items():
            if not row_indices:
                continue

            global_weights[sheet_name] = []
            for row_index in row_indices:
                global_weight = self.calculate_global_weight_for_feature(sheet_name, row_index)
                global_weights[sheet_name].append(global_weight)

                # 记录详细信息
                feature_num = row_index + 1  # 转换为从1开始
                feature_label = f"{sheet_name} 第{feature_num}行"
                self.end_features_info.append({
                    'label': feature_label,
                    'sheet': sheet_name,
                    'row_index': row_index,
                    'feature_num': feature_num,
                    'weight': global_weight
                })

                total_weight += global_weight

        print(f"全局权重计算完成，总和: {total_weight:.10f}")
        return global_weights, total_weight

    def save_global_weights(self, output_file, global_weights):
        """
        保存全局权重到Excel文件

        参数:
            output_file: str, 输出文件路径
            global_weights: dict, 全局权重数据
        """
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 为每个有末端特性的sheet创建一个新sheet
            for sheet_name, weights_list in global_weights.items():
                if weights_list:
                    # 转换为DataFrame（单列）
                    result_df = pd.DataFrame(weights_list)
                    # 写入Excel，不包含索引和列名
                    result_df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                else:
                    # 写入空DataFrame
                    pd.DataFrame().to_excel(writer, sheet_name=sheet_name, index=False, header=False)

        print(f"全局权重已保存到: {output_file}")

    def create_summary_sheet(self, output_file):
        """
        创建汇总sheet，将所有末端特性权重放在一个sheet中

        参数:
            output_file: str, 汇总Excel文件路径
        """
        if not self.end_features_info:
            print("错误：没有找到末端特性信息，请先运行calculate_all_global_weights")
            return

        # 创建汇总数据
        labels = []
        weights = []

        # 按权重降序排序
        sorted_info = sorted(self.end_features_info, key=lambda x: x['weight'], reverse=True)

        for info in sorted_info:
            labels.append(info['label'])
            weights.append(info['weight'])

        # 创建DataFrame
        summary_df = pd.DataFrame({
            '末端特性': labels,
            '权重': weights
        })

        # 保存到Excel
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='汇总', index=False)

        # 验证权重和
        total_weight = sum(weights)

        print(f"\n汇总文件已创建: {output_file}")
        print(f"汇总信息:")
        print(f"  末端特性总数: {len(self.end_features_info)}")
        print(f"  汇总权重和: {total_weight:.10f}")

        if abs(total_weight - 1.0) < 0.000001:
            print(f"  ✓ 权重和验证通过: ≈ 1.000000")
        else:
            print(f"  ⚠ 警告: 权重和 ≠ 1.000000")
            print(f"     偏差: {abs(total_weight - 1.0):.10f}")

        return summary_df


def main():
    """
    主函数：计算所有末端特性的体系权重
    """
    # 设置文件路径
    weight_file = '统计表_权重计算结果_镗铣床加入信息熵.xlsx'
    output_file = '统计表_镗铣床体系权重.xlsx'
    summary_file = '统计表_镗铣床体系权重_汇总.xlsx'

    try:
        # 创建权重计算器
        calculator = HierarchicalWeightCalculator(weight_file)

        # 加载权重数据
        calculator.load_weights()

        # 构建层次结构
        calculator.build_hierarchy_tree()

        # 计算所有末端特性的全局权重
        global_weights, total_weight = calculator.calculate_all_global_weights()

        # 保存原始格式的结果（每个sheet单独保存）
        calculator.save_global_weights(output_file, global_weights)

        # 创建汇总文件（所有末端特性在一个sheet中）
        calculator.create_summary_sheet(summary_file)

        # 验证和显示结果
        print(f"\n{'=' * 60}")
        print(f"计算结果验证:")
        print(f"{'=' * 60}")
        print(f"所有末端特性的全局权重和: {total_weight:.10f}")

        if abs(total_weight - 1.0) < 0.000001:
            print(f"✓ 验证通过: 全局权重和 ≈ 1.000000")
        else:
            print(f"⚠ 警告: 全局权重和 ≠ 1.000000")
            print(f"   偏差: {abs(total_weight - 1.0):.10f}")

        # 显示主要信息
        print(f"\n{'=' * 60}")
        print(f"输出信息:")
        print(f"{'=' * 60}")
        print(f"输入文件: {weight_file}")
        print(f"输出文件1 (原始格式): {output_file}")
        print(f"输出文件2 (汇总格式): {summary_file}")

        # 统计输出情况
        output_data = pd.read_excel(output_file, sheet_name=None, header=None)
        non_empty_sheets = sum(1 for df in output_data.values() if not df.empty)
        total_features = sum(len(df) for df in output_data.values() if not df.empty)

        print(f"\n文件1统计:")
        print(f"  包含 {len(output_data)} 个sheet")
        print(f"  其中有 {non_empty_sheets} 个sheet包含数据")
        print(f"  总末端特性数: {total_features}")

        # 读取汇总文件并显示前几行
        print(f"\n文件2统计 (汇总):")
        summary_data = pd.read_excel(summary_file, sheet_name='汇总')
        print(f"  末端特性总数: {len(summary_data)}")
        print(f"  前5个最重要的末端特性:")
        for i in range(min(5, len(summary_data))):
            label = summary_data.iloc[i, 0]
            weight = summary_data.iloc[i, 1]
            print(f"    第{i + 1}名: {label} (权重: {weight:.6f})")

        # 显示权重分布信息
        print(f"\n权重分布信息:")
        weights = summary_data['权重'].values
        print(f"  最大权重: {np.max(weights):.6f}")
        print(f"  最小权重: {np.min(weights):.6f}")
        print(f"  平均权重: {np.mean(weights):.6f}")
        print(f"  权重标准差: {np.std(weights):.6f}")

        # 权重分段统计
        print(f"\n权重分段统计:")
        bins = [0, 0.01, 0.05, 0.1, 0.2, 0.3, 1.0]
        for i in range(len(bins) - 1):
            lower = bins[i]
            upper = bins[i + 1]
            count = np.sum((weights >= lower) & (weights < upper))
            if i == len(bins) - 2 and upper == 1.0:
                count = np.sum(weights >= lower)  # 包含上限
            percentage = count / len(weights) * 100
            print(f"  权重在 [{lower:.2f}, {upper:.2f}) 之间: {count}个 ({percentage:.1f}%)")

    except FileNotFoundError as e:
        print(f"错误: {e}")
        print(f"请确保文件 '{weight_file}' 在当前目录中")
    except Exception as e:
        print(f"处理过程中发生错误: {e}")


if __name__ == "__main__":
    main()
