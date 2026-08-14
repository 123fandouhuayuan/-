/**
 * comprehensive-weight-calculation.js - 精度分数计算JavaScript文件
 *
 * 功能说明:
 * - 实现机床精度评价的精度分数计算功能
 * - 集成AHP（层次分析法和熵权法两种权重计算方法
 * - 支持自定义AHP权重和熵权法的融合比例（alpha参数）
 * - 处理机床指标的二级、三级权重体系
 * - 从localStorage恢复用户评价数据
 * - 支持计算结果的保存和导出
 *
 * 主要配置:
 * - CONFIG: 指标分类、排序、三级指标映射关系等配置
 * - STATE: 用户角色、计算结果、模拟数据等状态管理
 * - DOM: 页面DOM元素缓存
 */

(function() {
    'use strict';

    // ============================================
    // 配置常量：定义指标分类和排序结构
    // - DEFAULT_ALPHA: AHP与熵权法融合比例的默认值(0.5表示各占50%)
    // - INDICATOR_ORDER: 三级指标映射到四级指标的顺序
    // - TERTIARY_ORDER: 二级指标对应的三级指标列表
    // - SECONDARY_KEYS: 四个二级指标分类
    // ============================================
    const CONFIG = {
        DEFAULT_ALPHA: 0.5,
        // 加工中心指标配置
        MACHINING_CENTER: {
            INDICATOR_ORDER: {
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
            },
            TERTIARY_ORDER: {
                '几何精度': ['进给轴精度', '工作台精度', '主轴精度', '刀库精度'],
                '位置精度': ['重复定位精度', '定位精度', '平均位置偏移', '定位系统偏差', '最小分辨率', '反向间隙(差值)'],
                '加工精度': ['微观几何形状误差', '加工分散性', '工件几何精度'],
                '运动精度': ['主轴运动精度', '多轴联动精度', '传动精度', '热误差', '磨损精度']
            },
            SECONDARY_KEYS: ['几何精度', '位置精度', '加工精度', '运动精度']
        },
        // 镗铣床指标配置
        BORING_MILLING: {
            INDICATOR_ORDER: {
                '进给轴精度': ['直线度', '平行度', '角度误差', '垂直度'],
                '工作台精度': ['平面度', '平行度', 'T型槽平行度'],  // 镗铣床：直线度->平行度
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
            },
            TERTIARY_ORDER: {
                '几何精度': ['进给轴精度', '工作台精度', '主轴精度', '刀库精度'],
                '位置精度': ['重复定位精度', '定位精度', '平均位置偏移', '定位系统偏差', '最小分辨率', '反向间隙(差值)'],
                '加工精度': ['微观几何形状误差', '加工分散性', '工件几何精度'],
                '运动精度': ['主轴运动精度', '多轴联动精度', '传动精度', '热误差', '磨损精度']
            },
            SECONDARY_KEYS: ['几何精度', '位置精度', '加工精度', '运动精度']
        }
    };

    // 获取当前机床类型的配置
    function getCurrentConfig() {
        const machineType = STATE.currentMachineType || 'machining_center';
        if (machineType === 'boring_milling_machine') {
            return CONFIG.BORING_MILLING;
        }
        return CONFIG.MACHINING_CENTER;
    }

    // 根据当前机床类型获取指标名称列表
    function getIndicatorsForCurrentMachineType(secondary, tertiary) {
        const currentConfig = getCurrentConfig();
        
        // 如果三级指标在配置中有定义，使用配置中的指标顺序
        if (currentConfig.INDICATOR_ORDER[tertiary]) {
            return currentConfig.INDICATOR_ORDER[tertiary];
        }
        
        // 否则返回空数组或默认指标
        return STATE.mockData.indicators[secondary][tertiary] || [];
    }

    // ============================================
    // 状态管理：存储全局状态数据
    // - isUserAdmin: 当前用户是否为管理员
    // - currentMachineType: 当前选中的机床类型
    // - currentCalculationResult: 当前计算结果缓存
    // - mockData: 模拟数据存储（指标、AHP权重、熵权、测量值等）
    // ============================================
    const STATE = {
        isUserAdmin: false,
        currentMachineType: 'machining_center',  // 默认加工中心
        currentCalculationResult: null,
        mockData: {
            indicators: {
                '几何精度': {
                    '进给轴精度': ['直线度', '平行度', '角度误差', '垂直度'],
                    '工作台精度': ['平面度', '直线度', 'T型槽平行度'],
                    '主轴精度': ['圆度', '同轴度', '主轴径向跳动', '主轴端面跳动', '主轴轴向窜动'],
                    '刀库精度': ['刀库定位精度', '刀库重复定位精度']
                },
                '位置精度': {
                    '重复定位精度': [],
                    '定位精度': [],
                    '平均位置偏移': [],
                    '定位系统偏差': [],
                    '最小分辨率': [],
                    '反向间隙(差值)': []
                },
                '加工精度': {
                    '微观几何形状误差': ['表面粗糙度'],
                    '加工分散性': ['加工工序能力'],
                    '工件几何精度': ['尺寸精度', '形状精度']
                },
                '运动精度': {
                    '主轴运动精度': ['主轴径向误差', '主轴轴向误差', '主轴角度误差', '主轴启停响应时间', '主轴高速旋转时的动平衡精度'],
                    '多轴联动精度': ['平面圆度误差', '多轴联动同步误差', '轮廓精度', '空间精度', '动态RTCP精度'],
                    '传动精度': ['直线圆弧插补轨迹误差', '伺服跟随误差', '高速移动过冲滞后', '低速移动爬行'],
                    '热误差': ['进给轴热误差', '主轴径向误差', '主轴轴向误差'],
                    '磨损精度': ['刀具磨损', '砂轮磨损']
                }
            },
            ahpWeights: {},
            entropyWeights: {},
            measuredValues: {},
            standardValues: {},
            tolerances: {}
        }
    };

    // ============================================
    // DOM元素缓存：存储页面常用元素的引用
    // 用于提高性能，避免重复查询DOM
    // ============================================
    const DOM = {
        machineSelect: null,
        alphaInput: null,
        calculateBtn: null,
        saveBtn: null,
        saveAlphaBtn: null,
        resultContainer: null,
        processContainer: null,
        weightSummaryContainer: null,
        weightSummaryCard: null
    };

    // ============================================
    // 初始化函数：页面加载时调用的入口函数
    // 依次执行：用户角色初始化 -> DOM缓存 -> 事件绑定 -> URL参数处理
    // ============================================
    function init() {
        initializeUserRole();
        cacheDOMElements();
        bindEventListeners();
        handleURLParameters();
        loadAlphaCoefficient();
        console.log('页面初始化完成');
    }

    // ============================================
    // 初始化用户角色
    // 从页面DOM元素读取用户角色数据，判断是否为管理员
    // ============================================
    function initializeUserRole() {
        const userData = document.getElementById('user-role-data');
        if (userData) {
            STATE.isUserAdmin = userData.getAttribute('data-is-admin') === 'true';
        }
    }

    // ============================================
    // 缓存DOM元素
    // 将页面常用元素缓存到DOM对象中，避免重复查询
    // ============================================
    function cacheDOMElements() {
        DOM.machineSelect = document.getElementById('machine-select');
        DOM.alphaInput = document.getElementById('alpha-input');
        DOM.calculateBtn = document.getElementById('calculate-btn');
        DOM.saveBtn = document.getElementById('save-result-btn');
        DOM.saveAlphaBtn = document.getElementById('save-alpha-btn');
        DOM.resultContainer = document.getElementById('result-container');
        DOM.processContainer = document.getElementById('process-container');
        DOM.weightSummaryContainer = document.getElementById('weight-summary-container');
        DOM.weightSummaryCard = document.getElementById('weight-summary-card');

        if (!DOM.calculateBtn) {
            console.error('计算按钮不存在！');
            return;
        }
    }

    // ============================================
    // 绑定事件监听器
    // 为计算、保存、下一步等按钮绑定点击事件
    // ============================================
    function bindEventListeners() {
        if (DOM.calculateBtn) {
            DOM.calculateBtn.addEventListener('click', handleCalculateClick);
        }

        if (DOM.saveBtn) {
            DOM.saveBtn.addEventListener('click', handleSaveClick);
        }

        if (DOM.saveAlphaBtn) {
            DOM.saveAlphaBtn.addEventListener('click', handleSaveAlphaClick);
        }

        if (DOM.machineSelect) {
            DOM.machineSelect.addEventListener('change', handleMachineSelectChange);
        }
    }

    // ============================================
    // 处理URL参数
    // 如果URL中包含machine_id参数，自动选中对应机床
    // ============================================
    function handleURLParameters() {
        const urlParams = new URLSearchParams(window.location.search);
        const machineId = urlParams.get('machine_id');

        if (machineId && DOM.machineSelect) {
            DOM.machineSelect.value = machineId;
            DOM.machineSelect.dispatchEvent(new Event('change'));
        }
    }

    // ============================================
    // 机床选择变更处理
    // 切换时更新表单元素的验证状态样式，并根据机床类型更新指标配置
    // ============================================
    function handleMachineSelectChange() {
        const value = this.value;
        if (value) {
            this.classList.add('is-valid');
            this.classList.remove('is-invalid');
            
            // 获取选中的机床类型
            const selectedOption = this.options[this.selectedIndex];
            const machineType = selectedOption.getAttribute('data-machine-type') || 'machining_center';
            
            // 更新当前机床类型状态
            STATE.currentMachineType = machineType;
            console.log(`[机床选择] 机床ID: ${value}, 机床类型: ${machineType}`);
            
            // 如果已经显示计算结果，更新步骤显示
            if (STATE.currentCalculationResult) {
                updateProcessDisplay();
            }
        } else {
            this.classList.add('is-invalid');
            this.classList.remove('is-valid');
            STATE.currentMachineType = 'machining_center';  // 重置为默认值
        }
    }
    
    // ============================================
    // 更新计算过程显示
    // 根据当前机床类型重新渲染步骤一、二、三
    // ============================================
    function updateProcessDisplay() {
        if (!STATE.currentCalculationResult) return;
        
        const alpha = parseFloat(DOM.alphaInput.value) || CONFIG.DEFAULT_ALPHA;
        const ahpWeight = alpha;
        const entropyWeight = 1 - alpha;
        
        // 重新构建计算过程HTML
        const processHtml = buildProcessHtml(ahpWeight, entropyWeight, STATE.currentCalculationResult);
        DOM.processContainer.innerHTML = processHtml;
        
        console.log(`[过程显示更新] 已切换为${STATE.currentMachineType === 'boring_milling_machine' ? '镗铣床' : '加工中心'}指标配置`);
    }

    // ============================================
    // 计算按钮点击处理
    // 触发精度分数计算流程
    // ============================================
    function handleCalculateClick(e) {
        e.preventDefault();
        calculateComprehensiveWeight();
    }

    // ============================================
    // 保存按钮点击处理
    // 触发计算结果的保存操作
    // ============================================
    function handleSaveClick(e) {
        e.preventDefault();
        saveCalculationResult();
    }

    // ============================================
    // 保存组合系数按钮点击处理
    // 验证并保存组合系数到数据库，同时设置为全局默认值
    // ============================================
    function handleSaveAlphaClick(e) {
        e.preventDefault();

        const alphaInput = DOM.alphaInput;
        const alphaValue = parseFloat(alphaInput.value);

        // 验证alpha值
        if (isNaN(alphaValue) || alphaValue < 0 || alphaValue > 1) {
            alphaInput.classList.add('is-invalid');
            alphaInput.classList.remove('is-valid');
            showAlphaSaveResult(false, '组合系数必须在0-1之间');
            return;
        }

        alphaInput.classList.remove('is-invalid');
        alphaInput.classList.add('is-valid');

        // 显示加载状态
        const saveBtn = DOM.saveAlphaBtn;
        const originalText = saveBtn.innerHTML;
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm mr-2"></span>保存中...';

        // 发送API请求
        saveAlphaCoefficient(alphaValue)
            .then(result => {
                if (result.success) {
                    showAlphaSaveResult(true, '组合系数已保存并设为默认值');
                } else {
                    showAlphaSaveResult(false, result.message || '保存失败');
                }
            })
            .catch(error => {
                console.error('保存组合系数失败:', error);
                showAlphaSaveResult(false, '保存失败: ' + error.message);
            })
            .finally(() => {
                saveBtn.disabled = false;
                saveBtn.innerHTML = originalText;
            });
    }

    // ============================================
    // 页面加载时从数据库读取保存的组合系数
    // ============================================
    async function loadAlphaCoefficient() {
        try {
            const csrfToken = getCsrfToken();
            const response = await fetch('/evaluation/api/get-alpha-coefficient/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            });

            if (!response.ok) {
                throw new Error(`请求失败: ${response.status}`);
            }

            const result = await response.json();
            if (result.success && result.alpha !== null && DOM.alphaInput) {
                DOM.alphaInput.value = result.alpha;
            }
        } catch (error) {
            console.log('读取组合系数失败，使用默认值:', error);
        }
    }

    // ============================================
    // 显示保存结果提示
    // ============================================
    function showAlphaSaveResult(success, message) {
        // 创建临时提示消息
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert ${success ? 'alert-success' : 'alert-danger'} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 80px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            <i class="fas fa-${success ? 'check-circle' : 'exclamation-circle'} mr-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        document.body.appendChild(alertDiv);

        // 3秒后自动移除
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 300);
        }, 3000);
    }

    // ============================================
    // 保存组合系数到服务器
    // ============================================
    async function saveAlphaCoefficient(alphaValue) {
        try {
            const csrfToken = getCsrfToken();
            const response = await fetch('/evaluation/api/save-alpha-coefficient/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    alpha: alphaValue
                })
            });

            if (!response.ok) {
                throw new Error(`请求失败: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('保存组合系数请求失败:', error);
            throw error;
        }
    }

    // ============================================
    // 验证输入表单
    // 检查机床选择和alpha值是否合法
    // alpha值必须在0-1之间
    // ============================================
    function validateInputs() {
        let isValid = true;

        if (!DOM.machineSelect.value) {
            DOM.machineSelect.classList.add('is-invalid');
            isValid = false;
        } else {
            DOM.machineSelect.classList.remove('is-invalid');
        }

        const alpha = parseFloat(DOM.alphaInput.value);
        if (isNaN(alpha) || alpha < 0 || alpha > 1) {
            DOM.alphaInput.classList.add('is-invalid');
            isValid = false;
        } else {
            DOM.alphaInput.classList.remove('is-invalid');
        }

        return isValid;
    }

    // ============================================
    // 设置按钮加载状态
    // @param {HTMLElement} btn - 目标按钮元素
    // @param {boolean} isLoading - 是否显示加载状态
    // @param {string} text - 按钮显示文本
    // ============================================
    function setButtonLoading(btn, isLoading, text) {
        btn.disabled = isLoading;
        if (isLoading) {
            btn.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i>${text}`;
        } else {
            btn.innerHTML = `<i class="fas fa-calculator mr-2"></i>${text}`;
        }
    }

    // ============================================
    // 显示加载状态
    // 在结果区域和过程区域显示加载动画和提示信息
    // ============================================
    function showLoadingState() {
        DOM.resultContainer.innerHTML = `
            <div class="alert alert-warning text-center p-5">
                <div class="spinner-border text-primary mb-3" style="width: 4rem; height: 4rem;"></div>
                <h4 class="mt-2 mb-3">计算中...</h4>
                <p class="mb-0">正在从数据库获取权重数据并进行精度分数计算，请稍候</p>
            </div>
        `;

        DOM.processContainer.innerHTML = `
            <div class="alert alert-secondary text-center p-5">
                <div class="spinner-border text-secondary mb-3" style="width: 4rem; height: 4rem;"></div>
                <h4 class="mt-2 mb-3">计算过程</h4>
                <p class="mb-0">正在处理数据，请稍候</p>
            </div>
        `;
    }

    // ============================================
    // 显示错误状态
    // @param {string} message - 错误信息文本
    // ============================================
    function showErrorState(message) {
        DOM.resultContainer.innerHTML = `
            <div class="alert alert-danger text-center p-5">
                <i class="fas fa-exclamation-circle fa-3x mb-3 text-danger"></i>
                <h4 class="mt-2 mb-3">计算失败</h4>
                <p class="mb-0">${message}</p>
            </div>
        `;
    }

    // ============================================
    // 获取CSRF令牌
    // 从Cookie中读取Django的csrftoken
    // ============================================
    function getCsrfToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }

    // ============================================
    // 异步获取API数据
    // @param {string} url - API地址
    // @returns {Promise} 返回JSON响应数据
    // ============================================
    async function fetchAPI(url) {
        const timestamp = new Date().getTime();
        const separator = url.includes('?') ? '&' : '?';
        const response = await fetch(`${url}${separator}t=${timestamp}`);

        if (!response.ok) {
            throw new Error(`请求失败: ${response.status}`);
        }

        return await response.json();
    }

    function parseMachineInfo() {
        const machineSelect = DOM.machineSelect;
        const machineId = machineSelect.value;
        const machineText = machineSelect.options[machineSelect.selectedIndex]?.text || '';
        const machineType = machineSelect.options[machineSelect.selectedIndex]?.getAttribute('data-machine-type') || '';

        let machineName = '';
        let reportNumber = '';
        
        if (machineText) {
            const match = machineText.match(/^(.+?)\s*\((.+?)\)$/);
            if (match) {
                machineName = match[1].trim();
                reportNumber = match[2].trim();
            } else {
                machineName = machineText.trim();
            }
        }

        return { machineId, machineName, reportNumber, machineType };
    }

    function getIndicatorScore(category, subcategory, indicator, indicatorScores) {
        if (!indicatorScores || !indicatorScores[category]) {
            return 0;
        }

        const categoryData = indicatorScores[category];

        if (subcategory === null || subcategory === undefined) {
            if (typeof categoryData === 'object' && !Array.isArray(categoryData)) {
                return categoryData[indicator] || 0;
            } else if (typeof categoryData === 'number') {
                return categoryData;
            }
            return 0;
        }

        if (categoryData[subcategory]) {
            const subcategoryData = categoryData[subcategory];
            if (typeof subcategoryData === 'object' && !Array.isArray(subcategoryData)) {
                return subcategoryData[indicator] || 0;
            } else if (typeof subcategoryData === 'number') {
                return subcategoryData;
            }
        }

        if (!subcategory && typeof categoryData === 'object' && !Array.isArray(categoryData)) {
            return categoryData[indicator] || 0;
        }

        return 0;
    }

    function buildIndicatorScoresArray(indicatorScores) {
        const indicatorScoresArray = {};
        
        // 获取当前机床类型的配置
        const currentConfig = getCurrentConfig();
        
        for (const category in STATE.mockData.indicators) {
            indicatorScoresArray[category] = {};
            for (const subcategory in STATE.mockData.indicators[category]) {
                // 使用动态获取的指标列表
                const indicators = getIndicatorsForCurrentMachineType(category, subcategory);
                
                if (indicators.length > 0) {
                    let subcategoryScore = null;
                    if (indicatorScores[category] && indicatorScores[category][subcategory]) {
                        const subcategoryData = indicatorScores[category][subcategory];
                        if (typeof subcategoryData === 'number') {
                            subcategoryScore = subcategoryData;
                        }
                    }
                    
                    if (subcategoryScore !== null) {
                        const scores = indicators.map(() => subcategoryScore);
                        indicatorScoresArray[category][subcategory] = scores;
                    } else {
                        const scores = indicators.map(indicator => 
                            getIndicatorScore(category, subcategory, indicator, indicatorScores)
                        );
                        indicatorScoresArray[category][subcategory] = scores;
                    }
                } else {
                    const score = getIndicatorScore(category, null, subcategory, indicatorScores);
                    indicatorScoresArray[category][subcategory] = [score];
                }
            }
        }
        
        return indicatorScoresArray;
    }

    function mergeLocalStorageData(indicatorScores, machineId) {
        const localStorageKey = 'user_evaluation_min_scores_' + machineId;
        const localData = JSON.parse(localStorage.getItem(localStorageKey) || '{}');
        
        if (Object.keys(localData).length === 0) {
            return indicatorScores;
        }

        const mapping = {
            'feed_axis_straightness_min_score': ['几何精度', '进给轴精度', '直线度'],
            'feed_axis_parallelism_min_score': ['几何精度', '进给轴精度', '平行度'],
            'feed_axis_angle_min_score': ['几何精度', '进给轴精度', '角度误差'],
            'feed_axis_perpendicularity_min_score': ['几何精度', '进给轴精度', '垂直度'],
            'worktable_flatness_min_score': ['几何精度', '工作台精度', '平面度'],
            'worktable_straightness_min_score': ['几何精度', '工作台精度', '直线度'],
            'worktable_parallelism_min_score': ['几何精度', '工作台精度', '平行度'],
            'worktable_tslot_min_score': ['几何精度', '工作台精度', 'T型槽平行度'],
            'roundness_min_score': ['几何精度', '主轴精度', '圆度'],
            'coaxiality_min_score': ['几何精度', '主轴精度', '同轴度'],
            'spindle_radial_runout_min_score': ['几何精度', '主轴精度', '主轴径向跳动'],
            'spindle_end_runout_min_score': ['几何精度', '主轴精度', '主轴端面跳动'],
            'spindle_axial_runout_min_score': ['几何精度', '主轴精度', '主轴轴向窜动'],
            'tool_magazine_positioning_min_score': ['几何精度', '刀库精度', '刀库定位精度'],
            'tool_magazine_repeatability_min_score': ['几何精度', '刀库精度', '刀库重复定位精度'],
            'position_repeatability_min_score': ['位置精度', null, '重复定位精度'],
            'position_positioning_min_score': ['位置精度', null, '定位精度'],
            'position_offset_min_score': ['位置精度', null, '平均位置偏移'],
            'position_deviation_min_score': ['位置精度', null, '定位系统偏差'],
            'position_backlash_min_score': ['位置精度', null, '反向间隙(差值)'],
            'position_resolution_min_score': ['位置精度', null, '最小分辨率'],
            'machining_surface_roughness_min_score': ['加工精度', '微观几何形状误差', '表面粗糙度'],
            'machining_dimension_min_score': ['加工精度', '工件几何精度', '尺寸精度'],
            'machining_geometry_min_score': ['加工精度', '工件几何精度', '形状精度'],
            'motion_spindle_min_score': ['运动精度', '主轴运动精度', '主轴径向误差']
        };

        for (const [key, value] of Object.entries(localData)) {
            if (mapping[key]) {
                const [category, subcategory, indicator] = mapping[key];
                if (!indicatorScores[category]) indicatorScores[category] = {};
                if (subcategory && !indicatorScores[category][subcategory]) {
                    indicatorScores[category][subcategory] = {};
                }
                if (subcategory) {
                    indicatorScores[category][subcategory][indicator] = value;
                } else {
                    indicatorScores[category][indicator] = value;
                }
            }
        }

        return indicatorScores;
    }

    async function calculateComprehensiveWeight() {
        if (DOM.calculateBtn.disabled) {
            return;
        }

        if (!validateInputs()) {
            alert('请填写所有必填字段');
            return;
        }

        setButtonLoading(DOM.calculateBtn, true, '计算中...');
        showLoadingState();

        try {
            const { machineId, machineName, reportNumber, machineType } = parseMachineInfo();
            const alpha = parseFloat(DOM.alphaInput.value);
            
            // 更新当前机床类型状态
            STATE.currentMachineType = machineType || 'machining_center';
            console.log(`[计算] 机床ID: ${machineId}, 机床类型: ${STATE.currentMachineType}`);

            const [ahpData, entropyData, toleranceData, userEvaluationData] = await Promise.all([
                fetchAPI('/evaluation/api/get-ahp-weights/'),
                fetchAPI(`/evaluation/api/get-entropy-weights/?machine_id=${machineId}`),
                fetchAPI(`/evaluation/api/get-tolerances/?machine_id=${machineId}`),
                fetchAPI(`/evaluation/api/get-user-evaluation-result/?machine_id=${machineId}`)
            ]);

            const ahpWeights = ahpData.weights;
            const entropyWeights = entropyData.weights;
            const tolerances = toleranceData.values || STATE.mockData.tolerances;

            let indicatorScores = {};
            let machineGroupMapping = {};
            let currentGroupNumber = 0;

            if (userEvaluationData.success && userEvaluationData.data) {
                indicatorScores = userEvaluationData.data.indicator_scores || {};
                machineGroupMapping = userEvaluationData.data.machine_group_mapping || {};
                currentGroupNumber = userEvaluationData.data.group_number || 0;
            }

            indicatorScores = mergeLocalStorageData(indicatorScores, machineId);
            const indicatorScoresArray = buildIndicatorScoresArray(indicatorScores);

            STATE.mockData.ahpWeights = ahpWeights;
            STATE.mockData.entropyWeights = entropyWeights;
            STATE.mockData.tolerances = tolerances;
            STATE.mockData.indicatorScores = indicatorScoresArray;
            STATE.mockData.machineGroupMapping = machineGroupMapping;
            STATE.mockData.currentGroupNumber = currentGroupNumber;

            const requestData = {
                ahp_weight: alpha,
                entropy_weight: 1 - alpha,
                ahp_weights: ahpWeights,
                entropy_weights: entropyWeights,
                secondary_to_primary: {
                    '几何精度': ahpWeights['二级对一级']['精度'][0],
                    '位置精度': ahpWeights['二级对一级']['精度'][1],
                    '加工精度': ahpWeights['二级对一级']['精度'][2],
                    '运动精度': ahpWeights['二级对一级']['精度'][3]
                },
                tertiary_to_secondary: {
                    '几何精度': {
                        '进给轴精度': ahpWeights['三级对二级']['几何精度'][0],
                        '工作台精度': ahpWeights['三级对二级']['几何精度'][1],
                        '主轴精度': ahpWeights['三级对二级']['几何精度'][2],
                        '刀库精度': ahpWeights['三级对二级']['几何精度'][3]
                    },
                    '位置精度': {
                        '重复定位精度': ahpWeights['三级对二级']['位置精度'][0],
                        '定位精度': ahpWeights['三级对二级']['位置精度'][1],
                        '平均位置偏移': ahpWeights['三级对二级']['位置精度'][2],
                        '定位系统偏差': ahpWeights['三级对二级']['位置精度'][3],
                        '最小分辨率': ahpWeights['三级对二级']['位置精度'][4],
                        '反向间隙(差值)': ahpWeights['三级对二级']['位置精度'][5]
                    },
                    '加工精度': {
                        '微观几何形状误差': ahpWeights['三级对二级']['加工精度'][0],
                        '加工分散性': ahpWeights['三级对二级']['加工精度'][1],
                        '工件几何精度': ahpWeights['三级对二级']['加工精度'][2]
                    },
                    '运动精度': {
                        '主轴运动精度': ahpWeights['三级对二级']['运动精度'][0],
                        '多轴联动精度': ahpWeights['三级对二级']['运动精度'][1],
                        '传动精度': ahpWeights['三级对二级']['运动精度'][2],
                        '热误差': ahpWeights['三级对二级']['运动精度'][3],
                        '磨损精度': ahpWeights['三级对二级']['运动精度'][4]
                    }
                },
                indicator_scores: indicatorScoresArray,
                standard_tolerances: tolerances
            };

            const response = await fetch('/evaluation/api/calculate-comprehensive-weight/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(requestData)
            });

            const calculationResult = await response.json();

            if (calculationResult.success) {
                const result = calculationResult.result;

                console.log('[DEBUG] 后端返回的 filter_result:', result.filter_result);
                console.log('[DEBUG] 关键指标数量:', result.filter_result ? result.filter_result.key_indicator_count : 0);
                console.log('[DEBUG] 关键指标列表:', result.filter_result ? result.filter_result.key_indicators : []);

                const totalResults = {
                    totalWeight: result.filter_result ? (result.filter_result.total_weight_original || 0) : 0,
                    totalScore: result.final_score || 0,
                    keyIndicatorsCount: result.filter_result ? (result.filter_result.key_indicator_count || 0) : 0,
                    totalIndicatorsCount: result.filter_result ? (result.filter_result.total_indicator_count || 0) : 0,
                    totalScoreOriginal: 0,
                    keyIndicators: result.filter_result ? result.filter_result.key_indicators || [] : []
                };

                const processHtml = buildProcessHtml(alpha, 1 - alpha, result);
                DOM.processContainer.innerHTML = processHtml;
                setupCollapseButtons();

                const resultHtml = buildResultHtml(totalResults);
                DOM.resultContainer.innerHTML = resultHtml;

                DOM.saveBtn.style.display = 'block';

                STATE.currentCalculationResult = {
                    machine_id: machineId,
                    machine_name: machineName,
                    report_number: reportNumber,
                    machine_type: machineType,
                    alpha: alpha,
                    ahp_weights: ahpWeights,
                    entropy_weights: entropyWeights,
                    combined_weights: result.combined_weights || {},
                    indicator_scores: indicatorScoresArray,
                    standard_tolerances: tolerances,
                    global_weights: result.global_weights || {},
                    weighted_scores: result.weighted_scores || {},
                    total_score: result.final_score || 0,
                    total_weight: result.filter_result ? (result.filter_result.total_weight_original || 0) : 0,
                    // 五维度评分 - 精度维度得分等于综合得分（因为这是精度分数计算）
                    precision_score: result.final_score || 0,
                    performance_score: 0,
                    reliability_score: 0,
                    intelligence_score: 0,
                    green_score: 0
                };
            } else {
                throw new Error(calculationResult.error || '计算失败');
            }
        } catch (error) {
            console.error('计算失败:', error);
            showErrorState(`获取权重数据失败，请稍后重试<br>错误信息: ${error.message}`);
        } finally {
            setButtonLoading(DOM.calculateBtn, false, '开始计算精度分数');
        }
    }

    function buildProcessHtml(ahpWeight, entropyWeight, result) {
        return `
            <div class="card mb-4 border-left-primary">
                <div class="card-header bg-primary bg-opacity-10" data-bs-toggle="collapse" data-bs-target="#algorithmOverviewCollapse" aria-expanded="true" aria-controls="algorithmOverviewCollapse">
                    <div class="d-flex justify-content-between align-items-center">
                        <h6 class="card-title font-weight-bold mb-0">算法概述</h6>
                        <button class="btn btn-sm btn-outline-primary">
                            <i class="fas fa-chevron-down"></i>
                        </button>
                    </div>
                </div>
                <div id="algorithmOverviewCollapse" class="collapse show">
                    <div class="card-body">
                        <p class="mb-3">精度分数计算算法采用层次分析法(AHP)与信息熵法相结合的组合赋权方法，仅保留信息熵权重不为零的指标作为关键指标，提高评价的准确性和可靠性。</p>
                        
                        <h6 class="font-weight-bold mb-2">算法流程：</h6>
                        <ol class="list-decimal pl-5 mb-4">
                            <li>获取AHP权重（专家主观权重）</li>
                            <li>获取信息熵权重（数据客观权重）</li>
                            <li>计算局部组合权重（主观与客观权重的加权平均）</li>
                            <li>计算全局原始权重（层级权重传递）</li>
                            <li>计算指标得分（使用用户评价界面录入的分数）</li>
                            <li>筛选关键指标（仅保留信息熵权重不为零的指标）</li>
                            <li>计算最终综合得分</li>
                        </ol>
                        
                        <h6 class="font-weight-bold mb-2">核心参数：</h6>
                        <ul class="list-disc pl-5 mb-4">
                            <li>α（AHP权重系数）：${ahpWeight}</li>
                            <li>1-α（信息熵权重系数）：${entropyWeight}</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="card mb-4 border-left-warning">
                <div class="card-header bg-warning bg-opacity-10" data-bs-toggle="collapse" data-bs-target="#localWeightsCollapse" aria-expanded="true" aria-controls="localWeightsCollapse">
                    <div class="d-flex justify-content-between align-items-center">
                        <h6 class="card-title font-weight-bold mb-0">步骤1：计算局部组合权重</h6>
                        <button class="btn btn-sm btn-outline-warning">
                            <i class="fas fa-chevron-down"></i>
                        </button>
                    </div>
                </div>
                <div id="localWeightsCollapse" class="collapse show">
                    <div class="card-body">
                        <p class="mb-3">局部组合权重是AHP权重与信息熵权重的加权平均值，计算公式如下：</p>
                        <div class="bg-light p-3 rounded mb-4">
                            <code class="font-weight-bold">W_combined = α × W_AHP + (1−α) × W_Entropy</code>
                        </div>
                        
                        <div class="table-responsive mt-4">
                            ${generateCombinedWeightsTable(ahpWeight, entropyWeight)}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card mb-4 border-left-info">
                <div class="card-header bg-info bg-opacity-10" data-bs-toggle="collapse" data-bs-target="#globalWeightsCollapse" aria-expanded="true" aria-controls="globalWeightsCollapse">
                    <div class="d-flex justify-content-between align-items-center">
                        <h6 class="card-title font-weight-bold mb-0">步骤2：计算全局权重与指标得分</h6>
                        <button class="btn btn-sm btn-outline-info">
                            <i class="fas fa-chevron-down"></i>
                        </button>
                    </div>
                </div>
                <div id="globalWeightsCollapse" class="collapse show">
                    <div class="card-body">
                        <div class="table-responsive mt-4">
                            ${generateGlobalWeightsAndScoresTableFromBackend(result)}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card mb-4 border-left-success">
                <div class="card-header bg-success bg-opacity-10" data-bs-toggle="collapse" data-bs-target="#filterCollapse" aria-expanded="true" aria-controls="filterCollapse">
                    <div class="d-flex justify-content-between align-items-center">
                        <h6 class="card-title font-weight-bold mb-0">步骤3：筛选关键指标并计算最终得分</h6>
                        <button class="btn btn-sm btn-outline-success">
                            <i class="fas fa-chevron-down"></i>
                        </button>
                    </div>
                </div>
                <div id="filterCollapse" class="collapse show">
                    <div class="card-body">
                        <h6 class="font-weight-bold mb-3">关键指标筛选：</h6>
                        <p class="mb-3">仅保留信息熵权重不为零的指标作为关键指标。信息熵权重为零表示该指标在数据中没有区分度，因此不参与最终得分计算。</p>
                        
                        <h6 class="font-weight-bold mb-3">最终得分计算：</h6>
                        <div class="bg-light p-3 rounded mb-4">
                            <code class="font-weight-bold">最终得分 = Σ(WS_i^关键) / Σ(W_i原始^关键)</code>
                        </div>
                        
                        <div class="bg-light p-3 rounded mb-4">
                            <h6 class="font-weight-bold mb-2">计算结果：</h6>
                            <ul class="list-disc pl-5">
                                <li>关键指标数量：${result.filter_result ? (result.filter_result.key_indicator_count || 0) : 0}/${result.filter_result ? (result.filter_result.total_indicator_count || 0) : 0}</li>
                                <li>关键指标总权重：${result.filter_result ? (result.filter_result.total_weight_original || 0).toFixed(4) : '0.0000'}</li>
                                <li>最终综合得分：${result.final_score ? result.final_score.toFixed(2) : '0.00'}</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    function generateCombinedWeightsTable(ahpWeight, entropyWeight) {
        const htmlSegments = [];
        const entropyWeights = STATE.mockData.entropyWeights;
        const ahpWeights = STATE.mockData.ahpWeights['四级对三级'];
        
        // 获取当前机床类型的配置
        const currentConfig = getCurrentConfig();
        
        let totalRowspan = 0;
        currentConfig.SECONDARY_KEYS.forEach(secondary => {
            const tertiaryKeys = currentConfig.TERTIARY_ORDER[secondary];
            tertiaryKeys.forEach(tertiary => {
                if (entropyWeights[secondary] && entropyWeights[secondary][tertiary]) {
                    const indicators = getIndicatorsForCurrentMachineType(secondary, tertiary);
                    totalRowspan += indicators.length > 0 ? indicators.length : 1;
                }
            });
        });

        let isFirstRow = true;
        let rowCounter = 0;

        currentConfig.SECONDARY_KEYS.forEach((secondary) => {
            let secondaryRowspan = 0;
            const tertiaryKeys = currentConfig.TERTIARY_ORDER[secondary];

            tertiaryKeys.forEach(tertiary => {
                if (entropyWeights[secondary] && entropyWeights[secondary][tertiary]) {
                    const indicators = getIndicatorsForCurrentMachineType(secondary, tertiary);
                    secondaryRowspan += indicators.length > 0 ? indicators.length : 1;
                }
            });

            tertiaryKeys.forEach((tertiary, tertiaryIndex) => {
                if (entropyWeights[secondary] && entropyWeights[secondary][tertiary]) {
                    const indicators = getIndicatorsForCurrentMachineType(secondary, tertiary);
                    const entropyW = entropyWeights[secondary][tertiary];
                    
                    let ahpW;
                    if (secondary === '位置精度') {
                        const tertiaryWeights = STATE.mockData.ahpWeights['三级对二级']['位置精度'] || [];
                        const tertiaryIndex = currentConfig.TERTIARY_ORDER[secondary].indexOf(tertiary);
                        ahpW = [tertiaryWeights[tertiaryIndex] || 0.2];
                    } else {
                        ahpW = ahpWeights[secondary][tertiary] || [];
                    }

                    if (indicators.length > 0) {
                        indicators.forEach((indicator, index) => {
                            const combined = calculateCombinedWeight(ahpW[index], entropyW[index], ahpWeight, entropyWeight, ahpW, entropyW);
                            const rowClass = rowCounter % 2 === 0 ? 'bg-white' : 'bg-light';

                            if (isFirstRow) {
                                htmlSegments.push(`
                                    <tr class="${rowClass}">
                                        <td rowspan="${totalRowspan}" class="align-middle">精度</td>
                                        <td rowspan="${secondaryRowspan}" class="align-middle">${secondary}</td>
                                        <td rowspan="${indicators.length}" class="align-middle">${tertiary}</td>
                                        <td class="align-middle">${indicator}</td>
                                        <td class="align-middle">${ahpW[index] !== undefined ? ahpW[index].toFixed(2) : '0.00'}</td>
                                        <td class="align-middle">${entropyW[index] !== undefined ? entropyW[index].toFixed(2) : '0.00'}</td>
                                        <td class="align-middle">${combined !== undefined ? combined.toFixed(2) : '0.00'}</td>
                                    </tr>
                                `);
                                isFirstRow = false;
                            } else if (index === 0) {
                                if (tertiaryIndex === 0) {
                                    htmlSegments.push(`
                                        <tr class="${rowClass}">
                                            <td rowspan="${secondaryRowspan}" class="align-middle">${secondary}</td>
                                            <td rowspan="${indicators.length}" class="align-middle">${tertiary}</td>
                                            <td class="align-middle">${indicator}</td>
                                            <td class="align-middle">${ahpW[index] !== undefined ? ahpW[index].toFixed(2) : '0.00'}</td>
                                            <td class="align-middle">${entropyW[index] !== undefined ? entropyW[index].toFixed(2) : '0.00'}</td>
                                            <td class="align-middle">${combined !== undefined ? combined.toFixed(2) : '0.00'}</td>
                                        </tr>
                                    `);
                                } else {
                                    htmlSegments.push(`
                                        <tr class="${rowClass}">
                                            <td rowspan="${indicators.length}" class="align-middle">${tertiary}</td>
                                            <td class="align-middle">${indicator}</td>
                                            <td class="align-middle">${ahpW[index] !== undefined ? ahpW[index].toFixed(2) : '0.00'}</td>
                                            <td class="align-middle">${entropyW[index] !== undefined ? entropyW[index].toFixed(2) : '0.00'}</td>
                                            <td class="align-middle">${combined !== undefined ? combined.toFixed(2) : '0.00'}</td>
                                        </tr>
                                    `);
                                }
                            } else {
                                htmlSegments.push(`
                                    <tr class="${rowClass}">
                                        <td class="align-middle">${indicator}</td>
                                        <td class="align-middle">${ahpW[index] !== undefined ? ahpW[index].toFixed(2) : '0.00'}</td>
                                        <td class="align-middle">${entropyW[index] !== undefined ? entropyW[index].toFixed(2) : '0.00'}</td>
                                        <td class="align-middle">${combined !== undefined ? combined.toFixed(2) : '0.00'}</td>
                                    </tr>
                                `);
                            }
                            rowCounter++;
                        });
                    } else {
                        const combined = calculateCombinedWeight(ahpW[0], entropyW[0], ahpWeight, entropyWeight, ahpW, entropyW);
                        const rowClass = rowCounter % 2 === 0 ? 'bg-white' : 'bg-light';

                        if (isFirstRow) {
                            htmlSegments.push(`
                                <tr class="${rowClass}">
                                    <td rowspan="${totalRowspan}" class="align-middle">精度</td>
                                    <td rowspan="${secondaryRowspan}" class="align-middle">${secondary}</td>
                                    <td class="align-middle">${tertiary}</td>
                                    <td class="align-middle">-</td>
                                    <td class="align-middle">${ahpW[0] !== undefined ? ahpW[0].toFixed(2) : '0.00'}</td>
                                    <td class="align-middle">${entropyW[0] !== undefined ? entropyW[0].toFixed(2) : '0.00'}</td>
                                    <td class="align-middle">${combined !== undefined ? combined.toFixed(2) : '0.00'}</td>
                                </tr>
                            `);
                            isFirstRow = false;
                        } else if (tertiaryIndex === 0) {
                            htmlSegments.push(`
                                <tr class="${rowClass}">
                                    <td rowspan="${secondaryRowspan}" class="align-middle">${secondary}</td>
                                    <td class="align-middle">${tertiary}</td>
                                    <td class="align-middle">-</td>
                                    <td class="align-middle">${ahpW[0] !== undefined ? ahpW[0].toFixed(2) : '0.00'}</td>
                                    <td class="align-middle">${entropyW[0] !== undefined ? entropyW[0].toFixed(2) : '0.00'}</td>
                                    <td class="align-middle">${combined !== undefined ? combined.toFixed(2) : '0.00'}</td>
                                </tr>
                            `);
                        } else {
                            htmlSegments.push(`
                                <tr class="${rowClass}">
                                    <td class="align-middle">${tertiary}</td>
                                    <td class="align-middle">-</td>
                                    <td class="align-middle">${ahpW[0] !== undefined ? ahpW[0].toFixed(2) : '0.00'}</td>
                                    <td class="align-middle">${entropyW[0] !== undefined ? entropyW[0].toFixed(2) : '0.00'}</td>
                                    <td class="align-middle">${combined !== undefined ? combined.toFixed(2) : '0.00'}</td>
                                </tr>
                            `);
                        }
                        rowCounter++;
                    }
                }
            });
        });

        return `
            <table class="table table-hover table-bordered">
                <thead class="bg-warning text-white">
                    <tr>
                        <th class="text-center align-middle" style="width: 10%;">一级指标</th>
                        <th class="text-center align-middle" style="width: 15%;">二级指标</th>
                        <th class="text-center align-middle" style="width: 20%;">三级指标</th>
                        <th class="text-center align-middle" style="width: 20%;">四级指标</th>
                        <th class="text-center align-middle" style="width: 10%;">AHP权重</th>
                        <th class="text-center align-middle" style="width: 10%;">信息熵权重</th>
                        <th class="text-center align-middle" style="width: 15%;">组合权重</th>
                    </tr>
                </thead>
                <tbody class="text-center">
                    ${htmlSegments.join('')}
                </tbody>
            </table>
        `;
    }

    function calculateCombinedWeight(ahpW, entropyW, ahpWeight, entropyWeight, allAhpW, allEntropyW) {
        const zeroEntropyIndices = allEntropyW.map((ew, i) => ew === 0 ? i : -1).filter(i => i !== -1);

        if (zeroEntropyIndices.length > 0) {
            const s = zeroEntropyIndices.reduce((sum, i) => sum + (allAhpW[i] || 0), 0);
            const adjustmentFactor = 1 - s;

            if (entropyW === 0) {
                return ahpW || 0;
            } else {
                return adjustmentFactor * entropyW;
            }
        } else {
            return ahpWeight * ahpW + entropyWeight * entropyW;
        }
    }

    function generateGlobalWeightsAndScoresTableFromBackend(result) {
        const htmlSegments = [];
        const globalWeightsAndScores = result.global_weights || [];
        const filterResult = result.filter_result || {};
        const keyIndicators = filterResult.key_indicators || [];
        const totalWeightOriginal = filterResult.total_weight_original || 0;
        
        const keyIndicatorSet = new Set(keyIndicators.map(item => item.indicator));
        
        // 获取当前机床类型的配置
        const currentConfig = getCurrentConfig();

        currentConfig.SECONDARY_KEYS.forEach(secondary => {
            const tertiaryKeys = currentConfig.TERTIARY_ORDER[secondary];
            tertiaryKeys.forEach(tertiary => {
                const tertiaryData = globalWeightsAndScores.filter(item => 
                    item.secondary === secondary && item.tertiary === tertiary
                );
                const indicators = getIndicatorsForCurrentMachineType(secondary, tertiary);

                if (indicators.length > 0) {
                    indicators.forEach((indicator, index) => {
                        let item = tertiaryData.find(item => item.indicator === indicator) || {};
                        if (Object.keys(item).length === 0 && tertiaryData[index]) {
                            item = tertiaryData[index];
                        }

                        const isKey = keyIndicatorSet.has(item.indicator) || keyIndicators.includes(item);
                        const normalizedWeight = isKey ? item.global_original / totalWeightOriginal : 0;
                        const finalWeightedScore = isKey ? normalizedWeight * (item.score || 0) : 0;

                        htmlSegments.push(`
                            <tr ${isKey ? 'class="table-primary"' : ''}>
                                <td>四级</td>
                                <td>${indicator}</td>
                                <td>${item.combined !== undefined ? item.combined.toFixed(3) : '0.000'}</td>
                                <td>${item.weight_chain || '-'}</td>
                                <td>${item.global_original !== undefined ? item.global_original.toFixed(4) : '0.0000'}</td>
                                <td>${item.score !== undefined ? item.score.toFixed(4) : '0.0000'}</td>
                                <td>${item.weighted_score_original !== undefined ? item.weighted_score_original.toFixed(3) : '0.000'}</td>
                                <td>${isKey && normalizedWeight !== undefined ? normalizedWeight.toFixed(3) : '-'}</td>
                                <td>${isKey && finalWeightedScore !== undefined ? finalWeightedScore.toFixed(3) : '-'}</td>
                                <td>${isKey ? '是' : '否'}</td>
                            </tr>
                        `);
                    });
                } else if (tertiaryData.length > 0) {
                    const item = tertiaryData[0];
                    const isKey = keyIndicatorSet.has(item.indicator) || keyIndicators.some(ki => ki.indicator === item.indicator);
                    const normalizedWeight = isKey ? item.global_original / totalWeightOriginal : 0;
                    const finalWeightedScore = isKey ? normalizedWeight * (item.score || 0) : 0;

                    htmlSegments.push(`
                        <tr ${isKey ? 'class="table-primary"' : ''}>
                            <td>三级</td>
                            <td>${item.indicator || tertiary}</td>
                            <td>${item.combined !== undefined ? item.combined.toFixed(3) : '0.000'}</td>
                            <td>${item.weight_chain || '-'}</td>
                            <td>${item.global_original !== undefined ? item.global_original.toFixed(4) : '0.0000'}</td>
                            <td>${item.score !== undefined ? item.score.toFixed(4) : '0.0000'}</td>
                            <td>${item.weighted_score_original !== undefined ? item.weighted_score_original.toFixed(3) : '0.000'}</td>
                            <td>${isKey && normalizedWeight !== undefined ? normalizedWeight.toFixed(3) : '-'}</td>
                            <td>${isKey && finalWeightedScore !== undefined ? finalWeightedScore.toFixed(3) : '-'}</td>
                            <td>${isKey ? '是' : '否'}</td>
                        </tr>
                    `);
                }
            });
        });

        let finalScore = 0;
        keyIndicators.forEach(item => {
            const normalizedWeight = item.global_original / totalWeightOriginal;
            finalScore += normalizedWeight * (item.score || 0);
        });
        finalScore = finalScore * 100;

        htmlSegments.push(`
            <tr class="table-success">
                <td colspan="2">汇总</td>
                <td>${totalWeightOriginal !== undefined ? totalWeightOriginal.toFixed(3) : '0.000'}</td>
                <td>-</td>
                <td>-</td>
                <td>${keyIndicators.reduce((sum, item) => sum + (item.weighted_score_original || 0), 0).toFixed(3)}</td>
                <td>-</td>
                <td>${finalScore !== undefined ? finalScore.toFixed(2) : '0.00'}</td>
                <td>-</td>
                <td>-</td>
            </tr>
        `);

        return `
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>指标层级</th>
                        <th>指标名称</th>
                        <th>局部组合权重</th>
                        <th>上级AHP权重链</th>
                        <th>全局原始权重</th>
                        <th>指标得分</th>
                        <th>加权得分（原始）</th>
                        <th>归一化权重</th>
                        <th>最终加权得分</th>
                        <th>是否关键指标</th>
                    </tr>
                </thead>
                <tbody>
                    ${htmlSegments.join('')}
                </tbody>
            </table>
        `;
    }

    function buildResultHtml(totalResults) {
        const { totalWeight, totalScore, keyIndicatorsCount, totalIndicatorsCount } = totalResults;
        
        return `
            <div class="bg-gradient-success bg-opacity-10 p-3 rounded-lg">
                <h5 class="text-center mb-2">计算完成</h5>
                <div class="row justify-content-center">
                    <div class="col-md-6 mb-2">
                        <div class="card">
                            <div class="card-header bg-success text-white py-2">
                                <h6 class="card-title mb-0">综合评分</h6>
                            </div>
                            <div class="card-body text-center py-3">
                                <div class="h2 font-weight-bold text-success mb-1">${totalScore !== undefined ? totalScore.toFixed(2) : '0.00'}</div>
                                <p class="mb-0 small">基于${keyIndicatorsCount}/${totalIndicatorsCount}个关键指标计算</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    function buildWeightSummaryHtml(totalResults) {
        const { totalWeight, totalScore, keyIndicatorsCount, totalIndicatorsCount } = totalResults;
        
        return `
            <div class="row">
                <div class="col-md-6 mb-2">
                    <div class="card">
                        <div class="card-header bg-primary text-white py-2">
                            <h6 class="card-title mb-0">总权重 W</h6>
                        </div>
                        <div class="card-body text-center py-3">
                            <div class="h2 font-weight-bold text-primary mb-1">${totalWeight !== undefined ? totalWeight.toFixed(4) : '0.0000'}</div>
                            <p class="mb-0 small">所有关键指标的权重之和</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 mb-2">
                    <div class="card h-100">
                        <div class="card-header bg-info text-white py-2">
                            <h6 class="card-title mb-0">计算结果摘要</h6>
                        </div>
                        <div class="card-body py-2">
                            <ul class="list-unstyled mb-0 small">
                                <li class="mb-1"><i class="fas fa-check-circle text-primary mr-2"></i> 总权重 W: ${totalWeight !== undefined ? totalWeight.toFixed(4) : '0.0000'}</li>
                                <li class="mb-1"><i class="fas fa-check-circle text-primary mr-2"></i> 综合评分: ${totalScore !== undefined ? totalScore.toFixed(2) : '0.00'}</li>
                                <li class="mb-1"><i class="fas fa-check-circle text-primary mr-2"></i> 关键指标数量: ${keyIndicatorsCount}个</li>
                                <li class="mb-1"><i class="fas fa-check-circle text-primary mr-2"></i> 总指标数量: ${totalIndicatorsCount}个</li>
                                <li><i class="fas fa-check-circle text-primary mr-2"></i> 关键指标占比: ${((keyIndicatorsCount/totalIndicatorsCount)*100).toFixed(1)}%</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    function setupCollapseButtons() {
        document.querySelectorAll('.card-header[data-bs-toggle="collapse"]').forEach(cardHeader => {
            cardHeader.addEventListener('click', function() {
                const target = this.getAttribute('data-bs-target');
                const targetElement = document.querySelector(target);
                const isCollapsed = targetElement.classList.contains('show');
                const icon = this.querySelector('i');
                
                if (isCollapsed) {
                    icon.classList.remove('fa-chevron-up');
                    icon.classList.add('fa-chevron-down');
                } else {
                    icon.classList.remove('fa-chevron-down');
                    icon.classList.add('fa-chevron-up');
                }
            });
        });
    }

    function saveToLocalStore(data) {
        try {
            const timestamp = new Date().toISOString();
            const storageKey = 'comprehensive_weight_results';
            
            let results = JSON.parse(localStorage.getItem(storageKey) || '[]');
            
            const resultItem = {
                timestamp: timestamp,
                machine_id: parseInt(data.machine_id),
                machine_name: data.machine_name || '',
                report_number: data.report_number || '',
                machine_type: data.machine_type || '',
                total_score: data.total_score,
                total_weight: data.total_weight,
                alpha: data.alpha,
                comprehensive_weights: data.comprehensive_weights,
                // 五维度评分
                precision_score: data.precision_score || 0,
                performance_score: data.performance_score || 0,
                reliability_score: data.reliability_score || 0,
                intelligence_score: data.intelligence_score || 0,
                green_score: data.green_score || 0
            };
            
            // 查找是否已存在该machine_id的记录（使用严格相等）
            const existingIndex = results.findIndex(item => item.machine_id === parseInt(data.machine_id));
            
            if (existingIndex !== -1) {
                // 更新现有记录，合并数据
                const existingRecord = results[existingIndex];
                
                // 保留已有的非零值，只更新新计算的字段
                // 如果新数据为零，但旧数据有值，则保留旧数据
                if (data.intelligence_score === 0 && existingRecord.intelligence_score > 0) {
                    resultItem.intelligence_score = existingRecord.intelligence_score;
                }
                if (data.precision_score === 0 && existingRecord.precision_score > 0) {
                    resultItem.precision_score = existingRecord.precision_score;
                }
                if (data.performance_score === 0 && existingRecord.performance_score > 0) {
                    resultItem.performance_score = existingRecord.performance_score;
                }
                if (data.reliability_score === 0 && existingRecord.reliability_score > 0) {
                    resultItem.reliability_score = existingRecord.reliability_score;
                }
                if (data.green_score === 0 && existingRecord.green_score > 0) {
                    resultItem.green_score = existingRecord.green_score;
                }
                
                // 如果total_score不为0，使用新计算的total_score
                if (data.total_score > 0) {
                    resultItem.total_score = data.total_score;
                }
                
                results[existingIndex] = resultItem;
                console.log('更新现有记录，合并数据:', resultItem);
            } else {
                // 添加新记录
                results.push(resultItem);
                console.log('添加新记录:', resultItem);
            }
            
            localStorage.setItem(storageKey, JSON.stringify(results));
            
            return {
                success: true,
                message: '计算结果已保存到本地存储',
                machine_id: data.machine_id
            };
        } catch (error) {
            console.error('本地存储保存失败:', error);
            return {
                success: false,
                message: '本地存储保存失败: ' + error.message
            };
        }
    }

    async function saveCalculationResult() {
        if (!STATE.currentCalculationResult) {
            alert('请先进行计算再保存结果');
            return;
        }

        const saveBtn = DOM.saveBtn;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>保存中...';
        saveBtn.disabled = true;

        try {
            const response = await fetch('/evaluation/api/save-comprehensive-weight-result/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(STATE.currentCalculationResult)
            });

            const data = await response.json();
            if (data.success) {
                // 保存精度得分（在更新total_score之前）
                const precisionScore = STATE.currentCalculationResult.total_score;
                // 同时保存到本地存储作为备份
                const localData = {...STATE.currentCalculationResult, total_score: data.final_score};
                saveToLocalStore(localData);
                // 弹窗显示精度得分，与评分汇总界面显示一致
                const formattedScore = parseFloat(precisionScore).toFixed(2);
                alert('保存成功！精度部分得分为：' + formattedScore);
                notifyParentScoreCalculated();
            } else {
                alert('保存失败：' + data.error);
            }
        } catch (error) {
            console.error('保存失败:', error);
            alert('保存失败，请稍后重试');
        } finally {
            saveBtn.innerHTML = '<i class="fas fa-save mr-2"></i>保存计算结果';
            saveBtn.disabled = false;
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // ============================================
    // 通知父页面评分计算已保存
    // 当保存成功时调用，更新父页面评分计算模块的图标状态
    // ============================================
    function notifyParentScoreCalculated() {
        try {
            const machineId = getMachineIdFromUrl();

            // 方法1：尝试调用父页面的全局函数
            if (window.parent && window.parent !== window && window.parent.notifyScoreCalculationSaved) {
                window.parent.notifyScoreCalculationSaved(machineId);
            }

            // 方法2：postMessage作为备用
            if (window.parent && window.parent !== window) {
                window.parent.postMessage({
                    type: 'scoreCalculationSaved',
                    machineId: machineId
                }, '*');
            }

            // 同时设置localStorage标志
            if (machineId) {
                localStorage.setItem('score_calculation_saved_' + machineId, 'true');
            }
        } catch (e) {
            console.log('无法通知父页面:', e);
        }
    }

    // 从URL获取machine_id
    function getMachineIdFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('machine_id');
    }

    // ============================================
    // 监听父页面的消息
    // 用于响应父页面的自动计算和保存请求
    // ============================================
    window.addEventListener('message', function(event) {
        console.log('收到父页面消息:', event.data);
        
        if (event.data && event.data.type === 'triggerCalculate') {
            console.log('收到计算触发消息，开始计算');
            // 触发计算按钮点击
            if (DOM.calculateBtn) {
                DOM.calculateBtn.click();
            }
        }
        
        if (event.data && event.data.type === 'triggerSave') {
            console.log('收到保存触发消息，开始保存');
            // 触发保存按钮点击
            if (DOM.saveBtn && DOM.saveBtn.style.display !== 'none') {
                DOM.saveBtn.click();
            }
        }
    });

})();
