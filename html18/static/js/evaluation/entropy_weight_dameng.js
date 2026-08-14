/**
 * entropy_weight_dameng.js - 信息熵权计算与达梦数据库交互JavaScript文件
 *
 * 功能说明:
 * - saveEntropyToDamengDatabase: 将信息熵计算结果保存到达梦数据库
 * - getEntropyWeightFromDameng: 从达梦数据库获取信息熵权重数据
 * - 支持机床类型和精度类型的分类存储
 * - 处理样本数量、指标名称、熵值、权重等数据的传输
 *
 * 主要依赖:
 * - jQuery (AJAX请求)
 */

// ============================================
// 保存信息熵计算结果到达梦数据库
// @param {string} machineType - 机床类型
// @param {string} precisionType - 精度类型
// @param {Object} data - 信息熵数据（样本数、指标名、熵值、权重等）
// @param {string} csrfToken - CSRF令牌
// @returns {Promise} 返回保存操作的结果
// ============================================
function saveEntropyToDamengDatabase(machineType, precisionType, data, csrfToken) {
    return new Promise(function(resolve, reject) {
        console.log('开始保存信息熵计算结果到达梦数据库...');
        console.log('机床类型:', machineType);
        console.log('精度类型:', precisionType);

        var damengData = {
            precision_type: precisionType,
            sample_count: data.sample_count || 0,
            indicator_names: data.indicator_names || [],
            input_data: data.input_data || [],
            entropy_values: data.entropy_values || [],
            weights: data.weights || [],
            tolerance_values: data.tolerance_values || null,
            standard_values: data.standard_values || null,
            description: data.description || ''
        };

        $.ajax({
            url: '/dameng/api/entropy-weight/' + machineType + '/',
            type: 'POST',
            data: JSON.stringify(damengData),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': csrfToken
            },
            xhrFields: {
                withCredentials: true
            },
            success: function(response) {
                console.log('达梦数据库保存成功:', response);
                resolve(response);
            },
            error: function(xhr, status, error) {
                console.error('达梦数据库保存失败:', error);
                console.error('响应状态:', xhr.status);
                console.error('响应文本:', xhr.responseText);

                var errorMessage = error;
                try {
                    var errorResponse = JSON.parse(xhr.responseText);
                    if (errorResponse.message) {
                        errorMessage = errorResponse.message;
                    }
                } catch (e) {
                }

                reject(errorMessage);
            }
        });
    });
}

// ============================================
// 从达梦数据库获取信息熵权重数据
// @param {string} machineType - 机床类型
// @param {string} precisionType - 精度类型
// @param {string} csrfToken - CSRF令牌
// @returns {Promise} 返回获取的数据
// ============================================
function getEntropyWeightFromDameng(machineType, precisionType, csrfToken) {
    return new Promise(function(resolve, reject) {
        console.log('开始从达梦数据库获取信息熵计算结果...');
        console.log('机床类型:', machineType);
        console.log('精度类型:', precisionType);

        var url = '/dameng/api/entropy-weight/' + machineType + '/';
        if (precisionType) {
            url += '?precision_type=' + precisionType;
        }

        $.ajax({
            url: url,
            type: 'GET',
            headers: {
                'X-CSRFToken': csrfToken
            },
            xhrFields: {
                withCredentials: true
            },
            success: function(response) {
                console.log('达梦数据库获取成功:', response);
                resolve(response);
            },
            error: function(xhr, status, error) {
                console.error('达梦数据库获取失败:', error);
                reject(error);
            }
        });
    });
}

// ============================================
// 导出函数到全局作用域
// 使其他模块可以调用这两个函数
// ============================================
window.saveEntropyToDamengDatabase = saveEntropyToDamengDatabase;
window.getEntropyWeightFromDameng = getEntropyWeightFromDameng;
