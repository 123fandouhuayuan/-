import logging

logger = logging.getLogger(__name__)


def fill_modules_data_from_database(wb, machine_id, machine_type):
    """
    从数据库读取机床参数并填充到Excel工作簿
    
    功能说明：
        根据机床ID和类型，从数据库中读取机床参数数据，并填充到Excel工作簿的各个Sheet中。
        支持加工中心和镗铣床两种机床类型，每种类型有不同的参数字段映射。
    
    参数：
        wb: openpyxl.Workbook对象，要填充的Excel工作簿
        machine_id: 机床ID，用于查询数据库
        machine_type: 机床类型，'boring_milling_machine'表示镗铣床，其他表示加工中心
    
    处理模块：
        1. 精度模块
           - 1.1 几何精度：进给轴直线度、角度偏差、垂直度、主轴精度、工作台精度
           - 1.2 位置精度：线性轴和回转轴的重复定位精度、定位精度、平均偏差、系统偏差、反向间隙
           - 1.3 加工精度：圆柱度、垂直度、直线度、平行度、倾斜度、位置度、同轴度
        
        2. 性能模块
           - 2.1 加工性能：Cp值、速度参数、定位精度、进给速度
           - 2.2 机床刚度：径向刚度、轴向刚度、静刚度
           - 2.3 运行性能：振动速度、噪声值、功率参数、电流不平衡度、电压频率波动、热位移
           - 2.4 负荷能力：最大功率、最大扭矩、负载重量、切削参数、长径比
        
        3. 可靠性模块
           - 3.1 平均故障间隔时间：总运行时间、故障次数
           - 3.2 平均修复时间：修复时间列表（动态行数）
           - 3.3 当量故障率：致命故障、严重故障、一般故障次数、运行时间
           - 3.4 加工一致性：标准差σ、均值μ
           - 3.5 加工精度保持性：初始精度、失效精度、当前精度
           - 3.6 平均首次故障时间：故障时间列表（动态行数）
        
        4. 绿色化模块
           - 5.1 资源循环与耗材：切削液消耗量、润滑油消耗量、轻量化设计项目
           - 5.2 能源-能效：待机功率、空运转功率、切削功率、材料去除率、切削体积
    
    数据格式：
        - 数值型参数：直接读取并填充到对应单元格
        - 列表型参数（如修复时间列表、故障时间列表）：动态调整行数，填充多行数据
        - JSON型参数（如轻量化设计项目）：解析JSON数据，根据内容填充对应单元格
    
    异常处理：
        - 如果未找到机床参数，记录警告日志并返回
        - 如果填充过程中发生错误，记录错误日志并抛出异常
    """
    try:
        # 导入数据库模型
        from ..data_management.models_dameng import MachineParameters, BoringMillingParameters
        
        logger.info(f"开始从数据库读取机床{machine_id}的各模块数据")
        
        # 根据机床类型读取参数
        if machine_type == 'boring_milling_machine':
            params = BoringMillingParameters.objects.filter(machine_id=machine_id).first()
            logger.info(f"查询镗铣床参数: machine_id={machine_id}, 找到: {params is not None}")
        else:
            params = MachineParameters.objects.filter(machine_id=machine_id).first()
            logger.info(f"查询加工中心参数: machine_id={machine_id}, 找到: {params is not None}")
        
        if not params:
            logger.warning(f"未找到机床{machine_id}的参数数据")
            return
        
        logger.info(f"成功读取机床{machine_id}的参数数据，类型: {type(params).__name__}")
        
        # 打印一些字段值用于调试
        if hasattr(params, 'x_axis_linearity_xy'):
            logger.info(f"x_axis_linearity_xy = {params.x_axis_linearity_xy}")
        if hasattr(params, 'z_axis_linearity_yz'):
            logger.info(f"z_axis_linearity_yz = {params.z_axis_linearity_yz}")
        
        # 1. 精度模块
        # 1.1 几何精度
        if '1.1 几何精度' in wb.sheetnames:
            ws = wb['1.1 几何精度']
            logger.info(f"开始处理几何精度数据，Sheet: {ws.title}")
            
            # 建立字段映射（描述 -> 数据库字段名）
            if machine_type == 'boring_milling_machine':
                field_mapping = {
                    '立柱直线度（Y-Z垂直平面内）': 'bm_column_linearity_yz',
                    '立柱直线度（Z-X水平平面内）': 'bm_column_linearity_zx',
                    'X轴直线度（X-Y垂直平面内）': 'bm_worktable_x_linearity_xy',
                    'X轴直线度（Z-X水平平面内）': 'bm_worktable_x_linearity_zx',
                    'Y轴直线度（Y-Z平面内）': 'bm_spindle_box_y_linearity_yz',
                    'Y轴直线度（X-Y平面内）': 'bm_spindle_box_y_linearity_xy',
                    '立柱角度偏差（YZ俯仰）': 'bm_column_angle_yz',
                    '立柱角度偏差（XY倾斜）': 'bm_column_angle_xy',
                    '立柱角度偏差（ZX偏摆）': 'bm_column_angle_zx',
                    'X轴角度偏差（YZ俯仰）': 'bm_worktable_x_angle_yz',
                    'X轴角度偏差（XY俯仰）': 'bm_worktable_x_angle_xy',
                    'Y轴角度偏差（YZ俯仰）': 'bm_spindle_box_y_angle_yz',
                    'Y轴角度偏差（ZX偏摆）': 'bm_spindle_box_y_angle_zx',
                    'X轴与立柱垂直度': 'bm_worktable_x_column_perpendicularity',
                    'Y轴与立柱垂直度': 'bm_spindle_box_y_column_perpendicularity',
                    '主轴轴向窜动': 'bm_spindle_axial_runout',
                    '主轴锥孔径向跳动（靠近端部）': 'bm_spindle_radial_runout_near',
                    '主轴锥孔径向跳动（距端部300mm）': 'bm_spindle_radial_runout_300mm',
                    '主轴轴线与Y轴平行度（YZ平面）': 'bm_spindle_parallelism_yz',
                    '主轴轴线与Y轴平行度（XY平面）': 'bm_spindle_parallelism_xy',
                    '主轴轴线与X轴垂直度': 'bm_spindle_perpendicularity_x',
                    '主轴轴线与立柱垂直度': 'bm_spindle_perpendicularity_column',
                    '工作台面平面度': 'bm_worktable_flatness',
                    '工作台面与X轴平行度': 'bm_worktable_parallelism_x',
                }
            else:
                field_mapping = {
                    'X轴直线度（X-Y垂直平面内）': 'x_axis_linearity_xy',
                    'X轴直线度（Z-X水平平面内）': 'x_axis_linearity_zx',
                    'Z轴直线度（Y-Z垂直平面内）': 'z_axis_linearity_yz',
                    'Z轴直线度（Z-X水平平面内）': 'z_axis_linearity_zx',
                    'Y轴直线度（X-Y垂直平面内）': 'y_axis_linearity_xy',
                    'Y轴直线度（Y-Z垂直平面内）': 'y_axis_linearity_yz',
                    'X轴角度偏差（俯仰）': 'x_axis_angle_pitch',
                    'X轴角度偏差（偏摆）': 'x_axis_angle_yaw',
                    'X轴角度偏差（倾斜）': 'x_axis_angle_roll',
                    'Z轴角度偏差（俯仰）': 'z_axis_angle_pitch',
                    'Z轴角度偏差（偏摆）': 'z_axis_angle_yaw',
                    'Z轴角度偏差（倾斜）': 'z_axis_angle_roll',
                    'Y轴角度偏差（Y-Z垂直平面内）': 'y_axis_angle_yz',
                    'Y轴角度偏差（X-Y垂直平面内）': 'y_axis_angle_xy',
                    'Y轴角度偏差（ZX水平面内）': 'y_axis_angle_zx',
                    'Y轴与X轴垂直度': 'y_axis_perpendicularity_x',
                    'Y轴与Z轴垂直度': 'y_axis_perpendicularity_z',
                    'Z轴与X轴垂直度': 'z_axis_perpendicularity_x',
                    '主轴轴向窜动': 'spindle_axial_runout',
                    '主轴锥孔径向跳动（靠近端部）': 'spindle_radial_runout_near',
                    '主轴锥孔径向跳动（距端部300mm）': 'spindle_radial_runout_300mm',
                    '主轴轴线与Z轴平行度（Y-Z平面）': 'spindle_parallelism_yz',
                    '主轴轴线与Z轴平行度（Z-X平面）': 'spindle_parallelism_zx',
                    '主轴轴线与X轴垂直度': 'spindle_perpendicularity_x',
                    '主轴轴线与Y轴垂直度': 'spindle_perpendicularity_y',
                    '工作台面平面度': 'worktable_flatness',
                    '工作台面与X轴平行度': 'worktable_parallelism_x',
                    '工作台面与Z轴平行度': 'worktable_parallelism_z'
                }
            
            logger.info(f"几何精度字段映射数量: {len(field_mapping)}")
            
            # 遍历Excel行，找到描述并填充数据
            count = 0
            for row_idx, row in enumerate(ws.iter_rows(min_row=2), start=2):
                if not row or len(row) < 5:
                    continue
                description_cell = row[2]  # C列是描述
                if not description_cell.value:
                    continue
                description = str(description_cell.value).strip()
                
                if description in field_mapping:
                    field_name = field_mapping[description]
                    value = getattr(params, field_name, None)
                    if value is not None:
                        row[4].value = value  # E列是机床1实测值
                        count += 1
                        logger.debug(f"几何精度 [行{row_idx}]: {description} = {value} (字段: {field_name})")
                    else:
                        logger.debug(f"几何精度 [行{row_idx}]: {description} 字段值为None (字段: {field_name})")
                else:
                    logger.debug(f"几何精度 [行{row_idx}]: 描述'{description}'未在映射中找到")
            
            logger.info(f"已填充几何精度数据: {count}条记录")
        
        # 1.2 位置精度
        if '1.2 位置精度' in wb.sheetnames:
            ws = wb['1.2 位置精度']
            logger.info(f"开始处理位置精度数据，Sheet: {ws.title}")
            
            # 线性轴字段映射（X、Y、Z轴）
            # 只处理双向参数（D1、D3、D5、D6、D8）
            linear_axis_fields = {
                '双向重复定位精度R': ('linear_axis_repeatability_x', 'linear_axis_repeatability_y', 'linear_axis_repeatability_z'),
                '双向定位精度A': ('linear_axis_positioning_accuracy_x', 'linear_axis_positioning_accuracy_y', 'linear_axis_positioning_accuracy_z'),
                '轴线的平均双向位置偏差范围M': ('linear_axis_mean_deviation_x', 'linear_axis_mean_deviation_y', 'linear_axis_mean_deviation_z'),
                '双向定位系统偏差E': ('linear_axis_system_deviation_x', 'linear_axis_system_deviation_y', 'linear_axis_system_deviation_z'),
                '轴线的反向差值B': ('linear_axis_backlash_x', 'linear_axis_backlash_y', 'linear_axis_backlash_z'),
            }
            
            # 回转轴字段映射（A、B、C轴）
            # 只处理双向参数（D1、D3、D5、D6、D8）
            rotary_axis_fields = {
                '双向重复定位精度R': ('rotary_axis_repeatability_a', 'rotary_axis_repeatability_b', 'rotary_axis_repeatability_c'),
                '双向定位精度A': ('rotary_axis_positioning_accuracy_a', 'rotary_axis_positioning_accuracy_b', 'rotary_axis_positioning_accuracy_c'),
                '轴线的平均双向位置偏差范围M': ('rotary_axis_mean_deviation_a', 'rotary_axis_mean_deviation_b', 'rotary_axis_mean_deviation_c'),
                '双向定位系统偏差E': ('rotary_axis_system_deviation_a', 'rotary_axis_system_deviation_b', 'rotary_axis_system_deviation_c'),
                '轴线的反向差值B': ('rotary_axis_backlash_a', 'rotary_axis_backlash_b', 'rotary_axis_backlash_c'),
            }
            
            logger.info(f"线性轴字段映射数量: {len(linear_axis_fields)}")
            logger.info(f"回转轴字段映射数量: {len(rotary_axis_fields)}")
            
            count = 0
            
            # 处理线性轴数据（第3-14行）
            logger.info("开始处理线性轴数据（第3-14行）")
            for row_idx in range(3, 15):  # 第3-14行
                description = ws.cell(row=row_idx, column=3).value  # C列是描述
                if not description:
                    logger.debug(f"线性轴 [行{row_idx}]: 描述为空，跳过")
                    continue
                description = str(description).strip()
                
                if description in linear_axis_fields:
                    field_x, field_y, field_z = linear_axis_fields[description]
                    value_x = getattr(params, field_x, None)
                    value_y = getattr(params, field_y, None)
                    value_z = getattr(params, field_z, None)
                    
                    logger.debug(f"线性轴 [行{row_idx}]: 描述'{description}', X={value_x}, Y={value_y}, Z={value_z}")
                    
                    if value_x is not None:
                        ws.cell(row=row_idx, column=4, value=value_x)  # D列是X轴
                        count += 1
                        logger.debug(f"线性轴 [行{row_idx}]: X轴 {description} = {value_x}")
                    if value_y is not None:
                        ws.cell(row=row_idx, column=5, value=value_y)  # E列是Y轴
                        count += 1
                        logger.debug(f"线性轴 [行{row_idx}]: Y轴 {description} = {value_y}")
                    if value_z is not None:
                        ws.cell(row=row_idx, column=6, value=value_z)  # F列是Z轴
                        count += 1
                        logger.debug(f"线性轴 [行{row_idx}]: Z轴 {description} = {value_z}")
                else:
                    logger.debug(f"线性轴 [行{row_idx}]: 描述'{description}'未在映射中找到（可能是单向参数）")
            
            # 处理回转轴数据（第18-29行）
            logger.info("开始处理回转轴数据（第18-29行）")
            for row_idx in range(18, 30):  # 第18-29行
                description = ws.cell(row=row_idx, column=3).value  # C列是描述
                if not description:
                    logger.debug(f"回转轴 [行{row_idx}]: 描述为空，跳过")
                    continue
                description = str(description).strip()
                
                if description in rotary_axis_fields:
                    field_a, field_b, field_c = rotary_axis_fields[description]
                    value_a = getattr(params, field_a, None)
                    value_b = getattr(params, field_b, None)
                    value_c = getattr(params, field_c, None)
                    
                    logger.debug(f"回转轴 [行{row_idx}]: 描述'{description}', A={value_a}, B={value_b}, C={value_c}")
                    
                    if value_a is not None:
                        ws.cell(row=row_idx, column=4, value=value_a)  # D列是A轴
                        count += 1
                        logger.debug(f"回转轴 [行{row_idx}]: A轴 {description} = {value_a}")
                    if value_b is not None:
                        ws.cell(row=row_idx, column=5, value=value_b)  # E列是B轴
                        count += 1
                        logger.debug(f"回转轴 [行{row_idx}]: B轴 {description} = {value_b}")
                    if value_c is not None:
                        ws.cell(row=row_idx, column=6, value=value_c)  # F列是C轴
                        count += 1
                        logger.debug(f"回转轴 [行{row_idx}]: C轴 {description} = {value_c}")
                else:
                    logger.debug(f"回转轴 [行{row_idx}]: 描述'{description}'未在映射中找到（可能是单向参数）")
            
            logger.info(f"已填充位置精度数据: {count}条记录")
        
        # 1.3 加工精度
        if '1.3 加工精度' in wb.sheetnames:
            ws = wb['1.3 加工精度']
            logger.info(f"开始处理加工精度数据，Sheet: {ws.title}")
            
            # 加工精度字段映射
            workpiece_fields = {
                '圆柱度': 'cylindricity',
                '孔中心轴线与基孔A的垂直度': 'hole_perpendicularity_a',
                '侧面的直线度': 'side_linearity',
                '相邻面与基面B的垂直度': 'adjacent_perpendicularity_b',
                '相对面与基面B的平行度': 'opposite_parallelism_b',
                '侧面对基准B的倾斜度': 'side_inclination_b',
                '圆度': 'circularity',
                '外圆和内圆孔C的同心度': 'concentricity_c',
                '斜面的直线度': 'slope_linearity',
                '3°角斜面对基准B的倾斜度': 'slope_inclination_b',
                '孔相对于内孔C的位置度': 'hole_position_c',
                '内孔与外孔D的同心度': 'concentricity_d',
            }
            
            count = 0
            for row_idx, row in enumerate(ws.iter_rows(min_row=2), start=2):
                if not row or len(row) < 4:
                    continue
                description_cell = row[2]
                if not description_cell.value:
                    continue
                description = str(description_cell.value).strip()
                
                if description in workpiece_fields:
                    field_name = workpiece_fields[description]
                    value = getattr(params, field_name, None)
                    if value is not None:
                        row[3].value = value  # D列是机床1实测值
                        count += 1
                        logger.debug(f"加工精度 [行{row_idx}]: {description} = {value}")
                    else:
                        logger.debug(f"加工精度 [行{row_idx}]: {description} 字段值为None")
                else:
                    logger.debug(f"加工精度 [行{row_idx}]: 描述'{description}'未在映射中找到")
            
            logger.info(f"已填充加工精度数据: {count}条记录")
        
        # 2. 性能模块
        # 2.1 加工性能
        if '2.1 加工性能' in wb.sheetnames:
            ws = wb['2.1 加工性能']
            logger.info(f"开始处理加工性能数据，Sheet: {ws.title}")
            
            count = 0
            # CP值
            if hasattr(params, 'cp_value') and params.cp_value is not None:
                ws['B2'] = params.cp_value
                count += 1
                logger.debug(f"加工性能: CP值 = {params.cp_value}")
            
            # 峰值转速
            if hasattr(params, 'peak_speed') and params.peak_speed is not None:
                ws['B4'] = params.peak_speed
                count += 1
                logger.debug(f"加工性能: 峰值转速 = {params.peak_speed}")
            
            # 谷值转速
            if hasattr(params, 'valley_speed') and params.valley_speed is not None:
                ws['B5'] = params.valley_speed
                count += 1
                logger.debug(f"加工性能: 谷值转速 = {params.valley_speed}")
            
            # 设计最大转速
            if hasattr(params, 'design_max_speed') and params.design_max_speed is not None:
                ws['B6'] = params.design_max_speed
                count += 1
                logger.debug(f"加工性能: 设计最大转速 = {params.design_max_speed}")
            
            # 最高快移速度
            if hasattr(params, 'max_fast_speed') and params.max_fast_speed is not None:
                ws['B8'] = params.max_fast_speed
                count += 1
                logger.debug(f"加工性能: 最高快移速度 = {params.max_fast_speed}")
            
            # 设计最高速度
            if hasattr(params, 'design_max_fast_speed') and params.design_max_fast_speed is not None:
                ws['B9'] = params.design_max_fast_speed
                count += 1
                logger.debug(f"加工性能: 设计最高速度 = {params.design_max_fast_speed}")
            
            # 最高速度下重复定位精度
            if hasattr(params, 'repeat_positioning_accuracy') and params.repeat_positioning_accuracy is not None:
                ws['B10'] = params.repeat_positioning_accuracy
                count += 1
                logger.debug(f"加工性能: 最高速度下重复定位精度 = {params.repeat_positioning_accuracy}")
            
            # 最大进给速度
            if hasattr(params, 'max_feed_speed') and params.max_feed_speed is not None:
                ws['B12'] = params.max_feed_speed
                count += 1
                logger.debug(f"加工性能: 最大进给速度 = {params.max_feed_speed}")
            
            # 目标最高速度
            if hasattr(params, 'target_max_speed') and params.target_max_speed is not None:
                ws['B13'] = params.target_max_speed
                count += 1
                logger.debug(f"加工性能: 目标最高速度 = {params.target_max_speed}")
            
            # 最大进给速度及加速度下的重复定位精度
            if hasattr(params, 'repeat_positioning_accuracy_feed') and params.repeat_positioning_accuracy_feed is not None:
                ws['B14'] = params.repeat_positioning_accuracy_feed
                count += 1
                logger.debug(f"加工性能: 最大进给速度及加速度下的重复定位精度 = {params.repeat_positioning_accuracy_feed}")
            
            logger.info(f"已填充加工性能数据: {count}条记录")
        
        # 2.2 机床刚度
        if '2.2 机床刚度' in wb.sheetnames:
            ws = wb['2.2 机床刚度']
            logger.info(f"开始处理机床刚度数据，Sheet: {ws.title}")
            
            count = 0
            # 主轴径向刚度
            if hasattr(params, 'radial_stiffness') and params.radial_stiffness is not None:
                ws['B2'] = params.radial_stiffness
                count += 1
                logger.debug(f"机床刚度: 主轴径向刚度 = {params.radial_stiffness}")
            
            # 主轴轴向刚度
            if hasattr(params, 'axial_stiffness') and params.axial_stiffness is not None:
                ws['B3'] = params.axial_stiffness
                count += 1
                logger.debug(f"机床刚度: 主轴轴向刚度 = {params.axial_stiffness}")
            
            # 机床类型（转换为中文）
            if hasattr(params, 'radial_machine_type') and params.radial_machine_type is not None:
                machine_type_map = {
                    'machining_center': '加工中心',
                    'boring_milling_machine': '镗铣床',
                    'tool-rotating': '刀具旋转',
                    'workpiece-rotating': '工件旋转',
                    '加工中心': '加工中心',
                    '镗铣床': '镗铣床',
                    '刀具旋转': '刀具旋转',
                    '工件旋转': '工件旋转',
                }
                machine_type_cn = machine_type_map.get(params.radial_machine_type, params.radial_machine_type)
                ws['B4'] = machine_type_cn
                count += 1
                logger.debug(f"机床刚度: 机床类型 = {machine_type_cn}")
            
            # 切削刚度
            if hasattr(params, 'cutting_stiffness') and params.cutting_stiffness is not None:
                ws['B6'] = params.cutting_stiffness
                count += 1
                logger.debug(f"机床刚度: 切削刚度 = {params.cutting_stiffness}")
            
            # 静刚度合格线
            if hasattr(params, 'static_stiffness_accept') and params.static_stiffness_accept is not None:
                ws['B7'] = params.static_stiffness_accept
                count += 1
                logger.debug(f"机床刚度: 静刚度合格线 = {params.static_stiffness_accept}")
            
            # 静刚度
            if hasattr(params, 'static_stiffness_value') and params.static_stiffness_value is not None:
                ws['B8'] = params.static_stiffness_value
                count += 1
                logger.debug(f"机床刚度: 静刚度 = {params.static_stiffness_value}")
            
            logger.info(f"已填充机床刚度数据: {count}条记录")
        
        # 2.3 运行性能
        if '2.3 运行性能' in wb.sheetnames:
            ws = wb['2.3 运行性能']
            logger.info(f"开始处理运行性能数据，Sheet: {ws.title}")
            
            count = 0
            # 最大振动速度
            if hasattr(params, 'max_vibration_speed') and params.max_vibration_speed is not None:
                ws['B2'] = params.max_vibration_speed
                count += 1
                logger.debug(f"运行性能: 最大振动速度 = {params.max_vibration_speed}")
            
            # 机床类型
            if hasattr(params, 'noise_machine_type') and params.noise_machine_type is not None:
                ws['B4'] = params.noise_machine_type
                count += 1
                logger.debug(f"运行性能: 机床类型 = {params.noise_machine_type}")
            
            # 重量选择
            if hasattr(params, 'noise_weight') and params.noise_weight is not None:
                ws['B5'] = params.noise_weight
                count += 1
                logger.debug(f"运行性能: 重量选择 = {params.noise_weight}")
            
            # 噪声值
            if hasattr(params, 'noise_value') and params.noise_value is not None:
                ws['B6'] = params.noise_value
                count += 1
                logger.debug(f"运行性能: 噪声值 = {params.noise_value}")
            
            # 初检功率
            if hasattr(params, 'initial_power') and params.initial_power is not None:
                ws['B8'] = params.initial_power
                count += 1
                logger.debug(f"运行性能: 初检功率 = {params.initial_power}")
            
            # 终检功率
            if hasattr(params, 'final_power') and params.final_power is not None:
                ws['B9'] = params.final_power
                count += 1
                logger.debug(f"运行性能: 终检功率 = {params.final_power}")
            
            # 电流不平衡量
            if hasattr(params, 'current_unbalance') and params.current_unbalance is not None:
                ws['B11'] = params.current_unbalance
                count += 1
                logger.debug(f"运行性能: 电流不平衡量 = {params.current_unbalance}")
            
            # 电流波动度
            if hasattr(params, 'current_fluctuation') and params.current_fluctuation is not None:
                ws['B12'] = params.current_fluctuation
                count += 1
                logger.debug(f"运行性能: 电流波动度 = {params.current_fluctuation}")
            
            # 电压波动范围
            if hasattr(params, 'voltage_fluctuation_min') and hasattr(params, 'voltage_fluctuation_max'):
                if params.voltage_fluctuation_min is not None and params.voltage_fluctuation_max is not None:
                    ws['B14'] = f"{params.voltage_fluctuation_min}~{params.voltage_fluctuation_max}"
                    count += 1
                    logger.debug(f"运行性能: 电压波动范围 = {params.voltage_fluctuation_min}~{params.voltage_fluctuation_max}")
            
            # 频率波动范围
            if hasattr(params, 'frequency_fluctuation_min') and hasattr(params, 'frequency_fluctuation_max'):
                if params.frequency_fluctuation_min is not None and params.frequency_fluctuation_max is not None:
                    ws['B15'] = f"{params.frequency_fluctuation_min}~{params.frequency_fluctuation_max}"
                    count += 1
                    logger.debug(f"运行性能: 频率波动范围 = {params.frequency_fluctuation_min}~{params.frequency_fluctuation_max}")
            
            # 径向热位移范围
            if hasattr(params, 'radial_thermal_displacement') and params.radial_thermal_displacement is not None:
                ws['B17'] = params.radial_thermal_displacement
                count += 1
                logger.debug(f"运行性能: 径向热位移范围 = {params.radial_thermal_displacement}")
            
            # 热平衡梯度 G1
            if hasattr(params, 'radial_thermal_gradient') and params.radial_thermal_gradient is not None:
                ws['B18'] = params.radial_thermal_gradient
                count += 1
                logger.debug(f"运行性能: 热平衡梯度 G1 = {params.radial_thermal_gradient}")
            
            # 轴向热位移范围
            if hasattr(params, 'axial_thermal_displacement') and params.axial_thermal_displacement is not None:
                ws['B20'] = params.axial_thermal_displacement
                count += 1
                logger.debug(f"运行性能: 轴向热位移范围 = {params.axial_thermal_displacement}")
            
            # 热平衡梯度 G2
            if hasattr(params, 'axial_thermal_gradient') and params.axial_thermal_gradient is not None:
                ws['B21'] = params.axial_thermal_gradient
                count += 1
                logger.debug(f"运行性能: 热平衡梯度 G2 = {params.axial_thermal_gradient}")
            
            logger.info(f"已填充运行性能数据: {count}条记录")
        
        # 2.4 负荷能力
        if '2.4 负荷能力' in wb.sheetnames:
            ws = wb['2.4 负荷能力']
            logger.info(f"开始处理负荷能力数据，Sheet: {ws.title}")
            
            count = 0
            # 实测主轴最大功率
            if hasattr(params, 'measured_max_power') and params.measured_max_power is not None:
                ws['B2'] = params.measured_max_power
                count += 1
                logger.debug(f"负荷能力: 实测主轴最大功率 = {params.measured_max_power}")
            
            # 设计主轴最大功率
            if hasattr(params, 'design_max_power') and params.design_max_power is not None:
                ws['B3'] = params.design_max_power
                count += 1
                logger.debug(f"负荷能力: 设计主轴最大功率 = {params.design_max_power}")
            
            # 切削振动速度1
            if hasattr(params, 'cutting_vibration_speed1') and params.cutting_vibration_speed1 is not None:
                ws['B4'] = params.cutting_vibration_speed1
                count += 1
                logger.debug(f"负荷能力: 切削振动速度1 = {params.cutting_vibration_speed1}")
            
            # 实测主轴最大扭矩
            if hasattr(params, 'measured_max_torque') and params.measured_max_torque is not None:
                ws['B6'] = params.measured_max_torque
                count += 1
                logger.debug(f"负荷能力: 实测主轴最大扭矩 = {params.measured_max_torque}")
            
            # 设计主轴最大扭矩
            if hasattr(params, 'design_max_torque') and params.design_max_torque is not None:
                ws['B7'] = params.design_max_torque
                count += 1
                logger.debug(f"负荷能力: 设计主轴最大扭矩 = {params.design_max_torque}")
            
            # 切削振动速度2
            if hasattr(params, 'cutting_vibration_speed2') and params.cutting_vibration_speed2 is not None:
                ws['B8'] = params.cutting_vibration_speed2
                count += 1
                logger.debug(f"负荷能力: 切削振动速度2 = {params.cutting_vibration_speed2}")
            
            # 试验实际负重
            if hasattr(params, 'actual_load_weight') and params.actual_load_weight is not None:
                ws['B10'] = params.actual_load_weight
                count += 1
                logger.debug(f"负荷能力: 试验实际负重 = {params.actual_load_weight}")
            
            # 最大设计重量
            if hasattr(params, 'max_design_weight') and params.max_design_weight is not None:
                ws['B11'] = params.max_design_weight
                count += 1
                logger.debug(f"负荷能力: 最大设计重量 = {params.max_design_weight}")
            
            # 试验运行速度
            if hasattr(params, 'actual_load_velocity') and params.actual_load_velocity is not None:
                ws['B12'] = params.actual_load_velocity
                count += 1
                logger.debug(f"负荷能力: 试验运行速度 = {params.actual_load_velocity}")
            
            # 最大设计速度
            if hasattr(params, 'max_design_velocity') and params.max_design_velocity is not None:
                ws['B13'] = params.max_design_velocity
                count += 1
                logger.debug(f"负荷能力: 最大设计速度 = {params.max_design_velocity}")
            
            # 切削振动速度3
            if hasattr(params, 'cutting_vibration_speed3') and params.cutting_vibration_speed3 is not None:
                ws['B14'] = params.cutting_vibration_speed3
                count += 1
                logger.debug(f"负荷能力: 切削振动速度3 = {params.cutting_vibration_speed3}")
            
            # 机床类型（转换为中文）
            if hasattr(params, 'load_machine_type') and params.load_machine_type is not None:
                machine_type_map = {
                    'machining_center': '加工中心',
                    'boring_milling_machine': '镗铣床',
                    '加工中心': '加工中心',
                    '镗铣床': '镗铣床',
                }
                machine_type_cn = machine_type_map.get(params.load_machine_type, params.load_machine_type)
                ws['B16'] = machine_type_cn
                count += 1
                logger.debug(f"负荷能力: 机床类型 = {machine_type_cn}")
            
            # 评价方案
            if hasattr(params, 'evaluation_scheme') and params.evaluation_scheme is not None:
                ws['B17'] = params.evaluation_scheme
                count += 1
                logger.debug(f"负荷能力: 评价方案 = {params.evaluation_scheme}")
            
            # 参数1：根据机床类型和评价方案动态映射
            param1_filled = False
            if hasattr(params, 'load_machine_type') and params.load_machine_type:
                machine_type = params.load_machine_type
                evaluation_scheme = getattr(params, 'evaluation_scheme', '') or ''
                
                # 铣床：最大切削宽度
                if '铣' in machine_type:
                    if hasattr(params, 'max_cutting_width') and params.max_cutting_width is not None:
                        ws['B18'] = params.max_cutting_width
                        count += 1
                        param1_filled = True
                        logger.debug(f"负荷能力: 参数1(最大切削宽度) = {params.max_cutting_width}")
                # 车床：根据评价方案选择字段
                elif '车' in machine_type:
                    if '径比' in evaluation_scheme:
                        if hasattr(params, 'max_length_diameter_ratio') and params.max_length_diameter_ratio is not None:
                            ws['B18'] = params.max_length_diameter_ratio
                            count += 1
                            param1_filled = True
                            logger.debug(f"负荷能力: 参数1(最大长径比) = {params.max_length_diameter_ratio}")
                    else:
                        if hasattr(params, 'max_cutting_length') and params.max_cutting_length is not None:
                            ws['B18'] = params.max_cutting_length
                            count += 1
                            param1_filled = True
                            logger.debug(f"负荷能力: 参数1(最大切削长度) = {params.max_cutting_length}")
            
            # 参数2：根据机床类型和评价方案动态映射
            param2_filled = False
            if hasattr(params, 'load_machine_type') and params.load_machine_type:
                machine_type = params.load_machine_type
                evaluation_scheme = getattr(params, 'evaluation_scheme', '') or ''
                
                # 铣床：刀具直径
                if '铣' in machine_type:
                    if hasattr(params, 'tool_diameter') and params.tool_diameter is not None:
                        ws['B19'] = params.tool_diameter
                        count += 1
                        param2_filled = True
                        logger.debug(f"负荷能力: 参数2(刀具直径) = {params.tool_diameter}")
                # 车床：根据评价方案选择字段
                elif '车' in machine_type:
                    if '径比' in evaluation_scheme:
                        if hasattr(params, 'design_length_diameter_ratio') and params.design_length_diameter_ratio is not None:
                            ws['B19'] = params.design_length_diameter_ratio
                            count += 1
                            param2_filled = True
                            logger.debug(f"负荷能力: 参数2(设计长径比) = {params.design_length_diameter_ratio}")
                    else:
                        if hasattr(params, 'expected_cutting_length') and params.expected_cutting_length is not None:
                            ws['B19'] = params.expected_cutting_length
                            count += 1
                            param2_filled = True
                            logger.debug(f"负荷能力: 参数2(预期切削长度) = {params.expected_cutting_length}")
            
            # 切削振动速度4
            if hasattr(params, 'cutting_vibration_speed4') and params.cutting_vibration_speed4 is not None:
                ws['B20'] = params.cutting_vibration_speed4
                count += 1
                logger.debug(f"负荷能力: 切削振动速度4 = {params.cutting_vibration_speed4}")
            
            logger.info(f"已填充负荷能力数据: {count}条记录")
        
        # 3. 可靠性模块
        # 3.1 平均故障间隔时间
        if '3.1 平均故障间隔时间' in wb.sheetnames:
            ws = wb['3.1 平均故障间隔时间']
            logger.info(f"开始处理MTBF数据，Sheet: {ws.title}")
            
            count = 0
            if hasattr(params, 'total_run_time') and params.total_run_time is not None:
                ws['B2'] = params.total_run_time
                count += 1
                logger.debug(f"MTBF: 总运行时间 = {params.total_run_time}")
            if hasattr(params, 'fault_count') and params.fault_count is not None:
                ws['C2'] = params.fault_count
                count += 1
                logger.debug(f"MTBF: 故障次数 = {params.fault_count}")
            
            logger.info(f"已填充MTBF数据: {count}条记录")
        
        # 3.2 平均修复时间
        if '3.2 平均修复时间' in wb.sheetnames:
            ws = wb['3.2 平均修复时间']
            logger.info(f"开始处理MTTR数据，Sheet: {ws.title}")
            
            # 导入样式类
            from openpyxl.styles import Alignment, Border, Side
            
            count = 0
            # repair_time_values是一个JSON字段，包含修复时间列表
            if hasattr(params, 'repair_time_values') and params.repair_time_values is not None:
                repair_times = params.repair_time_values
                # 处理字符串类型的JSON数据（达梦数据库可能返回字符串）
                if isinstance(repair_times, str):
                    try:
                        import json
                        repair_times = json.loads(repair_times)
                        logger.info(f"MTTR: 成功解析JSON字符串")
                    except Exception as e:
                        logger.error(f"MTTR: 解析JSON字符串失败: {e}")
                        repair_times = None
                
                if isinstance(repair_times, list):
                    # 过滤掉None值，保留所有有效数据（包括0值）
                    valid_times = [t for t in repair_times if t is not None]
                    # 不限制数量，根据实际数据导出
                    
                    # 计算需要的行数（标题行 + 数据行）
                    needed_rows = 1 + len(valid_times)
                    current_rows = ws.max_row
                    
                    # 如果当前行数不足，添加行
                    if current_rows < needed_rows:
                        for _ in range(needed_rows - current_rows):
                            ws.append([])
                        logger.info(f"MTTR: 已添加{needed_rows - current_rows}行")
                    # 如果当前行数过多，删除多余的行
                    elif current_rows > needed_rows:
                        for row in range(current_rows, needed_rows, -1):
                            ws.delete_rows(row)
                        logger.info(f"MTTR: 已删除{current_rows - needed_rows}行")
                    
                    # 设置对齐样式
                    center_alignment = Alignment(horizontal='center', vertical='center')
                    
                    # 填充数据
                    for i, value in enumerate(valid_times, start=2):
                        # 设置A列（故障次序）
                        cell_a = ws[f'A{i}']
                        cell_a.value = i - 1  # 更新故障次序编号
                        cell_a.alignment = center_alignment
                        
                        # 设置B列（修复时间）
                        cell_b = ws[f'B{i}']
                        cell_b.value = value
                        cell_b.alignment = center_alignment
                        
                        count += 1
                        logger.debug(f"MTTR: 修复时间{i-1} = {value}")
                    
                    # 根据参数行数为有数据的单元格添加边框
                    if count > 0:
                        thin_border = Border(
                            left=Side(style='thin'),
                            right=Side(style='thin'),
                            top=Side(style='thin'),
                            bottom=Side(style='thin')
                        )
                        
                        # 为标题行和数据行添加边框
                        for row_idx in range(1, count + 2):  # 从第1行（标题）到最后一行数据
                            for col in ['A', 'B']:
                                cell = ws[f'{col}{row_idx}']
                                cell.border = thin_border
                        
                        logger.info(f"MTTR: 已为{count + 1}行（标题+数据）的A、B列设置边框")
            
            logger.info(f"已填充MTTR数据: {count}条记录")
        
        # 3.3 当量故障率
        if '3.3 当量故障率' in wb.sheetnames:
            ws = wb['3.3 当量故障率']
            logger.info(f"开始处理当量故障率数据，Sheet: {ws.title}")
            
            count = 0
            if hasattr(params, 'fatal_failure') and params.fatal_failure is not None:
                ws['B2'] = params.fatal_failure
                count += 1
                logger.debug(f"当量故障率: 致命故障数 = {params.fatal_failure}")
            if hasattr(params, 'serious_failure') and params.serious_failure is not None:
                ws['C2'] = params.serious_failure
                count += 1
                logger.debug(f"当量故障率: 严重故障数 = {params.serious_failure}")
            if hasattr(params, 'general_failure') and params.general_failure is not None:
                ws['D2'] = params.general_failure
                count += 1
                logger.debug(f"当量故障率: 一般故障数 = {params.general_failure}")
            if hasattr(params, 'operation_time') and params.operation_time is not None:
                ws['E2'] = params.operation_time
                count += 1
                logger.debug(f"当量故障率: 运行时间 = {params.operation_time}")
            
            logger.info(f"已填充当量故障率数据: {count}条记录")
        
        # 3.4 加工一致性
        if '3.4 加工一致性' in wb.sheetnames:
            ws = wb['3.4 加工一致性']
            logger.info(f"开始处理加工一致性数据，Sheet: {ws.title}")
            
            count = 0
            # 标准差σ
            if hasattr(params, 'standard_deviation') and params.standard_deviation is not None:
                ws['B2'] = params.standard_deviation
                count += 1
                logger.debug(f"加工一致性: 标准差σ = {params.standard_deviation}")
            
            # 均值μ
            if hasattr(params, 'mean_value') and params.mean_value is not None:
                ws['C2'] = params.mean_value
                count += 1
                logger.debug(f"加工一致性: 均值μ = {params.mean_value}")
            
            logger.info(f"已填充加工一致性数据: {count}条记录")
        
        # 3.5 加工精度保持性
        if '3.5 加工精度保持性' in wb.sheetnames:
            ws = wb['3.5 加工精度保持性']
            logger.info(f"开始处理加工精度保持性数据，Sheet: {ws.title}")
            
            count = 0
            # 原始精度φ_I
            if hasattr(params, 'original_precision') and params.original_precision is not None:
                ws['B2'] = params.original_precision
                count += 1
                logger.debug(f"加工精度保持性: 原始精度φ_I = {params.original_precision}")
            
            # 失效精度φ_F
            if hasattr(params, 'failure_precision') and params.failure_precision is not None:
                ws['C2'] = params.failure_precision
                count += 1
                logger.debug(f"加工精度保持性: 失效精度φ_F = {params.failure_precision}")
            
            # 初始精度P_0
            if hasattr(params, 'initial_precision') and params.initial_precision is not None:
                ws['D2'] = params.initial_precision
                count += 1
                logger.debug(f"加工精度保持性: 初始精度P_0 = {params.initial_precision}")
            
            logger.info(f"已填充加工精度保持性数据: {count}条记录")
        
        # 3.6 平均首次故障时间
        if '3.6 平均首次故障时间' in wb.sheetnames:
            ws = wb['3.6 平均首次故障时间']
            logger.info(f"开始处理MTTF数据，Sheet: {ws.title}")
            
            # 导入样式类
            from openpyxl.styles import Alignment, Border, Side
            
            count = 0
            # failure_time_values是一个JSON字段，包含故障时间列表
            if hasattr(params, 'failure_time_values') and params.failure_time_values is not None:
                failure_times = params.failure_time_values
                # 处理字符串类型的JSON数据（达梦数据库可能返回字符串）
                if isinstance(failure_times, str):
                    try:
                        import json
                        failure_times = json.loads(failure_times)
                        logger.info(f"MTTF: 成功解析JSON字符串")
                    except Exception as e:
                        logger.error(f"MTTF: 解析JSON字符串失败: {e}")
                        failure_times = None
                
                if isinstance(failure_times, list):
                    # 过滤掉None值，保留所有有效数据（包括0值）
                    valid_times = [t for t in failure_times if t is not None]
                    # 不限制数量，根据实际数据导出
                    
                    # 计算需要的行数（标题行 + 数据行）
                    needed_rows = 1 + len(valid_times)
                    current_rows = ws.max_row
                    
                    # 如果当前行数不足，添加行
                    if current_rows < needed_rows:
                        for _ in range(needed_rows - current_rows):
                            ws.append([])
                        logger.info(f"MTTF: 已添加{needed_rows - current_rows}行")
                    # 如果当前行数过多，删除多余的行
                    elif current_rows > needed_rows:
                        for row in range(current_rows, needed_rows, -1):
                            ws.delete_rows(row)
                        logger.info(f"MTTF: 已删除{current_rows - needed_rows}行")
                    
                    # 设置对齐样式
                    center_alignment = Alignment(horizontal='center', vertical='center')
                    
                    # 填充数据
                    for i, value in enumerate(valid_times, start=2):
                        # 设置A列（故障次序）
                        cell_a = ws[f'A{i}']
                        cell_a.value = i - 1  # 更新故障次序编号
                        cell_a.alignment = center_alignment
                        
                        # 设置B列（故障时间）
                        cell_b = ws[f'B{i}']
                        cell_b.value = value
                        cell_b.alignment = center_alignment
                        
                        count += 1
                        logger.debug(f"MTTF: 故障时间{i-1} = {value}")
                    
                    # 根据参数行数为有数据的单元格添加边框
                    if count > 0:
                        thin_border = Border(
                            left=Side(style='thin'),
                            right=Side(style='thin'),
                            top=Side(style='thin'),
                            bottom=Side(style='thin')
                        )
                        
                        # 为标题行和数据行添加边框
                        for row_idx in range(1, count + 2):  # 从第1行（标题）到最后一行数据
                            for col in ['A', 'B']:
                                cell = ws[f'{col}{row_idx}']
                                cell.border = thin_border
                        
                        logger.info(f"MTTF: 已为{count + 1}行（标题+数据）的A、B列设置边框")
            
            logger.info(f"已填充MTTF数据: {count}条记录")
        
        # 4. 智能化
        if '4 智能化' in wb.sheetnames:
            ws = wb['4 智能化']
            logger.info(f"开始处理智能化数据，Sheet: {ws.title}")
            
            count = 0
            # intelligence_checkbox_states是一个JSON字段，包含checkbox状态（列表格式）
            if hasattr(params, 'intelligence_checkbox_states') and params.intelligence_checkbox_states is not None:
                checkbox_states = params.intelligence_checkbox_states
                if isinstance(checkbox_states, list):
                    # 将列表转换为字典，便于查找
                    checkbox_dict = {}
                    for item in checkbox_states:
                        if isinstance(item, dict) and 'feature' in item:
                            checkbox_dict[item['feature']] = item.get('satisfied', False)
                    
                    logger.info(f"智能化checkbox状态字典: {checkbox_dict}")
                    
                    # 遍历Excel的每一行，找到核心特征并填充checkbox状态
                    for row_idx in range(2, 23):  # 第2-22行
                        row = list(ws.iter_rows(min_row=row_idx, max_row=row_idx))[0]
                        if not row or len(row) < 4:
                            continue
                        feature_cell = row[2]  # C列是核心特征
                        if not feature_cell.value:
                            continue
                        feature = str(feature_cell.value).strip()
                        
                        # 查找对应的checkbox状态
                        if feature in checkbox_dict:
                            value = checkbox_dict[feature]
                            # 以0、1形式保存
                            ws.cell(row=row_idx, column=4, value=1 if value else 0)  # D列是机床1是否满足
                            count += 1
                            logger.debug(f"智能化 [行{row_idx}]: {feature} = {1 if value else 0}")
                        else:
                            logger.debug(f"智能化 [行{row_idx}]: 特征'{feature}'未在数据库中找到")
            
            logger.info(f"已填充智能化数据: {count}条记录")
        
        # 5. 绿色化模块
        # 5.1 资源循环与耗材
        if '5.1 资源循环与耗材' in wb.sheetnames:
            ws = wb['5.1 资源循环与耗材']
            logger.info(f"开始处理资源循环与耗材数据，Sheet: {ws.title}")
            
            # 为C列（第10-17行）添加水平和垂直居中
            from openpyxl.styles import Alignment
            center_alignment = Alignment(horizontal='center', vertical='center')
            for row_idx in range(10, 18):
                cell = ws.cell(row=row_idx, column=3)  # C列
                cell.alignment = center_alignment
            logger.info("已为表5.1的C列（第10-17行）设置居中对齐")
            
            count = 0
            # 切削液消耗量Q
            if hasattr(params, 'cutting_fluid_q') and params.cutting_fluid_q is not None:
                ws['B2'] = params.cutting_fluid_q
                count += 1
                logger.debug(f"资源循环与耗材: 切削液消耗量Q = {params.cutting_fluid_q}")
            
            # 切削液主轴功率P1
            if hasattr(params, 'cutting_fluid_p') and params.cutting_fluid_p is not None:
                ws['B3'] = params.cutting_fluid_p
                count += 1
                logger.debug(f"资源循环与耗材: 切削液主轴功率P1 = {params.cutting_fluid_p}")
            
            # 润滑油消耗量L
            if hasattr(params, 'lubricant_l') and params.lubricant_l is not None:
                ws['B5'] = params.lubricant_l
                count += 1
                logger.debug(f"资源循环与耗材: 润滑油消耗量L = {params.lubricant_l}")
            
            # 润滑油主轴功率P2
            if hasattr(params, 'lubricant_p') and params.lubricant_p is not None:
                ws['B6'] = params.lubricant_p
                count += 1
                logger.debug(f"资源循环与耗材: 润滑油主轴功率P2 = {params.lubricant_p}")
            
            # 润滑油消耗限定值x
            if hasattr(params, 'lubricant_x') and params.lubricant_x is not None:
                ws['B7'] = params.lubricant_x
                count += 1
                logger.debug(f"资源循环与耗材: 润滑油消耗限定值x = {params.lubricant_x}")
            
            # 轻量化设计项目（JSON字段，存储为对象列表）
            if hasattr(params, 'lightweight_items') and params.lightweight_items is not None:
                lightweight_items = params.lightweight_items
                if isinstance(lightweight_items, list):
                    # 将列表转换为字典，方便查找
                    items_dict = {}
                    for item in lightweight_items:
                        if isinstance(item, dict) and 'feature' in item and 'satisfied' in item:
                            items_dict[item['feature']] = item['satisfied']
                    
                    # 拓扑优化/形貌优化
                    satisfied = items_dict.get('拓扑优化/形貌优化', False)
                    ws['C10'] = 1 if satisfied else 0
                    if satisfied:
                        count += 1
                        logger.debug(f"资源循环与耗材: 拓扑优化/形貌优化 = 1")
                    
                    # 加强筋/蜂窝结构优化
                    satisfied = items_dict.get('加强筋/蜂窝结构优化', False)
                    ws['C11'] = 1 if satisfied else 0
                    if satisfied:
                        count += 1
                        logger.debug(f"资源循环与耗材: 加强筋/蜂窝结构优化 = 1")
                    
                    # 尺寸/参数优化
                    satisfied = items_dict.get('尺寸/参数优化', False)
                    ws['C12'] = 1 if satisfied else 0
                    if satisfied:
                        count += 1
                        logger.debug(f"资源循环与耗材: 尺寸/参数优化 = 1")
                    
                    # 轻质材料应用
                    satisfied = items_dict.get('轻质材料应用', False)
                    ws['C13'] = 1 if satisfied else 0
                    if satisfied:
                        count += 1
                        logger.debug(f"资源循环与耗材: 轻质材料应用 = 1")
                    
                    # 高强度材料应用
                    satisfied = items_dict.get('高强度材料应用', False)
                    ws['C14'] = 1 if satisfied else 0
                    if satisfied:
                        count += 1
                        logger.debug(f"资源循环与耗材: 高强度材料应用 = 1")
                    
                    # 中空/薄壁结构
                    satisfied = items_dict.get('中空/薄壁结构', False)
                    ws['C15'] = 1 if satisfied else 0
                    if satisfied:
                        count += 1
                        logger.debug(f"资源循环与耗材: 中空/薄壁结构 = 1")
                    
                    # 集成化设计
                    satisfied = items_dict.get('集成化设计', False)
                    ws['C16'] = 1 if satisfied else 0
                    if satisfied:
                        count += 1
                        logger.debug(f"资源循环与耗材: 集成化设计 = 1")
                    
                    # 有限元分析与验证
                    satisfied = items_dict.get('有限元分析与验证', False)
                    ws['C17'] = 1 if satisfied else 0
                    if satisfied:
                        count += 1
                        logger.debug(f"资源循环与耗材: 有限元分析与验证 = 1")
            
            logger.info(f"已填充资源循环与耗材数据: {count}条记录")
        
        # 5.2 能源-能效
        if '5.2 能源-能效' in wb.sheetnames:
            ws = wb['5.2 能源-能效']
            logger.info(f"开始处理能源-能效数据，Sheet: {ws.title}")
            
            count = 0
            # 待机功率Est
            if hasattr(params, 'est_value') and params.est_value is not None:
                ws['B2'] = params.est_value
                count += 1
                logger.debug(f"能源-能效: 待机功率Est = {params.est_value}")
            
            # 空运转功率Eu
            if hasattr(params, 'eu_value') and params.eu_value is not None:
                ws['B3'] = params.eu_value
                count += 1
                logger.debug(f"能源-能效: 空运转功率Eu = {params.eu_value}")
            
            # 切削功率Ec
            if hasattr(params, 'ec_value') and params.ec_value is not None:
                ws['B4'] = params.ec_value
                count += 1
                logger.debug(f"能源-能效: 切削功率Ec = {params.ec_value}")
            
            # 材料去除率n
            if hasattr(params, 'n_value') and params.n_value is not None:
                ws['B5'] = params.n_value
                count += 1
                logger.debug(f"能源-能效: 材料去除率n = {params.n_value}")
            
            # 切削体积v
            if hasattr(params, 'v_value') and params.v_value is not None:
                ws['B6'] = params.v_value
                count += 1
                logger.debug(f"能源-能效: 切削体积v = {params.v_value}")
            
            logger.info(f"已填充能源-能效数据: {count}条记录")
        
        logger.info(f"机床{machine_id}的所有模块数据填充完成")
        
    except Exception as e:
        logger.error(f"填充模块数据失败: {str(e)}", exc_info=True)
        raise


