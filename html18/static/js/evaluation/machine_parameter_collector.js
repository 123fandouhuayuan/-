/**
 * 机床参数数据收集模块
 * 
 * 功能：从各个子页面收集修改的参数，并同步至数据库
 * 
 * 使用方法：
 * 1. 在每个子页面调用对应的collect函数收集参数
 * 2. 调用updateMachineParameters函数将参数同步至数据库
 */

// ========== 通用函数 ==========

/**
 * 更新机床参数到数据库
 * @param {number} machineId - 机床ID
 * @param {object} parameters - 参数字典
 * @param {string} module - 模块名称
 * @returns {Promise} 更新结果
 */
async function updateMachineParameters(machineId, parameters, module) {
    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        const response = await fetch('/evaluation/api/update-machine-parameters/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                machine_id: machineId,
                parameters: parameters,
                module: module
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log(`参数更新成功: 模块=${module}, 更新字段数=${result.updated_count}`);
            return result;
        } else {
            console.error(`参数更新失败: ${result.message}`);
            throw new Error(result.message);
        }
    } catch (error) {
        console.error('更新机床参数时发生错误:', error);
        throw error;
    }
}

/**
 * 提取数值（处理空值和字符串）
 * @param {string|number} value - 输入值
 * @returns {number|null} 数值或null
 */
function extractNumericValue(value) {
    if (value === null || value === undefined || value === '') {
        return null;
    }
    
    const num = parseFloat(value);
    return isNaN(num) ? null : num;
}

// ========== 位置精度数据收集函数 ==========

/**
 * 收集位置精度参数
 * @returns {object} 参数字典
 */
function collectPositionAccuracyParameters() {
    const parameters = {};
    const isBoringMilling = window.IS_BORING_MILLING || window.CURRENT_MACHINE_TYPE === 'boring_milling_machine';
    
    // 表5.1：反向间隙（线性轴X/Y/Z/W）
    $('#backlash-table tr').each(function() {
        const row = $(this);
        const inputs = row.find('input[type="number"]');
        
        // X轴实测值
        const xValue = extractNumericValue(inputs.eq(0).val());
        if (xValue !== null) {
            if (isBoringMilling) {
                parameters['bm_linear_axis_backlash_x'] = xValue;
            } else {
                parameters['linear_axis_backlash_x'] = xValue;
            }
        }
        
        // Y轴实测值
        const yValue = extractNumericValue(inputs.eq(2).val());
        if (yValue !== null) {
            if (isBoringMilling) {
                parameters['bm_linear_axis_backlash_y'] = yValue;
            } else {
                parameters['linear_axis_backlash_y'] = yValue;
            }
        }
        
        // Z轴实测值
        const zValue = extractNumericValue(inputs.eq(4).val());
        if (zValue !== null) {
            if (isBoringMilling) {
                parameters['bm_linear_axis_backlash_z'] = zValue;
            } else {
                parameters['linear_axis_backlash_z'] = zValue;
            }
        }
        
        // W轴实测值（镗铣床专用）
        if (isBoringMilling) {
            const wValue = extractNumericValue(inputs.eq(6).val());
            if (wValue !== null) {
                parameters['bm_linear_axis_backlash_w'] = wValue;
            }
        }
    });
    
    // 表5.2：反向间隙（回转轴A/B/C）
    $('#backlash-table-2 tr').each(function() {
        const row = $(this);
        const inputs = row.find('input[type="number"]');
        
        // A轴实测值
        const aValue = extractNumericValue(inputs.eq(0).val());
        if (aValue !== null) {
            if (isBoringMilling) {
                parameters['bm_rotary_axis_backlash_a'] = aValue;
            } else {
                parameters['rotary_axis_backlash_a'] = aValue;
            }
        }
        
        // B轴实测值
        const bValue = extractNumericValue(inputs.eq(2).val());
        if (bValue !== null) {
            if (isBoringMilling) {
                parameters['bm_rotary_axis_backlash_b'] = bValue;
            } else {
                parameters['rotary_axis_backlash_b'] = bValue;
            }
        }
        
        // C轴实测值
        const cValue = extractNumericValue(inputs.eq(4).val());
        if (cValue !== null) {
            if (isBoringMilling) {
                parameters['bm_rotary_axis_backlash_c'] = cValue;
            } else {
                parameters['rotary_axis_backlash_c'] = cValue;
            }
        }
    });
    
    // 表1.2：重复定位精度（线性轴X/Y/Z）
    $('#position-accuracy-table tr').each(function() {
        const row = $(this);
        const inputs = row.find('input[type="number"]');
        
        // X轴实测值
        const xValue = extractNumericValue(inputs.eq(0).val());
        if (xValue !== null) {
            if (isBoringMilling) {
                parameters['bm_linear_axis_repeatability_x'] = xValue;
            } else {
                parameters['linear_axis_repeatability_x'] = xValue;
            }
        }
        
        // Y轴实测值
        const yValue = extractNumericValue(inputs.eq(2).val());
        if (yValue !== null) {
            if (isBoringMilling) {
                parameters['bm_linear_axis_repeatability_y'] = yValue;
            } else {
                parameters['linear_axis_repeatability_y'] = yValue;
            }
        }
        
        // Z轴实测值
        const zValue = extractNumericValue(inputs.eq(4).val());
        if (zValue !== null) {
            if (isBoringMilling) {
                parameters['bm_linear_axis_repeatability_z'] = zValue;
            } else {
                parameters['linear_axis_repeatability_z'] = zValue;
            }
        }
        
        // W轴实测值（镗铣床专用）
        if (isBoringMilling) {
            const wValue = extractNumericValue(inputs.eq(6).val());
            if (wValue !== null) {
                parameters['bm_linear_axis_repeatability_w'] = wValue;
            }
        }
    });
    
    // 表1.2：重复定位精度（回转轴A/B/C）
    $('#position-accuracy-table-2 tr').each(function() {
        const row = $(this);
        const inputs = row.find('input[type="number"]');
        
        // A轴实测值
        const aValue = extractNumericValue(inputs.eq(0).val());
        if (aValue !== null) {
            if (isBoringMilling) {
                parameters['bm_rotary_axis_repeatability_a'] = aValue;
            } else {
                parameters['rotary_axis_repeatability_a'] = aValue;
            }
        }
        
        // B轴实测值
        const bValue = extractNumericValue(inputs.eq(2).val());
        if (bValue !== null) {
            if (isBoringMilling) {
                parameters['bm_rotary_axis_repeatability_b'] = bValue;
            } else {
                parameters['rotary_axis_repeatability_b'] = bValue;
            }
        }
        
        // C轴实测值
        const cValue = extractNumericValue(inputs.eq(4).val());
        if (cValue !== null) {
            if (isBoringMilling) {
                parameters['bm_rotary_axis_repeatability_c'] = cValue;
            } else {
                parameters['rotary_axis_repeatability_c'] = cValue;
            }
        }
    });
    
    return parameters;
}

// ========== 进给轴精度数据收集函数 ==========

/**
 * 收集进给轴精度参数
 * @returns {object} 参数字典
 */
