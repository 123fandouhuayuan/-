// 从DOM中获取CSRF令牌
    function getCSRFToken() {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenElement) {
            console.log('找到CSRF令牌元素:', tokenElement);
            console.log('CSRF令牌值:', tokenElement.value.substring(0, 20) + '...');
            return tokenElement.value;
        } else {
            console.error('未找到CSRF令牌元素');
            // 尝试从cookie中获取
            const cookieValue = document.cookie
                .split('; ')
                .find(row => row.startsWith('csrftoken='))
                ?.split('=')[1];
            if (cookieValue) {
                console.log('从cookie中获取CSRF令牌:', cookieValue.substring(0, 20) + '...');
                return cookieValue;
            }
            console.error('未从cookie中找到CSRF令牌');
            return '';
        }
    }
    
    // 统一的DOMContentLoaded事件处理
    document.addEventListener('DOMContentLoaded', function() {
        // 从达梦数据库加载机床参数到表单的通用函数
        // 增强的从达梦数据库加载机床参数到表单的通用函数
        async function loadMachineParamsFromDameng() {
            console.log('开始从达梦数据库加载机床参数...');
            
            try {
                // 获取当前机床ID（从URL参数，不使用默认值避免数据共用）
                const urlParams = new URLSearchParams(window.location.search);
                const machineId = urlParams.get('machine_id');
                
                // 如果没有machineId参数，直接返回，不进行请求
                if (!machineId) {
                    console.log('未找到机床ID参数，跳过从达梦数据库加载参数');
                    return;
                }
                
                console.log('机床编辑页面：获取机床参数，机床ID:', machineId);
                
                // 首先从Django主数据库获取机床类型
                const machineInfoResponse = await fetch(`/data/machines/edit/${machineId}/`);
                if (!machineInfoResponse.ok) {
                    throw new Error(`获取机床信息失败: HTTP ${machineInfoResponse.status}`);
                }
                const machineInfo = await machineInfoResponse.json();
                
                if (!machineInfo.success || !machineInfo.machine) {
                    throw new Error('机床信息不存在');
                }
                
                const machineType = machineInfo.machine.machine_type;
                console.log('机床类型:', machineType);
                
                let response;
                let result;
                
                // 根据机床类型调用不同的达梦数据库API
                if (machineType === 'boring_milling_machine') {
                    console.log('调用镗铣床API...');
                    response = await fetch(`/dameng/api/boring-milling-parameters/${machineId}/`);
                } else {
                    console.log('调用加工中心API...');
                    response = await fetch(`/dameng/api/machine-parameters/${machineId}/`);
                }
                
                console.log('达梦数据库API响应状态:', response.status, response.statusText);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                result = await response.json();
                
                console.log('达梦数据库API返回数据:', result);
                
                if (result.success && result.data) {
                    console.log('从达梦数据库加载的机床参数:', result.data);
                    
                    // 清理localStorage中的旧数据
                    localStorage.removeItem('machine_params');
                    localStorage.removeItem('globalMachineParams');
                    console.log('已清理localStorage中的旧数据');
                    
                    // 根据机床类型加载不同的参数
                    if (machineType === 'boring_milling_machine') {
                        // 工作台类型中文到英文映射（兼容达梦数据库中存储的中文值）
                        const worktableTypeMap = {
                            '固定分度的回转工作台': 'fixed_indexing',
                            '任意角度定位的回转工作台': 'arbitrary_positioning',
                            'fixed_indexing': 'fixed_indexing',
                            'arbitrary_positioning': 'arbitrary_positioning',
                        };
                        const worktableType = worktableTypeMap[result.data.worktable_type] || result.data.worktable_type;
                        
                        // 加载镗铣床参数
                        loadParamsToForm('boring-milling-column-range', result.data.column_measurement_range);
                        loadParamsToForm('boring-milling-worktable-x-range', result.data.worktable_x_range);
                        loadParamsToForm('boring-milling-spindle-box-y-range', result.data.spindle_box_y_range);
                        loadParamsToForm('boring-milling-z-axis-range', result.data.z_axis_measurement_range);
                        loadParamsToForm('boring-milling-worktable-length-lc', result.data.worktable_length_lc);
                        loadParamsToForm('boring-milling-boring-axis-diameter', result.data.boring_axis_diameter);
                        loadParamsToForm('boring-milling-milling-axis-diameter', result.data.milling_axis_diameter);
                        loadParamsToForm('boring-milling-worktable-type', worktableType);
                        
                        loadParamsToForm('edit-boring-milling-column-range', result.data.column_measurement_range);
                        loadParamsToForm('edit-boring-milling-worktable-x-range', result.data.worktable_x_range);
                        loadParamsToForm('edit-boring-milling-spindle-box-y-range', result.data.spindle_box_y_range);
                        loadParamsToForm('edit-boring-milling-z-axis-range', result.data.z_axis_measurement_range);
                        loadParamsToForm('edit-boring-milling-worktable-length-lc', result.data.worktable_length_lc);
                        loadParamsToForm('edit-boring-milling-boring-axis-diameter', result.data.boring_axis_diameter);
                        loadParamsToForm('edit-boring-milling-milling-axis-diameter', result.data.milling_axis_diameter);
                        loadParamsToForm('edit-boring-milling-worktable-type', worktableType);
                    } else {
                        // 加载加工中心参数
                        loadParamsToForm('x-axis-travel', result.data.x_axis_travel);
                        loadParamsToForm('y-axis-travel', result.data.y_axis_travel);
                        loadParamsToForm('z-axis-travel', result.data.z_axis_travel);
                        loadParamsToForm('worktable-length', result.data.worktable_length);
                        loadParamsToForm('workpiece-size', result.data.workpiece_size);
                        loadParamsToForm('spindle-type', result.data.spindle_type);
                        
                        loadParamsToForm('edit-x-axis-travel', result.data.x_axis_travel);
                        loadParamsToForm('edit-y-axis-travel', result.data.y_axis_travel);
                        loadParamsToForm('edit-z-axis-travel', result.data.z_axis_travel);
                        loadParamsToForm('edit-worktable-length', result.data.worktable_length);
                        loadParamsToForm('edit-workpiece-size', result.data.workpiece_size);
                        loadParamsToForm('edit-spindle-type', result.data.spindle_type);
                    }
                    
                    // 保存数据到machineIdToParams，供run_evaluation_user.html使用
                    const machineIdToParams = JSON.parse(localStorage.getItem('machineIdToParams') || '{}');
                    machineIdToParams[machineId] = { ...result.data, machine_type: machineType };
                    localStorage.setItem('machineIdToParams', JSON.stringify(machineIdToParams));
                    console.log('已将数据保存到machineIdToParams，供run_evaluation_user.html使用');
                    
                    console.log('达梦数据库参数加载完成');
                    MachineDataManager.showUserFeedback('数据加载成功', 'success');
                } else {
                    console.warn('达梦数据库API调用失败，回退到localStorage');
                    MachineDataManager.showUserFeedback('数据库连接失败，使用本地数据', 'warning');
                    loadMachineParamsFromLocalStorage();
                }
                
            } catch (error) {
                console.error('从达梦数据库加载参数时发生错误:', error);
                console.warn('达梦数据库连接失败，回退到localStorage');
                MachineDataManager.showUserFeedback('数据库连接失败，使用本地数据', 'error');
                loadMachineParamsFromLocalStorage();
            }
        }
        
        // 增强的机床数据管理工具函数
        const MachineDataManager = {
            // 获取当前机床ID（严格验证）
            getCurrentMachineId: function() {
                const urlParams = new URLSearchParams(window.location.search);
                const machineId = urlParams.get('machine_id');
                
                if (!machineId) {
                    console.warn('未找到机床ID参数，无法进行数据隔离');
                    return null;
                }
                
                // 验证机床ID格式（必须是数字）
                if (!/^\d+$/.test(machineId)) {
                    console.error('机床ID格式无效，必须是数字:', machineId);
                    return null;
                }
                
                return parseInt(machineId);
            },
            
            // 获取特定机床的数据（严格隔离）
            getMachineData: function(machineId) {
                if (!machineId) {
                    console.warn('机床ID无效，无法获取数据');
                    return {};
                }
                
                const machineIdToParams = JSON.parse(localStorage.getItem('machineIdToParams') || '{}');
                const machineData = machineIdToParams[machineId] || {};
                
                console.log(`获取机床数据，机床ID: ${machineId}`, machineData);
                return machineData;
            },
            
            // 保存机床数据（严格隔离）
            saveMachineData: function(machineId, machineData) {
                if (!machineId) {
                    console.error('机床ID无效，无法保存数据');
                    return false;
                }
                
                // 验证数据完整性
                if (!machineData || typeof machineData !== 'object') {
                    console.error('机床数据无效，无法保存');
                    return false;
                }
                
                const machineIdToParams = JSON.parse(localStorage.getItem('machineIdToParams') || '{}');
                
                // 记录操作类型（创建或更新）
                const operationType = machineIdToParams[machineId] ? '更新' : '创建';
                
                machineIdToParams[machineId] = machineData;
                localStorage.setItem('machineIdToParams', JSON.stringify(machineIdToParams));
                
                console.log(`${operationType}机床数据成功，机床ID: ${machineId}`, machineData);
                console.log('当前存储的所有机床ID:', Object.keys(machineIdToParams));
                
                return true;
            },
            
            // 验证机床数据是否有效
            validateMachineData: function(machineData) {
                if (!machineData || typeof machineData !== 'object') {
                    return false;
                }
                
                // 根据机床类型检查关键字段
                const machineType = machineData.machine_type;
                
                if (machineType === 'boring_milling_machine') {
                    // 镗铣床必填字段
                    const requiredFields = ['column_measurement_range', 'worktable_x_range', 'spindle_box_y_range', 'worktable_length_lc'];
                    for (const field of requiredFields) {
                        if (machineData[field] === null || machineData[field] === undefined) {
                            console.warn(`镗铣床数据验证失败，缺少字段: ${field}`);
                            return false;
                        }
                    }
                } else {
                    // 加工中心必填字段（默认）
                    const requiredFields = ['x_axis_travel', 'y_axis_travel', 'z_axis_travel', 'worktable_length'];
                    for (const field of requiredFields) {
                        if (machineData[field] === null || machineData[field] === undefined) {
                            console.warn(`加工中心数据验证失败，缺少字段: ${field}`);
                            return false;
                        }
                    }
                }
                
                // 检查工件尺寸字段，如果存在但为空，则设置为默认值
                if (machineData.workpiece_size !== null && machineData.workpiece_size !== undefined && machineData.workpiece_size === '') {
                    console.warn('工件尺寸为空，设置为默认值320');
                    machineData.workpiece_size = '320';
                }
                
                return true;
            },
            
            // 数据验证和清理
            sanitizeMachineData: function(machineData) {
                if (!machineData || typeof machineData !== 'object') {
                    return {};
                }
                
                const sanitized = {};
                
                // 保留机床类型字段
                if (machineData.machine_type) {
                    sanitized.machine_type = machineData.machine_type;
                }
                
                // 加工中心数值字段验证和清理
                const numericFields = ['x_axis_travel', 'y_axis_travel', 'z_axis_travel', 'worktable_length'];
                numericFields.forEach(field => {
                    if (machineData[field] !== null && machineData[field] !== undefined) {
                        const value = parseFloat(machineData[field]);
                        sanitized[field] = isNaN(value) ? null : value;
                    } else {
                        sanitized[field] = null;
                    }
                });
                
                // 镗铣床数值字段验证和清理
                const boringMillingNumericFields = ['column_measurement_range', 'worktable_x_range', 'spindle_box_y_range', 'z_axis_measurement_range', 'worktable_length_lc', 'boring_axis_diameter', 'milling_axis_diameter'];
                boringMillingNumericFields.forEach(field => {
                    if (machineData[field] !== null && machineData[field] !== undefined) {
                        const value = parseFloat(machineData[field]);
                        sanitized[field] = isNaN(value) ? null : value;
                    } else {
                        sanitized[field] = null;
                    }
                });
                
                // 字符串字段验证和清理
                const stringFields = ['workpiece_size', 'spindle_type', 'worktable_type'];
                stringFields.forEach(field => {
                    if (machineData[field] !== null && machineData[field] !== undefined) {
                        sanitized[field] = String(machineData[field]).trim();
                    } else {
                        sanitized[field] = null;
                    }
                });
                
                return sanitized;
            },
            
            // 显示用户反馈
            showUserFeedback: function(message, type = 'info') {
                // 创建或更新用户反馈元素
                let feedbackElement = document.getElementById('machine-data-feedback');
                if (!feedbackElement) {
                    feedbackElement = document.createElement('div');
                    feedbackElement.id = 'machine-data-feedback';
                    feedbackElement.style.cssText = `
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        padding: 15px 20px;
                        border-radius: 5px;
                        z-index: 10000;
                        max-width: 400px;
                        font-size: 14px;
                        transition: all 0.3s ease;
                    `;
                    document.body.appendChild(feedbackElement);
                }
                
                // 设置样式基于类型
                const styles = {
                    success: { backgroundColor: '#d4edda', color: '#155724', border: '1px solid #c3e6cb' },
                    error: { backgroundColor: '#f8d7da', color: '#721c24', border: '1px solid #f5c6cb' },
                    warning: { backgroundColor: '#fff3cd', color: '#856404', border: '1px solid #ffeaa7' },
                    info: { backgroundColor: '#d1ecf1', color: '#0c5460', border: '1px solid #bee5eb' }
                };
                
                Object.assign(feedbackElement.style, styles[type]);
                feedbackElement.textContent = message;
                
                // 自动隐藏
                setTimeout(() => {
                    feedbackElement.style.opacity = '0';
                    setTimeout(() => {
                        if (feedbackElement.parentNode) {
                            feedbackElement.parentNode.removeChild(feedbackElement);
                        }
                    }, 300);
                }, 5000);
            }
        };
        
        // 从localStorage加载机床参数到表单的通用函数（备用）
        function loadMachineParamsFromLocalStorage() {
            console.log('开始从localStorage加载机床参数...');
            
            // 使用新的数据管理工具获取机床ID
            const machineId = MachineDataManager.getCurrentMachineId();
            
            if (!machineId) {
                console.log('当前为机床列表页面，使用全局默认数据初始化表单');
                // 机床列表页面：使用全局数据初始化表单
                const globalMachineParams = JSON.parse(localStorage.getItem('machine_params') || '{}');
                
                // 设置默认值（优先使用达梦数据库的数据，如果无效则使用1300而不是800）
                const defaultParams = {
                    x_axis_travel: globalMachineParams.x_axis_travel || null,
                    y_axis_travel: globalMachineParams.y_axis_travel || null,
                    z_axis_travel: globalMachineParams.z_axis_travel || null,
                    worktable_length: globalMachineParams.worktable_length || null,
                    workpiece_size: globalMachineParams.workpiece_size || null,
                    spindle_type: globalMachineParams.spindle_type || null
                };
                
                console.log('全局默认数据初始化参数:', defaultParams);
                
                loadParamsToForm('x-axis-travel', defaultParams.x_axis_travel);
                loadParamsToForm('y-axis-travel', defaultParams.y_axis_travel);
                loadParamsToForm('z-axis-travel', defaultParams.z_axis_travel);
                loadParamsToForm('worktable-length', defaultParams.worktable_length);
                loadParamsToForm('workpiece-size', defaultParams.workpiece_size);
                loadParamsToForm('spindle-type', defaultParams.spindle_type);
                
                // 同时初始化编辑表单
                loadParamsToForm('edit-x-axis-travel', defaultParams.x_axis_travel);
                loadParamsToForm('edit-y-axis-travel', defaultParams.y_axis_travel);
                loadParamsToForm('edit-z-axis-travel', defaultParams.z_axis_travel);
                loadParamsToForm('edit-worktable-length', defaultParams.worktable_length);
                loadParamsToForm('edit-workpiece-size', defaultParams.workpiece_size);
                loadParamsToForm('edit-spindle-type', defaultParams.spindle_type);
                
                return;
            }
            
            // 机床编辑页面：使用新的数据管理工具获取特定机床数据
            let machineParams = MachineDataManager.getMachineData(machineId);
            
            // 检查数据有效性 - 修正逻辑：1300可以是有效值
            const hasValidData = machineParams.x_axis_travel !== null && 
                               machineParams.x_axis_travel !== undefined &&
                               machineParams.y_axis_travel !== null && 
                               machineParams.y_axis_travel !== undefined &&
                               machineParams.z_axis_travel !== null && 
                               machineParams.z_axis_travel !== undefined &&
                               machineParams.worktable_length !== null && 
                               machineParams.worktable_length !== undefined;
            
            // 如果没有找到特定机床的有效数据，回退到全局machine_params
            if (!hasValidData || Object.keys(machineParams).length === 0) {
                machineParams = JSON.parse(localStorage.getItem('machine_params') || '{}');
                console.log('回退到全局machine_params:', machineParams);
                
                // 检查全局数据是否有效 - 修正逻辑：1300可以是有效值
                const globalHasValidData = machineParams.x_axis_travel !== null && 
                                         machineParams.x_axis_travel !== undefined &&
                                         machineParams.y_axis_travel !== null && 
                                         machineParams.y_axis_travel !== undefined &&
                                         machineParams.z_axis_travel !== null && 
                                         machineParams.z_axis_travel !== undefined &&
                                         machineParams.worktable_length !== null && 
                                         machineParams.worktable_length !== undefined;
                
                if (!globalHasValidData) {
                    console.warn('全局machine_params也无效，使用空数据');
                    machineParams = {};
                }
            } else {
                console.log('从机床ID映射加载的有效machine_params:', machineParams, '机床ID:', machineId);
            }
            
            // 检查数据有效性，如果主要数值字段都为null，尝试使用默认值
            const hasNonNullData = machineParams.x_axis_travel !== null || 
                                  machineParams.y_axis_travel !== null || 
                                  machineParams.z_axis_travel !== null || 
                                  machineParams.worktable_length !== null;
            
            if (!hasNonNullData) {
                console.log('检测到localStorage数据可能被清空，尝试使用默认值');
                
                // 如果数据无效，使用默认值
                const defaultParams = {
                    x_axis_travel: null,
                    y_axis_travel: null,
                    z_axis_travel: null,
                    worktable_length: null,
                    workpiece_size: null,
                    spindle_type: null
                };
                
                // 合并现有数据（保留可能有效的字段如spindle_type）
                const mergedParams = { ...defaultParams, ...machineParams };
                console.log('合并后的参数:', mergedParams);
                
                // 加载合并后的数据
                loadParamsToForm('x-axis-travel', mergedParams.x_axis_travel);
                loadParamsToForm('y-axis-travel', mergedParams.y_axis_travel);
                loadParamsToForm('z-axis-travel', mergedParams.z_axis_travel);
                loadParamsToForm('worktable-length', mergedParams.worktable_length);
                loadParamsToForm('workpiece-size', mergedParams.workpiece_size);
                loadParamsToForm('spindle-type', mergedParams.spindle_type);
                
                loadParamsToForm('edit-x-axis-travel', mergedParams.x_axis_travel);
                loadParamsToForm('edit-y-axis-travel', mergedParams.y_axis_travel);
                loadParamsToForm('edit-z-axis-travel', mergedParams.z_axis_travel);
                loadParamsToForm('edit-worktable-length', mergedParams.worktable_length);
                loadParamsToForm('edit-workpiece-size', mergedParams.workpiece_size);
                loadParamsToForm('edit-spindle-type', mergedParams.spindle_type);
            } else {
                // 数据有效，正常加载
                loadParamsToForm('x-axis-travel', machineParams.x_axis_travel);
                loadParamsToForm('y-axis-travel', machineParams.y_axis_travel);
                loadParamsToForm('z-axis-travel', machineParams.z_axis_travel);
                loadParamsToForm('worktable-length', machineParams.worktable_length);
                loadParamsToForm('workpiece-size', machineParams.workpiece_size);
                loadParamsToForm('spindle-type', machineParams.spindle_type);
                
                loadParamsToForm('edit-x-axis-travel', machineParams.x_axis_travel);
                loadParamsToForm('edit-y-axis-travel', machineParams.y_axis_travel);
                loadParamsToForm('edit-z-axis-travel', machineParams.z_axis_travel);
                loadParamsToForm('edit-worktable-length', machineParams.worktable_length);
                loadParamsToForm('edit-workpiece-size', machineParams.workpiece_size);
                loadParamsToForm('edit-spindle-type', machineParams.spindle_type);
            }
            
            console.log('localStorage参数加载完成');
            
            // 将数据保存到machineIdToParams，供run_evaluation_user.html使用
            if (machineId) {
                const machineIdToParams = JSON.parse(localStorage.getItem('machineIdToParams') || '{}');
                machineIdToParams[machineId] = machineParams;
                localStorage.setItem('machineIdToParams', JSON.stringify(machineIdToParams));
                console.log('已将数据保存到machineIdToParams，供run_evaluation_user.html使用，机床ID:', machineId, '数据:', machineParams);
            }
        }
        
        // 加载参数到指定表单元素的辅助函数
        function loadParamsToForm(elementId, value) {
            const element = document.getElementById(elementId);
            if (element && value !== undefined && value !== null) {
                // 确保元素可见
                element.style.display = 'block';
                element.style.visibility = 'visible';
                element.style.opacity = '1';
                
                if (element.type === 'select-one') {
                    // 对于下拉框，设置对应的选项
                    element.value = value;
                    // 触发change事件确保选项正确显示
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                } else {
                    // 对于输入框，直接设置值
                    element.value = value;
                    // 触发input事件确保值正确显示
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                }
                
                // 强制重绘确保DOM更新
                element.offsetHeight;
                
                console.log(`加载参数到 ${elementId}:`, value, '元素:', element);
            }
        }
        
        // 显示添加机床表单
        document.getElementById('add-machine-btn').addEventListener('click', function() {
            document.getElementById('add-machine-form').style.display = 'block';
        });
        
        // 隐藏添加机床表单
        document.getElementById('cancel-add-machine').addEventListener('click', function() {
            document.getElementById('add-machine-form').style.display = 'none';
        });
        
        // 初始化机床类型表单
        initMachineTypeForms();
        
        // 表单提交处理
        
        const form = document.getElementById('machine-form');
        if (form) {
            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                
                // 前端验证
                const machineNameElement = document.getElementById('machine-name');
                const reportNumberElement = document.getElementById('report-number');
                const machineName = machineNameElement ? machineNameElement.value : '';
                const reportNumber = reportNumberElement ? reportNumberElement.value : '';
                
                // 验证报告编号唯一性
                const machineMap = JSON.parse(localStorage.getItem('machineMap') || '{}');
                let reportNumberExists = false;
                Object.values(machineMap).forEach(machine => {
                    if (machine.report_number === reportNumber) {
                        reportNumberExists = true;
                    }
                });
                if (reportNumberExists) {
                    alert('报告编号已存在，请使用不同的报告编号');
                    return;
                }
                
                const machineTypeElement = document.getElementById('machine-type');
                const machineType = machineTypeElement ? machineTypeElement.value : null;
                
                if (!machineType) {
                    console.error('找不到机床类型');
                    alert('机床类型错误，请刷新页面重试');
                    return;
                }
                
                if (machineType === 'machining_center') {
                    const xAxisTravelElement = document.getElementById('x-axis-travel');
                    const yAxisTravelElement = document.getElementById('y-axis-travel');
                    const zAxisTravelElement = document.getElementById('z-axis-travel');
                    const worktableLengthElement = document.getElementById('worktable-length');
                    
                    const xAxisTravel = xAxisTravelElement ? xAxisTravelElement.value : '';
                    const yAxisTravel = yAxisTravelElement ? yAxisTravelElement.value : '';
                    const zAxisTravel = zAxisTravelElement ? zAxisTravelElement.value : '';
                    const worktableLength = worktableLengthElement ? worktableLengthElement.value : '';
                    
                    // 验证必填字段
                    if (!xAxisTravel || !yAxisTravel || !zAxisTravel || !worktableLength) {
                        alert('请填写加工中心的所有必填参数');
                        return;
                    }
                    
                    // 验证数值有效性
                    if (isNaN(parseFloat(xAxisTravel)) || parseFloat(xAxisTravel) <= 0) {
                        alert('X轴行程必须是大于0的数值');
                        return;
                    }
                    if (isNaN(parseFloat(yAxisTravel)) || parseFloat(yAxisTravel) <= 0) {
                        alert('Y轴行程必须是大于0的数值');
                        return;
                    }
                    if (isNaN(parseFloat(zAxisTravel)) || parseFloat(zAxisTravel) <= 0) {
                        alert('Z轴行程必须是大于0的数值');
                        return;
                    }
                    if (isNaN(parseFloat(worktableLength)) || parseFloat(worktableLength) <= 0) {
                        alert('工作台长度必须是大于0的数值');
                        return;
                    }
                } else if (machineType === 'boring_milling_machine') {
                    const columnRangeElement = document.getElementById('boring-milling-column-range');
                    const worktableXRangeElement = document.getElementById('boring-milling-worktable-x-range');
                    const spindleBoxYRangeElement = document.getElementById('boring-milling-spindle-box-y-range');
                    const worktableLengthLcElement = document.getElementById('boring-milling-worktable-length-lc');
                    const boringAxisDiameterElement = document.getElementById('boring-milling-boring-axis-diameter');
                    const millingAxisDiameterElement = document.getElementById('boring-milling-milling-axis-diameter');
                    const worktableTypeElement = document.getElementById('boring-milling-worktable-type');
                    
                    const columnRange = columnRangeElement ? columnRangeElement.value : '';
                    const worktableXRange = worktableXRangeElement ? worktableXRangeElement.value : '';
                    const spindleBoxYRange = spindleBoxYRangeElement ? spindleBoxYRangeElement.value : '';
                    const worktableLengthLc = worktableLengthLcElement ? worktableLengthLcElement.value : '';
                    const boringAxisDiameter = boringAxisDiameterElement ? boringAxisDiameterElement.value : '';
                    const millingAxisDiameter = millingAxisDiameterElement ? millingAxisDiameterElement.value : '';
                    const worktableType = worktableTypeElement ? worktableTypeElement.value : '';
                    
                    // 验证必填字段
                    if (!columnRange || !worktableXRange || !spindleBoxYRange || !worktableLengthLc || !boringAxisDiameter || !millingAxisDiameter || !worktableType) {
                        alert('请填写镗铣床的所有必填参数');
                        return;
                    }
                    
                    // 验证数值有效性
                    if (isNaN(parseFloat(columnRange)) || parseFloat(columnRange) <= 0) {
                        alert('立柱测量范围必须是大于0的数值');
                        return;
                    }
                    if (isNaN(parseFloat(worktableXRange)) || parseFloat(worktableXRange) <= 0) {
                        alert('工作台X轴测量范围必须是大于0的数值');
                        return;
                    }
                    if (isNaN(parseFloat(spindleBoxYRange)) || parseFloat(spindleBoxYRange) <= 0) {
                        alert('主轴箱Y轴测量范围必须是大于0的数值');
                        return;
                    }
                    if (isNaN(parseFloat(worktableLengthLc)) || parseFloat(worktableLengthLc) <= 0) {
                        alert('工作台长边长度必须是大于0的数值');
                        return;
                    }
                    if (isNaN(parseFloat(boringAxisDiameter)) || parseFloat(boringAxisDiameter) <= 0) {
                        alert('镗轴直径必须是大于0的数值');
                        return;
                    }
                    if (isNaN(parseFloat(millingAxisDiameter)) || parseFloat(millingAxisDiameter) <= 0) {
                        alert('铣轴直径必须是大于0的数值');
                        return;
                    }
                }
                
                // 获取表单数据
                const formData = new FormData(form);
                
                // 发送AJAX请求
                fetch(window.APP_URLS.add_machine, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': form.querySelector('input[name="csrfmiddlewaretoken"]').value
                    }
                })
                .then(response => response.json())
                .then(async data => {
                    if (data.success) {
                        // 显示成功弹窗
                        alert(data.message);
                        
                        // 动态添加新机床到表格
                        const tbody = document.querySelector('table.table-striped tbody');
                        
                        // 检查是否有暂无数据的提示
                        const noDataRow = tbody.querySelector('tr td[colspan="6"]');
                        if (noDataRow) {
                            noDataRow.closest('tr').remove();
                        }
                        
                        // 创建新行
                        const newRow = document.createElement('tr');
                        
                        newRow.innerHTML = `
                            <td>${data.machine.id}</td>
                            <td>${data.machine.name}</td>
                            <td>${data.machine.model}</td>
                            <td>${data.machine.report_number}</td>
                            <td>${data.machine.manufacturer || ''}</td>
                            <td>${data.machine.created_at}</td>
                            <td>${data.machine.machine_type_display}</td>
                            <td>
                                <a href="#" class="btn btn-sm btn-primary edit-btn" data-id="${data.machine.id}">编辑</a>
                                <a href="#" class="btn btn-sm btn-danger delete-btn" data-id="${data.machine.id}">删除</a>
                            </td>
                        `;
                        
                        // 添加到表格
                        tbody.appendChild(newRow);
                        
                        // 为新添加的按钮添加事件监听器
                        addEventListeners();
                        
                        // 检查是否是加工中心，如果是则存储参数到localStorage并调用允差API
                        if (data.machine.machine_type === 'machining_center') {
                            // 优先使用表单中的用户提交数据，而不是后端返回的数据
                            const formData = new FormData(form);
                            const machineParams = {
                                x_axis_travel: parseFloat(formData.get('x_axis_travel')) || data.machine.x_axis_travel,
                                y_axis_travel: parseFloat(formData.get('y_axis_travel')) || data.machine.y_axis_travel,
                                z_axis_travel: parseFloat(formData.get('z_axis_travel')) || data.machine.z_axis_travel,
                                worktable_length: parseFloat(formData.get('worktable_length')) || data.machine.worktable_length,
                                workpiece_size: formData.get('workpiece_size') || data.machine.workpiece_size,
                                spindle_type: formData.get('spindle_type') || data.machine.spindle_type,
                                measured_x: data.machine.measured_x,
                                measured_y: data.machine.measured_y,
                                measured_z: data.machine.measured_z
                            };
                            
                            console.log('用户提交的表单数据:', {
                                x_axis_travel: formData.get('x_axis_travel'),
                                y_axis_travel: formData.get('y_axis_travel'),
                                z_axis_travel: formData.get('z_axis_travel'),
                                worktable_length: formData.get('worktable_length'),
                                workpiece_size: formData.get('workpiece_size'),
                                spindle_type: formData.get('spindle_type')
                            });
                            
                            console.log('后端返回的数据:', {
                                x_axis_travel: data.machine.x_axis_travel,
                                y_axis_travel: data.machine.y_axis_travel,
                                z_axis_travel: data.machine.z_axis_travel,
                                worktable_length: data.machine.worktable_length,
                                workpiece_size: data.machine.workpiece_size,
                                spindle_type: data.machine.spindle_type
                            });
                            
                            // 检查后端返回的数据是否有效，避免用null值覆盖表单数据
                            // 只有当所有关键字段都不为null时才更新localStorage
                            const hasValidData = machineParams.x_axis_travel !== null && 
                                                machineParams.y_axis_travel !== null && 
                                                machineParams.z_axis_travel !== null && 
                                                machineParams.worktable_length !== null;
                            
                            // 验证机床ID的唯一性和有效性
                            if (!data.machine.id) {
                                console.error('机床ID无效，无法存储参数映射');
                                return;
                            }
                            
                            // 使用增强的数据保存函数保存机床数据
                            const saveSuccess = await saveMachineParamsToDameng('x-axis-travel', 'y-axis-travel', 'z-axis-travel', 'worktable-length', 'workpiece-size', 'spindle-type', data.machine.id);
                            
                            if (!saveSuccess) {
                                console.error('机床数据保存失败，机床ID:', data.machine.id);
                                return;
                            }
                            
                            // 存储机床名称和型号的映射关系
                            const machineMap = JSON.parse(localStorage.getItem('machineMap') || '{}');
                            machineMap[data.machine.name] = {
                                model: data.machine.model,
                                id: data.machine.id
                            };
                            localStorage.setItem('machineMap', JSON.stringify(machineMap));
                            
                            // 不再更新全局machine_params，避免数据同步问题
                            console.log('跳过更新全局machine_params，避免数据同步问题');
                            
                            // 调用允差API获取组别1的允差值
                            fetch('/evaluation/api/get-tolerances-by-machine-data/', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': form.querySelector('input[name="csrfmiddlewaretoken"]').value
                                },
                                body: JSON.stringify({
                                    machine_id: data.machine.id,  // 提供机床ID用于数据持久化
                                    machine_type: data.machine.machine_type,
                                    x_axis_travel: data.machine.x_axis_travel,
                                    y_axis_travel: data.machine.y_axis_travel,
                                    z_axis_travel: data.machine.z_axis_travel,
                                    worktable_length: data.machine.worktable_length,
                                    workpiece_size: data.machine.workpiece_size,
                                    spindle_type: data.machine.spindle_type,
                                    measured_x: data.machine.measured_x,
                                    measured_y: data.machine.measured_y,
                                    measured_z: data.machine.measured_z
                                })
                            })
                            .then(response => response.json())
                            .then(toleranceData => {
                                if (toleranceData.success) {
                                    // 存储允差值到localStorage
                                    localStorage.setItem('tolerance_group_1', JSON.stringify(toleranceData.tolerance_group_1));
                                    
                                    // 显示成功消息
                                    alert('机床数据保存成功！组别1允差值已自动计算并保存。');
                                } else {
                                    alert('机床数据保存成功，但获取允差值失败：' + toleranceData.error);
                                }
                            })
                            .catch(error => {
                                alert('机床数据保存成功，但调用允差API失败，请稍后手动获取允差值。');
                            });
                        } else if (data.machine.machine_type === 'boring_milling_machine') {
                            console.log('镗铣床添加成功，开始保存参数到达梦数据库...');
                            
                            const saveSuccess = await saveBoringMillingParamsToDameng(
                                'boring-milling-column-range',
                                'boring-milling-worktable-x-range',
                                'boring-milling-spindle-box-y-range',
                                'boring-milling-z-axis-range',
                                'boring-milling-worktable-length-lc',
                                'boring-milling-boring-axis-diameter',
                                'boring-milling-milling-axis-diameter',
                                'boring-milling-worktable-type',
                                data.machine.id
                            );
                            
                            if (!saveSuccess) {
                                console.error('镗铣床参数保存到达梦数据库失败，机床ID:', data.machine.id);
                            } else {
                                console.log('镗铣床参数保存到达梦数据库成功');
                            }
                            
                            // 存储机床名称和型号的映射关系
                            const machineMap = JSON.parse(localStorage.getItem('machineMap') || '{}');
                            machineMap[data.machine.name] = {
                                model: data.machine.model,
                                id: data.machine.id
                            };
                            localStorage.setItem('machineMap', JSON.stringify(machineMap));
                            
                            alert('镗铣床数据保存成功！允差获取成功，数据已保存到数据库。');
                        }
                        
                        // 清空表单
                        form.reset();
                        
                        // 隐藏表单
                        document.getElementById('add-machine-form').style.display = 'none';
                    } else {
                        // 显示错误弹窗
                        alert(data.message);
                    }
                })
                .catch(error => {
                    console.error('编辑表单提交失败:', error);
                    console.error('错误详情:', error.message);
                    console.error('错误堆栈:', error.stack);
                    alert('网络错误: ' + error.message + '\n请重试或查看控制台获取详细信息');
                });
            });
        }
        
        // 添加事件监听器
        function addEventListeners() {
            // 为所有删除按钮添加点击事件监听器
            document.querySelectorAll('.delete-btn').forEach(btn => {
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    // 获取机床ID
                    const machineId = this.getAttribute('data-id');
                    
                    // 确认删除
                    if (confirm('确定要删除这台机床吗？')) {
                        // 发送AJAX请求
                        fetch(`/data/machines/delete/${machineId}/`, {
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value,
                                'Content-Type': 'application/json'
                            }
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                // 显示成功弹窗
                                alert(data.message);
                                
                                // 刷新页面
                                window.location.reload();
                                
                                // 从localStorage中删除对应的映射关系
                                const machineMap = JSON.parse(localStorage.getItem('machineMap') || '{}');
                                const machineIdToParams = JSON.parse(localStorage.getItem('machineIdToParams') || '{}');
                                
                                // 先查找要删除的机床名称
                                let machineNameToDelete = null;
                                Object.keys(machineMap).forEach(function(name) {
                                    if (machineMap[name].id == machineId) {
                                        machineNameToDelete = name;
                                    }
                                });
                                
                                // 删除映射关系
                                if (machineNameToDelete) {
                                    delete machineMap[machineNameToDelete];
                                    localStorage.setItem('machineMap', JSON.stringify(machineMap));
                                }
                                
                                // 删除机床ID到参数的映射
                                if (machineIdToParams[machineId]) {
                                    delete machineIdToParams[machineId];
                                    localStorage.setItem('machineIdToParams', JSON.stringify(machineIdToParams));
                                }
                                
                                // 移除表格行
                                this.closest('tr').remove();
                                
                                // 检查表格是否为空
                                const tbody = document.querySelector('table.table-striped tbody');
                                if (tbody.children.length === 0) {
                                    // 添加暂无数据提示
                                    const noDataRow = document.createElement('tr');
                                    noDataRow.innerHTML = `
                                        <td colspan="6" class="text-center">
                                            <p class="text-muted">暂无机床数据，请先添加机床信息。</p>
                                        </td>
                                    `;
                                    tbody.appendChild(noDataRow);
                                }
                            } else {
                                // 显示错误弹窗
                                alert(data.message);
                            }
                        })
                        .catch(error => {
                            // 显示网络错误弹窗
                            alert('网络错误，请重试');
                        });
                    }
                });
            });
            
            // 为所有编辑按钮添加点击事件监听器
            document.querySelectorAll('.edit-btn').forEach(btn => {
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    // 获取机床ID
                    const machineId = this.getAttribute('data-id');
                    
                    // 隐藏添加表单
                    document.getElementById('add-machine-form').style.display = 'none';
                    
                    // 显示编辑表单前清空表单
                    document.getElementById('edit-machine-form').style.display = 'block';
                    
                    // 清空所有表单元素的值
                    const editForm = document.getElementById('edit-machine-form-form');
                    if (editForm) {
                        editForm.reset();
                        console.log('编辑表单已清空');
                    }
                    
                    // 将machineId添加到URL参数中
                    const url = new URL(window.location.href);
                    url.searchParams.set('machine_id', machineId);
                    window.history.pushState({}, '', url);
                    
                    // 获取机床信息
                    fetch(`/data/machines/edit/${machineId}/`, {
                        method: 'GET',
                        headers: {
                            'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
                        }
                    })
                    .then(response => {
                        console.log('编辑请求响应状态:', response.status);
                        return response.json();
                    })
                    .then(data => {
                        console.log('编辑请求响应数据:', data);
                        console.log('worktable_length_lc 响应值:', data.machine ? data.machine.worktable_length_lc : 'machine 对象不存在');
                        console.log('完整的 machine 对象:', data.machine);
                        console.log('machine 对象的所有字段:', data.machine ? Object.keys(data.machine) : 'machine 对象不存在');
                        if (data && data.success) {
                            // 简化并优化数据填充逻辑
                            const fillFormData = (machineData) => {
                                const editMachineIdInput = document.getElementById('edit-machine-id');
                                if (editMachineIdInput) {
                                    editMachineIdInput.value = machineData.id;
                                }
                                document.getElementById('edit-machine-name').value = machineData.name || '';
                                document.getElementById('edit-machine-number').value = machineData.machine_number || '';
                                document.getElementById('edit-machine-report-number').value = machineData.report_number || '';
                                document.getElementById('edit-specification-model').value = machineData.model || '';
                                document.getElementById('edit-machine-manufacturer').value = machineData.manufacturer || '';
                                document.getElementById('edit-production-date').value = machineData.production_date || '';

                                // 正确设置机床类型选择框
                                const machineTypeSelect = document.getElementById('edit-machine-type');
                                if (machineTypeSelect) {
                                    console.log('设置机床类型选择框，后端数据:', machineData.machine_type);
                                    console.log('选择框选项:', Array.from(machineTypeSelect.options).map(opt => ({value: opt.value, text: opt.text})));
                                    
                                    let found = false;
                                    for (let option of machineTypeSelect.options) {
                                        if (option.value === machineData.machine_type) {
                                            option.selected = true;
                                            found = true;
                                            console.log('找到匹配的机床类型选项:', option.value, option.text);
                                            break;
                                        }
                                    }
                                    if (!found && machineTypeSelect.options.length > 0) {
                                        machineTypeSelect.options[0].selected = true;
                                        console.log('未找到匹配选项，默认选择第一个选项:', machineTypeSelect.options[0].value);
                                    }
                                    
                                    // 验证设置结果
                                    console.log('机床类型选择框设置完成，当前选中值:', machineTypeSelect.value);
                                }
                                
                                // 智能数据填充函数 - 优先使用用户修改的数据
                                const setValueSafely = (elementId, value) => {
                                    const element = document.getElementById(elementId);
                                    if (element) {
                                        // 确保元素可见
                                        element.style.display = 'block';
                                        element.style.visibility = 'visible';
                                        element.style.opacity = '1';
                                        
                                        // 优先使用基于机床ID的独立数据
                                        // 严格基于机床ID加载数据，避免数据共用
                                        const machineIdToParams = JSON.parse(localStorage.getItem('machineIdToParams') || '{}');
                                        let machineParams = {};
                                        
                                        // 优先使用特定机床ID的数据
                                        if (machineData.id && machineIdToParams[machineData.id]) {
                                            machineParams = machineIdToParams[machineData.id];
                                            console.log(`使用机床ID特定数据，机床ID: ${machineData.id}`, machineParams);
                                        } else {
                                            // 如果没有找到特定机床数据，使用全局数据作为备用
                                            machineParams = JSON.parse(localStorage.getItem('machine_params') || '{}');
                                            console.log(`未找到机床ID特定数据，使用全局数据，机床ID: ${machineData.id}`);
                                        }
                                        
                                        // 字段名映射：将 HTML ID 转换为数据库字段名
                                        let fieldName;
                                        
                                        // 特殊处理镗铣床参数
                                        if (elementId.startsWith('edit-boring-milling-')) {
                                            const boringMillingFieldName = elementId.replace('edit-boring-milling-', '');
                                            
                                            if (boringMillingFieldName === 'column-range') {
                                                fieldName = 'column_measurement_range';
                                            } else if (boringMillingFieldName === 'worktable-x-range') {
                                                fieldName = 'worktable_x_range';
                                            } else if (boringMillingFieldName === 'spindle-box-y-range') {
                                                fieldName = 'spindle_box_y_range';
                                            } else if (boringMillingFieldName === 'z-axis-range') {
                                                fieldName = 'z_axis_measurement_range';
                                            } else if (boringMillingFieldName === 'worktable-length-lc') {
                                                fieldName = 'worktable_length_lc';
                                            } else if (boringMillingFieldName === 'boring-axis-diameter') {
                                                fieldName = 'boring_axis_diameter';
                                            } else if (boringMillingFieldName === 'milling-axis-diameter') {
                                                fieldName = 'milling_axis_diameter';
                                            } else if (boringMillingFieldName === 'worktable-type') {
                                                fieldName = 'worktable_type';
                                            } else {
                                                fieldName = boringMillingFieldName.replace(/-/g, '_');
                                            }
                                            console.log(`镗铣床字段映射：${elementId} -> ${fieldName}`);
                                        } else {
                                            // 普通字段：直接转换
                                            fieldName = elementId.replace('edit-', '').replace(/-/g, '_');
                                        }
                                        
                                        let localStorageValue = machineParams[fieldName];
                                        
                                        console.log(`查找 localStorage 数据 ${elementId}:`, '字段名:', fieldName, '机床 ID 数据:', machineParams[fieldName], '全局数据:', JSON.parse(localStorage.getItem('machine_params') || '{}')[fieldName]);
                                        
                                        // 如果基于机床ID的数据无效，尝试从全局数据获取（备用方案）
                                        if (localStorageValue === null || localStorageValue === undefined || localStorageValue === '') {
                                            const globalMachineParams = JSON.parse(localStorage.getItem('machine_params') || '{}');
                                            localStorageValue = globalMachineParams[fieldName];
                                            console.log(`回退到全局machine_params获取 ${elementId}:`, localStorageValue);
                                        }
                                        
                                        let finalValue = value;
                                        
                                        // 数据优先级：后端数据库数据 > localStorage数据 > 默认值
                                        // 编辑时应优先显示数据库中实际保存的值
                                        if (value !== null && value !== undefined && value !== '') {
                                            // 优先使用后端数据库数据（最新保存的值）
                                            if (element.type === 'select-one') {
                                                finalValue = value.toString();
                                            } else {
                                                finalValue = value;
                                            }
                                            console.log(`优先使用后端数据库数据 ${elementId}:`, finalValue, '后端原始值:', value);
                                        } else if (localStorageValue !== null && localStorageValue !== undefined && localStorageValue !== '') {
                                            // 使用localStorage中的数据作为备用
                                            if (element.type === 'select-one') {
                                                finalValue = localStorageValue.toString();
                                            } else {
                                                finalValue = localStorageValue;
                                            }
                                            console.log(`使用localStorage备用数据 ${elementId}:`, finalValue, '后端原始值:', value);
                                        } else {
                                            // 如果后端数据和localStorage都没有有效值，保持为空
                                            finalValue = '';
                                            console.log(`没有有效数据 ${elementId}，保持为空`);
                                        }
                                        
                                        // 直接设置值，避免复杂的DOM操作
                                        element.value = finalValue || '';
                                        
                                        // 触发相应事件确保值正确显示
                                        if (element.type === 'select-one') {
                                            element.dispatchEvent(new Event('change', { bubbles: true }));
                                        } else {
                                            element.dispatchEvent(new Event('input', { bubbles: true }));
                                        }
                                        
                                        // 强制重绘确保DOM更新
                                        element.offsetHeight;
                                        
                                        console.log(`最终设置表单值 ${elementId}:`, finalValue, '后端原始值:', value, '元素:', element);
                                    }
                                };
                                
                                // 填充加工中心参数
                                setValueSafely('edit-x-axis-travel', machineData.x_axis_travel);
                                setValueSafely('edit-y-axis-travel', machineData.y_axis_travel);
                                setValueSafely('edit-z-axis-travel', machineData.z_axis_travel);
                                setValueSafely('edit-worktable-length', machineData.worktable_length);
                                setValueSafely('edit-workpiece-size', machineData.workpiece_size);
                                setValueSafely('edit-spindle-type', machineData.spindle_type);
                                
                                // 根据机床类型填充对应的参数
                                if (machineData.machine_type === 'boring_milling_machine') {
                                    setValueSafely('edit-boring-milling-column-range', machineData.column_measurement_range);
                                    setValueSafely('edit-boring-milling-worktable-x-range', machineData.worktable_x_range);
                                    setValueSafely('edit-boring-milling-spindle-box-y-range', machineData.spindle_box_y_range);
                                    setValueSafely('edit-boring-milling-z-axis-range', machineData.z_axis_measurement_range);
                                    
                                    setValueSafely('edit-boring-milling-worktable-length-lc', machineData.worktable_length_lc);
                                    
                                    setValueSafely('edit-boring-milling-boring-axis-diameter', machineData.boring_axis_diameter);
                                    setValueSafely('edit-boring-milling-milling-axis-diameter', machineData.milling_axis_diameter);
                                    setValueSafely('edit-boring-milling-worktable-type', machineData.worktable_type);
                                } else {
                                    console.log('加工中心，清空镗铣床参数');
                                    setValueSafely('edit-boring-milling-column-range', null);
                                    setValueSafely('edit-boring-milling-worktable-x-range', null);
                                    setValueSafely('edit-boring-milling-spindle-box-y-range', null);
                                    setValueSafely('edit-boring-milling-z-axis-range', null);
                                    setValueSafely('edit-boring-milling-worktable-length-lc', null);
                                    setValueSafely('edit-boring-milling-boring-axis-diameter', null);
                                    setValueSafely('edit-boring-milling-milling-axis-diameter', null);
                                    setValueSafely('edit-boring-milling-worktable-type', null);
                                }
                                
                                // 调试：输出完整的 machineData
                                console.log('machineData 完整内容:', machineData);
                                console.log('machineData.machine_type:', machineData.machine_type);
                                console.log('machineData.id:', machineData.id);
                                console.log('machineData.name:', machineData.name);
                                
                                // 使用统一的表单显示控制函数来确保一致性
                                const editMachineTypeSelect = document.getElementById('edit-machine-type');
                                const editHorizontalMachiningForm = document.getElementById('edit-horizontal-machining-form');
                                const editBoringMillingForm = document.getElementById('edit-boring-milling-form');
                                
                                console.log('表单元素检查:', {
                                    editMachineTypeSelect: !!editMachineTypeSelect,
                                    editHorizontalMachiningForm: !!editHorizontalMachiningForm,
                                    editBoringMillingForm: !!editBoringMillingForm
                                });
                                
                                if (editMachineTypeSelect && editHorizontalMachiningForm && editBoringMillingForm) {
                                    // 调试：输出机床类型
                                    console.log('机床类型检查:', 'machineData.machine_type =', machineData.machine_type);
                                    
                                    // 强制显示正确的参数表单
                                    if (machineData.machine_type === 'machining_center') {
                                        console.log('强制显示加工中心参数表单');
                                        // 立即显示加工中心表单
                                        editHorizontalMachiningForm.style.setProperty('display', 'block', 'important');
                                        editHorizontalMachiningForm.style.setProperty('visibility', 'visible', 'important');
                                        editHorizontalMachiningForm.style.setProperty('opacity', '1', 'important');
                                        editHorizontalMachiningForm.classList.remove('d-none', 'hidden', 'invisible', 'collapse');
                                        editHorizontalMachiningForm.classList.add('d-block', 'visible');
                                        
                                        // 隐藏镗铣床表单 - 彻底重置所有显示相关属性
                                        editBoringMillingForm.style.removeProperty('display');
                                        editBoringMillingForm.style.removeProperty('visibility');
                                        editBoringMillingForm.style.removeProperty('opacity');
                                        editBoringMillingForm.style.display = 'none';
                                        editBoringMillingForm.classList.remove('d-block', 'visible');
                                        editBoringMillingForm.classList.add('d-none');
                                    } else if (machineData.machine_type === 'boring_milling_machine') {
                                        console.log('强制显示镗铣床参数表单');
                                        // 立即显示镗铣床表单
                                        editBoringMillingForm.style.setProperty('display', 'block', 'important');
                                        editBoringMillingForm.style.setProperty('visibility', 'visible', 'important');
                                        editBoringMillingForm.style.setProperty('opacity', '1', 'important');
                                        editBoringMillingForm.classList.remove('d-none', 'hidden', 'invisible', 'collapse');
                                        editBoringMillingForm.classList.add('d-block', 'visible');
                                        
                                        // 隐藏加工中心表单 - 彻底重置所有显示相关属性
                                        editHorizontalMachiningForm.style.removeProperty('display');
                                        editHorizontalMachiningForm.style.removeProperty('visibility');
                                        editHorizontalMachiningForm.style.removeProperty('opacity');
                                        editHorizontalMachiningForm.style.display = 'none';
                                        editHorizontalMachiningForm.classList.remove('d-block', 'visible');
                                        editHorizontalMachiningForm.classList.add('d-none');
                                    } else {
                                        // 其他机床类型，隐藏所有参数表单
                                        editHorizontalMachiningForm.style.display = 'none';
                                        editHorizontalMachiningForm.classList.remove('d-block', 'visible');
                                        editHorizontalMachiningForm.classList.add('d-none');
                                        editBoringMillingForm.style.display = 'none';
                                        editBoringMillingForm.classList.remove('d-block', 'visible');
                                        editBoringMillingForm.classList.add('d-none');
                                    }
                                    
                                    // 强制重绘确保DOM更新
                                    editHorizontalMachiningForm.offsetHeight;
                                    editBoringMillingForm.offsetHeight;
                                }
                            };
                            
                            // 执行数据填充
                            fillFormData(data.machine);
                            
                            // 重新绑定实时同步机床型号到表格的事件监听器
                            const editMachineNameInput = document.getElementById('edit-machine-name');
                            if (editMachineNameInput) {
                                // 移除之前的事件监听器（如果有）
                                const newInput = editMachineNameInput.cloneNode(true);
                                editMachineNameInput.parentNode.replaceChild(newInput, editMachineNameInput);
                                
                                // 重新添加事件监听器
                                newInput.addEventListener('input', function() {
                                    const currentMachineId = document.getElementById('edit-machine-id').value;
                                    const machineName = this.value;
                                    
                                    console.log('机床型号输入变化:', machineName, '机床ID:', currentMachineId);
                                    
                                    // 更新表格中对应行的机床型号
                                    const rows = document.querySelectorAll('table.table-striped tbody tr');
                                    rows.forEach(row => {
                                        const editBtn = row.querySelector('.edit-btn');
                                        if (editBtn && editBtn.getAttribute('data-id') === currentMachineId) {
                                            row.children[1].textContent = machineName;
                                            console.log('更新表格行机床型号:', machineName);
                                        }
                                    });
                                });
                                
                                console.log('实时同步事件监听器已重新绑定');
                            }
                            
                            // 根据机床类型从达梦数据库加载参数
                            // 镗铣床参数仅存储在达梦数据库中，必须从达梦数据库加载
                            // 加工中心参数如果MySQL中不完整，也从达梦数据库加载
                            const machineType = data.machine.machine_type;
                            if (machineType === 'boring_milling_machine') {
                                console.log('镗铣床类型，从达梦数据库加载参数');
                                loadMachineParamsFromDameng();
                            } else if (!data.machine.x_axis_travel || !data.machine.y_axis_travel || !data.machine.z_axis_travel) {
                                console.log('加工中心后端数据不完整，尝试从达梦数据库获取数据');
                                loadMachineParamsFromDameng();
                            }
                        } else {
                            // 显示错误弹窗
                            alert(data.message);
                            // 隐藏编辑表单
                            document.getElementById('edit-machine-form').style.display = 'none';
                        }
                    })
                    .catch(error => {
                        console.error('编辑请求错误:', error);
                        // 显示详细的错误信息
                        alert('网络错误，请重试。错误详情: ' + error.message);
                        // 隐藏编辑表单
                        document.getElementById('edit-machine-form').style.display = 'none';
                    });
                });
            });
            
            // 为所有"保存"按钮添加点击事件监听器（管理员保存其他用户上传的机床）
            document.querySelectorAll('.enable-edit-btn').forEach(btn => {
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    const machineId = this.getAttribute('data-id');
                    const createdBy = this.getAttribute('data-created-by');
                    
                    if (!confirm(`确认保存该机床数据？保存后该机床评分数据将在可视化分析界面中显示。\n上传用户: ${createdBy}`)) {
                        return;
                    }
                    
                    console.log('点击保存按钮，机床ID:', machineId, '上传用户:', createdBy);
                    
                    // 直接调用保存API
                    fetch(`/data/machines/save/${machineId}/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('保存成功！该机床数据已标记为管理员保存，将在可视化分析界面中显示。');
                            // 刷新页面以更新按钮状态
                            window.location.reload();
                        } else {
                            alert('保存失败: ' + (data.message || '未知错误'));
                        }
                    })
                    .catch(error => {
                        console.error('保存请求失败:', error);
                        alert('保存请求失败，请稍后重试');
                    });
                });
            });
        }
        
        // 初始化事件监听器
        addEventListeners();
        
        // 机床类型选择事件监听 - 增强版本（支持加工中心和镗铣床）
        function toggleMachineSpecificForm(selectElement, horizontalFormElement, fiveAxisFormElement) {
            if (selectElement && horizontalFormElement && fiveAxisFormElement) {
                console.log('切换表单状态:', selectElement.value, '卧式表单:', !!horizontalFormElement, '五轴表单:', !!fiveAxisFormElement);
                
                // 隐藏所有表单
                const hideForm = (formElement) => {
                    if (formElement) {
                        formElement.style.opacity = '0';
                        formElement.style.transform = 'translateY(-10px)';
                        setTimeout(() => {
                            formElement.style.display = 'none';
                            formElement.style.visibility = 'hidden';
                            formElement.classList.add('d-none');
                        }, 300);
                    }
                };
                
                // 显示表单
                const showForm = (formElement) => {
                    if (formElement) {
                        // 立即设置显示状态
                        formElement.style.setProperty('display', 'block', 'important');
                        formElement.style.setProperty('visibility', 'visible', 'important');
                        
                        setTimeout(() => {
                            // 动画效果
                            formElement.style.setProperty('opacity', '1', 'important');
                            formElement.style.setProperty('transform', 'translateY(0)', 'important');
                            
                            // 强制移除可能隐藏元素的CSS类
                            formElement.classList.remove('d-none', 'hidden', 'invisible', 'collapse');
                            formElement.classList.add('d-block', 'visible');
                            
                            // 强制重绘确保DOM更新
                            formElement.offsetHeight;
                        }, 10);
                    }
                };
                
                // 根据选择类型显示对应表单
                if (selectElement.value === 'machining_center') {
                    console.log('显示加工中心参数表单');
                    hideForm(fiveAxisFormElement);
                    showForm(horizontalFormElement);
                } else if (selectElement.value === 'boring_milling_machine') {
                    console.log('显示镗铣床参数表单');
                    hideForm(horizontalFormElement);
                    showForm(fiveAxisFormElement);
                } else {
                    // 其他机床类型，隐藏所有参数表单
                    console.log('隐藏所有参数表单');
                    hideForm(horizontalFormElement);
                    hideForm(fiveAxisFormElement);
                }
            } else {
                console.error('切换表单失败: selectElement或表单元素不存在');
            }
        }
        
        // 初始化表单状态 - 增强版本（支持加工中心和镗铣床）
        function initMachineTypeForms() {
            console.log('开始初始化机床类型表单...');
            
            // 延迟执行，确保DOM完全加载
            setTimeout(function() {
                const machineTypeSelect = document.getElementById('machine-type');
                const horizontalMachiningForm = document.getElementById('horizontal-machining-form');
                const boringMillingForm = document.getElementById('boring-milling-form');
                const editMachineTypeSelect = document.getElementById('edit-machine-type');
                const editHorizontalMachiningForm = document.getElementById('edit-horizontal-machining-form');
                const editBoringMillingForm = document.getElementById('edit-boring-milling-form');
                
                console.log('找到的元素:', {
                    machineTypeSelect: !!machineTypeSelect,
                    horizontalMachiningForm: !!horizontalMachiningForm,
                    boringMillingForm: !!boringMillingForm,
                    editMachineTypeSelect: !!editMachineTypeSelect,
                    editHorizontalMachiningForm: !!editHorizontalMachiningForm,
                    editBoringMillingForm: !!editBoringMillingForm
                });
                
                // 页面加载时从达梦数据库加载数据到表单
                loadMachineParamsFromDameng();
                
                // 设置初始CSS样式 - 优化版本
                const setFormStyles = (formElement) => {
                    if (formElement) {
                        formElement.style.transition = 'all 0.3s ease-in-out';
                        formElement.style.opacity = '0';
                        formElement.style.transform = 'translateY(-10px)';
                        // 保持HTML的初始display状态，避免冲突
                    }
                };
                
                setFormStyles(horizontalMachiningForm);
                setFormStyles(boringMillingForm);
                setFormStyles(editHorizontalMachiningForm);
                setFormStyles(editBoringMillingForm);
                
                // 添加事件监听器 - 增强版本
                if (machineTypeSelect && horizontalMachiningForm && boringMillingForm) {
                    console.log('绑定添加表单事件监听器');
                    machineTypeSelect.addEventListener('change', function() {
                        console.log('机床类型变更:', this.value);
                        toggleMachineSpecificForm(this, horizontalMachiningForm, boringMillingForm);
                    });
                    
                    // 页面加载时检查初始状态
                    console.log('初始化添加表单状态:', machineTypeSelect.value);
                    toggleMachineSpecificForm(machineTypeSelect, horizontalMachiningForm, boringMillingForm);
                }
                
                if (editMachineTypeSelect && editHorizontalMachiningForm && editBoringMillingForm) {
                    console.log('绑定编辑表单事件监听器');
                    editMachineTypeSelect.addEventListener('change', function() {
                        console.log('编辑表单机床类型变更:', this.value);
                        toggleMachineSpecificForm(this, editHorizontalMachiningForm, editBoringMillingForm);
                    });
                    
                    // 页面加载时检查初始状态
                    console.log('初始化编辑表单状态:', editMachineTypeSelect.value);
                    toggleMachineSpecificForm(editMachineTypeSelect, editHorizontalMachiningForm, editBoringMillingForm);
                }
                
                console.log('机床类型表单初始化完成');
            }, 100); // 延迟100ms确保DOM完全加载
        }
        
        // 编辑表单取消按钮事件监听
        const cancelEditMachineBtn = document.getElementById('cancel-edit-machine');
        if (cancelEditMachineBtn) {
            cancelEditMachineBtn.addEventListener('click', function() {
                // 隐藏编辑表单
                document.getElementById('edit-machine-form').style.display = 'none';
                
                // 同时隐藏加工中心参数表单
                const form = document.getElementById('edit-horizontal-machining-form');
                if (form) {
                    form.style.opacity = '0';
                    form.style.transform = 'translateY(-10px)';
                    setTimeout(() => {
                        form.style.display = 'none';
                        form.style.visibility = 'hidden';
                    }, 300);
                }
            });
        }
        
        // 编辑表单提交处理
        const editForm = document.getElementById('edit-machine-form-form');
        if (editForm) {
            editForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                
                // 获取机床ID
                const machineIdElement = document.getElementById('edit-machine-id');
                const machineId = machineIdElement ? machineIdElement.value : null;
                
                if (!machineId) {
                    console.error('找不到机床 ID');
                    alert('机床 ID错误，请刷新页面重试');
                    return;
                }
                
                // 前端验证
                const machineNameElement = document.getElementById('edit-machine-name');
                const machineModelElement = document.getElementById('edit-specification-model');
                const machineReportNumberElement = document.getElementById('edit-machine-report-number');
                const machineName = machineNameElement ? machineNameElement.value : '';
                const model = machineModelElement ? machineModelElement.value : '';
                const reportNumber = machineReportNumberElement ? machineReportNumberElement.value : '';
                
                // 验证报告编号唯一性
                const machineMap = JSON.parse(localStorage.getItem('machineMap') || '{}');
                let reportNumberExists = false;
                Object.values(machineMap).forEach(function(machine) {
                    if (machine.report_number === reportNumber && machine.id != machineId) {
                        reportNumberExists = true;
                    }
                });
                if (reportNumberExists) {
                    alert('报告编号已存在，请使用不同的报告编号');
                    return;
                }
                
                const machineTypeElement = document.getElementById('edit-machine-type');
                const machineType = machineTypeElement ? machineTypeElement.value : null;
                
                if (!machineType) {
                    console.error('找不到机床类型');
                    alert('机床类型错误，请刷新页面重试');
                    return;
                }
                
                if (machineType === 'machining_center') {
                    const hXAxisTravelElement = document.getElementById('edit-x-axis-travel');
                    const hYAxisTravelElement = document.getElementById('edit-y-axis-travel');
                    const hZAxisTravelElement = document.getElementById('edit-z-axis-travel');
                    const hWorktableLengthElement = document.getElementById('edit-worktable-length');
                    const hWorkpieceSizeElement = document.getElementById('edit-workpiece-size');
                    
                    const xAxisTravel = hXAxisTravelElement ? hXAxisTravelElement.value : '';
                    const yAxisTravel = hYAxisTravelElement ? hYAxisTravelElement.value : '';
                    const zAxisTravel = hZAxisTravelElement ? hZAxisTravelElement.value : '';
                    const worktableLength = hWorktableLengthElement ? hWorktableLengthElement.value : '';
                    const workpieceSize = hWorkpieceSizeElement ? hWorkpieceSizeElement.value : '';
                    
                    // 验证必填字段
                    if (!xAxisTravel || !yAxisTravel || !zAxisTravel || !worktableLength || !workpieceSize) {
                        alert('请填写加工中心的所有必填参数');
                        return;
                    }
                    
                    // 验证数值有效性
                    if (isNaN(parseFloat(xAxisTravel)) || parseFloat(xAxisTravel) <= 0) {
                        alert('X轴行程必须是大于0的数值');
                        return;
                    }
                    if (isNaN(parseFloat(yAxisTravel)) || parseFloat(yAxisTravel) <= 0) {
                        alert('Y轴行程必须是大于0的数值');
                        return;
                    }
                    if (isNaN(parseFloat(zAxisTravel)) || parseFloat(zAxisTravel) <= 0) {
                        alert('Z轴行程必须是大于0的数值');
                        return;
                    }
                    if (isNaN(parseFloat(worktableLength)) || parseFloat(worktableLength) <= 0) {
                        alert('工作台长度必须是大于0的数值');
                        return;
                    }
                } else if (machineType === 'boring_milling_machine') {
                    const fColumnRangeElement = document.getElementById('edit-boring-milling-column-range');
                    const fWorktableXRangeElement = document.getElementById('edit-boring-milling-worktable-x-range');
                    const fSpindleBoxYRangeElement = document.getElementById('edit-boring-milling-spindle-box-y-range');
                    const fWorktableLengthLcElement = document.getElementById('edit-boring-milling-worktable-length-lc');
                    const fBoringAxisDiameterElement = document.getElementById('edit-boring-milling-boring-axis-diameter');
                    const fMillingAxisDiameterElement = document.getElementById('edit-boring-milling-milling-axis-diameter');
                    const fWorktableTypeElement = document.getElementById('edit-boring-milling-worktable-type');
                    
                    const columnRange = fColumnRangeElement ? fColumnRangeElement.value : '';
                    const worktableXRange = fWorktableXRangeElement ? fWorktableXRangeElement.value : '';
                    const spindleBoxYRange = fSpindleBoxYRangeElement ? fSpindleBoxYRangeElement.value : '';
                    const worktableLengthLc = fWorktableLengthLcElement ? fWorktableLengthLcElement.value : '';
                    const boringAxisDiameter = fBoringAxisDiameterElement ? fBoringAxisDiameterElement.value : '';
                    const millingAxisDiameter = fMillingAxisDiameterElement ? fMillingAxisDiameterElement.value : '';
                    const worktableType = fWorktableTypeElement ? fWorktableTypeElement.value : '';
                    
                    if (!columnRange || !worktableXRange || !spindleBoxYRange || !worktableLengthLc || !boringAxisDiameter || !millingAxisDiameter || !worktableType) {
                        alert('请填写镗铣床的所有必填参数');
                        return;
                    }
                    
                    // 验证数值有效性
                    if (isNaN(parseFloat(columnRange)) || parseFloat(columnRange) <= 0) {
                        alert('立柱测量范围必须是大于0的数值');
                        return;
                    }
                    if (isNaN(parseFloat(worktableXRange)) || parseFloat(worktableXRange) <= 0) {
                        alert('工作台X轴测量范围必须是大于0的数值');
                        return;
                    }
                    if (isNaN(parseFloat(spindleBoxYRange)) || parseFloat(spindleBoxYRange) <= 0) {
                        alert('主轴箱Y轴测量范围必须是大于0的数值');
                        return;
                    }
                    if (isNaN(parseFloat(worktableLengthLc)) || parseFloat(worktableLengthLc) <= 0) {
                        alert('工作台长边长度必须是大于0的数值');
                        return;
                    }
                    if (isNaN(parseFloat(boringAxisDiameter)) || parseFloat(boringAxisDiameter) <= 0) {
                        alert('镗轴直径必须是大于0的数值');
                        return;
                    }
                    if (isNaN(parseFloat(millingAxisDiameter)) || parseFloat(millingAxisDiameter) <= 0) {
                        alert('铣轴直径必须是大于0的数值');
                        return;
                    }
                }
                
                const formData = new FormData();
                
                // 获取CSRF token
                const csrfTokenElement = document.querySelector('input[name="csrfmiddlewaretoken"]');
                if (!csrfTokenElement) {
                    console.error('找不到CSRF token元素');
                    alert('CSRF token错误，请刷新页面重试');
                    return;
                }
                
                // 添加基本字段
                formData.append('csrfmiddlewaretoken', csrfTokenElement.value);
                formData.append('machine_id', machineId);

                if (machineNameElement) formData.append('name', machineNameElement.value);
                if (machineModelElement) formData.append('model', machineModelElement.value);
                if (machineReportNumberElement) formData.append('report_number', machineReportNumberElement.value);

                const machineManufacturerElement = document.getElementById('edit-machine-manufacturer');
                if (machineManufacturerElement) formData.append('manufacturer', machineManufacturerElement.value);

                // 新增字段：机床编号、生产日期
                const machineNumberElement = document.getElementById('edit-machine-number');
                if (machineNumberElement) formData.append('machine_number', machineNumberElement.value);

                const productionDateElement = document.getElementById('edit-production-date');
                if (productionDateElement) formData.append('production_date', productionDateElement.value);

                if (machineTypeElement) formData.append('machine_type', machineTypeElement.value);
                
                // 根据机床类型添加相应的字段
                if (machineType === 'machining_center') {
                    // 加工中心字段
                    const hXTravelElement = document.getElementById('edit-x-axis-travel');
                    const hYTravelElement = document.getElementById('edit-y-axis-travel');
                    const hZTravelElement = document.getElementById('edit-z-axis-travel');
                    const hWorktableLengthElement = document.getElementById('edit-worktable-length');
                    const hWorkpieceSizeElement = document.getElementById('edit-workpiece-size');
                    const hSpindleTypeElement = document.getElementById('edit-spindle-type');
                    
                    if (hXTravelElement) formData.append('x_axis_travel', hXTravelElement.value);
                    if (hYTravelElement) formData.append('y_axis_travel', hYTravelElement.value);
                    if (hZTravelElement) formData.append('z_axis_travel', hZTravelElement.value);
                    if (hWorktableLengthElement) formData.append('worktable_length', hWorktableLengthElement.value);
                    if (hWorkpieceSizeElement) formData.append('workpiece_size', hWorkpieceSizeElement.value);
                    if (hSpindleTypeElement) formData.append('spindle_type', hSpindleTypeElement.value);
                } else if (machineType === 'boring_milling_machine') {
                    const fColumnRangeElement = document.getElementById('edit-boring-milling-column-range');
                    const fWorktableXRangeElement = document.getElementById('edit-boring-milling-worktable-x-range');
                    const fSpindleBoxYRangeElement = document.getElementById('edit-boring-milling-spindle-box-y-range');
                    const fZAxisRangeElement = document.getElementById('edit-boring-milling-z-axis-range');
                    const fWorktableLengthLcElement = document.getElementById('edit-boring-milling-worktable-length-lc');
                    const fBoringAxisDiameterElement = document.getElementById('edit-boring-milling-boring-axis-diameter');
                    const fMillingAxisDiameterElement = document.getElementById('edit-boring-milling-milling-axis-diameter');
                    const fWorktableTypeElement = document.getElementById('edit-boring-milling-worktable-type');
                    
                    if (fColumnRangeElement) formData.append('column_measurement_range', fColumnRangeElement.value);
                    if (fWorktableXRangeElement) formData.append('worktable_x_range', fWorktableXRangeElement.value);
                    if (fSpindleBoxYRangeElement) formData.append('spindle_box_y_range', fSpindleBoxYRangeElement.value);
                    if (fZAxisRangeElement) formData.append('z_axis_measurement_range', fZAxisRangeElement.value);
                    if (fWorktableLengthLcElement) formData.append('worktable_length_lc', fWorktableLengthLcElement.value);
                    if (fBoringAxisDiameterElement) formData.append('boring_axis_diameter', fBoringAxisDiameterElement.value);
                    if (fMillingAxisDiameterElement) formData.append('milling_axis_diameter', fMillingAxisDiameterElement.value);
                    if (fWorktableTypeElement) formData.append('worktable_type', fWorktableTypeElement.value);
                }
                
                console.log('开始提交编辑表单，机床ID:', machineId);
                console.log('表单数据:');
                for (let [key, value] of formData.entries()) {
                    console.log(`  ${key}: ${value}`);
                }
                
                const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
                if (!csrfToken) {
                    console.error('找不到CSRF token元素');
                    alert('CSRF token错误，请刷新页面重试');
                    return;
                }
                console.log('CSRF token:', csrfToken.value.substring(0, 20) + '...');
                
                // 发送AJAX请求
                fetch(`/data/machines/edit/${machineId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken.value
                    },
                    body: formData
                })
                .then(response => {
                    console.log('编辑请求响应状态:', response.status, response.statusText);
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(async data => {
                    console.log('编辑请求响应数据:', data);
                    if (data.success) {
                        // 显示成功弹窗
                        alert(data.message);
                        
                        // 刷新页面
                        window.location.reload();
                        
                        // 隐藏编辑表单
                        document.getElementById('edit-machine-form').style.display = 'none';
                        
                        // 更新表格中的数据
                        // 表格列顺序: 0=ID, 1=机床名称, 2=机床编号, 3=报告编号, 4=规格型号(model), 5=生产厂家, 6=生产日期, 7=机床类型
                        const rows = document.querySelectorAll('table.table-striped tbody tr');
                        rows.forEach(row => {
                            const editBtn = row.querySelector('.edit-btn');
                            if (editBtn && editBtn.getAttribute('data-id') === machineId) {
                                // 更新表格行数据
                                row.children[1].textContent = data.machine.name;
                                row.children[2].textContent = data.machine.machine_number || '';
                                row.children[3].textContent = data.machine.report_number;
                                row.children[4].textContent = data.machine.model || '';
                                row.children[5].textContent = data.machine.manufacturer || '';
                                row.children[6].textContent = data.machine.production_date || '';
                                row.children[7].textContent = data.machine.machine_type_display;
                            }
                        });
                        
                        // 检查是否是加工中心，如果是则更新localStorage
                        if (data.machine.machine_type === 'machining_center') {
                            // 优先使用表单中的用户提交数据，而不是后端返回的数据
                            const formData = new FormData(form);
                            const machineParams = {
                                x_axis_travel: parseFloat(formData.get('x_axis_travel')) || data.machine.x_axis_travel,
                                y_axis_travel: parseFloat(formData.get('y_axis_travel')) || data.machine.y_axis_travel,
                                z_axis_travel: parseFloat(formData.get('z_axis_travel')) || data.machine.z_axis_travel,
                                worktable_length: parseFloat(formData.get('worktable_length')) || data.machine.worktable_length,
                                workpiece_size: formData.get('workpiece_size') || data.machine.workpiece_size,
                                spindle_type: formData.get('spindle_type') || data.machine.spindle_type,
                                measured_x: data.machine.measured_x,
                                measured_y: data.machine.measured_y,
                                measured_z: data.machine.measured_z
                            };
                            
                            console.log('用户提交的表单数据:', {
                                x_axis_travel: formData.get('x_axis_travel'),
                                y_axis_travel: formData.get('y_axis_travel'),
                                z_axis_travel: formData.get('z_axis_travel'),
                                worktable_length: formData.get('worktable_length'),
                                workpiece_size: formData.get('workpiece_size'),
                                spindle_type: formData.get('spindle_type')
                            });
                            
                            console.log('后端返回的数据:', {
                                x_axis_travel: data.machine.x_axis_travel,
                                y_axis_travel: data.machine.y_axis_travel,
                                z_axis_travel: data.machine.z_axis_travel,
                                worktable_length: data.machine.worktable_length,
                                workpiece_size: data.machine.workpiece_size,
                                spindle_type: data.machine.spindle_type
                            });
                            
                            // 使用增强的数据保存函数保存机床数据
                            const saveSuccess = await saveMachineParamsToDameng('edit-x-axis-travel', 'edit-y-axis-travel', 'edit-z-axis-travel', 'edit-worktable-length', 'edit-workpiece-size', 'edit-spindle-type', data.machine.id);
                            
                            if (!saveSuccess) {
                                console.error('机床数据保存失败，机床ID:', data.machine.id);
                                return;
                            }
                            
                            // 注意：saveMachineParamsToDameng函数已经包含了重新加载数据的逻辑
                            console.log('数据保存成功，saveMachineParamsToDameng函数已处理重新加载');
                            
                            // 更新机床名称和型号的映射关系
                            const machineMap = JSON.parse(localStorage.getItem('machineMap') || '{}');
                            
                            // 先删除旧的映射（如果存在）
                            Object.keys(machineMap).forEach(key => {
                                if (machineMap[key].id == data.machine.id) {
                                    delete machineMap[key];
                                }
                            });
                            
                            // 添加新的映射
                            machineMap[data.machine.name] = {
                                model: data.machine.model,
                                id: data.machine.id
                            };
                            localStorage.setItem('machineMap', JSON.stringify(machineMap));
                            
                            // 不再更新全局machine_params，避免数据同步问题
                            console.log('跳过更新全局machine_params，避免数据同步问题');
                        } else if (data.machine.machine_type === 'boring_milling_machine') {
                            console.log('镗铣床编辑成功，开始保存参数到达梦数据库...');
                            
                            const saveSuccess = await saveBoringMillingParamsToDameng(
                                'edit-boring-milling-column-range',
                                'edit-boring-milling-worktable-x-range',
                                'edit-boring-milling-spindle-box-y-range',
                                'edit-boring-milling-z-axis-range',
                                'edit-boring-milling-worktable-length-lc',
                                'edit-boring-milling-boring-axis-diameter',
                                'edit-boring-milling-milling-axis-diameter',
                                'edit-boring-milling-worktable-type',
                                data.machine.id
                            );
                            
                            if (!saveSuccess) {
                                console.error('镗铣床参数保存到达梦数据库失败，机床ID:', data.machine.id);
                            } else {
                                console.log('镗铣床参数保存到达梦数据库成功');
                            }
                            
                            const machineMap = JSON.parse(localStorage.getItem('machineMap') || '{}');
                            Object.keys(machineMap).forEach(key => {
                                if (machineMap[key].id == data.machine.id) {
                                    delete machineMap[key];
                                }
                            });
                            machineMap[data.machine.name] = {
                                model: data.machine.model,
                                id: data.machine.id
                            };
                            localStorage.setItem('machineMap', JSON.stringify(machineMap));
                            
                            // 显示允差获取成功提示
                            alert('镗铣床数据编辑成功！允差获取成功，数据已保存到数据库。');
                        }
                    } else {
                        // 显示错误弹窗
                        alert(data.message);
                    }
                })
                .catch(error => {
                    console.error('编辑表单提交失败:', error);
                    console.error('错误详情:', error.message);
                    console.error('错误堆栈:', error.stack);
                    alert('网络错误: ' + error.message + '\n请重试或查看控制台获取详细信息');
                });
            });
        }
        
        // 获取CSRF token的辅助函数
        function getCSRFToken() {
            const csrfTokenElement = document.querySelector('input[name="csrfmiddlewaretoken"]');
            if (!csrfTokenElement) {
                console.error('找不到CSRF token元素');
                throw new Error('CSRF token错误，请刷新页面重试');
            }
            return csrfTokenElement.value;
        }
        
        // 增强的保存机床参数到达梦数据库的通用函数
        async function saveMachineParamsToDameng(xInputId, yInputId, zInputId, worktableInputId, workpieceInputId = null, spindleInputId = null, targetMachineId = null) {
            console.log('开始保存机床参数到达梦数据库...');
            
            try {
                // 获取输入元素的值
                const xElement = document.getElementById(xInputId);
                const yElement = document.getElementById(yInputId);
                const zElement = document.getElementById(zInputId);
                const worktableElement = document.getElementById(worktableInputId);
                
                if (!xElement || !yElement || !zElement || !worktableElement) {
                    const errorMsg = '保存失败: 找不到表单元素';
                    console.error(errorMsg);
                    MachineDataManager.showUserFeedback(errorMsg, 'error');
                    return false;
                }
                
                // 数据收集和验证
                const machineData = {
                    x_axis_travel: parseFloat(xElement.value),
                    y_axis_travel: parseFloat(yElement.value),
                    z_axis_travel: parseFloat(zElement.value),
                    worktable_length: parseFloat(worktableElement.value)
                };
                
                // 处理可选参数 - 确保工件尺寸正确获取
                if (workpieceInputId) {
                    const workpieceElement = document.getElementById(workpieceInputId);
                    if (workpieceElement) {
                        // 确保工件尺寸有值，如果没有选择则使用默认值
                        if (workpieceElement.value) {
                            machineData.workpiece_size = parseInt(workpieceElement.value);
                        } else {
                            machineData.workpiece_size = '320'; // 默认值
                            console.log('工件尺寸未选择，使用默认值320');
                        }
                    }
                }
                
                if (spindleInputId) {
                    const spindleElement = document.getElementById(spindleInputId);
                    if (spindleElement && spindleElement.value) {
                        machineData.spindle_type = spindleElement.value;
                    }
                }
                
                console.log('保存机床参数到达梦数据库:');
                console.log('X轴行程:', machineData.x_axis_travel, '原始值:', xElement.value, '元素:', xInputId);
                console.log('Y轴行程:', machineData.y_axis_travel, '原始值:', yElement.value, '元素:', yInputId);
                console.log('Z轴行程:', machineData.z_axis_travel, '原始值:', zElement.value, '元素:', zInputId);
                console.log('工作台长度:', machineData.worktable_length, '原始值:', worktableElement.value, '元素:', worktableInputId);
                
                // 数据清理和验证
                const sanitizedData = MachineDataManager.sanitizeMachineData(machineData);
                
                // 验证数据完整性
                if (!MachineDataManager.validateMachineData(sanitizedData)) {
                    const errorMsg = '数据验证失败: 请检查所有必填字段是否已正确填写';
                    console.error(errorMsg);
                    MachineDataManager.showUserFeedback(errorMsg, 'error');
                    return false;
                }
                
                // 获取当前机床ID - 优先使用传入的参数，然后尝试从编辑表单获取，最后从URL获取
                let machineId = targetMachineId;
                if (!machineId) {
                    const editMachineIdField = document.getElementById('edit-machine-id');
                    if (editMachineIdField && editMachineIdField.value) {
                        machineId = parseInt(editMachineIdField.value);
                        console.log('从编辑表单获取机床ID:', machineId);
                    }
                }
                if (!machineId) {
                    machineId = MachineDataManager.getCurrentMachineId();
                }
                if (!machineId) {
                    const errorMsg = '保存失败: 无法获取机床ID';
                    console.error(errorMsg);
                    MachineDataManager.showUserFeedback(errorMsg, 'error');
                    return false;
                }
                console.log('保存机床参数，机床ID:', machineId);
                
                // 事务处理：先保存到localStorage，再保存到达梦数据库
                let localStorageSuccess = false;
                let databaseSuccess = false;
                
                // 步骤1：保存到localStorage
                try {
                    localStorageSuccess = MachineDataManager.saveMachineData(machineId, sanitizedData);
                    if (!localStorageSuccess) {
                        throw new Error('localStorage保存失败');
                    }
                    console.log('localStorage保存成功');
                } catch (localStorageError) {
                    console.error('localStorage保存失败:', localStorageError);
                    MachineDataManager.showUserFeedback('本地数据保存失败，请重试', 'error');
                    return false;
                }
                
                // 步骤2：保存到达梦数据库
                try {
                    const response = await fetch(`/dameng/api/machine-parameters/${machineId}/`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCSRFToken()
                        },
                        body: JSON.stringify({
                            ...sanitizedData,
                            machine_id: machineId,
                            updated_at: new Date().toISOString()
                        })
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        databaseSuccess = true;
                        console.log('机床参数保存到达梦数据库成功:', result);
                        MachineDataManager.showUserFeedback('数据保存成功', 'success');
                    } else {
                        throw new Error(result.message || '数据库操作失败');
                    }
                    
                } catch (databaseError) {
                    console.error('达梦数据库保存失败:', databaseError);
                    
                    // 如果数据库保存失败，尝试回滚localStorage
                    try {
                        const machineIdToParams = JSON.parse(localStorage.getItem('machineIdToParams') || '{}');
                        delete machineIdToParams[machineId];
                        localStorage.setItem('machineIdToParams', JSON.stringify(machineIdToParams));
                        console.log('数据库保存失败，已回滚localStorage');
                    } catch (rollbackError) {
                        console.error('回滚localStorage失败:', rollbackError);
                    }
                    
                    MachineDataManager.showUserFeedback('数据库保存失败，请检查网络连接', 'error');
                    return false;
                }
                
                // 步骤3：数据保存成功后，重新加载数据到编辑表单
                if (localStorageSuccess && databaseSuccess) {
                    console.log('数据保存成功，重新加载数据到编辑表单...');
                    
                    // 重新填充编辑表单数据
                    const fillEditFormData = () => {
                        const machineParams = MachineDataManager.getMachineData(machineId);
                        
                        console.log('重新加载的机床数据，机床ID:', machineId, machineParams);
                        
                        // 重新填充编辑表单
                        if (machineParams.x_axis_travel) {
                            document.getElementById('edit-x-axis-travel').value = machineParams.x_axis_travel;
                        }
                        if (machineParams.y_axis_travel) {
                            document.getElementById('edit-y-axis-travel').value = machineParams.y_axis_travel;
                        }
                        if (machineParams.z_axis_travel) {
                            document.getElementById('edit-z-axis-travel').value = machineParams.z_axis_travel;
                        }
                        if (machineParams.worktable_length) {
                            document.getElementById('edit-worktable-length').value = machineParams.worktable_length;
                        }
                        if (machineParams.workpiece_size) {
                            document.getElementById('edit-workpiece-size').value = machineParams.workpiece_size;
                        }
                        if (machineParams.spindle_type) {
                            document.getElementById('edit-spindle-type').value = machineParams.spindle_type;
                        }
                        
                        console.log('编辑表单数据重新加载完成');
                    };
                    
                    // 立即重新加载数据
                    fillEditFormData();
                }
                
                return localStorageSuccess && databaseSuccess;
                
            } catch (error) {
                console.error('保存过程中发生未知错误:', error);
                MachineDataManager.showUserFeedback('保存过程中发生错误，请重试', 'error');
                return false;
            }
        }
        
        async function saveBoringMillingParamsToDameng(
            columnRangeInputId,
            worktableXRangeInputId,
            spindleBoxYRangeInputId,
            zAxisRangeInputId,
            worktableLengthLcInputId,
            boringAxisDiameterInputId,
            millingAxisDiameterInputId,
            worktableTypeInputId,
            targetMachineId
        ) {
            console.log('开始保存镗铣床参数到达梦数据库...');
            
            try {
                const columnElement = document.getElementById(columnRangeInputId);
                const worktableXElement = document.getElementById(worktableXRangeInputId);
                const spindleBoxYElement = document.getElementById(spindleBoxYRangeInputId);
                const zAxisRangeElement = document.getElementById(zAxisRangeInputId);
                const worktableLcElement = document.getElementById(worktableLengthLcInputId);
                const boringAxisElement = document.getElementById(boringAxisDiameterInputId);
                const millingAxisElement = document.getElementById(millingAxisDiameterInputId);
                const worktableTypeElement = document.getElementById(worktableTypeInputId);
                
                if (!columnElement || !worktableXElement || !spindleBoxYElement || !worktableLcElement) {
                    const errorMsg = '保存失败: 找不到镗铣床表单元素';
                    console.error(errorMsg);
                    MachineDataManager.showUserFeedback(errorMsg, 'error');
                    return false;
                }
                
                const machineData = {
                    machine_type: 'boring_milling_machine',
                    column_measurement_range: columnElement.value ? parseFloat(columnElement.value) : null,
                    worktable_x_range: worktableXElement.value ? parseFloat(worktableXElement.value) : null,
                    spindle_box_y_range: spindleBoxYElement.value ? parseFloat(spindleBoxYElement.value) : null,
                    z_axis_measurement_range: zAxisRangeElement && zAxisRangeElement.value ? parseFloat(zAxisRangeElement.value) : null,
                    worktable_length_lc: worktableLcElement.value ? parseFloat(worktableLcElement.value) : null,
                    boring_axis_diameter: boringAxisElement && boringAxisElement.value ? parseFloat(boringAxisElement.value) : null,
                    milling_axis_diameter: millingAxisElement && millingAxisElement.value ? parseFloat(millingAxisElement.value) : null,
                    worktable_type: worktableTypeElement && worktableTypeElement.value ? worktableTypeElement.value : null
                };
                
                console.log('镗铣床参数数据:', machineData);
                
                let machineId = targetMachineId;
                if (!machineId) {
                    const editMachineIdField = document.getElementById('edit-machine-id');
                    if (editMachineIdField && editMachineIdField.value) {
                        machineId = parseInt(editMachineIdField.value);
                    }
                }
                if (!machineId) {
                    machineId = MachineDataManager.getCurrentMachineId();
                }
                if (!machineId) {
                    const errorMsg = '保存失败: 无法获取机床ID';
                    console.error(errorMsg);
                    MachineDataManager.showUserFeedback(errorMsg, 'error');
                    return false;
                }
                console.log('保存镗铣床参数，机床ID:', machineId);
                
                let localStorageSuccess = false;
                let databaseSuccess = false;
                
                try {
                    const existingData = MachineDataManager.getMachineData(machineId) || {};
                    const mergedData = { ...existingData, ...machineData };
                    localStorageSuccess = MachineDataManager.saveMachineData(machineId, mergedData);
                    if (!localStorageSuccess) {
                        throw new Error('localStorage保存失败');
                    }
                    console.log('镗铣床参数localStorage保存成功');
                } catch (localStorageError) {
                    console.error('镗铣床参数localStorage保存失败:', localStorageError);
                    return false;
                }
                
                try {
                    const response = await fetch(`/dameng/api/boring-milling-parameters/${machineId}/`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCSRFToken()
                        },
                        body: JSON.stringify({
                            ...machineData,
                            machine_id: machineId,
                            updated_at: new Date().toISOString()
                        })
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        databaseSuccess = true;
                        console.log('镗铣床参数保存到达梦数据库成功:', result);
                        MachineDataManager.showUserFeedback('镗铣床数据保存成功', 'success');
                    } else {
                        throw new Error(result.message || '数据库操作失败');
                    }
                    
                } catch (databaseError) {
                    console.error('镗铣床参数达梦数据库保存失败:', databaseError);
                    
                    try {
                        const machineIdToParams = JSON.parse(localStorage.getItem('machineIdToParams') || '{}');
                        delete machineIdToParams[machineId];
                        localStorage.setItem('machineIdToParams', JSON.stringify(machineIdToParams));
                    } catch (rollbackError) {
                        console.error('回滚localStorage失败:', rollbackError);
                    }
                    
                    MachineDataManager.showUserFeedback('镗铣床数据库保存失败，请检查网络连接', 'error');
                    return false;
                }
                
                return localStorageSuccess && databaseSuccess;
                
            } catch (error) {
                console.error('镗铣床参数保存过程中发生未知错误:', error);
                MachineDataManager.showUserFeedback('保存过程中发生错误，请重试', 'error');
                return false;
            }
        }
        
        // 添加X轴行程变化的实时监听功能
        function setupXAxisTravelListeners() {
            
            // 监听添加表单中的X轴行程输入框
            const addXAxisInput = document.getElementById('x-axis-travel');
            if (addXAxisInput) {
                addXAxisInput.addEventListener('input', function() {
                    const xAxisTravel = parseFloat(this.value);
                    if (!isNaN(xAxisTravel) && xAxisTravel > 0) {
                        updateTolerancePreview(xAxisTravel);
                    }
                });
            }
            
            // 监听编辑表单中的X轴行程输入框
            const editXAxisInput = document.getElementById('edit-x-axis-travel');
            if (editXAxisInput) {
                editXAxisInput.addEventListener('input', function() {
                    const xAxisTravel = parseFloat(this.value);
                    if (!isNaN(xAxisTravel) && xAxisTravel > 0) {
                        updateTolerancePreview(xAxisTravel);
                    }
                });
            }
            
            // 更新允差预览
            async function updateTolerancePreview(xAxisTravel) {
                const toleranceValue = await calculateToleranceByXAxisTravel(xAxisTravel);
                
                // 显示允差预览信息
                await showTolerancePreview(xAxisTravel, toleranceValue);
            }
            
            // 显示允差预览信息
            async function showTolerancePreview(xAxisTravel, toleranceValue) {
                // 创建或更新预览信息
                let previewElement = document.getElementById('tolerance-preview');
                if (!previewElement) {
                    previewElement = document.createElement('div');
                    previewElement.id = 'tolerance-preview';
                    previewElement.style.cssText = 'display: none;'; // 隐藏预览元素
                    
                    // 找到X轴行程输入框的父元素，插入预览信息
                    const xAxisInput = document.getElementById('x-axis-travel') || document.getElementById('edit-x-axis-travel');
                    if (xAxisInput) {
                        const parentElement = xAxisInput.closest('tr');
                        if (parentElement) {
                            parentElement.parentNode.insertBefore(previewElement, parentElement.nextSibling);
                        }
                    }
                }
                
                // 从允差管理界面获取所有轴的允差值
                try {
                    const machineId = getCurrentMachineId();
                    if (!machineId) {
                        console.warn('未找到机床ID，无法从允差管理界面获取允差数据');
                        return;
                    }
                    
                    // 调用允差管理界面的API
                    const response = await fetch(`/evaluation/api/get-tolerances/?machine_id=${machineId}`);
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const data = await response.json();
                    if (!data.success) {
                        throw new Error(data.error || '获取允差数据失败');
                    }
                    
                    // 解析允差数据
                    const tolerances = data.values;
                    const feedAxisTolerances = tolerances.几何精度?.进给轴精度 || [0.020, 0.015, 0.015, 0.060];
                    
                    // 显示从允差管理界面获取的允差数据
                    console.log('允差管理界面数据:', {
                        'X轴行程': xAxisTravel + ' mm',
                        'X轴直线度允差': feedAxisTolerances[0] + ' mm',
                        'Y轴直线度允差': feedAxisTolerances[1] + ' mm',
                        'Z轴直线度允差': feedAxisTolerances[2] + ' mm',
                        '平行度允差': feedAxisTolerances[3] + ' mm'
                    });
                    
                } catch (error) {
                    console.error('从允差管理界面获取允差数据失败:', error);
                    // 失败时显示警告
                    console.warn('使用默认允差数据:', {
                        'X轴行程': xAxisTravel + ' mm',
                        'X轴直线度允差': toleranceValue + ' mm',
                        'Y轴直线度允差': '0.015 mm',
                        'Z轴直线度允差': '0.015 mm',
                        '平行度允差': '0.060 mm'
                    });
                }
            }
            

            
            // 保存机床参数到localStorage的通用函数（备用）
            function saveMachineParamsToLocalStorage(xInputId, yInputId, zInputId, worktableInputId, workpieceInputId = null, spindleInputId = null) {
                console.log('开始保存机床参数到localStorage...');
                
                // 获取输入元素的值
                const xElement = document.getElementById(xInputId);
                const yElement = document.getElementById(yInputId);
                const zElement = document.getElementById(zInputId);
                const worktableElement = document.getElementById(worktableInputId);
                
                if (!xElement || !yElement || !zElement || !worktableElement) {
                    console.error('保存失败: 找不到表单元素');
                    return;
                }
                
                const xAxisTravel = parseFloat(xElement.value);
                const yAxisTravel = parseFloat(yElement.value);
                const zAxisTravel = parseFloat(zElement.value);
                const worktableLength = parseFloat(worktableElement.value);
                
                console.log('保存机床参数到localStorage:');
                console.log('X轴行程:', xAxisTravel, '原始值:', xElement.value, '元素:', xInputId);
                console.log('Y轴行程:', yAxisTravel, '原始值:', yElement.value, '元素:', yInputId);
                console.log('Z轴行程:', zAxisTravel, '原始值:', zElement.value, '元素:', zInputId);
                console.log('工作台长度:', worktableLength, '原始值:', worktableElement.value, '元素:', worktableInputId);
                
                // 获取现有的localStorage数据
                let machineParams = {};
                try {
                    machineParams = JSON.parse(localStorage.getItem('machine_params') || '{}');
                    console.log('现有的localStorage数据:', machineParams);
                } catch (error) {
                    console.error('解析localStorage数据失败:', error);
                    machineParams = {};
                }
                
                // 强制保存数值数据（确保是数字类型）
                machineParams.x_axis_travel = isNaN(xAxisTravel) ? 1300 : Number(xAxisTravel);
                machineParams.y_axis_travel = isNaN(yAxisTravel) ? 1300 : Number(yAxisTravel);
                machineParams.z_axis_travel = isNaN(zAxisTravel) ? 1300 : Number(zAxisTravel);
                machineParams.worktable_length = isNaN(worktableLength) ? 1300 : Number(worktableLength);
                
                // 保存工件尺寸数据（如果提供了工件尺寸输入框ID）
                if (workpieceInputId) {
                    const workpieceElement = document.getElementById(workpieceInputId);
                    if (workpieceElement) {
                        machineParams.workpiece_size = workpieceElement.value ? parseInt(workpieceElement.value) : null;
                        console.log('工件尺寸:', machineParams.workpiece_size, '元素:', workpieceInputId);
                    }
                }
                
                // 保存主轴类型数据（如果提供了主轴类型输入框ID）
                if (spindleInputId) {
                    const spindleElement = document.getElementById(spindleInputId);
                    if (spindleElement) {
                        machineParams.spindle_type = spindleElement.value || null;
                        console.log('主轴类型:', machineParams.spindle_type, '元素:', spindleInputId);
                    }
                }
                
                // 确保所有数值字段都是数字类型
                ['x_axis_travel', 'y_axis_travel', 'z_axis_travel', 'worktable_length'].forEach(key => {
                    if (machineParams[key] !== null && machineParams[key] !== undefined) {
                        machineParams[key] = Number(machineParams[key]);
                    }
                });
                
                console.log('保存后的machine_params:', machineParams);
                console.log('数据类型检查:', {
                    x_axis_travel: typeof machineParams.x_axis_travel,
                    y_axis_travel: typeof machineParams.y_axis_travel,
                    z_axis_travel: typeof machineParams.z_axis_travel,
                    worktable_length: typeof machineParams.worktable_length
                });
                
                try {
                    localStorage.setItem('machine_params', JSON.stringify(machineParams));
                    console.log('localStorage保存成功');
                    
                    // 验证保存的数据
                    const savedData = JSON.parse(localStorage.getItem('machine_params') || '{}');
                    console.log('验证保存的数据:', savedData);
                } catch (error) {
                    console.error('保存到localStorage失败:', error);
                }
            }
            
            // 注意：主提交事件处理程序已经在第478行和第1123行处理了数据保存
            // 不再需要重复的提交事件处理程序，避免数据保存冲突
            console.log('表单提交事件处理程序已正确配置，避免重复处理');
        }
        
        // 初始化X轴行程监听器
        setupXAxisTravelListeners();
        
        // 初始化用户信息tooltip功能
        setupUserInfoTooltip();
        
        // 初始化排序功能
        setupSorting();
        
        // 初始化搜索功能
        setupSearch();
        
        // 初始化列宽度
        setupColumnWidths();
    });
    
    // 用户信息tooltip功能
    function setupUserInfoTooltip() {
        const userTooltips = document.querySelectorAll('.user-info-tooltip');
        
        userTooltips.forEach(tooltip => {
            tooltip.addEventListener('mouseenter', function(e) {
                const username = this.getAttribute('data-username');
                const userId = this.getAttribute('data-user-id');
                const fullName = this.getAttribute('data-full-name');
                const company = this.getAttribute('data-company') || '未设置';
                const phone = this.getAttribute('data-phone') || '未设置';
                const email = this.getAttribute('data-email') || '未设置';
                
                const tooltipContent = `
                    <div style="padding: 10px; min-width: 200px;">
                        <div style="font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid #ddd; padding-bottom: 5px;">
                            ${fullName}
                        </div>
                        <div style="margin-bottom: 4px;"><strong>用户名:</strong> ${username}</div>
                        <div style="margin-bottom: 4px;"><strong>用户ID:</strong> U${userId}</div>
                        <div style="margin-bottom: 4px;"><strong>部门:</strong> ${company}</div>
                        <div style="margin-bottom: 4px;"><strong>联系方式:</strong> ${phone}</div>
                        <div style="margin-bottom: 4px;"><strong>邮箱:</strong> ${email}</div>
                    </div>
                `;
                
                const tooltipElement = document.createElement('div');
                tooltipElement.className = 'custom-tooltip';
                tooltipElement.innerHTML = tooltipContent;
                tooltipElement.style.cssText = `
                    position: fixed;
                    background: white;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                    z-index: 9999;
                    font-size: 12px;
                    color: #333;
                    pointer-events: none;
                    opacity: 0;
                    transition: opacity 0.2s;
                `;
                
                document.body.appendChild(tooltipElement);
                
                const rect = this.getBoundingClientRect();
                const tooltipRect = tooltipElement.getBoundingClientRect();
                
                let left = rect.left + window.scrollX;
                let top = rect.bottom + window.scrollY + 5;
                
                if (left + tooltipRect.width > window.innerWidth) {
                    left = window.innerWidth - tooltipRect.width - 10;
                }
                
                if (top + tooltipRect.height > window.innerHeight) {
                    top = rect.top + window.scrollY - tooltipRect.height - 5;
                }
                
                tooltipElement.style.left = left + 'px';
                tooltipElement.style.top = top + 'px';
                tooltipElement.style.opacity = '1';
                
                this._tooltipElement = tooltipElement;
            });
            
            tooltip.addEventListener('mouseleave', function() {
                if (this._tooltipElement) {
                    this._tooltipElement.style.opacity = '0';
                    setTimeout(() => {
                        if (this._tooltipElement && this._tooltipElement.parentNode) {
                            this._tooltipElement.parentNode.removeChild(this._tooltipElement);
                        }
                    }, 200);
                }
            });
        });
    }
    
    // 排序功能
    function setupSorting() {
        const sortLinks = document.querySelectorAll('.sort-link');
        
        sortLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                const sortField = this.getAttribute('data-sort');
                const sortIcon = this.querySelector('.sort-icon i');
                
                if (!sortField) return;
                
                const currentSort = localStorage.getItem('machineSortField') || '';
                const currentDirection = localStorage.getItem('machineSortDirection') || 'asc';
                
                let newDirection = 'asc';
                if (currentSort === sortField) {
                    newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
                }
                
                localStorage.setItem('machineSortField', sortField);
                localStorage.setItem('machineSortDirection', newDirection);
                
                updateSortIcons(sortField, newDirection);
                
                sortTable(sortField, newDirection);
            });
        });
        
        const savedSortField = localStorage.getItem('machineSortField');
        const savedSortDirection = localStorage.getItem('machineSortDirection');
        
        if (savedSortField && savedSortDirection) {
            updateSortIcons(savedSortField, savedSortDirection);
            sortTable(savedSortField, savedSortDirection);
        }
    }
    
    function updateSortIcons(activeField, direction) {
        const sortIcons = document.querySelectorAll('.sort-icon i');
        
        sortIcons.forEach(icon => {
            const field = icon.closest('.sort-icon').getAttribute('data-sort');
            
            icon.className = 'fas fa-sort';
            
            if (field === activeField) {
                icon.className = direction === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down';
            }
        });
    }
    
    function sortTable(sortField, direction) {
        const tableBody = document.querySelector('table tbody');
        if (!tableBody) return;
        
        const rows = Array.from(tableBody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            let aValue, bValue;
            
            if (sortField === 'uploaded_by') {
                const aUserSpan = a.querySelector('.user-info-tooltip');
                const bUserSpan = b.querySelector('.user-info-tooltip');
                
                if (!aUserSpan || !bUserSpan) return 0;
                
                aValue = aUserSpan.getAttribute('data-username') || '';
                bValue = bUserSpan.getAttribute('data-username') || '';
            } else {
                const aCell = a.querySelector(`td:nth-child(${getCellIndex(sortField)})`);
                const bCell = b.querySelector(`td:nth-child(${getCellIndex(sortField)})`);
                
                if (!aCell || !bCell) return 0;
                
                aValue = aCell.textContent.trim();
                bValue = bCell.textContent.trim();
            }
            
            if (direction === 'asc') {
                return aValue.localeCompare(bValue, 'zh-CN');
            } else {
                return bValue.localeCompare(aValue, 'zh-CN');
            }
        });
        
        rows.forEach(row => tableBody.appendChild(row));
    }
    
    function getCellIndex(sortField) {
        const fieldMap = {
            'id': 1,
            'name': 2,
            'report_number': 3,
            'created_at': 4,
            'machine_type': 5,
            'uploaded_by': 6
        };
        
        return fieldMap[sortField] || 1;
    }
    
    // 搜索功能
    function setupSearch() {
        const searchBtn = document.getElementById('search-btn');
        const resetSearchBtn = document.getElementById('reset-search-btn');
        
        if (searchBtn) {
            searchBtn.addEventListener('click', performSearch);
        }
        
        if (resetSearchBtn) {
            resetSearchBtn.addEventListener('click', resetSearch);
        }
        
        const searchInputs = document.querySelectorAll('#search-machine-name, #search-report-number');
        searchInputs.forEach(input => {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    performSearch();
                }
            });
        });
    }
    
    function performSearch() {
        const machineName = document.getElementById('search-machine-name').value.toLowerCase();
        const reportNumber = document.getElementById('search-report-number').value.toLowerCase();
        
        console.log('搜索执行中...');
        console.log('机床型号:', machineName);
        console.log('报告编号:', reportNumber);
        
        const table = document.querySelector('.table-responsive[style*="max-height: 600px"] table');
        if (!table) {
            console.log('未找到机床列表表格');
            return;
        }
        
        const tableBody = table.querySelector('tbody');
        if (!tableBody) {
            console.log('未找到表格body');
            return;
        }
        
        const rows = Array.from(tableBody.querySelectorAll('tr'));
        console.log('找到行数:', rows.length);
        
        let visibleCount = 0;
        
        rows.forEach((row, index) => {
            let showRow = true;
            
            if (machineName) {
                const nameCell = row.querySelector('td:nth-child(2)');
                if (nameCell) {
                    const nameText = nameCell.textContent.toLowerCase();
                    console.log(`行${index} 机床型号: "${nameText}"`);
                    if (!nameText.includes(machineName)) {
                        showRow = false;
                    }
                } else {
                    console.log(`行${index} 未找到机床型号单元格`);
                }
            }
            
            if (reportNumber && showRow) {
                const reportCell = row.querySelector('td:nth-child(3)');
                if (reportCell) {
                    const reportText = reportCell.textContent.toLowerCase();
                    console.log(`行${index} 报告编号: "${reportText}"`);
                    if (!reportText.includes(reportNumber)) {
                        showRow = false;
                    }
                } else {
                    console.log(`行${index} 未找到报告编号单元格`);
                }
            }
            
            row.style.display = showRow ? '' : 'none';
            if (showRow) visibleCount++;
        });
        
        console.log('搜索完成，显示行数:', visibleCount);
    }
    
    function resetSearch() {
        document.getElementById('search-machine-name').value = '';
        document.getElementById('search-report-number').value = '';
        
        const table = document.querySelector('.table-responsive[style*="max-height: 600px"] table');
        if (table) {
            const tableBody = table.querySelector('tbody');
            if (tableBody) {
                const rows = tableBody.querySelectorAll('tr');
                rows.forEach(row => {
                    row.style.display = '';
                });
            }
        }
    }
    
    function setupColumnWidths() {
        const machineNameColumn = document.querySelector('.machine-name-column');
        const reportNumberColumn = document.querySelector('.report-number-column');
        
        if (machineNameColumn && reportNumberColumn) {
            const uploadedByColumn = document.querySelector('th:has(.sort-link[data-sort="uploaded_by"])');
            const isAdmin = uploadedByColumn !== null;
            
            if (isAdmin) {
                machineNameColumn.style.width = '22%';
                reportNumberColumn.style.width = '18%';
            } else {
                machineNameColumn.style.width = '26%';
                reportNumberColumn.style.width = '22%';
            }
        }
    }