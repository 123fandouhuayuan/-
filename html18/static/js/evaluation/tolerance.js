// 全局变量 - 避免重复声明
    if (typeof toleranceHistory === 'undefined') {
        var toleranceHistory = JSON.parse(localStorage.getItem('toleranceHistory') || '[]');
    }
    if (typeof selectedMachineType === 'undefined') {
        var selectedMachineType = localStorage.getItem('selectedMachineType') || '';
    }
    
    // 自动保存容差数据功能 - 用于在特定条件下自动触发保存
    const AutoToleranceSaver = {
        // 检查元素是否存在并可见
        isElementReady: function(selector) {
            const element = document.querySelector(selector);
            return element && element.offsetParent !== null;
        },
        
        // 执行自动保存 - 不显示确认对话框，静默保存
        performAutoSave: function(machineTypes) {
            console.log('[AutoToleranceSaver] 开始自动保存容差数据...');
            
            const typesToSave = machineTypes || ['machining_center', 'boring_milling_machine'];
            
            // 优先使用全局加载器从服务器获取最新数据
            if (typeof ToleranceAutoLoader !== 'undefined' && ToleranceAutoLoader.isLoaded) {
                console.log('[AutoToleranceSaver] 使用全局加载器的缓存数据');
                typesToSave.forEach(function(machineType) {
                    const data = ToleranceAutoLoader.getToleranceData(machineType);
                    if (Object.keys(data).length > 0) {
                        const dataKey = `toleranceData_${machineType}`;
                        localStorage.setItem(dataKey, JSON.stringify(data));
                        console.log(`[AutoToleranceSaver] 已从全局加载器同步 ${machineType} 的容差数据`);
                    }
                });
            }
            
            // 如果当前页面有DOM表格，也执行DOM数据保存
            const hasToleranceTables = document.querySelector('.tolerance-table');
            if (hasToleranceTables) {
                typesToSave.forEach(function(machineType) {
                    const originalMachineType = selectedMachineType;
                    selectedMachineType = machineType;
                    
                    if (typeof saveToleranceData === 'function') {
                        try {
                            saveToleranceData();
                            console.log(`[AutoToleranceSaver] 已从DOM表格保存 ${machineType} 的容差数据`);
                        } catch (e) {
                            console.error(`[AutoToleranceSaver] 保存 ${machineType} 容差数据失败:`, e);
                        }
                    }
                    
                    selectedMachineType = originalMachineType;
                });
            }
            
            console.log('[AutoToleranceSaver] 自动保存完成');
        },
        
        // 初始化 - 检查当前页面URL并绑定事件
        init: function() {
            const pathname = window.location.pathname;
            
            console.log('[AutoToleranceSaver] 初始化，当前路径:', pathname);
            
            // 监听全局加载器完成事件
            document.addEventListener('toleranceDataLoaded', (e) => {
                console.log('[AutoToleranceSaver] 全局允差数据加载完成事件触发');
                this.performAutoSave();
            });
            
            // 条件2: 检查是否在 /evaluation/run_user/ 页面
            if (pathname.includes('/evaluation/run_user/') || pathname.includes('/evaluation/run_user')) {
                console.log('[AutoToleranceSaver] 检测到评价运行页面，准备自动保存');
                
                if (document.readyState === 'complete') {
                    setTimeout(() => this.performAutoSave(), 500);
                } else {
                    window.addEventListener('load', () => {
                        setTimeout(() => this.performAutoSave(), 500);
                    });
                }
            }
            
            // 条件1: 绑定信息熵计算按钮点击事件
            this.bindEntropyCalcButton();
        },
        
        // 绑定信息熵计算按钮事件
        bindEntropyCalcButton: function() {
            const self = this;
            
            document.addEventListener('click', function(e) {
                const target = e.target;
                const isEntropyBtn = target.id === 'entropy-calc-btn' || 
                                     target.closest('#entropy-calc-btn') ||
                                     target.textContent.includes('信息熵') ||
                                     target.textContent.includes('立即使用');
                
                if (isEntropyBtn) {
                    console.log('[AutoToleranceSaver] 检测到信息熵计算按钮点击');
                    setTimeout(function() {
                        self.performAutoSave();
                    }, 100);
                }
            });
            
            const entropyBtn = document.getElementById('entropy-calc-btn');
            if (entropyBtn) {
                console.log('[AutoToleranceSaver] 找到信息熵计算按钮，已添加自动保存监听');
            }
        }
    };
    
    // 模态框关闭后焦点返回逻辑
    document.addEventListener('DOMContentLoaded', function() {
        // 初始化自动保存功能
        AutoToleranceSaver.init();
        
        // 在允差管理页面加载时，自动从DOM读取所有机床类型的数据
        const pathname = window.location.pathname;
        if (pathname.includes('tolerance-management') || pathname.includes('tolerance_management')) {
            console.log('[ToleranceDOMSaver] 检测到允差管理页面，准备从DOM读取所有数据');
            setTimeout(function() {
                saveAllToleranceDataFromDOM();
            }, 1000);
        }
        
        // 返回修正按钮点击事件
        const closeModalAndFocusBtn = document.getElementById('closeModalAndFocusInput');
        if (closeModalAndFocusBtn) {
            closeModalAndFocusBtn.addEventListener('click', function() {
                const modal = bootstrap.Modal.getInstance(document.getElementById('toleranceOutOfRangeModal'));
                if (modal) modal.hide();
                
                // 延迟执行以确保模态框完全关闭
                setTimeout(function() {
                    if (window.lastOutOfRangeInput) {
                        window.lastOutOfRangeInput.focus();
                        window.lastOutOfRangeInput.select();
                        window.lastOutOfRangeInput = null;
                    }
                }, 300);
            });
        }
        
        // 监听模态框隐藏事件，确保关闭按钮也能正确返回焦点
        const toleranceModal = document.getElementById('toleranceOutOfRangeModal');
        if (toleranceModal) {
            toleranceModal.addEventListener('hidden.bs.modal', function() {
                setTimeout(function() {
                    if (window.lastOutOfRangeInput) {
                        window.lastOutOfRangeInput.focus();
                        window.lastOutOfRangeInput.select();
                        window.lastOutOfRangeInput = null;
                    }
                }, 300);
            });
        }
    });
    
    // 从DOM直接读取所有机床类型的允差数据并保存到localStorage
    function saveAllToleranceDataFromDOM() {
        console.log('[ToleranceDOMSaver] 开始从DOM读取所有机床类型的允差数据...');
        
        const machineTypes = ['machining_center', 'boring_milling_machine'];
        let totalSaved = 0;
        
        // 保存原始状态
        const originalStates = {
            contentSection: null,
            tableSection: null,
            selectedMachineType: selectedMachineType
        };
        
        // 获取主要区域元素
        const contentSection = document.getElementById('content-section');
        const tableSection = document.getElementById('tolerance-table-section');
        
        // 临时显示表格区域
        if (contentSection) {
            originalStates.contentSection = contentSection.classList.contains('hidden');
            contentSection.classList.remove('hidden');
        }
        if (tableSection) {
            originalStates.tableSection = tableSection.classList.contains('hidden');
            tableSection.classList.remove('hidden');
        }
        
        machineTypes.forEach(function(machineType) {
            const dataKey = `toleranceData_${machineType}`;
            const toleranceData = {};
            
            // 查找该机床类型的所有表格（包括隐藏的）
            const allTables = document.querySelectorAll(`.tolerance-table[data-machine-type="${machineType}"]`);
            
            console.log(`[ToleranceDOMSaver] ${machineType} 找到 ${allTables.length} 个表格`);
            
            if (allTables.length === 0) {
                console.log(`[ToleranceDOMSaver] ${machineType} 没有找到表格，跳过`);
                return;
            }
            
            // 临时显示所有隐藏的表格以便读取数据
            const hiddenTables = [];
            allTables.forEach(function(table) {
                if (table.classList.contains('hidden') || table.style.display === 'none') {
                    hiddenTables.push(table);
                    table.classList.remove('hidden');
                    table.style.display = 'block';
                }
            });
            
            // 遍历所有表格读取数据
            allTables.forEach(function(table) {
                const precision = table.dataset.precision;
                console.log(`[ToleranceDOMSaver] 处理 ${machineType} 的 ${precision} 表格`);
                
                const rows = table.querySelectorAll('tbody tr');
                console.log(`[ToleranceDOMSaver] 找到 ${rows.length} 行数据`);
                
                rows.forEach(function(row) {
                    const firstCell = row.querySelector('td:first-child');
                    if (!firstCell) return;
                    
                    const testItem = firstCell.textContent.trim().replace(/\s+/g, ' ');
                    if (!testItem) return;
                    
                    const toleranceValues = row.querySelectorAll('.tolerance-value');
                    
                    if (!toleranceValues.length) return;
                    
                    let values = [];
                    toleranceValues.forEach(function(toleranceValue) {
                        const valueCells = toleranceValue.querySelectorAll('table td');
                        if (valueCells.length > 0) {
                            valueCells.forEach(function(cell) {
                                const cellValue = cell.textContent.trim();
                                if (cellValue && cellValue !== '' && !isNaN(parseFloat(cellValue))) {
                                    values.push(cellValue);
                                }
                            });
                        } else {
                            const directCells = toleranceValue.querySelectorAll(':scope > td');
                            if (directCells.length > 0) {
                                directCells.forEach(function(cell) {
                                    const cellValue = cell.textContent.trim();
                                    if (cellValue && cellValue !== '' && !isNaN(parseFloat(cellValue))) {
                                        values.push(cellValue);
                                    }
                                });
                            } else {
                                const cellValue = toleranceValue.textContent.trim();
                                if (cellValue && !isNaN(parseFloat(cellValue))) {
                                    values.push(cellValue);
                                }
                            }
                        }
                    });
                    
                    if (values.length > 0) {
                        toleranceData[testItem] = values.join(', ');
                        console.log(`[ToleranceDOMSaver] ${testItem}: ${values.join(', ')}`);
                    }
                });
            });
            
            // 恢复表格的隐藏状态
            hiddenTables.forEach(function(table) {
                table.classList.add('hidden');
                table.style.display = 'none';
            });
            
            // 保存到localStorage
            if (Object.keys(toleranceData).length > 0) {
                localStorage.setItem(dataKey, JSON.stringify(toleranceData));
                console.log(`[ToleranceDOMSaver] ${machineType} 已保存 ${Object.keys(toleranceData).length} 条数据到 localStorage`);
                totalSaved += Object.keys(toleranceData).length;
            } else {
                console.log(`[ToleranceDOMSaver] ${machineType} 没有读取到数据`);
            }
        });
        
        // 恢复原始状态
        if (contentSection && originalStates.contentSection) {
            contentSection.classList.add('hidden');
        }
        if (tableSection && originalStates.tableSection) {
            tableSection.classList.add('hidden');
        }
        selectedMachineType = originalStates.selectedMachineType;
        
        console.log(`[ToleranceDOMSaver] 完成，共保存 ${totalSaved} 条数据`);
        
        // 触发事件通知其他组件
        const event = new CustomEvent('toleranceDataLoaded', {
            detail: {
                machining_center: JSON.parse(localStorage.getItem('toleranceData_machining_center') || '{}'),
                boring_milling_machine: JSON.parse(localStorage.getItem('toleranceData_boring_milling_machine') || '{}')
            }
        });
        document.dispatchEvent(event);
        
        return totalSaved;
    }
    
    // 暴露到全局作用域
    window.saveAllToleranceDataFromDOM = saveAllToleranceDataFromDOM;
    
    // 读取并应用主轴类型数据
    function applySpindleTypeData() {
        console.log('开始读取并应用主轴类型数据...');
        
        // 从localStorage读取主轴类型数据
        const spindleData = JSON.parse(localStorage.getItem('spindle_type_data') || '{}');
        
        if (!spindleData.spindle_type) {
            console.log('未找到主轴类型数据，使用默认值（整体主轴）');
            return;
        }
        
        console.log('读取到主轴类型数据:', spindleData);
        
        // 获取对应的允差值
        const tolerances = spindleData.spindle_tolerances;
        
        if (!tolerances) {
            console.error('主轴类型数据中缺少允差值');
            return;
        }
        
        console.log('获取到的允差值:', tolerances);
        
        // 查找并更新主轴锥孔径向跳动的允差值
        updateSpindleRunoutTolerances(spindleData.spindle_type, tolerances);
    }
    
    // 更新主轴锥孔径向跳动允差值
    function updateSpindleRunoutTolerances(spindleType, tolerances) {
        console.log('开始更新主轴锥孔径向跳动允差值，主轴类型:', spindleType);
        
        // 方法1：按照统一的类名逻辑查找并修改输入框值
        console.log('方法1：按照统一的类名逻辑查找输入框');
        
        // 查找所有主轴锥孔径向跳动允差输入框
        const spindleInputs = document.querySelectorAll('.spindle-runout-tolerance');
        console.log(`找到 ${spindleInputs.length} 个主轴锥孔径向跳动允差输入框`);
        
        let updatedCount = 0;
        
        // 根据主轴类型更新对应的输入框值
        spindleInputs.forEach((input, index) => {
            const inputSpindleType = input.getAttribute('data-spindle-type');
            const inputPosition = input.getAttribute('data-position');
            console.log(`输入框 ${index}: 主轴类型=${inputSpindleType}, 位置=${inputPosition}, 当前值=${input.value}`);
            
            // 如果输入框的主轴类型与当前选择的主轴类型匹配，则更新值
            if (inputSpindleType === spindleType) {
                let newValue = '';
                
                if (inputPosition === 'near') {
                    newValue = tolerances.near_spindle_end;
                } else if (inputPosition === 'away') {
                    newValue = tolerances.away_from_spindle_end;
                }
                
                if (newValue && input.value !== newValue.toString()) {
                    console.log(`更新输入框 ${index}: ${input.value} → ${newValue}`);
                    
                    // 临时移除只读属性（如果存在）
                    const originalReadOnly = input.readOnly;
                    if (input.readOnly) {
                        input.readOnly = false;
                    }
                    
                    // 更新值
                    input.value = newValue;
                    
                    // 恢复只读属性
                    if (originalReadOnly) {
                        input.readOnly = true;
                    }
                    
                    // 触发change事件
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    updatedCount++;
                }
            }
        });
        
        if (updatedCount > 0) {
            console.log(`统一类名更新完成：成功更新 ${updatedCount} 个输入框`);
            showSpindleUpdateResult(spindleType);
            return;
        }
        
        // 方法2：直接查找并修改输入框值（备用方法）
        console.log('方法1未找到输入框，尝试方法2：直接查找输入框');
        
        // 查找所有只读的数字输入框
        const allReadonlyInputs = document.querySelectorAll('input[type="number"][readonly]');
        console.log(`找到 ${allReadonlyInputs.length} 个只读数字输入框`);
        
        updatedCount = 0;
        
        // 查找并更新值为0.007和0.015的输入框
        allReadonlyInputs.forEach((input, index) => {
            console.log(`输入框 ${index}: value=${input.value}`);
            
            // 如果当前值是整体主轴的默认值，则更新为附加主轴的值
            if (input.value === '0.007' && spindleType === 'attached') {
                console.log('找到值为0.007的输入框，更新为0.01');
                
                // 临时移除只读属性
                const originalReadOnly = input.readOnly;
                input.readOnly = false;
                
                // 更新值
                input.value = tolerances.near_spindle_end; // 0.01
                
                // 恢复只读属性
                input.readOnly = originalReadOnly;
                
                // 触发change事件
                input.dispatchEvent(new Event('change', { bubbles: true }));
                
                updatedCount++;
                console.log('更新成功：0.007 → 0.01');
            }
            
            if (input.value === '0.015' && spindleType === 'attached') {
                console.log('找到值为0.015的输入框，更新为0.02');
                
                // 临时移除只读属性
                const originalReadOnly = input.readOnly;
                input.readOnly = false;
                
                // 更新值
                input.value = tolerances.away_from_spindle_end; // 0.02
                
                // 恢复只读属性
                input.readOnly = originalReadOnly;
                
                // 触发change事件
                input.dispatchEvent(new Event('change', { bubbles: true }));
                
                updatedCount++;
                console.log('更新成功：0.015 → 0.02');
            }
            
            // 如果是整体主轴，确保值正确
            if (spindleType === 'integral') {
                if (input.value === '0.01' || input.value === '0.02') {
                    console.log(`找到值为${input.value}的输入框，需要恢复为整体主轴值`);
                    
                    // 临时移除只读属性
                    const originalReadOnly = input.readOnly;
                    input.readOnly = false;
                    
                    // 根据当前值判断应该恢复为什么值
                    if (input.value === '0.01') {
                        input.value = 0.007;
                        console.log('恢复成功：0.01 → 0.007');
                    } else if (input.value === '0.02') {
                        input.value = 0.015;
                        console.log('恢复成功：0.02 → 0.015');
                    }
                    
                    // 恢复只读属性
                    input.readOnly = originalReadOnly;
                    
                    // 触发change事件
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    updatedCount++;
                }
            }
        });
        
        if (updatedCount > 0) {
            console.log(`直接更新完成：成功更新 ${updatedCount} 个输入框`);
            showSpindleUpdateResult(spindleType);
            return;
        }
        
        console.warn('未找到需要更新的主轴锥孔径向跳动输入框');
    }
    
    // 显示主轴更新结果
    function showSpindleUpdateResult(spindleType) {
        const spindleTypeName = spindleType === 'integral' ? '整体主轴' : '附加主轴';
        console.log(`主轴锥孔径向跳动允差值已更新为 ${spindleTypeName} 标准`);
        
        // 可以添加视觉提示（如果需要）
        // 例如：在页面顶部显示提示信息
    }
    
    // 获取主轴平行度允差值
    function getSpindleParallelTolerance() {
        console.log('开始查找主轴平行度允差值（仅加工中心）');
        
        // 临时显示几何精度表格（如果被隐藏了）
        const geometricTables = document.querySelectorAll('.tolerance-table[data-precision="geometric"][data-machine-type="machining_center"]');
        let wasHidden = false;
        geometricTables.forEach(function(table) {
            if (table.classList.contains('hidden')) {
                table.classList.remove('hidden');
                table.style.display = 'block';
                wasHidden = true;
                console.log('临时显示几何精度表格');
            }
        });
        
        // 只查找加工中心的几何精度表格
        const machiningCenterTable = document.querySelector('.tolerance-table[data-machine-type="machining_center"][data-precision="geometric"]:not(.hidden)');
        
        let tolerance = 0.015;
        
        if (!machiningCenterTable) {
            console.warn('未找到加工中心几何精度表格，使用默认值0.015');
        } else {
            // 在加工中心表格中查找包含主轴平行度的表格行
            const rows = machiningCenterTable.querySelectorAll('tr[data-category="parallelism"]');
            console.log(`在加工中心表格中找到 ${rows.length} 个平行度行`);
            
            for (let row of rows) {
                // 查找第一列单元格中的文本内容
                const firstCell = row.querySelector('td:first-child');
                
                // 检查文本匹配
                const hasMatch = firstCell && firstCell.textContent.includes('主轴轴线和Z轴线运动间的平行度');
                console.log('检查主轴平行度行，匹配结果:', hasMatch);
                
                if (hasMatch) {
                    console.log('找到主轴平行度行');
                    
                    // 在该行中查找允差值（第三列）
                    const toleranceCell = row.querySelector('td:nth-child(3)');
                    if (toleranceCell) {
                        console.log('找到主轴平行度行的第三列单元格');
                        
                        // 详细调试：检查单元格结构
                        const toleranceValueDiv = toleranceCell.querySelector('.tolerance-value');
                        if (toleranceValueDiv) {
                            console.log('找到主轴平行度的tolerance-value div');
                            console.log('tolerance-value div内容:', toleranceValueDiv.innerHTML);
                            
                            // 直接从tolerance-value div的文本内容中提取允差值
                            const toleranceText = toleranceValueDiv.textContent.trim();
                            if (toleranceText) {
                                tolerance = parseFloat(toleranceText);
                                console.log('找到主轴平行度允差值:', tolerance);
                                break;
                            } else {
                                console.warn('在主轴平行度行中允差值为空');
                            }
                        } else {
                            console.warn('在主轴平行度行中未找到tolerance-value div');
                        }
                    } else {
                        console.warn('在主轴平行度行中未找到第三列单元格');
                    }
                }
            }
            
            if (tolerance === 0.015) {
                console.warn('未在加工中心找到主轴平行度允差值，使用默认值0.015');
            }
        }
        
        // 恢复几何精度表格的隐藏状态
        if (wasHidden) {
            geometricTables.forEach(function(table) {
                table.classList.add('hidden');
                table.style.display = 'none';
                console.log('恢复几何精度表格隐藏状态');
            });
        }
        
        return tolerance;
    }
    
    // 获取位置精度允差值
    function getPositionTolerance(axisType, axisTravel) {
        console.log('开始查找位置精度允差值（仅加工中心）:', axisType, '轴行程:', axisTravel);
        
        // 只查找加工中心的位置精度表格
        const machiningCenterTable = document.querySelector('.tolerance-table[data-machine-type="machining_center"][data-precision="position"]:not(.hidden)');
        
        if (!machiningCenterTable) {
            console.warn('未找到加工中心位置精度表格，使用默认值');
            console.log('详细调试：检查所有位置精度表格状态');
            const allTables = document.querySelectorAll('.tolerance-table[data-precision="position"]');
            allTables.forEach((table, index) => {
                console.log(`位置精度表格 ${index + 1}:`, {
                    machineType: table.dataset.machineType,
                    hidden: table.classList.contains('hidden'),
                    display: table.style.display,
                    visible: table.offsetParent !== null
                });
            });
            return getDefaultPositionTolerance(axisType, axisTravel);
        }
        
        // 在加工中心表格中查找包含重复定位精度的表格行
        const rows = machiningCenterTable.querySelectorAll('tr[data-category="repeatability"]');
        console.log(`在加工中心表格中找到 ${rows.length} 个重复定位精度行`);
        
        for (let row of rows) {
            // 查找第一列单元格中的文本内容
            const firstCell = row.querySelector('td:first-child');
            
            if (firstCell) {
                const cellText = firstCell.textContent.trim();
                console.log(`检查重复定位精度行，文本内容:`, cellText);
                
                // 检查文本匹配 - 双向重复定位精度R
                if (cellText.includes('双向重复定位精度R')) {
                    console.log(`找到双向重复定位精度R行`);
                    
                    // 根据轴行程确定范围区间索引
                    let rangeIndex = getTravelRangeIndex(axisTravel, selectedMachineType);
                    
                    // 特殊处理：根据项目名称判断是否需要特殊处理
                    const firstCellText = row.querySelector('td:first-child').textContent.trim();
                    if (selectedMachineType === 'boring_milling_machine') {
                        // 镗铣床的特殊项目
                        if (firstCellText.includes('立柱移动的直线度')) {
                            // 立柱移动的直线度只有两个范围：1000内和超过1000
                            // 超过1000的都使用索引1的值（0.030）
                            rangeIndex = axisTravel > 1000 ? 1 : 0;
                            console.log(`镗铣床立柱移动的直线度，使用特殊范围索引:`, rangeIndex);
                        } else if (firstCellText.includes('立柱移动的角度偏差')) {
                            // 立柱移动的角度偏差只有一个范围：a)、b)和c)
                            // 使用索引0的值（0.040）
                            rangeIndex = 0;
                            console.log(`镗铣床立柱移动的角度偏差，使用固定索引:`, rangeIndex);
                        } else if (firstCellText.includes('主轴箱移动（Y轴）对')) {
                            // 主轴箱移动（Y轴）对：a）工作台移动（X轴）的垂直度；b）立柱移动的垂直度
                            // 只有一个范围：任意1000测量长度上
                            // 使用索引1的值（0.030）
                            rangeIndex = 1;
                            console.log(`镗铣床主轴箱移动（Y轴）对，使用固定索引:`, rangeIndex);
                        } else if (firstCellText.includes('主轴箱移动（Y轴）的角度偏差')) {
                            // 主轴箱移动（Y轴）的角度偏差有两个范围：4000以内和超过4000
                            // 超过4000的都使用索引2的值（0.060）
                            rangeIndex = axisTravel > 4000 ? 2 : 1;
                            console.log(`镗铣床主轴箱移动（Y轴）的角度偏差，使用特殊范围索引:`, rangeIndex);
                        } else if (firstCellText.includes('工作台移动（X轴）的角度偏差')) {
                            // 工作台移动（X轴）的角度偏差有两个范围：4000以内和超过4000
                            // 超过4000的都使用索引2的值（0.060）
                            rangeIndex = axisTravel > 4000 ? 2 : 1;
                            console.log(`镗铣床工作台移动（X轴）的角度偏差，使用特殊范围索引:`, rangeIndex);
                        } else if (firstCellText.includes('主轴箱移动（Y轴）的直线度')) {
                            // 主轴箱移动（Y轴）的直线度有七个范围
                            // 使用Y轴行程来确定范围索引
                            if (axisTravel <= 1000) rangeIndex = 1;
                            else if (axisTravel <= 2000) rangeIndex = 2;
                            else if (axisTravel <= 3000) rangeIndex = 3;
                            else if (axisTravel <= 4000) rangeIndex = 4;
                            else if (axisTravel <= 5000) rangeIndex = 5;
                            else if (axisTravel <= 6000) rangeIndex = 6;
                            else rangeIndex = 7;
                            console.log(`镗铣床主轴箱移动（Y轴）的直线度，使用特殊范围索引:`, rangeIndex);
                        } else if (firstCellText.includes('工作台移动（X轴）的直线度')) {
                            // 工作台移动（X轴）的直线度有四个范围
                            // 使用正常的范围索引
                            console.log(`镗铣床工作台移动（X轴）的直线度，使用正常范围索引:`, rangeIndex);
                        }
                    }
                    
                    console.log(`轴行程 ${axisTravel} 对应的范围索引:`, rangeIndex);
                    
                    // 在该行中查找对应范围的允差值
                    const toleranceCell = row.querySelector(`td:nth-child(${rangeIndex + 2})`); // +2因为第一列是项目名称
                    if (toleranceCell) {
                        console.log(`找到对应范围的允差值单元格`);
                        
                        // 详细调试：检查单元格结构
                        const toleranceValueDiv = toleranceCell.querySelector('.tolerance-value');
                        if (toleranceValueDiv) {
                            console.log(`找到允差值的tolerance-value div`);
                            console.log(`tolerance-value div内容:`, toleranceValueDiv.innerHTML);
                            
                            // 直接从tolerance-value div的文本内容中提取允差值
                            const toleranceText = toleranceValueDiv.textContent.trim();
                            if (toleranceText) {
                                const tolerance = parseFloat(toleranceText);
                                console.log(`找到${axisType}轴位置精度允差值:`, tolerance);
                                return tolerance;
                            } else {
                                console.warn(`在允差值单元格中允差值为空`);
                            }
                        } else {
                            console.warn(`在允差值单元格中未找到tolerance-value div`);
                        }
                    } else {
                        console.warn(`在重复定位精度行中未找到对应范围的单元格`);
                    }
                }
            }
        }
        
        console.warn(`未在加工中心找到${axisType}轴位置精度允差值，使用默认值`);
        return getDefaultPositionTolerance(axisType, axisTravel);
    }
    
    // 根据轴行程确定范围区间索引
    function getTravelRangeIndex(travel, machineType) {
        // 如果指定了机床类型，使用对应的范围
        if (machineType === 'boring_milling_machine') {
            // 镗铣床的范围
            if (travel <= 1000) return 0; // 测量长度在1000内
            if (travel <= 2000) return 1; // 测量长度在1000到2000
            if (travel <= 3000) return 2; // 测量长度在2000到3000
            return 3; // 测量长度在3000到4000
        } else {
            // 加工中心的范围（默认）
            if (travel <= 500) return 0; // ≤500
            if (travel <= 800) return 1; // 500-800
            if (travel <= 1250) return 2; // 800-1250
            return 3; // 1250-2000
        }
    }
    
    // 获取默认位置精度允差值
    function getDefaultPositionTolerance(axisType, axisTravel) {
        const rangeIndex = getTravelRangeIndex(axisTravel, selectedMachineType);
        const defaultTolerances = [0.012, 0.015, 0.018, 0.020];
        const tolerance = defaultTolerances[rangeIndex] || 0.02;
        console.log(`使用默认${axisType}轴位置精度允差值:`, tolerance);
        return tolerance;
    }
    
    // 获取轴行程数据
    function getAxisTravel(axisType) {
        // 从localStorage获取机床参数
        const machineParams = JSON.parse(localStorage.getItem('machine_params') || '{}');
        
        // 调试：检查machine_params数据
        console.log(`获取${axisType}轴行程 - machine_params数据:`, machineParams);
        
        let travel = 1300; // 默认值
        
        if (axisType === 'X轴' && machineParams.x_axis_travel) {
            travel = parseFloat(machineParams.x_axis_travel);
        } else if (axisType === 'Y轴' && machineParams.y_axis_travel) {
            travel = parseFloat(machineParams.y_axis_travel);
        } else if (axisType === 'Z轴' && machineParams.z_axis_travel) {
            travel = parseFloat(machineParams.z_axis_travel);
        }
        
        console.log(`获取${axisType}轴行程:`, travel);
        return travel;
    }

    // 获取垂直度允差值
    function getPerpendicularityTolerance(perpendicularityType) {
        console.log('开始查找垂直度允差值（仅加工中心）:', perpendicularityType);
        
        // 临时显示几何精度表格（如果被隐藏了）
        const geometricTables = document.querySelectorAll('.tolerance-table[data-precision="geometric"][data-machine-type="machining_center"]');
        let wasHidden = false;
        geometricTables.forEach(function(table) {
            if (table.classList.contains('hidden')) {
                table.classList.remove('hidden');
                table.style.display = 'block';
                wasHidden = true;
                console.log('临时显示几何精度表格');
            }
        });
        
        // 只查找加工中心的几何精度表格
        const machiningCenterTable = document.querySelector('.tolerance-table[data-machine-type="machining_center"][data-precision="geometric"]:not(.hidden)');
        
        let tolerance = 0.02;
        
        if (!machiningCenterTable) {
            console.warn('未找到加工中心几何精度表格，使用默认值0.02');
        } else {
            // 在加工中心表格中查找包含垂直度的表格行
            const rows = machiningCenterTable.querySelectorAll('tr[data-category="perpendicularity"]');
            console.log(`在加工中心表格中找到 ${rows.length} 个垂直度行`);
            
            for (let row of rows) {
                // 查找第一列单元格中的文本内容
                const firstCell = row.querySelector('td:first-child');
                
                if (firstCell) {
                    const cellText = firstCell.textContent.trim();
                    console.log(`检查垂直度行，文本内容:`, cellText);
                    
                    // 检查文本匹配
                    let hasMatch = false;
                    
                    if (perpendicularityType === 'yx' && cellText.includes('Y轴线运动和X轴线运动间的垂直度')) {
                        hasMatch = true;
                    } else if (perpendicularityType === 'yz' && cellText.includes('Y轴线运动和Z轴线运动间的垂直度')) {
                        hasMatch = true;
                    } else if (perpendicularityType === 'zx' && cellText.includes('Z轴线运动和X轴线运动间的垂直度')) {
                        hasMatch = true;
                    } else if (perpendicularityType === 'spindle_x' && cellText.includes('主轴轴线和X轴线运动间的垂直度')) {
                        hasMatch = true;
                    } else if (perpendicularityType === 'spindle_y' && cellText.includes('主轴轴线和Y轴线运动间的垂直度')) {
                        hasMatch = true;
                    } else if (perpendicularityType === 'zx' && cellText.includes('主轴箱移动（Y轴）对')) {
                        // 主轴箱移动（Y轴）对：a）工作台移动（X轴）的垂直度；b）立柱移动的垂直度
                        hasMatch = true;
                    }
                    
                    console.log(`检查垂直度行，匹配结果:`, hasMatch);
                    
                    if (hasMatch) {
                        console.log(`找到${perpendicularityType}垂直度行`);
                        
                        // 在该行中查找允差值（第三列）
                        const toleranceCell = row.querySelector('td:nth-child(3)');
                        if (toleranceCell) {
                            console.log(`找到垂直度行的第三列单元格`);
                            
                            // 详细调试：检查单元格结构
                            const toleranceValueDiv = toleranceCell.querySelector('.tolerance-value');
                            if (toleranceValueDiv) {
                                console.log(`找到垂直度的tolerance-value div`);
                                console.log(`tolerance-value div内容:`, toleranceValueDiv.innerHTML);
                                
                                // 直接从tolerance-value div的文本内容中提取允差值
                                const toleranceText = toleranceValueDiv.textContent.trim();
                                if (toleranceText) {
                                    tolerance = parseFloat(toleranceText);
                                    console.log(`找到${perpendicularityType}垂直度允差值:`, tolerance);
                                    break;
                                } else {
                                    console.warn(`在垂直度行中允差值为空`);
                                }
                            } else {
                                console.warn(`在垂直度行中未找到tolerance-value div`);
                            }
                        } else {
                            console.warn(`在垂直度行中未找到第三列单元格`);
                        }
                    }
                }
            }
            
            if (tolerance === 0.02) {
                console.warn(`未在加工中心找到${perpendicularityType}垂直度允差值，使用默认值0.02`);
            }
        }
        
        // 恢复几何精度表格的隐藏状态
        if (wasHidden) {
            geometricTables.forEach(function(table) {
                table.classList.add('hidden');
                table.style.display = 'none';
                console.log('恢复几何精度表格隐藏状态');
            });
        }
        
        return tolerance;
    }

    // 存储进给轴角度允差数据
    function storeFeedAxisTolerances() {
        console.log('开始存储进给轴角度允差数据...');
        
        // 查找X轴、Y轴、Z轴角度偏差的允差值
        const xAxisTolerance = getAxisAngleTolerance('X轴');
        const yAxisTolerance = getAxisAngleTolerance('Y轴');
        const zAxisTolerance = getAxisAngleTolerance('Z轴');
        
        // 查找主轴平行度允差值
        const spindleParallelTolerance = getSpindleParallelTolerance();
        
        // 查找垂直度允差值
        const yxPerpendicularityTolerance = getPerpendicularityTolerance('yx');
        const yzPerpendicularityTolerance = getPerpendicularityTolerance('yz');
        const zxPerpendicularityTolerance = getPerpendicularityTolerance('zx');
        
        // 查找主轴垂直度允差值
        const spindleXPerpendicularityTolerance = getPerpendicularityTolerance('spindle_x');
        const spindleYPerpendicularityTolerance = getPerpendicularityTolerance('spindle_y');
        
        // 查找位置精度允差值（需要获取轴行程数据）
        const xAxisTravel = getAxisTravel('X轴');
        const yAxisTravel = getAxisTravel('Y轴');
        const zAxisTravel = getAxisTravel('Z轴');
        
        const xPositionTolerance = getPositionTolerance('X', xAxisTravel);
        const yPositionTolerance = getPositionTolerance('Y', yAxisTravel);
        const zPositionTolerance = getPositionTolerance('Z', zAxisTravel);
        
        console.log('获取到的允差值:', {
            x_axis: xAxisTolerance,
            y_axis: yAxisTolerance,
            z_axis: zAxisTolerance,
            spindle_parallel: spindleParallelTolerance,
            yx_perpendicularity: yxPerpendicularityTolerance,
            yz_perpendicularity: yzPerpendicularityTolerance,
            zx_perpendicularity: zxPerpendicularityTolerance,
            spindle_x_perpendicularity: spindleXPerpendicularityTolerance,
            spindle_y_perpendicularity: spindleYPerpendicularityTolerance,
            x_position: xPositionTolerance,
            y_position: yPositionTolerance,
            z_position: zPositionTolerance
        });
        
        // 存储到localStorage
        const feedAxisData = {
            feed_axis_tolerances: {
                x_axis_angle: xAxisTolerance,
                y_axis_angle: yAxisTolerance,
                z_axis_angle: zAxisTolerance,
                spindle_parallel: spindleParallelTolerance,
                yx_perpendicularity: yxPerpendicularityTolerance,
                yz_perpendicularity: yzPerpendicularityTolerance,
                zx_perpendicularity: zxPerpendicularityTolerance,
                spindle_x_perpendicularity: spindleXPerpendicularityTolerance,
                spindle_y_perpendicularity: spindleYPerpendicularityTolerance,
                x_position: xPositionTolerance,
                y_position: yPositionTolerance,
                z_position: zPositionTolerance
            },
            stored_at: new Date().toISOString(),
            source: '允差管理界面 - 几何精度和位置精度'
        };
        
        localStorage.setItem('feed_axis_tolerance_data', JSON.stringify(feedAxisData));
        
        console.log('进给轴角度允差数据存储完成:', feedAxisData);
        
        // 触发自定义事件通知其他页面组件
        if (typeof window.dispatchEvent === 'function') {
            var event = new CustomEvent('toleranceDataChanged');
            window.dispatchEvent(event);
            console.log('已触发允差值变化事件');
        }
    }
    
    // 获取指定轴的角度偏差允差值（仅从加工中心获取）
    function getAxisAngleTolerance(axisName) {
        console.log(`开始查找${axisName}角度偏差允差值（仅加工中心）`);
        
        // 临时显示几何精度表格（如果被隐藏了）
        const geometricTables = document.querySelectorAll('.tolerance-table[data-precision="geometric"][data-machine-type="machining_center"]');
        let wasHidden = false;
        geometricTables.forEach(function(table) {
            if (table.classList.contains('hidden')) {
                table.classList.remove('hidden');
                table.style.display = 'block';
                wasHidden = true;
                console.log('临时显示几何精度表格');
            }
        });
        
        // 只查找加工中心的几何精度表格
        const machiningCenterTable = document.querySelector('.tolerance-table[data-machine-type="machining_center"][data-precision="geometric"]:not(.hidden)');
        
        let tolerance = 0.060;
        
        if (!machiningCenterTable) {
            console.warn('未找到加工中心的几何精度表格，可能表格未显示');
            console.log('当前显示的表格:', document.querySelectorAll('.tolerance-table:not(.hidden)'));
            console.log('所有表格属性检查:');
            document.querySelectorAll('.tolerance-table:not(.hidden)').forEach((table, index) => {
                console.log(`表格${index}: machine-type=${table.dataset.machineType}, precision=${table.dataset.precision}`);
            });
        } else {
            // 在加工中心表格中查找包含指定轴角度偏差的表格行
            const rows = machiningCenterTable.querySelectorAll('tr[data-category="angle"]');
            console.log(`在加工中心表格中找到 ${rows.length} 个角度偏差行`);
            
            for (let row of rows) {
                // 查找第一列单元格中的文本内容
                const firstCell = row.querySelector('td:first-child');
                
                // 检查文本匹配
                const matchText = axisName.replace('轴', '') + '轴线运动的角度偏差';
                const hasMatch = firstCell && firstCell.textContent.includes(matchText);
                console.log(`检查${axisName}角度偏差行，匹配结果:`, hasMatch);
                
                if (hasMatch) {
                    console.log(`找到${axisName}角度偏差行`);
                    
                    // 在该行中查找允差值（第三列）
                    const toleranceCell = row.querySelector('td:nth-child(3)');
                    if (toleranceCell) {
                        console.log(`找到${axisName}角度偏差行的第三列单元格`);
                        
                        // 详细调试：检查单元格结构
                        const toleranceValueDiv = toleranceCell.querySelector('.tolerance-value');
                        if (toleranceValueDiv) {
                            console.log(`找到${axisName}角度偏差的tolerance-value div`);
                            console.log(`tolerance-value div内容:`, toleranceValueDiv.innerHTML);
                            
                            // 直接从tolerance-value div的文本内容中提取允差值
                            const toleranceText = toleranceValueDiv.textContent.trim();
                            if (toleranceText) {
                                tolerance = parseFloat(toleranceText);
                                console.log(`找到${axisName}角度偏差允差值:`, tolerance);
                                break;
                            } else {
                                console.warn(`在${axisName}角度偏差行中允差值为空`);
                            }
                        } else {
                            console.warn(`在${axisName}角度偏差行中未找到tolerance-value div`);
                        }
                    } else {
                        console.warn(`在${axisName}角度偏差行中未找到第三列单元格`);
                    }
                }
            }
            
            if (tolerance === 0.060) {
                console.warn(`未在加工中心找到${axisName}角度偏差允差值，使用默认值0.060`);
            }
        }
        
        // 恢复几何精度表格的隐藏状态
        if (wasHidden) {
            geometricTables.forEach(function(table) {
                table.classList.add('hidden');
                table.style.display = 'none';
                console.log('恢复几何精度表格隐藏状态');
            });
        }
        
        return tolerance;
    }
    

    
    // DOM加载完成后初始化
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DOM加载完成，初始化允差管理界面');
        
        // 绑定机床选择事件
        bindMachineSelectionEvents();
        
        // 注释掉自动显示内容的逻辑，让用户每次都手动选择机床类型
        // if (selectedMachineType) {
        //     document.getElementById('machine-type').value = selectedMachineType;
        //     if (selectedMachineType === 'horizontal_machining_center') {
        //         showContent();
        //     }
        // }
        
        // 加载修改历史
        loadHistory();
        
        console.log('允差管理界面初始化完成');
    });
    
    // 绑定机床选择事件
    function bindMachineSelectionEvents() {
        const confirmBtn = document.getElementById('confirm-machine-btn');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', function() {
                const machineTypeSelect = document.getElementById('machine-type');
                const selectedType = machineTypeSelect.value;
                
                if (!selectedType) {
                    alert('请选择机床类型');
                    return;
                }
                
                if (selectedType === 'machining_center' || selectedType === 'boring_milling_machine') {
                    // 选择了加工中心或镗铣床，保存选择并显示内容
                    selectedMachineType = selectedType;
                    localStorage.setItem('selectedMachineType', selectedMachineType);
                    showContent();
                    
                    // 如果是加工中心，读取并应用主轴类型数据
                    if (selectedType === 'machining_center') {
                        applySpindleTypeData();
                    }
                } else {
                    // 选择了其他机床类型，显示错误提示
                    alert('当前功能仅适用于加工中心和镗铣床');
                }
            });
        }
    }
    
    // 显示内容
    function showContent() {
        // 隐藏机床选择部分
        document.getElementById('machine-selection-section').classList.add('hidden');
        
        // 显示内容部分
        document.getElementById('content-section').classList.remove('hidden');
        document.getElementById('precision-type-section').classList.remove('hidden');
        document.getElementById('tolerance-table-section').classList.remove('hidden');
        document.getElementById('history-section').classList.remove('hidden');
        
        // 更新页面标题显示当前机床类型
        const machineTypeDisplay = selectedMachineType === 'machining_center' ? '加工中心' : '镗铣床';
        document.querySelector('.card-header h5 strong').textContent = `允差管理 - ${machineTypeDisplay}`;
        
        // 隐藏所有表格，然后显示当前机床类型对应的表格
        const toleranceTables = document.querySelectorAll('.tolerance-table');
        toleranceTables.forEach(function(table) {
            table.classList.add('hidden');
        });
        
        // 绑定精度类型按钮事件
        bindPrecisionTypeEvents();
        
        // 绑定编辑按钮事件
        bindEditEvents();
        
        // 绑定切换机床类型按钮事件
        bindSwitchMachineEvents();
        
        // 自动显示几何精度表格（默认显示几何精度）
        const geometricTables = document.querySelectorAll('.tolerance-table[data-precision="geometric"]');
        geometricTables.forEach(function(table) {
            const machineType = table.dataset.machineType || 'machining_center';
            if (machineType === selectedMachineType) {
                table.classList.remove('hidden');
                table.style.display = 'block';
                console.log('自动显示几何精度表格:', machineType);
            }
        });

        // 确保精度类型选择部分可见
        const precisionTypeSection = document.getElementById('precision-type-section');
        if (precisionTypeSection) {
            precisionTypeSection.classList.remove('hidden');
        }

        // 页面加载时自动保存所有允差数据到localStorage
        const dataKey = `toleranceData_${selectedMachineType}`;
        const existingData = localStorage.getItem(dataKey);
        if (!existingData) {
            console.log('localStorage中无允差数据，自动从表格中读取并保存');
            saveToleranceData();
        } else {
            console.log('localStorage中已存在允差数据，跳过自动保存');
            // 检查数据是否完整，如果不完整则重新保存
            const toleranceData = JSON.parse(existingData);
            const requiredItems = [
                // 位置精度数据
                '双向定位精度A', '轴线的平均双向位置偏差范围M', '双向定位系统偏差E', '轴线的反向差值B',
                // 加工精度数据
                '圆柱度', '孔中心轴线与基准孔A的垂直度', '孔中心轴线与基准孔B的垂直度', '孔中心轴线与基准孔C的垂直度',
                '孔中心轴线与基准孔A的距离', '孔中心轴线与基准孔B的距离', '孔中心轴线与基准孔C的距离'
            ];
            let dataIncomplete = false;
            requiredItems.forEach(function(item) {
                if (!toleranceData[item]) {
                    console.log(`缺少允差数据: ${item}`);
                    dataIncomplete = true;
                }
            });
            if (dataIncomplete) {
                console.log('允差数据不完整，重新从表格中读取并保存');
                saveToleranceData();
            }
        }

        // 加载允差数据
        loadToleranceData();
        
        console.log(`显示允差管理界面内容 (机床类型: ${selectedMachineType})`);
    }
    
    // 隐藏内容
    function hideContent() {
        // 显示机床选择部分
        document.getElementById('machine-selection-section').classList.remove('hidden');
        
        // 隐藏内容部分
        document.getElementById('content-section').classList.add('hidden');
        document.getElementById('precision-type-section').classList.add('hidden');
        document.getElementById('tolerance-table-section').classList.add('hidden');
        document.getElementById('history-section').classList.add('hidden');
        
        console.log('隐藏允差管理界面内容');
    }
    
    // 绑定切换机床类型按钮事件
    function bindSwitchMachineEvents() {
        const switchBtn = document.getElementById('switch-machine-btn');
        if (switchBtn) {
            switchBtn.addEventListener('click', function() {
                // 确认切换
                if (confirm('切换机床类型将重新加载页面，当前未保存的修改将会丢失。确定要切换吗？')) {
                    // 清除当前选择的机床类型
                    localStorage.removeItem('selectedMachineType');
                    
                    // 重新加载页面
                    location.reload();
                }
            });
        }
    }
    
    // 绑定精度类型按钮事件
    function bindPrecisionTypeEvents() {
        const precisionBtns = document.querySelectorAll('.precision-type-btn');
        const toleranceTables = document.querySelectorAll('.tolerance-table');
        
        precisionBtns.forEach(function(btn) {
            btn.addEventListener('click', function() {
                const precisionType = this.dataset.type;
                
                // 更新按钮激活状态
                precisionBtns.forEach(function(b) {
                    b.classList.remove('active');
                });
                this.classList.add('active');
                
                // 显示对应的表格，隐藏其他表格
                toleranceTables.forEach(function(table) {
                    const tableType = table.dataset.precision;
                    const machineType = table.dataset.machineType || 'machining_center';
                    
                    // 只显示当前选择的机床类型对应的表格
                    if (tableType === precisionType && machineType === selectedMachineType) {
                        table.classList.remove('hidden');
                        table.style.display = 'block';
                        
                        // 确保表格内的所有元素都可见
                        const rows = table.querySelectorAll('tbody tr');
                        rows.forEach(function(row) {
                            row.style.display = '';
                            
                            const cells = row.querySelectorAll('td');
                            cells.forEach(function(cell) {
                                const specDiv = cell.querySelector('.tolerance-spec');
                                const valueDiv = cell.querySelector('.tolerance-value');
                                const editDiv = cell.querySelector('.tolerance-edit');
                                
                                if (specDiv) {
                                    specDiv.style.display = 'flex';
                                    specDiv.style.visibility = 'visible';
                                    specDiv.style.opacity = '1';
                                    
                                    // 确保 specDiv 内的所有表格都可见
                                    const specTables = specDiv.querySelectorAll('table');
                                    specTables.forEach(function(specTable) {
                                        specTable.style.display = 'table';
                                        specTable.style.visibility = 'visible';
                                        specTable.style.opacity = '1';
                                    });
                                    
                                    // 确保 specDiv 内的所有行都可见
                                    const specRows = specDiv.querySelectorAll('tr');
                                    specRows.forEach(function(specRow) {
                                        specRow.style.display = 'table-row';
                                        specRow.style.visibility = 'visible';
                                        specRow.style.opacity = '1';
                                    });
                                    
                                    // 确保 specDiv 内的所有单元格都可见
                                    const specCells = specDiv.querySelectorAll('td');
                                    specCells.forEach(function(specCell) {
                                        specCell.style.display = 'table-cell';
                                        specCell.style.visibility = 'visible';
                                        specCell.style.opacity = '1';
                                    });
                                }
                                
                                if (valueDiv) {
                                    valueDiv.style.display = 'flex';
                                    valueDiv.style.visibility = 'visible';
                                    valueDiv.style.opacity = '1';
                                    
                                    // 确保 valueDiv 内的所有表格都可见
                                    const valueTables = valueDiv.querySelectorAll('table');
                                    valueTables.forEach(function(valueTable) {
                                        valueTable.style.display = 'table';
                                        valueTable.style.visibility = 'visible';
                                        valueTable.style.opacity = '1';
                                    });
                                    
                                    // 确保 valueDiv 内的所有行都可见
                                    const valueRows = valueDiv.querySelectorAll('tr');
                                    valueRows.forEach(function(valueRow) {
                                        valueRow.style.display = 'table-row';
                                        valueRow.style.visibility = 'visible';
                                        valueRow.style.opacity = '1';
                                    });
                                    
                                    // 确保 valueDiv 内的所有单元格都可见
                                    const valueCells = valueDiv.querySelectorAll('td');
                                    valueCells.forEach(function(valueCell) {
                                        valueCell.style.display = 'table-cell';
                                        valueCell.style.visibility = 'visible';
                                        valueCell.style.opacity = '1';
                                    });
                                }
                                
                                if (editDiv) {
                                    editDiv.style.display = 'flex';
                                    editDiv.style.visibility = 'visible';
                                    editDiv.style.opacity = '1';
                                    const editRows = editDiv.querySelectorAll('tr');
                                    editRows.forEach(function(editRow) {
                                        editRow.style.display = 'table-row';
                                        editRow.style.visibility = 'visible';
                                        editRow.style.opacity = '1';
                                    });
                                    // 确保 editDiv 内的所有元素都可见
                                    const editElements = editDiv.querySelectorAll('*');
                                    editElements.forEach(function(element) {
                                        element.style.display = '';
                                        element.style.visibility = 'visible';
                                        element.style.opacity = '1';
                                    });
                                }
                            });
                        });
                    } else {
                        table.classList.add('hidden');
                    }
                });
                

                
                // 加载允差数据，确保新显示的表格中的数据正确显示
                loadToleranceData();
                
                // 重新绑定编辑事件，确保新显示的表格中的按钮也有事件监听器
                bindEditEvents();
                
                // 如果是几何精度类型，存储进给轴允差数据
                if (precisionType === 'geometric') {
                    // 延迟执行，确保几何精度表格已完全显示
                    setTimeout(() => {
                        // 检查表格是否已显示
                        const machiningCenterTable = document.querySelector('.tolerance-table[data-machine-type="machining_center"][data-precision="geometric"]:not(.hidden)');
                        if (machiningCenterTable) {
                            console.log('几何精度表格已显示，开始存储进给轴允差数据');
                            storeFeedAxisTolerances();
                        } else {
                            console.warn('几何精度表格未显示，延迟重试');
                            // 如果表格未显示，延迟重试
                            setTimeout(() => {
                                storeFeedAxisTolerances();
                            }, 1000);
                        }
                    }, 1000);
                }
                
                // 如果是位置精度类型，存储位置精度允差数据
                if (precisionType === 'position') {
                    console.log('=== 开始处理位置精度类型 ===');
                    
                    // 立即检查表格显示状态
                    const allPositionTables = document.querySelectorAll('.tolerance-table[data-precision="position"]');
                    console.log(`立即检查：找到 ${allPositionTables.length} 个位置精度表格`);
                    
                    allPositionTables.forEach((table, index) => {
                        console.log(`位置精度表格 ${index + 1} 立即状态:`, {
                            machineType: table.dataset.machineType,
                            hidden: table.classList.contains('hidden'),
                            display: table.style.display,
                            visible: table.offsetParent !== null
                        });
                    });
                    
                    // 延迟执行，确保位置精度表格已完全显示
                    setTimeout(() => {
                        console.log('=== 延迟检查位置精度表格 ===');
                        
                        // 详细调试：检查所有位置精度表格
                        const allPositionTables = document.querySelectorAll('.tolerance-table[data-precision="position"]');
                        console.log(`延迟检查：找到 ${allPositionTables.length} 个位置精度表格`);
                        
                        allPositionTables.forEach((table, index) => {
                            console.log(`位置精度表格 ${index + 1} 延迟状态:`, {
                                machineType: table.dataset.machineType,
                                hidden: table.classList.contains('hidden'),
                                display: table.style.display,
                                visible: table.offsetParent !== null
                            });
                        });
                        
                        // 检查表格是否已显示
                        const positionTable = document.querySelector('.tolerance-table[data-machine-type="machining_center"][data-precision="position"]:not(.hidden)');
                        if (positionTable) {
                            console.log('位置精度表格已显示，开始存储位置精度允差数据');
                            storeFeedAxisTolerances();
                        } else {
                            console.warn('位置精度表格未显示，延迟重试');
                            // 如果表格未显示，延迟重试
                            setTimeout(() => {
                                console.log('=== 延迟重试检查位置精度表格 ===');
                                storeFeedAxisTolerances();
                            }, 1000);
                        }
                    }, 100);
                }
                
                console.log('选择精度类型:', precisionType);
            });
        });
        
        // 默认显示几何精度表格
        const geometricBtn = document.querySelector('.precision-type-btn[data-type="geometric"]');
        if (geometricBtn) {
            geometricBtn.click();
        }
    }
    
    // 独立保存允差值到localStorage
    function saveIndependentToleranceValue(testItem, index, value) {
        const toleranceData = JSON.parse(localStorage.getItem('toleranceData') || '{}');
        
        // 根据机床类型创建独立的数据存储键
        const machineType = selectedMachineType || 'machining_center';
        const dataKey = `toleranceData_${machineType}`;
        
        // 获取当前机床类型的数据
        const machineToleranceData = JSON.parse(localStorage.getItem(dataKey) || '{}');
        
        // 初始化检验项目的数据结构
        if (!machineToleranceData[testItem]) {
            machineToleranceData[testItem] = [];
        }
        
        // 更新允差值
        machineToleranceData[testItem][index] = value;
        
        // 保存到localStorage
        localStorage.setItem(dataKey, JSON.stringify(machineToleranceData));
        console.log(`保存允差值: ${testItem}[${index}] = ${value} (机床类型: ${machineType})`);
    }
    
    // 绑定编辑按钮事件
    function bindEditEvents() {
        // 只处理当前激活机床类型的表格
        const machineType = selectedMachineType || 'machining_center';
        const activeTable = document.querySelector(`.tolerance-table[data-machine-type="${machineType}"]:not(.hidden)`);
        if (!activeTable) {
            console.warn('未找到当前激活的机床类型表格:', machineType);
            return;
        }
        
        // 移除所有已有的事件监听器，避免重复绑定
        // 使用克隆节点的方式移除所有事件监听器
        activeTable.querySelectorAll('.edit-btn, .save-btn, .cancel-btn').forEach(function(btn) {
            // 克隆按钮以移除所有事件监听器
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
        });
        
        // 重新绑定编辑按钮点击事件
        activeTable.querySelectorAll('.edit-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                const row = this.closest('tr');
                const toleranceValues = row.querySelectorAll('.tolerance-value');
                const toleranceEdits = row.querySelectorAll('.tolerance-edit');
                const editBtn = row.querySelector('.edit-btn');
                const saveBtn = row.querySelector('.save-btn');
                const cancelBtn = row.querySelector('.cancel-btn');
                
                // 添加编辑状态标识
                row.classList.add('editing');
                
                // 显示编辑模式
                toleranceValues.forEach(function(value) {
                    value.classList.add('hidden');
                });
                toleranceEdits.forEach(function(edit) {
                    edit.classList.remove('hidden');
                });
                editBtn.classList.add('hidden');
                saveBtn.classList.remove('hidden');
                cancelBtn.classList.remove('hidden');
                
                // 记录原始数据状态
                const originalValues = [];
                toleranceValues.forEach(function(value, index) {
                    const rowValues = [];
                    // 检查是否是表格结构
                    const valueCells = value.querySelectorAll('td');
                    if (valueCells.length > 0) {
                        // 表格结构：遍历单元格
                        valueCells.forEach(function(cell, cellIndex) {
                            const cellValue = cell.textContent.trim();
                            // 只记录非空值，过滤掉空的单元格（如表头）
                            if (cellValue) {
                                rowValues.push(cellValue);
                            }
                        });
                    } else {
                        // 非表格结构：直接获取文本内容
                        const cellValue = value.textContent.trim();
                        if (cellValue) {
                            rowValues.push(cellValue);
                        }
                    }
                    originalValues.push(rowValues);
                });
                
                console.log('=== 编辑模式初始化 ===');
                console.log('检验项目:', row.querySelector('td:first-child').textContent);
                console.log('记录的原始数据:', originalValues);
                
                // 存储原始数据到行元素中，以便后续访问
                row.dataset.originalValues = JSON.stringify(originalValues);
                console.log('原始数据已存储到dataset:', row.dataset.originalValues);
                
                // 为输入框添加即时验证和变更检测
                toleranceEdits.forEach(function(edit, editIndex) {
                    const inputs = edit.querySelectorAll('input, textarea');
                    inputs.forEach(function(input, inputIndex) {
                        input.addEventListener('input', function() {
                            validateInput(this);
                            // 检测数据变更
                            checkChanges(row);
                        });
                    });
                });
                
                // 初始检测变更状态
                checkChanges(row);
            });
        });
        
        // 重新绑定保存按钮点击事件
        activeTable.querySelectorAll('.save-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                // 如果按钮被禁用，直接返回
                if (this.disabled) {
                    return;
                }
                
                const row = this.closest('tr');
                const toleranceValues = row.querySelectorAll('.tolerance-value');
                const toleranceEdits = row.querySelectorAll('.tolerance-edit');
                const editBtn = row.querySelector('.edit-btn');
                const saveBtn = row.querySelector('.save-btn');
                const cancelBtn = row.querySelector('.cancel-btn');
                const testItem = row.querySelector('td:first-child').textContent;
                
                // 检测是否有内容变更
                let hasChanges = false;
                let oldValues = [];
                let newValues = [];
                
                // 使用与checkChanges函数相同的原始数据来源
                const originalValues = JSON.parse(row.dataset.originalValues || '[]');
                
                console.log('=== 保存操作开始 ===');
                console.log('检验项目:', testItem);
                console.log('原始数据:', originalValues);
                
                toleranceEdits.forEach(function(edit, editIndex) {
                    const inputs = edit.querySelectorAll('input, textarea');
                    inputs.forEach(function(input, inputIndex) {
                        const currentValue = input.value.trim();
                        // 确保获取到的原始值不是 undefined，使用空字符串作为默认值
                        const originalValue = originalValues[editIndex] && originalValues[editIndex][inputIndex] !== undefined 
                            ? originalValues[editIndex][inputIndex] 
                            : '';
                        
                        console.log(`输入框 ${inputIndex + 1}: 当前值="${currentValue}", 原始值="${originalValue}"`);
                        
                        if (currentValue !== originalValue) {
                            hasChanges = true;
                            console.log(`检测到变更: 输入框 ${inputIndex + 1} 从 "${originalValue}" 变为 "${currentValue}"`);
                        }
                        oldValues.push(originalValue);
                        newValues.push(currentValue);
                    });
                });
                
                console.log('变更检测结果:', hasChanges);
                
                // 如果没有变更，显示提示并返回
                if (!hasChanges) {
                    console.log('未检测到内容变更，取消保存操作');
                    showNotification('未检测到内容变更，无需保存', 'info');
                    return;
                }
                
                console.log('检测到内容变更，继续保存操作');
                // 过滤掉空字符串，避免显示多个连续的逗号
                const filteredOldValues = oldValues.filter(value => value !== '');
                const filteredNewValues = newValues.filter(value => value !== '');
                console.log('变更前值:', filteredOldValues.join(', '));
                console.log('变更后值:', filteredNewValues.join(', '));
                
                // 验证所有输入值
                let allValid = true;
                toleranceEdits.forEach(function(edit) {
                    const inputs = edit.querySelectorAll('input, textarea');
                    inputs.forEach(function(input) {
                        if (!validateInput(input)) {
                            allValid = false;
                        }
                    });
                });
                
                if (!allValid) {
                    showNotification('输入值格式不正确，请检查后重试！', 'danger');
                    return;
                }
                
                // 确认修改
                if (confirm('确定要修改此允差值吗？')) {
                    // 记录修改历史（在更新值之前获取原始值）
                    const oldValue = filteredOldValues.join(', ');
                    const newValue = filteredNewValues.join(', ');
                    
                    console.log('=== 开始更新显示值 ===');
                    
                    // 获取检验项目名称，用于确定保存路径
                    const testItemText = testItem.trim();
                    console.log('检验项目:', testItemText);
                    
                    // 更新所有显示值并独立保存到localStorage
                    toleranceValues.forEach(function(value, index) {
                        const inputs = toleranceEdits[index].querySelectorAll('input, textarea');
                        
                        // 检查是否是表格结构
                        const valueCells = value.querySelectorAll('td');
                        if (valueCells.length > 0) {
                            // 表格结构：遍历单元格
                            let inputCounter = 0;
                            valueCells.forEach(function(cell, cellIndex) {
                                // 只跳过第一个空单元格（表头），如果有的话
                                // 对于没有表头的情况（只有一行数据），不跳过任何单元格
                                if (cellIndex === 0 && !cell.textContent.trim()) {
                                    return;
                                }
                                
                                // 确保不超出输入框数量
                                if (inputCounter < inputs.length) {
                                    const newToleranceValue = inputs[inputCounter].value;
                                    cell.textContent = newToleranceValue;
                                    console.log(`更新显示值: 单元格 ${cellIndex + 1} 从 "${cell.textContent}" 变为 "${newToleranceValue}"`);
                                    
                                    // 独立保存每个允差值到localStorage
                                    saveIndependentToleranceValue(testItemText, cellIndex, newToleranceValue);
                                    inputCounter++;
                                    
                                    // 同时更新进给轴角度允差数据
                                    storeFeedAxisTolerances();
                                }
                            });
                        } else {
                            // 非表格结构：直接更新文本内容
                            if (inputs.length > 0) {
                                const newToleranceValue = inputs[0].value;
                                value.textContent = newToleranceValue;
                                console.log(`更新显示值: 从 "${value.textContent}" 变为 "${newToleranceValue}"`);
                                
                                // 独立保存允差值到localStorage
                                saveIndependentToleranceValue(testItemText, 0, newToleranceValue);
                                
                                // 同时更新进给轴角度允差数据
                                storeFeedAxisTolerances();
                            }
                        }
                    });
                    
                    console.log('=== 开始隐藏编辑模式 ===');
                    
                    // 隐藏编辑模式
                    toleranceValues.forEach(function(value) {
                        value.classList.remove('hidden');
                        
                        // 确保表格行可见
                        const valueRows = value.querySelectorAll('tr');
                        valueRows.forEach(function(valueRow) {
                            valueRow.style.display = 'table-row';
                            valueRow.style.visibility = 'visible';
                            valueRow.style.opacity = '1';
                        });
                        
                        // 确保表格单元格可见
                        const valueCells = value.querySelectorAll('td');
                        valueCells.forEach(function(cell) {
                            cell.style.display = 'table-cell';
                            cell.style.visibility = 'visible';
                            cell.style.opacity = '1';
                        });
                    });
                    toleranceEdits.forEach(function(edit) {
                        edit.classList.add('hidden');
                    });
                    editBtn.classList.remove('hidden');
                    saveBtn.classList.add('hidden');
                    cancelBtn.classList.add('hidden');
                    
                    // 移除编辑状态标识
                    row.classList.remove('editing');
                    
                    console.log('=== 开始添加历史记录 ===');
                    
                    // 添加历史记录
                    addHistoryRecord(testItem, oldValue, newValue);
                    
                    console.log('=== 开始保存到localStorage ===');
                    
                    // 保存到localStorage
                    saveToleranceData();
                    
                    console.log('=== 开始清理原始数据状态 ===');
                    
                    // 移除原始数据状态存储
                    delete row.dataset.originalValues;
                    
                    // 显示成功提示
                    showNotification('修改成功！', 'success');
                    
                    console.log('=== 保存操作完成 ===');
                    console.log('历史记录已添加');
                    console.log('数据已保存到localStorage');
                    console.log('原始数据状态已清理');
                }
            });
        });
        
        // 重新绑定取消按钮点击事件
        activeTable.querySelectorAll('.cancel-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                const row = this.closest('tr');
                const toleranceValues = row.querySelectorAll('.tolerance-value');
                const toleranceEdits = row.querySelectorAll('.tolerance-edit');
                const editBtn = row.querySelector('.edit-btn');
                const saveBtn = row.querySelector('.save-btn');
                const cancelBtn = row.querySelector('.cancel-btn');
                
                // 隐藏编辑模式
                toleranceValues.forEach(function(value) {
                    value.classList.remove('hidden');
                    
                    // 确保表格行可见
                    const valueRows = value.querySelectorAll('tr');
                    valueRows.forEach(function(valueRow) {
                        valueRow.style.display = 'table-row';
                        valueRow.style.visibility = 'visible';
                        valueRow.style.opacity = '1';
                    });
                    
                    // 确保表格单元格可见
                    const valueCells = value.querySelectorAll('td');
                    valueCells.forEach(function(cell) {
                        cell.style.display = 'table-cell';
                        cell.style.visibility = 'visible';
                        cell.style.opacity = '1';
                    });
                });
                toleranceEdits.forEach(function(edit) {
                    edit.classList.add('hidden');
                });
                editBtn.classList.remove('hidden');
                saveBtn.classList.add('hidden');
                cancelBtn.classList.add('hidden');
                
                // 移除编辑状态标识
                row.classList.remove('editing');
                
                // 移除原始数据状态存储
                delete row.dataset.originalValues;
                
                // 重置输入框验证状态
                toleranceEdits.forEach(function(edit) {
                    const inputs = edit.querySelectorAll('input, textarea');
                    inputs.forEach(function(input) {
                        input.classList.remove('is-valid', 'is-invalid');
                    });
                });
            });
        });
    }
    
    // 输入验证函数
    // 检测输入值是否超出允差范围
    function checkToleranceRange(input) {
        const value = parseFloat(input.value.trim());
        if (isNaN(value)) return false;
        
        // 获取当前行的允差类型和允许范围
        const row = input.closest('tr');
        if (!row) return false;
        
        const testItem = row.querySelector('td:first-child').textContent.trim();
        
        // 定义各类允差的允许范围（可根据实际需求调整）
        const toleranceRanges = {
            'X轴直线度': { min: 0.001, max: 0.050 },  // 示例范围
            'Y轴直线度': { min: 0.001, max: 0.050 },
            'Z轴直线度': { min: 0.001, max: 0.050 },
            '平行度': { min: 0.001, max: 0.050 },
            'X轴角度误差': { min: 0.001, max: 0.050 },
            'Y轴角度误差': { min: 0.001, max: 0.050 },
            'Z轴角度误差': { min: 0.001, max: 0.050 },
            'Y轴、X轴垂直度': { min: 0.001, max: 0.050 },
            'Y轴、Z轴垂直度': { min: 0.001, max: 0.050 },
            'Z轴、X轴垂直度': { min: 0.001, max: 0.050 }
        };
        
        // 查找匹配的允差类型
        let toleranceType = null;
        for (const [key, range] of Object.entries(toleranceRanges)) {
            if (testItem.includes(key)) {
                toleranceType = key;
                break;
            }
        }
        
        if (!toleranceType) return false;
        
        const range = toleranceRanges[toleranceType];
        
        // 检查是否超出范围
        if (value < range.min || value > range.max) {
            // 存储超出范围的输入元素，用于模态框关闭后聚焦
            window.lastOutOfRangeInput = input;
            
            // 显示超出范围模态框
            const modal = new bootstrap.Modal(document.getElementById('toleranceOutOfRangeModal'));
            modal.show();
            
            return true; // 超出范围
        }
        
        return false; // 在范围内
    }
    
    function validateInput(input) {
        const value = input.value.trim();
        
        // 移除之前的验证状态
        input.classList.remove('is-valid', 'is-invalid');
        
        // 验证是否为空
        if (!value) {
            input.classList.add('is-invalid');
            return false;
        }
        
        // 验证是否为数字或包含单位的数字
        const numberPattern = /^\d+(\.\d+)?(\s*\(或.*\))?$/;
        if (!numberPattern.test(value)) {
            input.classList.add('is-invalid');
            return false;
        }
        
        // 检查是否超出允差范围
        if (checkToleranceRange(input)) {
            input.classList.add('is-invalid');
            return false;
        }
        
        // 验证通过
        input.classList.add('is-valid');
        return true;
    }
    
    // 检测数据变更函数
    function checkChanges(row) {
        const saveBtn = row.querySelector('.save-btn');
        const originalValues = JSON.parse(row.dataset.originalValues || '[]');
        const toleranceEdits = row.querySelectorAll('.tolerance-edit');
        
        let hasChanges = false;
        
        toleranceEdits.forEach(function(edit, editIndex) {
            const inputs = edit.querySelectorAll('input, textarea');
            inputs.forEach(function(input, inputIndex) {
                const currentValue = input.value.trim();
                const originalValue = originalValues[editIndex] ? originalValues[editIndex][inputIndex] : '';
                
                if (currentValue !== originalValue) {
                    hasChanges = true;
                }
            });
        });
        
        // 更新保存按钮状态
        if (hasChanges) {
            saveBtn.disabled = false;
            saveBtn.classList.remove('btn-secondary');
            saveBtn.classList.add('btn-success');
            saveBtn.title = '';
        } else {
            saveBtn.disabled = true;
            saveBtn.classList.remove('btn-success');
            saveBtn.classList.add('btn-secondary');
            saveBtn.title = '未检测到更改';
        }
    }
    
    // 显示通知函数
    function showNotification(message, type) {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed top-20 right-20 z-50`;
        notification.role = 'alert';
        notification.innerHTML = `
            ${message}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        `;
        
        // 添加到页面
        document.body.appendChild(notification);
        
        // 3秒后自动消失
        setTimeout(function() {
            notification.classList.remove('show');
            setTimeout(function() {
                document.body.removeChild(notification);
            }, 500);
        }, 3000);
    }
    
    // 输入验证
    function validateToleranceInput(input) {
        // 基本验证：不能为空
        if (!input || input.trim() === '') {
            return false;
        }
        
        // 验证格式：允差格式通常为数字或数字范围
        const tolerancePattern = /^[\s\S]*[0-9]+[\s\S]*$/;
        return tolerancePattern.test(input);
    }
    
    // 添加历史记录
    function addHistoryRecord(testItem, oldValue, newValue) {
        const now = new Date();
        const historyRecord = {
            time: now.toLocaleString(),
            operator: '管理员', // 实际应用中应从登录信息获取
            testItem: testItem, // 完整显示检验项目
            oldValue: oldValue, // 完整显示修改前的值
            newValue: newValue // 完整显示修改后的值
        };
        
        // 添加到历史记录数组
        toleranceHistory.unshift(historyRecord);
        
        // 限制历史记录数量
        if (toleranceHistory.length > 50) {
            toleranceHistory = toleranceHistory.slice(0, 50);
        }
        
        // 保存到localStorage
        localStorage.setItem('toleranceHistory', JSON.stringify(toleranceHistory));
        
        // 更新历史记录表格
        loadHistory();
    }
    
    // 加载历史记录
    function loadHistory() {
        const historyTableBody = document.getElementById('history-table-body');
        historyTableBody.innerHTML = '';
        
        if (toleranceHistory.length === 0) {
            const emptyRow = document.createElement('tr');
            emptyRow.innerHTML = '<td colspan="5" class="text-center">暂无修改记录</td>';
            historyTableBody.appendChild(emptyRow);
            return;
        }
        
        toleranceHistory.forEach(function(record) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${record.time}</td>
                <td>${record.operator}</td>
                <td>${record.testItem}</td>
                <td>${record.oldValue}</td>
                <td>${record.newValue}</td>
            `;
            historyTableBody.appendChild(row);
        });
    }
    
    // 保存允差数据
    function saveToleranceData() {
        // 根据机床类型创建对应的数据存储键
        const machineType = selectedMachineType || 'machining_center';
        const dataKey = `toleranceData_${machineType}`;
        const toleranceData = JSON.parse(localStorage.getItem(dataKey) || '{}');
        
        console.log(`保存允差数据 (机床类型: ${machineType}):`, toleranceData);
        
        // 临时显示所有表格（几何精度和位置精度表格）
        const allTables = document.querySelectorAll(`.tolerance-table[data-machine-type="${machineType}"]`);
        const hiddenTables = [];
        console.log(`找到 ${allTables.length} 个表格（包括隐藏的）`);
        allTables.forEach(function(table, index) {
            const precision = table.dataset.precision;
            const isHidden = table.classList.contains('hidden');
            console.log(`表格 ${index + 1}: data-precision="${precision}", hidden=${isHidden}`);
            if (isHidden) {
                hiddenTables.push(table);
                table.classList.remove('hidden');
                table.style.display = 'block';
                console.log(`临时显示表格: ${precision}`);
            }
        });
        
        // 处理所有机床类型的表格（包括几何精度、位置精度、加工精度等所有表格）
        // 修复：不再只处理未隐藏的表格，而是处理所有机床类型的表格
        if (!allTables.length) {
            console.warn('未找到当前机床类型的表格:', machineType);
            return;
        }

        console.log(`找到 ${allTables.length} 个表格（包括隐藏的）`);
        allTables.forEach(function(table, index) {
            const precision = table.dataset.precision;
            const isHidden = table.classList.contains('hidden');
            console.log(`表格 ${index + 1}: data-precision="${precision}", hidden=${isHidden}`);
        });

        // 处理所有机床类型的表格（包括隐藏的表格）
        allTables.forEach(function(activeTable) {
            // 处理当前表格中包含编辑按钮的行
            const editButtons = activeTable.querySelectorAll('.edit-btn');
            
            editButtons.forEach(function(btn) {
                const row = btn.closest('tr');
                const testItem = row.querySelector('td:first-child').textContent;
                const toleranceValues = row.querySelectorAll('.tolerance-value');
                
                console.log(`处理检验项目: ${testItem}, 找到 ${toleranceValues.length} 个 tolerance-value 元素`);
                
                // 检查 toleranceValues 是否存在
                if (!toleranceValues.length) {
                    console.warn('未找到 tolerance-value 元素:', testItem);
                    return;
                }
                
                // 收集所有允差值
                let values = [];
                toleranceValues.forEach(function(toleranceValue) {
                    // 检查是否是表格结构
                    const valueCells = toleranceValue.querySelectorAll('td');
                    if (valueCells.length > 1) {
                        // 表格结构：提取每个允差值
                        valueCells.forEach(function(cell, index) {
                            if (index > 0) { // 跳过第一行（a）和b））
                                const cellValue = cell.textContent.trim();
                                if (cellValue) {
                                    values.push(cellValue);
                                }
                            }
                        });
                    } else {
                        // 非表格结构：直接获取文本内容
                        const cellValue = toleranceValue.textContent.trim();
                        if (cellValue) {
                            values.push(cellValue);
                        }
                    }
                });
                
                console.log(`检验项目 ${testItem} 收集到的允差值:`, values);
                console.log(`检验项目 ${testItem} 允差值数量: ${values.length}`);
                
                toleranceData[testItem] = values.join(', ');
            });
        });
        
        // 保存到对应机床类型的存储键
        localStorage.setItem(dataKey, JSON.stringify(toleranceData));
        console.log(`数据已保存到localStorage (机床类型: ${machineType}):`, toleranceData);
        
        // 恢复表格的隐藏状态
        hiddenTables.forEach(function(table) {
            table.classList.add('hidden');
            table.style.display = 'none';
            console.log(`恢复表格隐藏状态: ${table.dataset.precision}`);
        });
    }

    // 清除并重新初始化允差数据
    function clearAndReinitializeToleranceData() {
        const machineType = selectedMachineType || 'machining_center';
        const dataKey = `toleranceData_${machineType}`;
        
        if (confirm('确定要清除并重新初始化允差数据吗？这将删除当前保存的所有允差数据。')) {
            // 清除localStorage中的数据
            localStorage.removeItem(dataKey);
            console.log(`已清除localStorage中的允差数据 (机床类型: ${machineType})`);
            
            // 重新从表格中读取并保存数据
            saveToleranceData();
            
            // 重新加载数据
            loadToleranceData();
            
            alert('允差数据已重新初始化完成！');
        }
    }
    
    // 保存所有允差数据
    function saveAllToleranceData() {
        const machineType = selectedMachineType || 'machining_center';
        
        if (confirm('确定要保存所有允差数据吗？这将从所有表格中读取并保存允差数据到localStorage。')) {
            // 从表格中读取并保存数据
            saveToleranceData();
            
            // 重新加载数据
            loadToleranceData();
            
            alert('所有允差数据已保存完成！');
        }
    }
    
    // 加载允差数据
    function loadToleranceData() {
        // 根据机床类型获取对应的允差数据
        const machineType = selectedMachineType || 'machining_center';
        const dataKey = `toleranceData_${machineType}`;
        const toleranceData = JSON.parse(localStorage.getItem(dataKey) || '{}');
        
        console.log(`加载允差数据 (机床类型: ${machineType}):`, toleranceData);
        
        // 只处理当前激活机床类型的表格
        const activeTable = document.querySelector(`.tolerance-table[data-machine-type="${machineType}"]:not(.hidden)`);
        if (!activeTable) {
            console.warn('未找到当前激活的机床类型表格:', machineType);
            return;
        }
        
        Object.keys(toleranceData).forEach(function(testItem) {
            const rows = activeTable.querySelectorAll('tbody tr');
            rows.forEach(function(row) {
                const rowTestItem = row.querySelector('td:first-child').textContent;
                if (rowTestItem === testItem) {
                    const toleranceValues = row.querySelectorAll('.tolerance-value');
                    const toleranceEdits = row.querySelectorAll('.tolerance-edit');
                    
                    // 检查 toleranceValues 和 toleranceEdits 是否存在
                    if (!toleranceValues.length || !toleranceEdits.length) {
                        console.warn('未找到 tolerance-value 或 tolerance-edit 元素:', testItem);
                        return;
                    }
                    
                    // 检查是否是新的表格结构（第一个 tolerance-value 是否是表格结构）
                    const firstValueCells = toleranceValues[0].querySelectorAll('td');
                    if (firstValueCells.length > 1) {
                        // 表格结构：设置每个允差值
                        const values = toleranceData[testItem].split(', ');
                        let valueIndex = 0;
                        
                        toleranceValues.forEach(function(toleranceValue, index) {
                            const valueCells = toleranceValue.querySelectorAll('td');
                            const inputs = toleranceEdits[index].querySelectorAll('input');
                            
                            valueCells.forEach(function(cell, cellIndex) {
                                if (cellIndex > 0 && valueIndex < values.length) { // 跳过第一行（a）和b））
                                    cell.textContent = values[valueIndex];
                                    if (inputs[cellIndex - 1]) {
                                        inputs[cellIndex - 1].value = values[valueIndex];
                                    }
                                    valueIndex++;
                                }
                            });
                            
                            // 确保表格行可见
                            const valueRows = toleranceValue.querySelectorAll('tr');
                            valueRows.forEach(function(valueRow) {
                                valueRow.style.display = 'table-row';
                                valueRow.style.visibility = 'visible';
                                valueRow.style.opacity = '1';
                            });
                            
                            // 确保表格单元格可见
                            valueCells.forEach(function(cell) {
                                cell.style.display = 'table-cell';
                                cell.style.visibility = 'visible';
                                cell.style.opacity = '1';
                            });
                        });
                        
                        // 确保规格部分的表格行也可见
                        const specDivs = row.querySelectorAll('.tolerance-spec');
                        specDivs.forEach(function(specDiv) {
                            const specRows = specDiv.querySelectorAll('tr');
                            specRows.forEach(function(specRow) {
                                specRow.style.display = 'table-row';
                                specRow.style.visibility = 'visible';
                                specRow.style.opacity = '1';
                            });
                            
                            const specCells = specDiv.querySelectorAll('td');
                            specCells.forEach(function(cell) {
                                cell.style.display = 'table-cell';
                                cell.style.visibility = 'visible';
                                cell.style.opacity = '1';
                            });
                        });
                    } else {
                        // 非表格结构：设置每个允差值
                        const values = toleranceData[testItem].split(', ');
                        values.forEach(function(value, index) {
                            if (index < toleranceValues.length) {
                                toleranceValues[index].textContent = value;
                                const textarea = toleranceEdits[index].querySelector('textarea');
                                if (textarea) {
                                    textarea.value = value;
                                }
                            }
                        });
                    }
                }
            });
        });
    }