function collectFeedAxisAccuracyParameters() {
    const parameters = {};
    const isBoringMilling = window.IS_BORING_MILLING || window.CURRENT_MACHINE_TYPE === 'boring_milling_machine';
    
    // 进给轴精度表格
    $('#feed-axis-accuracy-table tr').each(function() {
        const row = $(this);
        const inputs = row.find('input[type="number"]');
        
        if (isBoringMilling) {
            // 镗铣床字段映射
            // 立柱移动直线度 YZ平面(EYW)
            const columnLinearityYz = extractNumericValue(inputs.eq(0).val());
            if (columnLinearityYz !== null) {
                parameters['bm_column_linearity_yz'] = columnLinearityYz;
            }
            
            // 立柱移动直线度 ZX平面(EXW)
            const columnLinearityZx = extractNumericValue(inputs.eq(1).val());
            if (columnLinearityZx !== null) {
                parameters['bm_column_linearity_zx'] = columnLinearityZx;
            }
            
            // 工作台移动(X轴)直线度 XY平面(EYX)
            const worktableXLinearityXy = extractNumericValue(inputs.eq(3).val());
            if (worktableXLinearityXy !== null) {
                parameters['bm_worktable_x_linearity_xy'] = worktableXLinearityXy;
            }
            
            // 工作台移动(X轴)直线度 ZX平面(EZX)
            const worktableXLinearityZx = extractNumericValue(inputs.eq(4).val());
            if (worktableXLinearityZx !== null) {
                parameters['bm_worktable_x_linearity_zx'] = worktableXLinearityZx;
            }
            
            // 主轴箱移动(Y轴)直线度 YZ平面(EZY)
            const spindleBoxYLinearityYz = extractNumericValue(inputs.eq(6).val());
            if (spindleBoxYLinearityYz !== null) {
                parameters['bm_spindle_box_y_linearity_yz'] = spindleBoxYLinearityYz;
            }
            
            // 主轴箱移动(Y轴)直线度 XY平面(EXY)
            const spindleBoxYLinearityXy = extractNumericValue(inputs.eq(7).val());
            if (spindleBoxYLinearityXy !== null) {
                parameters['bm_spindle_box_y_linearity_xy'] = spindleBoxYLinearityXy;
            }
        } else {
            // 加工中心字段映射
            // X轴直线度 XY平面
            const xAxisLinearityXy = extractNumericValue(inputs.eq(0).val());
            if (xAxisLinearityXy !== null) {
                parameters['x_axis_linearity_xy'] = xAxisLinearityXy;
            }
            
            // X轴直线度 ZX平面
            const xAxisLinearityZx = extractNumericValue(inputs.eq(1).val());
            if (xAxisLinearityZx !== null) {
                parameters['x_axis_linearity_zx'] = xAxisLinearityZx;
            }
            
            // Z轴直线度 YZ平面
            const zAxisLinearityYz = extractNumericValue(inputs.eq(3).val());
            if (zAxisLinearityYz !== null) {
                parameters['z_axis_linearity_yz'] = zAxisLinearityYz;
            }
            
            // Z轴直线度 ZX平面
            const zAxisLinearityZx = extractNumericValue(inputs.eq(4).val());
            if (zAxisLinearityZx !== null) {
                parameters['z_axis_linearity_zx'] = zAxisLinearityZx;
            }
            
            // Y轴直线度 XY平面
            const yAxisLinearityXy = extractNumericValue(inputs.eq(6).val());
            if (yAxisLinearityXy !== null) {
                parameters['y_axis_linearity_xy'] = yAxisLinearityXy;
            }
            
            // Y轴直线度 YZ平面
            const yAxisLinearityYz = extractNumericValue(inputs.eq(7).val());
            if (yAxisLinearityYz !== null) {
                parameters['y_axis_linearity_yz'] = yAxisLinearityYz;
            }
        }
    });
    
    // 角度误差表格
    $('#angle-error-table tr').each(function() {
        const row = $(this);
        const inputs = row.find('input[type="number"]');
        
        if (isBoringMilling) {
            // 镗铣床角度误差字段映射
            // 角度误差表格结构（每行11个input，索引0-10）：
            // 立柱移动: YZ平面(0), ZX平面(1), XY平面(2), 允差(3)
            // 工作台X轴: XY平面(4), ZX平面(5), YZ平面(6), 允差(7)
            // 主轴箱Y轴: YZ平面(8), ZX平面(9), 允差(10)
            
            // 立柱移动角度偏差 YZ平面(EAW) - 索引0
            const columnAngleYz = extractNumericValue(inputs.eq(0).val());
            if (columnAngleYz !== null) {
                parameters['bm_column_angle_yz'] = columnAngleYz;
            }
            
            // 立柱移动角度偏差 ZX平面(EBW) - 索引1
            const columnAngleZx = extractNumericValue(inputs.eq(1).val());
            if (columnAngleZx !== null) {
                parameters['bm_column_angle_zx'] = columnAngleZx;
            }
            
            // 立柱移动角度偏差 XY平面(ECW) - 索引2
            const columnAngleXy = extractNumericValue(inputs.eq(2).val());
            if (columnAngleXy !== null) {
                parameters['bm_column_angle_xy'] = columnAngleXy;
            }
            
            // 工作台移动(X轴)角度偏差 XY平面(ECX) - 索引4
            const worktableXAngleXy = extractNumericValue(inputs.eq(4).val());
            if (worktableXAngleXy !== null) {
                parameters['bm_worktable_x_angle_xy'] = worktableXAngleXy;
            }
            
            // 工作台移动(X轴)角度偏差 ZX平面(EBX) - 索引5
            const worktableXAngleZx = extractNumericValue(inputs.eq(5).val());
            if (worktableXAngleZx !== null) {
                parameters['bm_worktable_x_angle_zx'] = worktableXAngleZx;
            }
            
            // 工作台移动(X轴)角度偏差 YZ平面(EAX) - 索引6
            const worktableXAngleYz = extractNumericValue(inputs.eq(6).val());
            if (worktableXAngleYz !== null) {
                parameters['bm_worktable_x_angle_yz'] = worktableXAngleYz;
            }
            
            // 主轴箱移动(Y轴)角度偏差 YZ平面(EAY) - 索引8
            const spindleBoxYAngleYz = extractNumericValue(inputs.eq(8).val());
            if (spindleBoxYAngleYz !== null) {
                parameters['bm_spindle_box_y_angle_yz'] = spindleBoxYAngleYz;
            }
            
            // 主轴箱移动(Y轴)角度偏差 ZX平面(EBY) - 索引9
            const spindleBoxYAngleZx = extractNumericValue(inputs.eq(9).val());
            if (spindleBoxYAngleZx !== null) {
                parameters['bm_spindle_box_y_angle_zx'] = spindleBoxYAngleZx;
            }
        } else {
            // 加工中心角度误差字段映射
            // 角度误差表格结构（每行12个input，索引0-11）：
            // X轴: 俯仰(0), 偏摆(1), 倾斜(2), 允差(3)
            // Z轴: 俯仰(4), 偏摆(5), 倾斜(6), 允差(7)
            // Y轴: YZ(8), XY(9), ZX(10), 允差(11)
            
            // X轴角度偏差（俯仰）- 索引0
            const xAxisAnglePitch = extractNumericValue(inputs.eq(0).val());
            if (xAxisAnglePitch !== null) {
                parameters['x_axis_angle_pitch'] = xAxisAnglePitch;
            }
            
            // X轴角度偏差（偏摆）- 索引1
            const xAxisAngleYaw = extractNumericValue(inputs.eq(1).val());
            if (xAxisAngleYaw !== null) {
                parameters['x_axis_angle_yaw'] = xAxisAngleYaw;
            }
            
            // X轴角度偏差（倾斜）- 索引2
            const xAxisAngleRoll = extractNumericValue(inputs.eq(2).val());
            if (xAxisAngleRoll !== null) {
                parameters['x_axis_angle_roll'] = xAxisAngleRoll;
            }
            
            // Z轴角度偏差（俯仰）- 索引4（跳过允差索引3）
            const zAxisAnglePitch = extractNumericValue(inputs.eq(4).val());
            if (zAxisAnglePitch !== null) {
                parameters['z_axis_angle_pitch'] = zAxisAnglePitch;
            }
            
            // Z轴角度偏差（偏摆）- 索引5
            const zAxisAngleYaw = extractNumericValue(inputs.eq(5).val());
            if (zAxisAngleYaw !== null) {
                parameters['z_axis_angle_yaw'] = zAxisAngleYaw;
            }
            
            // Z轴角度偏差（倾斜）- 索引6
            const zAxisAngleRoll = extractNumericValue(inputs.eq(6).val());
            if (zAxisAngleRoll !== null) {
                parameters['z_axis_angle_roll'] = zAxisAngleRoll;
            }
            
            // Y轴角度偏差（Y-Z垂直平面内）- 索引8（跳过允差索引7）
            const yAxisAngleYz = extractNumericValue(inputs.eq(8).val());
            if (yAxisAngleYz !== null) {
                parameters['y_axis_angle_yz'] = yAxisAngleYz;
            }
            
            // Y轴角度偏差（X-Y垂直平面内）- 索引9
            const yAxisAngleXy = extractNumericValue(inputs.eq(9).val());
            if (yAxisAngleXy !== null) {
                parameters['y_axis_angle_xy'] = yAxisAngleXy;
            }
            
            // Y轴角度偏差（ZX水平面内）- 索引10
            const yAxisAngleZx = extractNumericValue(inputs.eq(10).val());
            if (yAxisAngleZx !== null) {
                parameters['y_axis_angle_zx'] = yAxisAngleZx;
            }
        }
    });
    
    // 垂直度表格
    $('#perpendicularity-table tr').each(function() {
        const row = $(this);
        const inputs = row.find('input[type="number"]');
        
        if (isBoringMilling) {
            // 镗铣床垂直度字段映射
            // 工作台移动(X轴)和立柱移动间的垂直度
            const worktableXColumnPerpendicularity = extractNumericValue(inputs.eq(0).val());
            if (worktableXColumnPerpendicularity !== null) {
                parameters['bm_worktable_x_column_perpendicularity'] = worktableXColumnPerpendicularity;
            }
            
            // 主轴箱移动(Y轴)对工作台移动(X轴)的垂直度
            const spindleBoxYWorktableXPerpendicularity = extractNumericValue(inputs.eq(1).val());
            if (spindleBoxYWorktableXPerpendicularity !== null) {
                parameters['bm_spindle_box_y_worktable_x_perpendicularity'] = spindleBoxYWorktableXPerpendicularity;
            }
            
            // 主轴箱移动(Y轴)对立柱移动的垂直度
            const spindleBoxYColumnPerpendicularity = extractNumericValue(inputs.eq(2).val());
            if (spindleBoxYColumnPerpendicularity !== null) {
                parameters['bm_spindle_box_y_column_perpendicularity'] = spindleBoxYColumnPerpendicularity;
            }
        } else {
            // 加工中心垂直度字段映射
            // 表格结构：每行6个input（索引0-5）
            // 索引0: Y轴、X轴垂直度-值, 索引1: Y轴、X轴垂直度-允差(readonly)
            // 索引2: Y轴、Z轴垂直度-值, 索引3: Y轴、Z轴垂直度-允差(readonly)
            // 索引4: Z轴、X轴垂直度-值, 索引5: Z轴、X轴垂直度-允差(readonly)
            
            // Y轴与X轴垂直度 - 索引0
            const yAxisPerpendicularityX = extractNumericValue(inputs.eq(0).val());
            if (yAxisPerpendicularityX !== null) {
                parameters['y_axis_perpendicularity_x'] = yAxisPerpendicularityX;
            }
            
            // Y轴与Z轴垂直度 - 索引2
            const yAxisPerpendicularityZ = extractNumericValue(inputs.eq(2).val());
            if (yAxisPerpendicularityZ !== null) {
                parameters['y_axis_perpendicularity_z'] = yAxisPerpendicularityZ;
            }
            
            // Z轴与X轴垂直度 - 索引4
            const zAxisPerpendicularityX = extractNumericValue(inputs.eq(4).val());
            if (zAxisPerpendicularityX !== null) {
                parameters['z_axis_perpendicularity_x'] = zAxisPerpendicularityX;
            }
        }
    });
    
    return parameters;
}