def apply_special_sheet_processing(wb):
    """
    对特定Sheet进行特殊处理
    
    功能说明：
        对导出的Excel工作簿中的特定Sheet进行格式调整和内容修改，
        确保导出的Excel文件符合用户要求。
    
    参数：
        wb: openpyxl.Workbook对象，要处理的Excel工作簿
    
    处理内容：
        1. 表5.1 资源循环与耗材
           - 将C列标题"机床7是否满足"修改为"机床1是否满足"
           - 原因：模板中预留了多台机床的列，但实际导出只处理单台机床
        
        2. 表3.4 加工一致性
           - 为第二行添加水平和垂直居中对齐
           - 原因：第二行是数据行，需要居中显示
        
        3. 表3.5 加工精度保持性
           - 为第二行添加水平和垂直居中对齐
           - 原因：第二行是数据行，需要居中显示
    
    异常处理：
        - 如果处理过程中发生错误，记录错误日志但不抛出异常（不影响主流程）
    """
    try:
        # 修改表5.1的C列"机床7是否满足"改为"机床1是否满足"
        if '5.1 资源循环与耗材' in wb.sheetnames:
            ws = wb['5.1 资源循环与耗材']
            # 找到"机床7是否满足"的单元格并修改
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value and '机床7是否满足' in str(cell.value):
                        cell.value = str(cell.value).replace('机床7是否满足', '机床1是否满足')
                        logger.info(f"已修改表5.1的'机床7是否满足'为'机床1是否满足'")
                        break
        
        # 为表3.4的第二行添加垂直居中
        if '3.4 加工一致性' in wb.sheetnames:
            ws = wb['3.4 加工一致性']
            from openpyxl.styles import Alignment
            for cell in ws[2]:  # 第二行
                cell.alignment = Alignment(horizontal='center', vertical='center')
            logger.info("已为表3.4的第二行添加垂直居中")
        
        # 为表3.5的第二行添加垂直居中
        if '3.5 加工精度保持性' in wb.sheetnames:
            ws = wb['3.5 加工精度保持性']
            from openpyxl.styles import Alignment
            for cell in ws[2]:  # 第二行
                cell.alignment = Alignment(horizontal='center', vertical='center')
            logger.info("已为表3.5的第二行添加垂直居中")
        
    except Exception as e:
        logger.error(f"特殊Sheet处理失败: {str(e)}", exc_info=True)
