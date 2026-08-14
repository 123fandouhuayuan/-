window.EvaluationUtils = (function() {
    function checkIsRegularUser() {
        const userRoleBadge = document.querySelector('.badge.bg-secondary');
        const isRegular = userRoleBadge ? userRoleBadge.textContent.trim() !== '管理员' : true;
        console.log('[用户类型判断] badge内容:', userRoleBadge ? userRoleBadge.textContent.trim() : '未找到', '是否为普通用户:', isRegular);
        return isRegular;
    }

    function getMachineIdFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('machine_id');
    }

    function getMachineSpecificKey(baseKey) {
        const machineId = window.selectedMachineId || 'default';
        return baseKey + '_' + machineId;
    }

    function saveMachineSpecificData(key, data) {
        const machineSpecificKey = getMachineSpecificKey(key);
        try {
            localStorage.setItem(machineSpecificKey, JSON.stringify(data));
            console.log('保存机床特定数据成功（机床ID:', window.selectedMachineId, '）：', key);
        } catch (error) {
            console.error('保存机床特定数据失败：', error);
        }
    }

    function getMachineSpecificData(key, defaultValue) {
        defaultValue = defaultValue || null;
        const machineSpecificKey = getMachineSpecificKey(key);
        try {
            const data = localStorage.getItem(machineSpecificKey);
            if (data) {
                return JSON.parse(data);
            }
        } catch (error) {
            console.error('读取机床特定数据失败：', error);
        }
        return defaultValue;
    }

    function clearMachineSpecificData(key) {
        const machineSpecificKey = getMachineSpecificKey(key);
        localStorage.removeItem(machineSpecificKey);
        console.log('清除机床特定数据（机床ID:', window.selectedMachineId, '）：', key);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function getCsrfToken() {
        return document.querySelector('input[name="csrfmiddlewaretoken"]') ?
            document.querySelector('input[name="csrfmiddlewaretoken"]').value : '';
    }

    function saveScoreToLocal(storageKey, scoreField, score, machineId, machineInfo, extraFields) {
        try {
            const localData = JSON.parse(localStorage.getItem(storageKey) || '[]');
            const timestamp = new Date().toISOString();
            const existingIndex = localData.findIndex(function(item) {
                return item.machine_id === parseInt(machineId);
            });

            var record = {
                user_role: 'user',
                report_number: machineInfo.report_number,
                machine_id: parseInt(machineId),
                machine_type: machineInfo.machine_type,
                machine_model: machineInfo.machine_model,
                comprehensive_score: 0,
                total_weight: 0,
                precision_score: 0,
                performance_score: 0,
                reliability_score: 0,
                intelligence_score: 0,
                green_score: 0,
                timestamp: timestamp,
                updated_at: timestamp
            };
            record[scoreField] = parseFloat(score);

            if (extraFields) {
                Object.keys(extraFields).forEach(function(key) {
                    record[key] = extraFields[key];
                });
            }

            if (existingIndex !== -1) {
                var existingRecord = localData[existingIndex];
                record.comprehensive_score = existingRecord.comprehensive_score || 0;
                record.total_weight = existingRecord.total_weight || 0;
                record.precision_score = existingRecord.precision_score || 0;
                record.performance_score = existingRecord.performance_score || 0;
                record.reliability_score = existingRecord.reliability_score || 0;
                record.intelligence_score = existingRecord.intelligence_score || 0;
                record.green_score = existingRecord.green_score || 0;
                if (existingRecord.intelligence_level) record.intelligence_level = existingRecord.intelligence_level;
                if (existingRecord.reliability_level) record.reliability_level = existingRecord.reliability_level;
                record[scoreField] = parseFloat(score);
                if (extraFields) {
                    Object.keys(extraFields).forEach(function(key) {
                        record[key] = extraFields[key];
                    });
                }
                localData[existingIndex] = record;
            } else {
                localData.push(record);
            }

            localStorage.setItem(storageKey, JSON.stringify(localData));
            console.log(scoreField + '已保存到localStorage:', record);
        } catch (e) {
            console.error('保存' + scoreField + '到localStorage失败:', e);
        }
    }

    function initGlobalState() {
        var machineId = getMachineIdFromUrl();
        window.selectedMachineId = machineId;
        window.machineName = '';

        window.precisionModule = window.precisionModule || { sampleCount: 1, machineCount: 0, machines: [] };
        window.performanceModule = window.performanceModule || { sampleCount: 2 };
        window.reliabilityModule = window.reliabilityModule || { sampleCount: 2 };
        window.intelligenceModule = window.intelligenceModule || { sampleCount: 2 };
        window.greenModule = window.greenModule || { sampleCount: 2 };
        window.currentModuleType = 'precision';

        console.log('[模块初始化] 全局状态初始化完成, machine_id:', machineId);
    }

    function resetModuleDataOnMachineChange(machineId) {
        var previousMachineId = localStorage.getItem('previous_machine_id');
        if (previousMachineId && previousMachineId !== machineId) {
            console.log('机床ID变化从', previousMachineId, '到', machineId);
            if (window.GreenModule && window.GreenModule.resetData) {
                window.GreenModule.resetData();
            }
            if (window.PerformanceModule && window.PerformanceModule.resetData) {
                window.PerformanceModule.resetData();
            }
        }
        localStorage.setItem('previous_machine_id', machineId || 'default');
    }

    function fetchMachineName(machineId) {
        if (!machineId) return;
        $.ajax({
            url: '/evaluation/api/get-machine-name/',
            type: 'GET',
            data: { machine_id: machineId },
            headers: {
                'X-CSRFToken': getCsrfToken()
            },
            success: function(response) {
                if (response.success) {
                    window.machineName = response.machine_name;
                    console.log('获取到的机床名称：', window.machineName);
                }
            },
            error: function(error) {
                console.error('获取机床名称时发生错误：', error);
            }
        });
    }

    function showAutoCalculationAlert(message) {
        var alertDiv = document.getElementById('auto-calculation-alert');
        var messageSpan = document.getElementById('auto-calculation-message');
        if (alertDiv && messageSpan) {
            messageSpan.textContent = message || '数据已自动计算并更新';
            alertDiv.classList.remove('d-none');
            setTimeout(function() {
                alertDiv.classList.add('d-none');
            }, 3000);
        }
    }

    function batchLoadFromStorage(prefix, keys) {
        var result = {};
        keys.forEach(function(key) {
            var fullKey = prefix + '_' + key;
            var value = localStorage.getItem(fullKey);
            result[key] = value ? parseFloat(value) : null;
        });
        return result;
    }

    function batchSaveToStorage(prefix, data) {
        Object.keys(data).forEach(function(key) {
            var fullKey = prefix + '_' + key;
            localStorage.setItem(fullKey, data[key]);
        });
    }

    function setCachedElementValue(id, value, setColor) {
        var el = document.getElementById(id);
        if (el) {
            el.value = value;
            if (setColor && value !== undefined && value !== null && value !== '') {
                var numVal = parseFloat(value);
                if (!isNaN(numVal)) {
                    if (numVal >= 4) {
                        el.style.color = 'green';
                    } else if (numVal >= 3) {
                        el.style.color = 'orange';
                    } else {
                        el.style.color = 'red';
                    }
                }
            }
        }
    }

    function getCachedElementFloatValue(id) {
        var el = document.getElementById(id);
        if (el && el.value) {
            var val = parseFloat(el.value);
            return isNaN(val) ? null : val;
        }
        return null;
    }

    return {
        checkIsRegularUser: checkIsRegularUser,
        getMachineIdFromUrl: getMachineIdFromUrl,
        getMachineSpecificKey: getMachineSpecificKey,
        saveMachineSpecificData: saveMachineSpecificData,
        getMachineSpecificData: getMachineSpecificData,
        clearMachineSpecificData: clearMachineSpecificData,
        getCookie: getCookie,
        getCsrfToken: getCsrfToken,
        saveScoreToLocal: saveScoreToLocal,
        initGlobalState: initGlobalState,
        resetModuleDataOnMachineChange: resetModuleDataOnMachineChange,
        fetchMachineName: fetchMachineName,
        showAutoCalculationAlert: showAutoCalculationAlert,
        batchLoadFromStorage: batchLoadFromStorage,
        batchSaveToStorage: batchSaveToStorage,
        setCachedElementValue: setCachedElementValue,
        getCachedElementFloatValue: getCachedElementFloatValue
    };
})();