// ========== 工件几何精度数据收集函数 ==========

/**
 * 收集工件几何精度参数
 * @returns {object} 参数字典
 */
function collectWorkpieceGeometryAccuracyParameters() {
    const parameters = {};
    const isBoringMilling = window.IS_BORING_MILLING || window.CURRENT_MACHINE_TYPE === 'boring_milling_machine';
    
    // 表1.1（加工中心）或表1（镗铣床）
    $('#workpiece-geometry-table-1 tr').each(function() {
        const row = $(this);
        const inputs = row.find('input[type="number"]');
        
        if (isBoringMilling) {
            // 镗铣床字段映射
            // 正方形a
            const squareA = extractNumericValue(inputs.eq(0).val());
            if (squareA !== null) {
                parameters['bm_square_a'] = squareA;
            }
            
            // 正方形b
            const squareB = extractNumericValue(inputs.eq(2).val());
            if (squareB !== null) {
                parameters['bm_square_b'] = squareB;
            }
            
            // 正方形c
            const squareC = extractNumericValue(inputs.eq(4).val());
            if (squareC !== null) {
                parameters['bm_square_c'] = squareC;
            }
            
            // 菱形d
            const diamondD = extractNumericValue(inputs.eq(6).val());
            if (diamondD !== null) {
                parameters['bm_diamond_d'] = diamondD;
            }
            
            // 菱形e
            const diamondE = extractNumericValue(inputs.eq(8).val());
            if (diamondE !== null) {
                parameters['bm_diamond_e'] = diamondE;
            }
            
            // 圆f
            const circleF = extractNumericValue(inputs.eq(10).val());
            if (circleF !== null) {
                parameters['bm_circle_f'] = circleF;
            }
            
            // 镗孔h
            const boringHoleH = extractNumericValue(inputs.eq(12).val());
            if (boringHoleH !== null) {
                parameters['bm_boring_hole_h'] = boringHoleH;
            }
        } else {
            // 加工中心字段映射
            // 圆柱度
            const cylindricity = extractNumericValue(inputs.eq(0).val());
            if (cylindricity !== null) {
                parameters['cylindricity'] = cylindricity;
            }
            
            // 孔中心轴线与基准孔A的垂直度
            const holePerpendicularityA = extractNumericValue(inputs.eq(2).val());
            if (holePerpendicularityA !== null) {
                parameters['hole_perpendicularity_a'] = holePerpendicularityA;
            }
            
            // 侧面的直线度
            const sideLinearity = extractNumericValue(inputs.eq(4).val());
            if (sideLinearity !== null) {
                parameters['side_linearity'] = sideLinearity;
            }
            
            // 相邻面与基面B的垂直度
            const adjacentPerpendicularityB = extractNumericValue(inputs.eq(6).val());
            if (adjacentPerpendicularityB !== null) {
                parameters['adjacent_perpendicularity_b'] = adjacentPerpendicularityB;
            }
            
            // 相对面与基面B的平行度
            const oppositeParallelismB = extractNumericValue(inputs.eq(8).val());
            if (oppositeParallelismB !== null) {
                parameters['opposite_parallelism_b'] = oppositeParallelismB;
            }
            
            // 侧面的直线度（第二组）
            const sideLinearity2 = extractNumericValue(inputs.eq(10).val());
            if (sideLinearity2 !== null) {
                parameters['side_linearity_2'] = sideLinearity2;
            }
            
            // 侧面对基准B的倾斜度
            const sideInclinationB = extractNumericValue(inputs.eq(12).val());
            if (sideInclinationB !== null) {
                parameters['side_inclination_b'] = sideInclinationB;
            }
        }
    });
    
    // 表1.2（仅加工中心）
    if (!isBoringMilling) {
        $('#workpiece-geometry-table-2 tr').each(function() {
            const row = $(this);
            const inputs = row.find('input[type="number"]');
            
            // 圆度
            const circularity = extractNumericValue(inputs.eq(0).val());
            if (circularity !== null) {
                parameters['circularity'] = circularity;
            }
            
            // 外圆和内圆孔C的同心度
            const concentricityC = extractNumericValue(inputs.eq(2).val());
            if (concentricityC !== null) {
                parameters['concentricity_c'] = concentricityC;
            }
            
            // 斜面的直线度
            const slopeLinearity = extractNumericValue(inputs.eq(4).val());
            if (slopeLinearity !== null) {
                parameters['slope_linearity'] = slopeLinearity;
            }
            
            // 3°角斜面对基准B的倾斜度
            const slopeInclinationB = extractNumericValue(inputs.eq(6).val());
            if (slopeInclinationB !== null) {
                parameters['slope_inclination_b'] = slopeInclinationB;
            }
            
            // 孔相对于内孔C的位置度
            const holePositionC = extractNumericValue(inputs.eq(8).val());
            if (holePositionC !== null) {
                parameters['hole_position_c'] = holePositionC;
            }
            
            // 内孔与外孔D的同心度
            const concentricityD = extractNumericValue(inputs.eq(10).val());
            if (concentricityD !== null) {
                parameters['concentricity_d'] = concentricityD;
            }
        });
    }
    
    return parameters;
}

