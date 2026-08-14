window.PrecisionModule = (function() {
    var _config = {
        moduleType: 'precision',
        level1Title: '精度',
        sampleCount: 1,
        machineCount: 0,
        machines: []
    };

    function getConfig() {
        return _config;
    }

    function getSampleCount() {
        return _config.sampleCount;
    }

    function setSampleCount(count) {
        _config.sampleCount = count;
        if (window.precisionModule) {
            window.precisionModule.sampleCount = count;
        }
    }

    function getMachineCount() {
        return _config.machineCount;
    }

    function getMachines() {
        return _config.machines;
    }

    async function loadMachineCount() {
        var urlParams = new URLSearchParams(window.location.search);
        var machineId = urlParams.get('machine_id');
        var isRegularUser = !!machineId;

        try {
            var response = await fetch('/evaluation/api/get-all-machines/?machine_type=machining_center', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('HTTP ' + response.status + ': ' + response.statusText);
            }

            var result = await response.json();

            if (result.success && result.machines) {
                _config.machineCount = result.machines.length;
                _config.machines = result.machines;

                if (isRegularUser) {
                    _config.sampleCount = 1;
                } else {
                    _config.sampleCount = result.machines.length;
                }

                if (window.precisionModule) {
                    window.precisionModule.machineCount = _config.machineCount;
                    window.precisionModule.machines = _config.machines;
                    window.precisionModule.sampleCount = _config.sampleCount;
                }
            }
        } catch (error) {
            console.error('[精度模块] 获取机床数量失败:', error);
        }
    }

    function isPrecisionIndicator(level1Title) {
        return level1Title === '精度';
    }

    function getIndicatorCount(level3Title) {
        var counts = {
            '进给轴精度': 4,
            '工作台精度': 3,
            '主轴精度': 5,
            '刀库精度': 2,
            '位置精度': 6,
            '工件几何精度': 2,
            '加工精度': 3,
            '几何精度': 4,
            '运动精度': 5,
            '主轴运动精度': 5,
            '多轴联动精度': 5,
            '传动精度': 4,
            '热误差': 3,
            '磨损精度': 2
        };
        return counts[level3Title] || 4;
    }

    function getTableHeaders(level3Title) {
        var headers = {
            '进给轴精度': ['组别', '直线度', '平行度', '角度误差', '垂直度'],
            '工作台精度': ['组别', '平面度', '直线度', 'T型槽平行度'],
            '主轴精度': ['组别', '主轴径向跳动', '主轴端面跳动', '主轴轴向窜动', '主轴锥孔径向跳动', '主轴周期性轴向窜动'],
            '刀库精度': ['组别', '刀库定位精度', '刀库重复定位精度'],
            '位置精度': ['组别', '重复定位精度', '定位精度', '平均位置偏移', '定位系统偏差', '反向间隙', '综合评分'],
            '工件几何精度': ['组别', '圆度/圆柱度', '位置度/同心度'],
            '运动精度': ['组别', '主轴运动精度', '多轴联动精度', '传动精度', '热误差', '磨损精度']
        };
        return headers[level3Title] || ['组别', '直线度', '平行度', '角度误差', '垂直度'];
    }

    function getTravelRangeIndex(axisTravel) {
        if (axisTravel <= 500) return 0;
        if (axisTravel <= 800) return 1;
        if (axisTravel <= 1250) return 2;
        if (axisTravel <= 2000) return 3;
        return 4;
    }

    function getLinearityTolerance(axisTravel) {
        if (axisTravel <= 500) return 0.010;
        if (axisTravel <= 800) return 0.015;
        if (axisTravel <= 1250) return 0.020;
        if (axisTravel <= 2000) return 0.025;
        return 0.030;
    }

    function getRepeatPositioningTolerance(axisTravel) {
        if (axisTravel <= 500) return 0.012;
        if (axisTravel <= 800) return 0.015;
        if (axisTravel <= 1250) return 0.018;
        if (axisTravel <= 2000) return 0.020;
        return 0.025;
    }

    // ========== 加工中心位置精度允差硬编码数据 ==========
    // 数据来源：tolerance_management.html 中的"位置精度允差 - 加工中心"表格
    var mcPositionToleranceData = {
        '双向定位精度A': [0.022, 0.025, 0.032, 0.042, 28.000],
        '单向定位精度（正向）A': [0.016, 0.020, 0.025, 0.030, 22.000],
        '单向定位精度（反向）A↓': [0.016, 0.020, 0.025, 0.030, 22.000],
        '双向重复定位精度R': [0.012, 0.015, 0.018, 0.020, 16.000],
        '单向重复定位精度（正向）R↑': [0.006, 0.008, 0.010, 0.013, 8.000],
        '单向重复定位精度（反向）R↓': [0.006, 0.008, 0.010, 0.013, 8.000],
        '轴线的反向差值B': [0.010, 0.010, 0.012, 0.012, 12.000],
        '双向定位系统偏差E': [0.015, 0.018, 0.022, 0.030, 20.000],
        '单向定位系统偏差（正向）E↑': [0.010, 0.012, 0.015, 0.018, 14.000],
        '单向定位系统偏差（反向）E↓': [0.010, 0.012, 0.015, 0.018, 14.000],
        '轴线的平均双向位置偏差范围M': [0.010, 0.012, 0.015, 0.020, 12.000]
    };

    // ========== 加工中心加工精度允差硬编码数据 ==========
    // 数据来源：tolerance_management.html 中的"加工精度允差 - 加工中心"表格
    var mcProcessingToleranceData = {
        '圆柱度': [0.01, 0.015],
        '孔中心轴线与基准孔A的垂直度': [0.01, 0.015],
        '侧面的直线度': [0.01, 0.015],
        '相邻面与基准面B的垂直度': [0.01, 0.02],
        '相对面与基准面B的平行度': [0.01, 0.02],
        '侧面直线度': [0.010, 0.015],
        '侧面对基准B的倾斜度': [0.01, 0.02],
        '圆度': [0.015, 0.02],
        '外圆和内圆孔C的同心度': [0.025, 0.025],
        '斜面的直线度': [0.01, 0.015],
        '3°角斜面对基准B的倾斜度': [0.01, 0.02],
        '孔相对于内孔C的位置度': [0.05, 0.05],
        '内孔与外孔D的同心度': [0.02, 0.02]
    };

    function getPositioningTolerance(axisTravel) {
        var values = mcPositionToleranceData['双向定位精度A'];
        var rangeIndex = getTravelRangeIndex(axisTravel);
        if (rangeIndex < values.length - 1) {
            return values[rangeIndex];
        }
        return values[values.length - 2]; // 超出范围取最后一档
    }

    function getAveragePositionTolerance(axisTravel) {
        var values = mcPositionToleranceData['轴线的平均双向位置偏差范围M'];
        var rangeIndex = getTravelRangeIndex(axisTravel);
        if (rangeIndex < values.length - 1) {
            return values[rangeIndex];
        }
        return values[values.length - 2];
    }

    function getPositioningSystemDeviationTolerance(axisTravel) {
        var values = mcPositionToleranceData['双向定位系统偏差E'];
        var rangeIndex = getTravelRangeIndex(axisTravel);
        if (rangeIndex < values.length - 1) {
            return values[rangeIndex];
        }
        return values[values.length - 2];
    }

    function getBacklashTolerance(axisTravel) {
        var values = mcPositionToleranceData['轴线的反向差值B'];
        var rangeIndex = getTravelRangeIndex(axisTravel);
        if (rangeIndex < values.length - 1) {
            return values[rangeIndex];
        }
        return values[values.length - 2];
    }

    function getRotaryAxisTolerance(dataKey, defaultValue) {
        var values = mcPositionToleranceData[dataKey];
        if (values && values.length > 4) {
            return values[4]; // 第5个值为回转轴允差
        }
        return defaultValue;
    }

    function getParallelismTolerance(axisTravel) {
        if (axisTravel <= 500) return 0.020;
        if (axisTravel <= 800) return 0.025;
        if (axisTravel <= 1250) return 0.030;
        if (axisTravel <= 2000) return 0.040;
        return 0.050;
    }

    function getWorktableFlatnessTolerance(tableLength) {
        if (tableLength <= 500) return 0.020;
        if (tableLength <= 800) return 0.025;
        if (tableLength <= 1250) return 0.030;
        if (tableLength <= 2000) return 0.035;
        return 0.040;
    }

    function getProcessingTolerance(testItem, workpieceSize) {
        var values = mcProcessingToleranceData[testItem];
        if (values) {
            var sizeIndex = (workpieceSize === 160) ? 0 : 1;
            return values[sizeIndex];
        }
        return 0.01;
    }

    // 镗铣床专用允差计算方法
    
    /**
     * 获取镗铣床立柱移动直线度允差
     * 根据立柱测量范围计算
     * @param {number} columnRange - 立柱测量范围(mm)
     * @returns {number} 直线度允差值
     */
    function getBoringMillingColumnLinearityTolerance(columnRange) {
        if (columnRange <= 1000) return 0.020;
        return 0.030;
    }
    
    /**
     * 获取镗铣床工作台移动(X轴)直线度允差
     * 根据X轴测量范围计算
     * @param {number} xAxisRange - X轴测量范围(mm)
     * @returns {number} 直线度允差值
     */
    function getBoringMillingXAxisLinearityTolerance(xAxisRange) {
        if (xAxisRange <= 1000) return 0.020;
        if (xAxisRange <= 2000) return 0.030;
        if (xAxisRange <= 3000) return 0.040;
        return 0.050;
    }
    
    /**
     * 获取镗铣床主轴箱移动(Y轴)直线度允差
     * 根据Y轴测量范围计算
     * @param {number} yAxisRange - Y轴测量范围(mm)
     * @returns {number} 直线度允差值
     */
    function getBoringMillingYAxisLinearityTolerance(yAxisRange) {
        if (yAxisRange <= 1000) return 0.020;
        if (yAxisRange <= 2000) return 0.030;
        if (yAxisRange <= 3000) return 0.040;
        if (yAxisRange <= 4000) return 0.050;
        if (yAxisRange <= 5000) return 0.070;
        if (yAxisRange <= 6000) return 0.090;
        return 0.110;
    }
    
    /**
     * 获取镗铣床角度偏差允差
     * 根据测量范围计算
     * @param {number} axisRange - 轴测量范围(mm)
     * @returns {number} 角度偏差允差值
     */
    function getBoringMillingAngleTolerance(axisRange) {
        if (axisRange <= 4000) return 0.040;
        return 0.060;
    }
    
    /**
     * 获取镗铣床加工精度允差
     * 数据来源于 tolerance_management.html 中的"加工精度允差 - 镗铣床"表格
     * 按顺序返回：正方形(直线度、垂直度、平行度)、菱形(直线度、倾斜度)、圆度、镗孔位置度
     * @returns {object} 加工精度允差数据对象
     */
    function getBoringMillingProcessingTolerance() {
        return {
            squareLinearity: 0.020,
            squarePerpendicularity: 0.040,
            squareParallelism: 0.040,
            diamondLinearity: 0.020,
            diamondAngularity: 0.020,
            circularity: 0.040,
            holePosition: 0.050
        };
    }
    
    /**
     * 获取镗铣床工作台面对立柱移动的平行度允差
     * 根据立柱测量范围计算
     * @param {number} columnRange - 立柱测量范围(mm)
     * @returns {number} 平行度允差值
     */
    function getBoringMillingTableColumnParallelismTolerance(columnRange) {
        if (columnRange <= 1000) return 0.040;
        if (columnRange <= 2000) return 0.050;
        return 0.060;
    }
    
    /**
     * 获取镗铣床工作台面对X轴移动的平行度允差
     * 根据X轴测量范围计算
     * @param {number} xAxisRange - X轴测量范围(mm)
     * @returns {number} 平行度允差值
     */
    function getBoringMillingTableXAxisParallelismTolerance(xAxisRange) {
        if (xAxisRange <= 1000) return 0.040;
        if (xAxisRange <= 2000) return 0.050;
        return 0.060;
    }
    
    /**
     * 获取镗铣床工作台面平面度允差
     * 根据工作台长边长度计算
     * @param {number} worktableLength - 工作台长边长度(mm)
     * @returns {number} 平面度允差值
     */
    function getBoringMillingWorktableFlatnessTolerance(worktableLength) {
        if (worktableLength <= 1000) return 0.030;
        if (worktableLength <= 2000) return 0.040;
        if (worktableLength <= 3000) return 0.050;
        return 0.060;
    }
    
    /**
     * 获取镗轴径向跳动允差
     * 根据镗轴直径计算
     * @param {number} boringAxisDiameter - 镗轴直径(mm)
     * @returns {object} 径向跳动允差值 {near_spindle_end, away_from_spindle_end}
     */
    function getBoringAxisRadialRunoutTolerance(boringAxisDiameter) {
        if (!boringAxisDiameter || isNaN(parseFloat(boringAxisDiameter))) {
            return { near_spindle_end: 0.01, away_from_spindle_end: 0.015 };
        }
        const diameter = parseFloat(boringAxisDiameter);
        if (diameter <= 125) {
            return { near_spindle_end: 0.01, away_from_spindle_end: 0.015 };
        } else {
            return { near_spindle_end: 0.02, away_from_spindle_end: 0.03 };
        }
    }
    
    /**
     * 获取铣轴径向跳动允差
     * 根据铣轴直径计算
     * @param {number} millingAxisDiameter - 铣轴直径(mm)
     * @returns {number} 径向跳动允差值
     */
    function getMillingAxisRadialRunoutTolerance(millingAxisDiameter) {
        if (!millingAxisDiameter || isNaN(parseFloat(millingAxisDiameter))) {
            return 0.010;
        }
        const diameter = parseFloat(millingAxisDiameter);
        if (diameter <= 125) {
            return 0.010;
        } else {
            return 0.015;
        }
    }
    
    /**
     * 获取镗轴轴向窜动允差
     * 根据镗轴直径计算
     * @param {number} boringAxisDiameter - 镗轴直径(mm)
     * @returns {number} 轴向窜动允差值
     */
    function getBoringAxisAxialRunoutTolerance(boringAxisDiameter) {
        if (!boringAxisDiameter || isNaN(parseFloat(boringAxisDiameter))) {
            return 0.010;
        }
        const diameter = parseFloat(boringAxisDiameter);
        if (diameter <= 125) {
            return 0.010;
        } else {
            return 0.015;
        }
    }
    
    /**
     * 获取铣轴轴向窜动允差
     * 根据铣轴直径计算
     * @param {number} millingAxisDiameter - 铣轴直径(mm)
     * @returns {number} 轴向窜动允差值
     */
    function getMillingAxisAxialRunoutTolerance(millingAxisDiameter) {
        if (!millingAxisDiameter || isNaN(parseFloat(millingAxisDiameter))) {
            return 0.010;
        }
        const diameter = parseFloat(millingAxisDiameter);
        if (diameter <= 125) {
            return 0.010;
        } else {
            return 0.015;
        }
    }

    /**
     * 获取固定分度回转工作台的允差数据（用于ABC回转轴）
     * 数据来源于 tolerance_management.html 中的"位置精度允差 - 镗铣床"表格第5列
     * @returns {object} 允差数据对象（单位为″）
     */
    function getFixedIndexingRotaryTableTolerance() {
        return {
            positioningAccuracy: { a: 11.000, b: 11.000, c: 11.000 },
            repeatability: { a: 8.000, b: 8.000, c: 8.000 },
            backlash: { a: 6.000, b: 6.000, c: 6.000 },
            systemDeviation: { a: 6.000, b: 6.000, c: 6.000 },
            averagePositionDeviation: { a: 4.000, b: 4.000, c: 4.000 }
        };
    }

    function getArbitraryAngleRotaryTableTolerance() {
        return {
            positioningAccuracy: { a: 18.000, b: 18.000, c: 18.000 },
            repeatability: { a: 12.000, b: 12.000, c: 12.000 },
            backlash: { a: 10.000, b: 10.000, c: 10.000 },
            systemDeviation: { a: 14.000, b: 14.000, c: 14.000 },
            averagePositionDeviation: { a: 6.000, b: 6.000, c: 6.000 }
        };
    }

    /**
     * 根据工作台类型获取回转轴（ABC轴）位置精度允差（镗铣床专用）
     * @param {string} worktableType - 工作台类型
     * @returns {object} 完整的允差数据对象，包含a/b/c三个回转轴的允差（单位为″）
     */
    function getRotaryAxisToleranceByWorktableType(worktableType) {
        if (!worktableType) {
            return getFixedIndexingRotaryTableTolerance();
        }
        
        const type = worktableType.trim();
        
        if (type === '固定分度的回转工作台' || type === 'fixed_indexing') {
            return getFixedIndexingRotaryTableTolerance();
        } else if (type === '任意角度定位的回转工作台' || type === 'arbitrary_positioning') {
            return getArbitraryAngleRotaryTableTolerance();
        } else {
            return getFixedIndexingRotaryTableTolerance();
        }
    }

    /**
     * 根据测量范围获取位置精度允差（镗铣床专用）
     * 数据来源于 tolerance_management.html 中的"位置精度允差 - 镗铣床"表格
     * @param {number} measurementRange - 测量范围(mm)
     * @returns {object} 该测量范围对应的允差数据对象
     */
    function getPositioningToleranceByMeasurementRange(measurementRange) {
        const range = parseFloat(measurementRange) || 0;
        
        let rangeKey;
        if (range <= 500) {
            rangeKey = '≤500';
        } else if (range <= 1000) {
            rangeKey = '≤1000';
        } else {
            rangeKey = '≤2000';
        }
        
        const toleranceData = {
            '≤500': {
                positioningAccuracy: 0.020,
                repeatability: 0.014,
                backlash: 0.005,
                systemDeviation: 0.012,
                averagePositionDeviation: 0.010
            },
            '≤1000': {
                positioningAccuracy: 0.025,
                repeatability: 0.018,
                backlash: 0.006,
                systemDeviation: 0.015,
                averagePositionDeviation: 0.013
            },
            '≤2000': {
                positioningAccuracy: 0.030,
                repeatability: 0.020,
                backlash: 0.008,
                systemDeviation: 0.018,
                averagePositionDeviation: 0.015
            }
        };
        
        return toleranceData[rangeKey];
    }

    /**
     * 根据各轴测量范围获取镗铣床位置精度允差（镗铣床专用）
     * @param {number} xRange - X轴测量范围(mm)，工作台X轴测量范围
     * @param {number} yRange - Y轴测量范围(mm)，主轴箱Y轴测量范围
     * @param {number} zRange - Z轴测量范围(mm)，Z轴测量范围
     * @param {number} wRange - W轴测量范围(mm)，立柱测量范围(COLUMN_MEASUREMENT_RANGE)
     * @returns {object} 完整的允差数据对象，包含x/y/z/w四个轴的允差
     */
    function getBoringMillingPositioningTolerance(xRange, yRange, zRange, wRange) {
        const xTolerance = getPositioningToleranceByMeasurementRange(xRange);
        const yTolerance = getPositioningToleranceByMeasurementRange(yRange);
        const zTolerance = getPositioningToleranceByMeasurementRange(zRange);
        const wTolerance = wRange ? getPositioningToleranceByMeasurementRange(wRange) : zTolerance;
        
        return {
            positioningAccuracy: { 
                x: xTolerance.positioningAccuracy, 
                y: yTolerance.positioningAccuracy, 
                z: zTolerance.positioningAccuracy, 
                w: wTolerance.positioningAccuracy 
            },
            repeatability: { 
                x: xTolerance.repeatability, 
                y: yTolerance.repeatability, 
                z: zTolerance.repeatability, 
                w: wTolerance.repeatability 
            },
            backlash: { 
                x: xTolerance.backlash, 
                y: yTolerance.backlash, 
                z: zTolerance.backlash, 
                w: wTolerance.backlash 
            },
            systemDeviation: { 
                x: xTolerance.systemDeviation, 
                y: yTolerance.systemDeviation, 
                z: zTolerance.systemDeviation, 
                w: wTolerance.systemDeviation 
            },
            averagePositionDeviation: { 
                x: xTolerance.averagePositionDeviation, 
                y: yTolerance.averagePositionDeviation, 
                z: zTolerance.averagePositionDeviation, 
                w: wTolerance.averagePositionDeviation 
            }
        };
    }

    /**
     * 根据工作台类型获取位置精度允差（已废弃，保留兼容性）
     * @param {string} worktableType - 工作台类型
     * @returns {object} 完整的允差数据对象
     */
    function getPositioningToleranceByWorktableType(worktableType) {
        return getFixedIndexingRotaryTableTolerance();
    }

    function init() {
        window.currentModuleType = 'precision';
    }

    return {
        getConfig: getConfig,
        getSampleCount: getSampleCount,
        setSampleCount: setSampleCount,
        getMachineCount: getMachineCount,
        getMachines: getMachines,
        loadMachineCount: loadMachineCount,
        isPrecisionIndicator: isPrecisionIndicator,
        getIndicatorCount: getIndicatorCount,
        getTableHeaders: getTableHeaders,
        getTravelRangeIndex: getTravelRangeIndex,
        getLinearityTolerance: getLinearityTolerance,
        getRepeatPositioningTolerance: getRepeatPositioningTolerance,
        getPositioningTolerance: getPositioningTolerance,
        getAveragePositionTolerance: getAveragePositionTolerance,
        getPositioningSystemDeviationTolerance: getPositioningSystemDeviationTolerance,
        getBacklashTolerance: getBacklashTolerance,
        getRotaryAxisTolerance: getRotaryAxisTolerance,
        getParallelismTolerance: getParallelismTolerance,
        getWorktableFlatnessTolerance: getWorktableFlatnessTolerance,
        getProcessingTolerance: getProcessingTolerance,
        // 镗铣床专用
        getBoringMillingColumnLinearityTolerance: getBoringMillingColumnLinearityTolerance,
        getBoringMillingXAxisLinearityTolerance: getBoringMillingXAxisLinearityTolerance,
        getBoringMillingYAxisLinearityTolerance: getBoringMillingYAxisLinearityTolerance,
        getBoringMillingAngleTolerance: getBoringMillingAngleTolerance,
        getBoringMillingTableColumnParallelismTolerance: getBoringMillingTableColumnParallelismTolerance,
        getBoringMillingTableXAxisParallelismTolerance: getBoringMillingTableXAxisParallelismTolerance,
        getBoringMillingWorktableFlatnessTolerance: getBoringMillingWorktableFlatnessTolerance,
        // 镗铣床加工精度
        getBoringMillingProcessingTolerance: getBoringMillingProcessingTolerance,
        // 镗铣床主轴精度（直径）
        getBoringAxisRadialRunoutTolerance: getBoringAxisRadialRunoutTolerance,
        getMillingAxisRadialRunoutTolerance: getMillingAxisRadialRunoutTolerance,
        getBoringAxisAxialRunoutTolerance: getBoringAxisAxialRunoutTolerance,
        getMillingAxisAxialRunoutTolerance: getMillingAxisAxialRunoutTolerance,
        // 镗铣床XYZ线性轴
        getPositioningToleranceByMeasurementRange: getPositioningToleranceByMeasurementRange,
        getBoringMillingPositioningTolerance: getBoringMillingPositioningTolerance,
        // 镗铣床ABC回转轴
        getRotaryAxisToleranceByWorktableType: getRotaryAxisToleranceByWorktableType,
        // 已废弃，保留兼容性
        getPositioningToleranceByWorktableType: getPositioningToleranceByWorktableType,
        getFixedIndexingRotaryTableTolerance: getFixedIndexingRotaryTableTolerance,
        getArbitraryAngleRotaryTableTolerance: getArbitraryAngleRotaryTableTolerance,
        init: init
    };
})();