// ========== 工作台精度数据收集函数 ==========

/**
 * 收集工作台精度参数
 * @returns {object} 参数字典
 */
function collectWorktableAccuracyParameters() {
    const parameters = {};
    const isBoringMilling = window.IS_BORING_MILLING || window.CURRENT_MACHINE_TYPE === 'boring_milling_machine';
    
    // 工作台精度表格
    $('#worktable-accuracy-table tr').each(function() {
        const row = $(this);
        const inputs = row.find('input[type="number"]');
        
        if (isBoringMilling) {
            // 镗铣床字段映射
            // 工作台面平面度
            const worktableFlatness = extractNumericValue(inputs.eq(0).val());
            if (worktableFlatness !== null) {
                parameters['bm_worktable_flatness'] = worktableFlatness;
            }
            
            // 立柱移动的平行度
            const columnParallelism = extractNumericValue(inputs.eq(2).val());
            if (columnParallelism !== null) {
                parameters['bm_column_parallelism'] = columnParallelism;
            }
            
            // 工作台移动(X轴)的平行度
            const worktableXParallelism = extractNumericValue(inputs.eq(4).val());
            if (worktableXParallelism !== null) {
                parameters['bm_worktable_x_parallelism'] = worktableXParallelism;
            }
        } else {
            // 加工中心字段映射
            // 工作台面平面度
            const worktableFlatness = extractNumericValue(inputs.eq(0).val());
            if (worktableFlatness !== null) {
                parameters['worktable_flatness'] = worktableFlatness;
            }
            
            // 台面和X轴轴线运动间的平行度
            const worktableParallelismX = extractNumericValue(inputs.eq(2).val());
            if (worktableParallelismX !== null) {
                parameters['worktable_parallelism_x'] = worktableParallelismX;
            }
            
            // 台面和Z轴轴线运动间的平行度
            const worktableParallelismZ = extractNumericValue(inputs.eq(4).val());
            if (worktableParallelismZ !== null) {
                parameters['worktable_parallelism_z'] = worktableParallelismZ;
            }
        }
    });
    
    return parameters;
}

// ========== 主轴精度数据收集函数 ==========

/**
 * 收集主轴精度参数
 * @returns {object} 参数字典
 */
function collectSpindleAccuracyParameters() {
    const parameters = {};
    const isBoringMilling = window.IS_BORING_MILLING || window.CURRENT_MACHINE_TYPE === 'boring_milling_machine';
    
    // 主轴精度表格
    $('#spindle-accuracy-table tr').each(function() {
        const row = $(this);
        const inputs = row.find('input[type="number"]');
        
        if (isBoringMilling) {
            // 镗铣床字段映射
            // 镗轴锥孔的径向跳动-靠近轴端部处
            const boringAxisTaperRadialNear = extractNumericValue(inputs.eq(0).val());
            if (boringAxisTaperRadialNear !== null) {
                parameters['bm_boring_axis_taper_radial_near'] = boringAxisTaperRadialNear;
            }
            
            // 镗轴锥孔的径向跳动-距镗轴端部300mm处
            const boringAxisTaperRadial300mm = extractNumericValue(inputs.eq(2).val());
            if (boringAxisTaperRadial300mm !== null) {
                parameters['bm_boring_axis_taper_radial_300mm'] = boringAxisTaperRadial300mm;
            }
            
            // 镗轴的径向跳动-镗轴缩回时
            const boringAxisRadialRetracted = extractNumericValue(inputs.eq(4).val());
            if (boringAxisRadialRetracted !== null) {
                parameters['bm_boring_axis_radial_retracted'] = boringAxisRadialRetracted;
            }
            
            // 镗轴的径向跳动-镗轴伸出300mm时
            const boringAxisRadialExtended = extractNumericValue(inputs.eq(6).val());
            if (boringAxisRadialExtended !== null) {
                parameters['bm_boring_axis_radial_extended'] = boringAxisRadialExtended;
            }
            
            // 铣轴端部的径向跳动
            const millingAxisRadial = extractNumericValue(inputs.eq(8).val());
            if (millingAxisRadial !== null) {
                parameters['bm_milling_axis_radial'] = millingAxisRadial;
            }
        } else {
            // 加工中心字段映射
            // 主轴的周期性轴向窜动
            const spindleAxialRunout = extractNumericValue(inputs.eq(0).val());
            if (spindleAxialRunout !== null) {
                parameters['spindle_axial_runout'] = spindleAxialRunout;
            }
            
            // 靠近主轴端部的径向跳动
            const spindleRadialRunoutNear = extractNumericValue(inputs.eq(2).val());
            if (spindleRadialRunoutNear !== null) {
                parameters['spindle_radial_runout_near'] = spindleRadialRunoutNear;
            }
            
            // 距主轴端部300mm处的径向跳动
            const spindleRadialRunout300mm = extractNumericValue(inputs.eq(4).val());
            if (spindleRadialRunout300mm !== null) {
                parameters['spindle_radial_runout_300mm'] = spindleRadialRunout300mm;
            }
        }
    });
    
    // 镗铣床：表2 - 轴向窜动
    if (isBoringMilling) {
        $('#spindle-axial-runout-table tr').each(function() {
            const row = $(this);
            const inputs = row.find('input[type="number"]');
            
            // 镗轴周期性的轴向窜动-主轴缩回
            const boringAxisAxialRetracted = extractNumericValue(inputs.eq(0).val());
            if (boringAxisAxialRetracted !== null) {
                parameters['bm_boring_axis_axial_retracted'] = boringAxisAxialRetracted;
            }
            
            // 铣轴端部的周期性轴向窜动
            const millingAxisAxial = extractNumericValue(inputs.eq(2).val());
            if (millingAxisAxial !== null) {
                parameters['bm_milling_axis_axial'] = millingAxisAxial;
            }
        });
    }
    
    return parameters;
}

// ========== 性能模块数据收集函数 ==========

/**
 * 收集性能模块参数
 * @returns {object} 参数字典
 */
function collectPerformanceParameters() {
    const parameters = {};
    
    // ========== 加工分散性参数 ==========
    // CP值（从localStorage读取）
    const cpValue = extractNumericValue(localStorage.getItem('cp_value'));
    if (cpValue !== null) {
        parameters['cp_value'] = cpValue;
    }
    
    // ========== 加工效率参数 ==========
    // 从HTML输入框读取参数
    // 峰值转速
    const peakSpeedInput = document.getElementById('speed-actual');
    if (peakSpeedInput) {
        const peakSpeed = extractNumericValue(peakSpeedInput.value);
        if (peakSpeed !== null) {
            parameters['peak_speed'] = peakSpeed;
        }
    }
    
    // 谷值转速
    const valleySpeedInput = document.getElementById('speed-design');
    if (valleySpeedInput) {
        const valleySpeed = extractNumericValue(valleySpeedInput.value);
        if (valleySpeed !== null) {
            parameters['valley_speed'] = valleySpeed;
        }
    }
    
    // 设计最大转速
    const designMaxSpeedInput = document.getElementById('speed-error');
    if (designMaxSpeedInput) {
        const designMaxSpeed = extractNumericValue(designMaxSpeedInput.value);
        if (designMaxSpeed !== null) {
            parameters['design_max_speed'] = designMaxSpeed;
        }
    }
    
    // 最高快移速度
    const maxFastSpeedInput = document.getElementById('fast-speed-actual');
    if (maxFastSpeedInput) {
        const maxFastSpeed = extractNumericValue(maxFastSpeedInput.value);
        if (maxFastSpeed !== null) {
            parameters['max_fast_speed'] = maxFastSpeed;
        }
    }
    
    // 设计最高速度
    const designMaxFastSpeedInput = document.getElementById('fast-speed-design');
    if (designMaxFastSpeedInput) {
        const designMaxFastSpeed = extractNumericValue(designMaxFastSpeedInput.value);
        if (designMaxFastSpeed !== null) {
            parameters['design_max_fast_speed'] = designMaxFastSpeed;
        }
    }
    
    // 最高速度下重复定位精度
    const repeatPositioningAccuracyInput = document.getElementById('positioning-accuracy');
    if (repeatPositioningAccuracyInput) {
        const repeatPositioningAccuracy = extractNumericValue(repeatPositioningAccuracyInput.value);
        if (repeatPositioningAccuracy !== null) {
            parameters['repeat_positioning_accuracy'] = repeatPositioningAccuracy;
        }
    }
    
    // 最大进给速度
    const maxFeedSpeedInput = document.getElementById('feed-speed-actual');
    if (maxFeedSpeedInput) {
        const maxFeedSpeed = extractNumericValue(maxFeedSpeedInput.value);
        if (maxFeedSpeed !== null) {
            parameters['max_feed_speed'] = maxFeedSpeed;
        }
    }
    
    // 目标最高速度
    const targetMaxSpeedInput = document.getElementById('feed-speed-target');
    if (targetMaxSpeedInput) {
        const targetMaxSpeed = extractNumericValue(targetMaxSpeedInput.value);
        if (targetMaxSpeed !== null) {
            parameters['target_max_speed'] = targetMaxSpeed;
        }
    }
    
    // R2及加速度下重复定位精度
    const repeatPositioningAccuracyFeedInput = document.getElementById('positioning-accuracy-feed');
    if (repeatPositioningAccuracyFeedInput) {
        const repeatPositioningAccuracyFeed = extractNumericValue(repeatPositioningAccuracyFeedInput.value);
        if (repeatPositioningAccuracyFeed !== null) {
            parameters['repeat_positioning_accuracy_feed'] = repeatPositioningAccuracyFeed;
        }
    }
    
    // ========== 静刚度参数 ==========
    // 主轴径向刚度值
    const radialStiffnessInput = document.getElementById('radial-stiffness-actual');
    if (radialStiffnessInput) {
        const radialStiffness = extractNumericValue(radialStiffnessInput.value);
        if (radialStiffness !== null) {
            parameters['radial_stiffness'] = radialStiffness;
        }
    }
    
    // 主轴轴向刚度值
    const axialStiffnessInput = document.getElementById('axial-stiffness-actual');
    if (axialStiffnessInput) {
        const axialStiffness = extractNumericValue(axialStiffnessInput.value);
        if (axialStiffness !== null) {
            parameters['axial_stiffness'] = axialStiffness;
        }
    }
    
    // ========== 主轴参数 ==========
    // 最大振动速度
    const vibrationVmaxInput = document.getElementById('vibration-vmax');
    if (vibrationVmaxInput) {
        const vibrationVmax = extractNumericValue(vibrationVmaxInput.value);
        if (vibrationVmax !== null) {
            parameters['max_vibration_speed'] = vibrationVmax;
        }
    }
    
    // ========== 噪声参数 ==========
    // 噪声值
    const noiseValueInput = document.getElementById('noise-value');
    if (noiseValueInput) {
        const noiseValue = extractNumericValue(noiseValueInput.value);
        if (noiseValue !== null) {
            parameters['noise_value'] = noiseValue;
        }
    }
    
    // 噪声机床类型
    const noiseMachineTypeSelect = document.getElementById('noise-machine-type');
    if (noiseMachineTypeSelect) {
        const noiseMachineType = noiseMachineTypeSelect.value;
        if (noiseMachineType) {
            // 转换为中文
            let machineTypeCn = '';
            if (noiseMachineType === 'cnc') {
                machineTypeCn = '数控机床';
            } else if (noiseMachineType === 'ordinary') {
                machineTypeCn = '普通机床';
            } else {
                machineTypeCn = noiseMachineType;
            }
            parameters['noise_machine_type'] = machineTypeCn;
        }
    }
    
    // 噪声重量选择
    const noiseWeightSelect = document.getElementById('noise-weight-select');
    if (noiseWeightSelect) {
        const noiseWeight = noiseWeightSelect.value;
        if (noiseWeight) {
            // 转换为中文格式
            let weightCn = '';
            if (noiseWeight === '10t') {
                weightCn = '≤10t';
            } else if (noiseWeight === '10-30t') {
                weightCn = '10~30t';
            } else if (noiseWeight === '30t') {
                weightCn = '≥30t';
            } else {
                weightCn = noiseWeight;
            }
            parameters['noise_weight'] = weightCn;
        }
    }
    
    // ========== 热变形参数 ==========
    // 径向热位移范围
    const radialThermalDisplacementInput = document.getElementById('radial-thermal-displacement');
    if (radialThermalDisplacementInput) {
        const radialThermalDisplacement = extractNumericValue(radialThermalDisplacementInput.value);
        if (radialThermalDisplacement !== null) {
            parameters['radial_thermal_displacement'] = radialThermalDisplacement;
        }
    }
    
    // 热平衡梯度G1
    const radialThermalGradientInput = document.getElementById('radial-thermal-gradient');
    if (radialThermalGradientInput) {
        const radialThermalGradient = extractNumericValue(radialThermalGradientInput.value);
        if (radialThermalGradient !== null) {
            parameters['radial_thermal_gradient'] = radialThermalGradient;
        }
    }
    
    // 轴向热位移范围
    const axialThermalDisplacementInput = document.getElementById('axial-thermal-displacement');
    if (axialThermalDisplacementInput) {
        const axialThermalDisplacement = extractNumericValue(axialThermalDisplacementInput.value);
        if (axialThermalDisplacement !== null) {
            parameters['axial_thermal_displacement'] = axialThermalDisplacement;
        }
    }
    
    // 热平衡梯度G2
    const axialThermalGradientInput = document.getElementById('axial-thermal-gradient');
    if (axialThermalGradientInput) {
        const axialThermalGradient = extractNumericValue(axialThermalGradientInput.value);
        if (axialThermalGradient !== null) {
            parameters['axial_thermal_gradient'] = axialThermalGradient;
        }
    }
    
    // ========== 电流稳定性参数 ==========
    // 初检功率
    const initialPowerInput = document.getElementById('initial-power');
    if (initialPowerInput) {
        const initialPower = extractNumericValue(initialPowerInput.value);
        if (initialPower !== null) {
            parameters['initial_power'] = initialPower;
        }
    }
    
    // 终检功率
    const finalPowerInput = document.getElementById('final-power');
    if (finalPowerInput) {
        const finalPower = extractNumericValue(finalPowerInput.value);
        if (finalPower !== null) {
            parameters['final_power'] = finalPower;
        }
    }
    
    // 电流不平衡量
    const currentImbalanceInput = document.getElementById('current-imbalance');
    if (currentImbalanceInput) {
        const currentImbalance = extractNumericValue(currentImbalanceInput.value);
        if (currentImbalance !== null) {
            parameters['current_unbalance'] = currentImbalance;
        }
    }
    
    // 电流波动度
    const currentFluctuationInput = document.getElementById('current-fluctuation');
    if (currentFluctuationInput) {
        const currentFluctuation = extractNumericValue(currentFluctuationInput.value);
        if (currentFluctuation !== null) {
            parameters['current_fluctuation'] = currentFluctuation;
        }
    }
    
    // 电压波动下限
    const voltageFluctuationMinInput = document.getElementById('voltage-fluctuation-min');
    if (voltageFluctuationMinInput) {
        const voltageFluctuationMin = extractNumericValue(voltageFluctuationMinInput.value);
        if (voltageFluctuationMin !== null) {
            parameters['voltage_fluctuation_min'] = voltageFluctuationMin;
        }
    }
    
    // 电压波动上限
    const voltageFluctuationMaxInput = document.getElementById('voltage-fluctuation-max');
    if (voltageFluctuationMaxInput) {
        const voltageFluctuationMax = extractNumericValue(voltageFluctuationMaxInput.value);
        if (voltageFluctuationMax !== null) {
            parameters['voltage_fluctuation_max'] = voltageFluctuationMax;
        }
    }
    
    // 频率波动下限
    const frequencyFluctuationMinInput = document.getElementById('frequency-fluctuation-min');
    if (frequencyFluctuationMinInput) {
        const frequencyFluctuationMin = extractNumericValue(frequencyFluctuationMinInput.value);
        if (frequencyFluctuationMin !== null) {
            parameters['frequency_fluctuation_min'] = frequencyFluctuationMin;
        }
    }
    
    // 频率波动上限
    const frequencyFluctuationMaxInput = document.getElementById('frequency-fluctuation-max');
    if (frequencyFluctuationMaxInput) {
        const frequencyFluctuationMax = extractNumericValue(frequencyFluctuationMaxInput.value);
        if (frequencyFluctuationMax !== null) {
            parameters['frequency_fluctuation_max'] = frequencyFluctuationMax;
        }
    }
    
    // ========== 主轴负载能力参数 ==========
    // 实测主轴最大功率
    const measuredMaxPowerInput = document.getElementById('power-actual');
    if (measuredMaxPowerInput) {
        const measuredMaxPower = extractNumericValue(measuredMaxPowerInput.value);
        if (measuredMaxPower !== null) {
            parameters['measured_max_power'] = measuredMaxPower;
        }
    }
    
    // 设计主轴最大功率
    const designMaxPowerInput = document.getElementById('power-design');
    if (designMaxPowerInput) {
        const designMaxPower = extractNumericValue(designMaxPowerInput.value);
        if (designMaxPower !== null) {
            parameters['design_max_power'] = designMaxPower;
        }
    }
    
    // 切削振动速度1
    const cuttingVibrationSpeed1Input = document.getElementById('power-vibration');
    if (cuttingVibrationSpeed1Input) {
        const cuttingVibrationSpeed1 = extractNumericValue(cuttingVibrationSpeed1Input.value);
        if (cuttingVibrationSpeed1 !== null) {
            parameters['cutting_vibration_speed1'] = cuttingVibrationSpeed1;
        }
    }
    
    // 实测主轴最大扭矩
    const measuredMaxTorqueInput = document.getElementById('torque-actual');
    if (measuredMaxTorqueInput) {
        const measuredMaxTorque = extractNumericValue(measuredMaxTorqueInput.value);
        if (measuredMaxTorque !== null) {
            parameters['measured_max_torque'] = measuredMaxTorque;
        }
    }
    
    // 设计主轴最大扭矩
    const designMaxTorqueInput = document.getElementById('torque-design');
    if (designMaxTorqueInput) {
        const designMaxTorque = extractNumericValue(designMaxTorqueInput.value);
        if (designMaxTorque !== null) {
            parameters['design_max_torque'] = designMaxTorque;
        }
    }
    
    // 切削振动速度2
    const cuttingVibrationSpeed2Input = document.getElementById('torque-vibration');
    if (cuttingVibrationSpeed2Input) {
        const cuttingVibrationSpeed2 = extractNumericValue(cuttingVibrationSpeed2Input.value);
        if (cuttingVibrationSpeed2 !== null) {
            parameters['cutting_vibration_speed2'] = cuttingVibrationSpeed2;
        }
    }
    
    // ========== 最大工件负重参数 ==========
    // 试验实际负重
    const actualLoadWeightInput = document.getElementById('max-load-actual');
    if (actualLoadWeightInput) {
        const actualLoadWeight = extractNumericValue(actualLoadWeightInput.value);
        if (actualLoadWeight !== null) {
            parameters['actual_load_weight'] = actualLoadWeight;
        }
    }
    
    // 最大设计重量
    const maxDesignWeightInput = document.getElementById('max-load-design');
    if (maxDesignWeightInput) {
        const maxDesignWeight = extractNumericValue(maxDesignWeightInput.value);
        if (maxDesignWeight !== null) {
            parameters['max_design_weight'] = maxDesignWeight;
        }
    }
    
    // 试验运行速度
    const actualLoadVelocityInput = document.getElementById('max-load-velocity-actual');
    if (actualLoadVelocityInput) {
        const actualLoadVelocity = extractNumericValue(actualLoadVelocityInput.value);
        if (actualLoadVelocity !== null) {
            parameters['actual_load_velocity'] = actualLoadVelocity;
        }
    }
    
    // 最大设计速度
    const maxDesignVelocityInput = document.getElementById('max-load-velocity-design');
    if (maxDesignVelocityInput) {
        const maxDesignVelocity = extractNumericValue(maxDesignVelocityInput.value);
        if (maxDesignVelocity !== null) {
            parameters['max_design_velocity'] = maxDesignVelocity;
        }
    }
    
    // 切削振动速度3
    const cuttingVibrationSpeed3Input = document.getElementById('max-load-vibration');
    if (cuttingVibrationSpeed3Input) {
        const cuttingVibrationSpeed3 = extractNumericValue(cuttingVibrationSpeed3Input.value);
        if (cuttingVibrationSpeed3 !== null) {
            parameters['cutting_vibration_speed3'] = cuttingVibrationSpeed3;
        }
    }
    
    // ========== 切削抗振性参数 ==========
    // 最大切削宽度
    const maxCuttingWidthInput = document.getElementById('max-cutting-width');
    if (maxCuttingWidthInput) {
        const maxCuttingWidth = extractNumericValue(maxCuttingWidthInput.value);
        if (maxCuttingWidth !== null) {
            parameters['max_cutting_width'] = maxCuttingWidth;
        }
    }
    
    // 刀具直径
    const toolDiameterInput = document.getElementById('tool-diameter');
    if (toolDiameterInput) {
        const toolDiameter = extractNumericValue(toolDiameterInput.value);
        if (toolDiameter !== null) {
            parameters['tool_diameter'] = toolDiameter;
        }
    }
    
    // 切削振动速度4 (铣削类或车削类)
    // 先尝试收集铣削类的切削振动速度V
    const cuttingVibrationSpeed4Input = document.getElementById('cutting-vibration');
    if (cuttingVibrationSpeed4Input) {
        const cuttingVibrationSpeed4 = extractNumericValue(cuttingVibrationSpeed4Input.value);
        if (cuttingVibrationSpeed4 !== null) {
            parameters['cutting_vibration_speed4'] = cuttingVibrationSpeed4;
        }
    }
    
    // 如果铣削类没有值，尝试收集车削类-切削长度方案的切削振动速度V
    if (!parameters['cutting_vibration_speed4']) {
        const cuttingVibrationTurningInput = document.getElementById('cutting-vibration-turning');
        if (cuttingVibrationTurningInput) {
            const cuttingVibrationTurning = extractNumericValue(cuttingVibrationTurningInput.value);
            if (cuttingVibrationTurning !== null) {
                parameters['cutting_vibration_speed4'] = cuttingVibrationTurning;
            }
        }
    }
    
    // 如果还没有值，尝试收集车削类-长径比方案的切削振动速度V
    if (!parameters['cutting_vibration_speed4']) {
        const cuttingVibrationRatioInput = document.getElementById('cutting-vibration-ratio');
        if (cuttingVibrationRatioInput) {
            const cuttingVibrationRatio = extractNumericValue(cuttingVibrationRatioInput.value);
            if (cuttingVibrationRatio !== null) {
                parameters['cutting_vibration_speed4'] = cuttingVibrationRatio;
            }
        }
    }
    
    // 最大切削长度
    const maxCuttingLengthInput = document.getElementById('max-cutting-length');
    if (maxCuttingLengthInput) {
        const maxCuttingLength = extractNumericValue(maxCuttingLengthInput.value);
        if (maxCuttingLength !== null) {
            parameters['max_cutting_length'] = maxCuttingLength;
        }
    }
    
    // 预期切削长度
    const expectedCuttingLengthInput = document.getElementById('expected-cutting-length');
    if (expectedCuttingLengthInput) {
        const expectedCuttingLength = extractNumericValue(expectedCuttingLengthInput.value);
        if (expectedCuttingLength !== null) {
            parameters['expected_cutting_length'] = expectedCuttingLength;
        }
    }
    
    // 最大径长比
    const maxLengthDiameterRatioInput = document.getElementById('max-length-diameter-ratio');
    if (maxLengthDiameterRatioInput) {
        const maxLengthDiameterRatio = extractNumericValue(maxLengthDiameterRatioInput.value);
        if (maxLengthDiameterRatio !== null) {
            parameters['max_length_diameter_ratio'] = maxLengthDiameterRatio;
        }
    }
    
    // 设计径长比
    const designLengthDiameterRatioInput = document.getElementById('design-length-diameter-ratio');
    if (designLengthDiameterRatioInput) {
        const designLengthDiameterRatio = extractNumericValue(designLengthDiameterRatioInput.value);
        if (designLengthDiameterRatio !== null) {
            parameters['design_length_diameter_ratio'] = designLengthDiameterRatio;
        }
    }
    
    return parameters;
}

// ========== 可靠性模块数据收集函数 ==========

/**
 * 收集可靠性模块参数
 * @returns {object} 参数字典
 */
function collectReliabilityParameters() {
    const parameters = {};
    const currentLevel3Title = window.currentLevel3Title || '';
    
    // ========== MTBF（平均故障间隔时间）参数 ==========
    if (currentLevel3Title === '平均故障间隔时间') {
        // 总运行时间 T1
        const totalRunTimeInput = document.getElementById('total-run-time');
        if (totalRunTimeInput) {
            const totalRunTime = extractNumericValue(totalRunTimeInput.value);
            if (totalRunTime !== null) {
                parameters['total_run_time'] = totalRunTime;
            }
        }
        
        // 故障次数 N
        const faultCountInput = document.getElementById('fault-count');
        if (faultCountInput) {
            const faultCount = extractNumericValue(faultCountInput.value);
            if (faultCount !== null) {
                parameters['fault_count'] = parseInt(faultCount);
            }
        }
    }
    
    // ========== MTTR（平均修复时间）参数 ==========
    else if (currentLevel3Title === '平均修复时间') {
        // 修复时间列表
        const repairTimeInputs = document.querySelectorAll('#repair-time-table-body input[type="number"]');
        const repairTimes = [];
        repairTimeInputs.forEach(input => {
            const value = extractNumericValue(input.value);
            // 收集所有值，包括null（空值），保持样本数量一致
            repairTimes.push(value !== null ? value : 0);
        });
        
        if (repairTimes.length > 0) {
            // 直接传递数组对象，不使用JSON.stringify
            parameters['repair_time_values'] = repairTimes;
        }
    }
    
    // ========== 当量故障率参数 ==========
    else if (currentLevel3Title === '当量故障率') {
        // 致命故障数 A
        const fatalFailureInput = document.getElementById('fatal-failure-count');
        if (fatalFailureInput) {
            const fatalFailure = extractNumericValue(fatalFailureInput.value);
            if (fatalFailure !== null) {
                parameters['fatal_failure'] = parseInt(fatalFailure);
            }
        }
        
        // 严重故障数 B
        const seriousFailureInput = document.getElementById('serious-failure-count');
        if (seriousFailureInput) {
            const seriousFailure = extractNumericValue(seriousFailureInput.value);
            if (seriousFailure !== null) {
                parameters['serious_failure'] = parseInt(seriousFailure);
            }
        }
        
        // 一般故障数 C
        const generalFailureInput = document.getElementById('general-failure-count');
        if (generalFailureInput) {
            const generalFailure = extractNumericValue(generalFailureInput.value);
            if (generalFailure !== null) {
                parameters['general_failure'] = parseInt(generalFailure);
            }
        }
        
        // 运行时间 T2
        const operationTimeInput = document.getElementById('operation-time');
        if (operationTimeInput) {
            const operationTime = extractNumericValue(operationTimeInput.value);
            if (operationTime !== null) {
                parameters['operation_time'] = operationTime;
            }
        }
    }
    
    // ========== 加工一致性参数 ==========
    else if (currentLevel3Title === '加工一致性') {
        // 标准差 σ
        const sigmaInput = document.getElementById('sigma-value');
        if (sigmaInput) {
            const sigma = extractNumericValue(sigmaInput.value);
            if (sigma !== null) {
                parameters['standard_deviation'] = sigma;
            }
        }
        
        // 均值 μ
        const muInput = document.getElementById('mu-value');
        if (muInput) {
            const mu = extractNumericValue(muInput.value);
            if (mu !== null) {
                parameters['mean_value'] = mu;
            }
        }
    }
    
    // ========== 加工精度保持性参数 ==========
    else if (currentLevel3Title === '加工精度保持性') {
        // 原始精度 φ_I
        const originalPrecisionInput = document.getElementById('original-precision');
        if (originalPrecisionInput) {
            const originalPrecision = extractNumericValue(originalPrecisionInput.value);
            if (originalPrecision !== null) {
                parameters['original_precision'] = originalPrecision;
            }
        }
        
        // 失效精度 φ_F
        const failurePrecisionInput = document.getElementById('failure-precision');
        if (failurePrecisionInput) {
            const failurePrecision = extractNumericValue(failurePrecisionInput.value);
            if (failurePrecision !== null) {
                parameters['failure_precision'] = failurePrecision;
            }
        }
        
        // 初始精度 P_0
        const initialPrecisionInput = document.getElementById('initial-precision');
        if (initialPrecisionInput) {
            const initialPrecision = extractNumericValue(initialPrecisionInput.value);
            if (initialPrecision !== null) {
                parameters['initial_precision'] = initialPrecision;
            }
        }
    }
    
    // ========== MTTF（平均首次故障时间）参数 ==========
    else if (currentLevel3Title === '平均首次故障时间') {
        // 故障时间列表
        const failureTimeInputs = document.querySelectorAll('#failure-time-table-body input[type="number"]');
        const failureTimes = [];
        failureTimeInputs.forEach(input => {
            const value = extractNumericValue(input.value);
            // 收集所有值，包括null（空值），保持样本数量一致
            failureTimes.push(value !== null ? value : 0);
        });
        
        if (failureTimes.length > 0) {
            // 直接传递数组对象，不使用JSON.stringify
            parameters['failure_time_values'] = failureTimes;
        }
    }
    
    return parameters;
}

// ========== 智能化模块数据收集函数 ==========

/**
 * 收集智能化模块参数
 * @returns {object} 参数字典
 */
function collectIntelligenceParameters() {
    const parameters = {};
    
    // 收集checkbox状态和核心特征名称
    const rows = document.querySelectorAll('#data-table-body tr');
    const checkboxStates = [];
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        
        // 由于第1列有rowspan，不同行的单元格数量不同
        // 有4个td的行：评价等级、核心特征、细化分值、是否满足
        // 有3个td的行：核心特征、细化分值、是否满足
        let featureName, checkbox;
        
        if (cells.length === 4) {
            // 第2列是核心特征名称，第4列是checkbox
            featureName = cells[1].textContent.trim();
            checkbox = cells[3].querySelector('input[type="checkbox"]');
        } else if (cells.length === 3) {
            // 第1列是核心特征名称，第3列是checkbox
            featureName = cells[0].textContent.trim();
            checkbox = cells[2].querySelector('input[type="checkbox"]');
        }
        
        if (featureName && checkbox) {
            checkboxStates.push({
                feature: featureName,
                satisfied: checkbox.checked
            });
        }
    });
    
    if (checkboxStates.length > 0) {
        parameters['intelligence_checkbox_states'] = checkboxStates;
    }
    
    return parameters;
}

// ========== 绿色化模块数据收集函数 ==========

/**
 * 收集绿色化模块参数
 * @returns {object} 参数字典
 */
function collectGreenParameters() {
    const parameters = {};
    
    // 资源循环与耗材参数
    const cuttingFluidQ = localStorage.getItem('cuttingFluidQ');
    const cuttingFluidP = localStorage.getItem('cuttingFluidP');
    const lubricantL = localStorage.getItem('lubricantL');
    const lubricantP = localStorage.getItem('lubricantP');
    const lubricantX = localStorage.getItem('lubricantX');
    
    if (cuttingFluidQ !== null) parameters['cutting_fluid_q'] = parseFloat(cuttingFluidQ);
    if (cuttingFluidP !== null) parameters['cutting_fluid_p'] = parseFloat(cuttingFluidP);
    if (lubricantL !== null) parameters['lubricant_l'] = parseFloat(lubricantL);
    if (lubricantP !== null) parameters['lubricant_p'] = parseFloat(lubricantP);
    if (lubricantX !== null) parameters['lubricant_x'] = parseFloat(lubricantX);
    
    // 轻量化设计项目
    const lightweightItemsStr = localStorage.getItem('lightweight_items');
    if (lightweightItemsStr) {
        try {
            const lightweightItems = JSON.parse(lightweightItemsStr);
            if (Array.isArray(lightweightItems) && lightweightItems.length > 0) {
                parameters['lightweight_items'] = lightweightItems;
            }
        } catch (e) {
            console.error('解析轻量化设计项目失败:', e);
        }
    }
    
    // 能源参数
    const estValue = localStorage.getItem('estValue');
    const euValue = localStorage.getItem('euValue');
    const ecValue = localStorage.getItem('ecValue');
    const nValue = localStorage.getItem('nValue');
    const vValue = localStorage.getItem('vValue');
    
    if (estValue !== null) parameters['est_value'] = parseFloat(estValue);
    if (euValue !== null) parameters['eu_value'] = parseFloat(euValue);
    if (ecValue !== null) parameters['ec_value'] = parseFloat(ecValue);
    if (nValue !== null) parameters['n_value'] = parseFloat(nValue);
    if (vValue !== null) parameters['v_value'] = parseFloat(vValue);
    
    return parameters;
}

// ========== 通用数据收集函数 ==========

/**
 * 根据当前页面收集参数
 * @returns {object} 参数字典
 */
function collectCurrentPageParameters() {
    const currentLevel3Title = window.currentLevel3Title || '';
    
    let parameters = {};
    let moduleName = '未知模块';
    
    // 根据当前页面标题选择对应的数据收集函数
    if (currentLevel3Title === '位置精度') {
        parameters = collectPositionAccuracyParameters();
        moduleName = '位置精度';
    } else if (currentLevel3Title === '工件几何精度') {
        parameters = collectWorkpieceGeometryAccuracyParameters();
        moduleName = '工件几何精度';
    } else if (currentLevel3Title === '进给轴精度') {
        parameters = collectFeedAxisAccuracyParameters();
        moduleName = '进给轴精度';
    } else if (currentLevel3Title === '主轴精度') {
        parameters = collectSpindleAccuracyParameters();
        moduleName = '主轴精度';
    } else if (currentLevel3Title === '工作台精度') {
        parameters = collectWorktableAccuracyParameters();
        moduleName = '工作台精度';
    } else if (currentLevel3Title === '加工分散性' || currentLevel3Title === '加工效率') {
        parameters = collectPerformanceParameters();
        moduleName = '性能模块';
    } else if (currentLevel3Title === '静刚度') {
        parameters = collectPerformanceParameters();
        moduleName = '性能模块';
    } else if (currentLevel3Title === '主轴' || currentLevel3Title === '噪声') {
        parameters = collectPerformanceParameters();
        moduleName = '性能模块';
    } else if (currentLevel3Title === '主轴温升热变形') {
        parameters = collectPerformanceParameters();
        moduleName = '性能模块';
    } else if (currentLevel3Title === '电流稳定性') {
        parameters = collectPerformanceParameters();
        moduleName = '性能模块';
    } else if (currentLevel3Title === '主轴负载能力' || currentLevel3Title === '最大工件负重' || currentLevel3Title === '切削抗振性') {
        parameters = collectPerformanceParameters();
        moduleName = '性能模块';
    } else if (currentLevel3Title.includes('性能')) {
        parameters = collectPerformanceParameters();
        moduleName = '性能模块';
    } else if (currentLevel3Title === '平均故障间隔时间' || currentLevel3Title === '平均修复时间' || 
               currentLevel3Title === '当量故障率' || currentLevel3Title === '加工一致性' || 
               currentLevel3Title === '加工精度保持性' || currentLevel3Title === '平均首次故障时间') {
        parameters = collectReliabilityParameters();
        moduleName = '可靠性模块';
    } else if (currentLevel3Title.includes('可靠性')) {
        parameters = collectReliabilityParameters();
        moduleName = '可靠性模块';
    } else if (currentLevel3Title.includes('智能化')) {
        parameters = collectIntelligenceParameters();
        moduleName = '智能化模块';
    } else if (currentLevel3Title.includes('绿色化')) {
        parameters = collectGreenParameters();
        moduleName = '绿色化模块';
    }
    
    return { parameters, moduleName };
}

/**
 * 保存当前页面参数到数据库
 * @returns {Promise} 保存结果
 */
async function saveCurrentPageParametersToDatabase() {
    const machineId = window.selectedMachineId;
    
    if (!machineId) {
        console.warn('未选择机床，无法保存参数');
        return { success: false, message: '未选择机床' };
    }
    
    const { parameters, moduleName } = collectCurrentPageParameters();
    
    if (Object.keys(parameters).length === 0) {
        console.log(`当前页面(${moduleName})没有需要保存的参数`);
        return { success: true, message: '没有需要保存的参数' };
    }
    
    try {
        const result = await updateMachineParameters(machineId, parameters, moduleName);
        return result;
    } catch (error) {
        console.error('保存参数失败:', error);
        return { success: false, message: error.message };
    }
}

// 导出函数（供其他模块使用）
window.MachineParameterCollector = {
    updateMachineParameters,
    collectPositionAccuracyParameters,
    collectWorkpieceGeometryAccuracyParameters,
    collectFeedAxisAccuracyParameters,
    collectSpindleAccuracyParameters,
    collectWorktableAccuracyParameters,
    collectPerformanceParameters,
    collectReliabilityParameters,
    collectIntelligenceParameters,
    collectGreenParameters,
    collectCurrentPageParameters,
    saveCurrentPageParametersToDatabase
};
