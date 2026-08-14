// 实现自动计算倒数的功能
$(document).ready(function() {
    // 初始化表面粗糙度和加工工序能力输入框的显示状态
    function initSurfaceRoughnessInputs() {
        var path = $('#current-path').text();
        var pathParts = path.split(' > ');
        var level2Indicator = pathParts[1] || '';

        // 控制表面粗糙度和加工工序能力输入的显示
        if (level2Indicator === '加工精度') {
            // 只在加工精度路径下显示
            $('.card-body:has(h5.card-title:contains("指标重要程度打分表"))').find('.row.mb-3').show();
        } else {
            // 其他路径下隐藏
            $('.card-body:has(h5.card-title:contains("指标重要程度打分表"))').find('.row.mb-3').hide();
        }
    }

    // 初始化表面粗糙度和加工工序能力输入框
    initSurfaceRoughnessInputs();

    // 获取URL中的path参数并更新当前路径显示
    function updateCurrentPath() {
        const urlParams = new URLSearchParams(window.location.search);
        const pathParam = urlParams.get('path');
        if (pathParam) {
            const decodedPath = decodeURIComponent(pathParam);
            $('#current-path').text(decodedPath);
            // 根据路径更新指标内容
            updateIndicatorsByPath(decodedPath);
        }
    }

    // 根据路径更新指标内容
    function updateIndicatorsByPath(path) {
        // 提取路径部分
        const pathParts = path.split(' > ');
        const level1Indicator = pathParts[0] || '';
        const level2Indicator = pathParts[1] || '';
        const level3Indicator = pathParts[2] || '';

        // 控制表面粗糙度和加工工序能力输入的显示
        if (level2Indicator === '加工精度') {
            // 只在加工精度路径下显示
            $('.card-body:has(h5.card-title:contains("指标重要程度打分表"))').find('.row.mb-3').show();
        } else {
            // 其他路径下隐藏
            $('.card-body:has(h5.card-title:contains("指标重要程度打分表"))').find('.row.mb-3').hide();
        }

        // 根据路径更新内容
        if (level2Indicator === '位置精度') {
            // 对于位置精度，显示其下的三级指标
            updatePositionPrecisionIndicators();
        } else if (level2Indicator === '加工精度') {
            // 对于加工精度，显示其下的三级指标
            updateMachiningPrecisionIndicators();
        } else if (level3Indicator === '工作台精度') {
            updateWorktablePrecisionIndicators();
        } else if (level3Indicator === '主轴精度') {
            updateSpindlePrecisionIndicators();
        } else if (level3Indicator === '刀库精度') {
            updateToolMagazinePrecisionIndicators();
        } else if (level3Indicator === '主轴运动精度') {
            updateSpindleMotionPrecisionIndicators();
        } else if (level3Indicator === '多轴联动精度') {
            updateMultiAxisMotionPrecisionIndicators();
        } else if (level3Indicator === '传动精度') {
            updateTransmissionPrecisionIndicators();
        } else if (level3Indicator === '热误差') {
            updateThermalErrorIndicators();
        } else if (level3Indicator === '磨损精度') {
            updateWearPrecisionIndicators();
        } else if (level3Indicator === '进给轴精度') {
            // 对于进给轴精度，显示其下的指标
            const indicators = ['直线度', '平行度', '垂直度', '角度误差'];
            updateIndicators(indicators);
        } else {
            // 默认显示工作台精度指标
            updateWorktablePrecisionIndicators();
        }
    }

    // 更新位置精度指标（使用其下的三级指标作为打分对象）
    function updatePositionPrecisionIndicators() {
        const indicators = ['重复定位精度', '定位精度', '平均位置偏移', '定位系统偏差', '最小分辨率', '反向间隙（差值）'];
        updateIndicators(indicators);
    }

    // 更新主轴运动精度指标
    function updateSpindleMotionPrecisionIndicators() {
        const indicators = ['主轴径向误差', '主轴轴向误差', '主轴角度误差', '主轴启停响应时间', '主轴高速旋转时的动平衡精度'];
        updateIndicators(indicators);
    }

    // 更新多轴联动精度指标
    function updateMultiAxisMotionPrecisionIndicators() {
        const indicators = ['平面圆度误差', '多轴联动同步误差', '轮廓精度', '空间精度', '动态RTCP精度'];
        updateIndicators(indicators);
    }

    // 更新传动精度指标
    function updateTransmissionPrecisionIndicators() {
        const indicators = ['直线、圆弧插补轨迹误差', '伺服跟随误差', '高速移动时"过冲"或"滞后"', '低速移动时"爬行"'];
        updateIndicators(indicators);
    }

    // 更新热误差指标
    function updateThermalErrorIndicators() {
        const indicators = ['进给轴热误差', '主轴径向误差', '主轴轴向误差'];
        updateIndicators(indicators);
    }

    // 更新磨损精度指标
    function updateWearPrecisionIndicators() {
        const indicators = ['刀具磨损', '砂轮磨损（磨床）'];
        updateIndicators(indicators);
    }

    // 更新加工精度指标（对工件几何精度打分，下属指标为尺寸精度、形状精度）
    function updateMachiningPrecisionIndicators() {
        const indicators = ['尺寸精度', '形状精度'];
        updateIndicators(indicators);
    }

    // 更新工作台精度指标
    function updateWorktablePrecisionIndicators() {
        const indicators = ['平面度', '直线度', 'T型槽平行度'];
        updateIndicators(indicators);
    }

    // 更新主轴精度指标
    function updateSpindlePrecisionIndicators() {
        const indicators = ['圆度', '同轴度', '主轴径向跳动', '主轴端面跳动', '主轴轴向窜动'];
        updateIndicators(indicators);
    }

    // 更新刀库精度指标
    function updateToolMagazinePrecisionIndicators() {
        const indicators = ['刀库定位精度', '刀库重复定位精度'];
        updateIndicators(indicators);
    }

    // 通用更新指标函数
    function updateIndicators(indicators) {
        // 更新指标重要程度打分表
        updateScoreTable(indicators);
        // 更新指标对比矩阵
        updateMatrixTable(indicators);
        // 初始化计算
        initMatrixCalculation();
    }

    // 更新指标重要程度打分表
    function updateScoreTable(indicators) {
        const tbody = $('.matrix-container table tbody');
        tbody.empty();

        // 生成所有两两对比项
        for (let i = 0; i < indicators.length; i++) {
            for (let j = i + 1; j < indicators.length; j++) {
                const tr = $('<tr>');
                tr.html(`
                    <td>${indicators[i]}对${indicators[j]}</td>
                    <td>
                        <div class="input-group input-group-sm">
                            <input type="text" class="form-control form-control-sm matrix-input" value="1" placeholder="输入1-9或1/2-1/9">
                            <button class="btn btn-outline-secondary dropdown-toggle matrix-dropdown-btn" type="button" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                <i class="fas fa-chevron-down" style="font-size: 0.75rem;"></i>
                            </button>
                            <ul class="dropdown-menu matrix-dropdown-menu">
                                <li><a class="dropdown-item" href="#" data-value="1/9">1/9</a></li>
                                <li><a class="dropdown-item" href="#" data-value="1/8">1/8</a></li>
                                <li><a class="dropdown-item" href="#" data-value="1/7">1/7</a></li>
                                <li><a class="dropdown-item" href="#" data-value="1/6">1/6</a></li>
                                <li><a class="dropdown-item" href="#" data-value="1/5">1/5</a></li>
                                <li><a class="dropdown-item" href="#" data-value="1/4">1/4</a></li>
                                <li><a class="dropdown-item" href="#" data-value="1/3">1/3</a></li>
                                <li><a class="dropdown-item" href="#" data-value="1/2">1/2</a></li>
                                <li><a class="dropdown-item" href="#" data-value="1">1</a></li>
                                <li><a class="dropdown-item" href="#" data-value="2">2</a></li>
                                <li><a class="dropdown-item" href="#" data-value="3">3</a></li>
                                <li><a class="dropdown-item" href="#" data-value="4">4</a></li>
                                <li><a class="dropdown-item" href="#" data-value="5">5</a></li>
                                <li><a class="dropdown-item" href="#" data-value="6">6</a></li>
                                <li><a class="dropdown-item" href="#" data-value="7">7</a></li>
                                <li><a class="dropdown-item" href="#" data-value="8">8</a></li>
                                <li><a class="dropdown-item" href="#" data-value="9">9</a></li>
                            </ul>
                        </div>
                    </td>
                `);
                tbody.append(tr);
            }
        }

        // 重新绑定事件
        bindScoreInputEvents();
    }

    // 更新指标对比矩阵
    function updateMatrixTable(indicators) {
        const matrixTable = $('.matrix-table');
        const thead = matrixTable.find('thead tr');
        const tbody = matrixTable.find('tbody');

        // 更新表头
        thead.empty();
        thead.append('<th>指标名称</th>');
        indicators.forEach(indicator => {
            thead.append(`<th>${indicator}</th>`);
        });
        thead.append('<th>说明</th>');

        // 更新表格内容
        tbody.empty();
        for (let i = 0; i < indicators.length; i++) {
            const tr = $('<tr>');
            tr.append(`<td>${indicators[i]}</td>`);

            for (let j = 0; j < indicators.length; j++) {
                if (i === j) {
                    tr.append('<td>1（固定）</td>');
                } else {
                    tr.append(`<td id="cell-${i}-${j}">1</td>`);
                }
            }

            tr.append('<td>参考标准：GB/T ...</td>');
            tbody.append(tr);
        }
    }

    // 绑定打分输入事件
    function bindScoreInputEvents() {
        // 为下拉菜单选项添加点击事件监听器
        $(document).on('click', '.matrix-dropdown-menu a', function(e) {
            e.preventDefault();
            var selectedValue = $(this).data('value');
            var inputElement = $(this).closest('.input-group').find('.matrix-input');

            // 更新输入框值
            inputElement.val(selectedValue);
            // 触发矩阵更新
            updateMatrixFromScores();
        });

        // 当输入框值变化时，自动计算对应的倒数
        $('.matrix-input').on('change', function() {
            updateMatrixFromScores();
        });
    }

    // 页面加载时更新当前路径
    updateCurrentPath();

    // 计算倒数的函数
    function calculateReciprocal(value) {
        if (value === '1') {
            return '1';
        } else if (value.includes('/')) {
            // 处理分数输入，如 1/3，下三角显示为整数 3
            var parts = value.split('/');
            if (parts.length === 2) {
                var numerator = parseFloat(parts[0]);
                var denominator = parseFloat(parts[1]);
                if (denominator !== 0) {
                    // 当上三角为分数时，下三角显示为整数
                    return denominator.toString();
                } else {
                    return '1';
                }
            } else {
                return '1/' + value;
            }
        } else {
            // 处理整数输入，如 3，下三角显示为分数 1/3
            return '1/' + value;
        }
    }

    // 从打分表更新矩阵
    function updateMatrixFromScores() {
        // 获取所有打分表输入框
        var scoreInputs = $('.matrix-input');
        var scores = [];
        scoreInputs.each(function() {
            scores.push($(this).val().trim());
        });

        // 动态生成上三角和下三角矩阵的单元格ID
        var upperTriangleCells = [];
        var lowerTriangleCells = [];
        var scoreIndex = 0;

        // 获取当前指标数量
        var indicatorCount = $('.matrix-table thead th').length - 2; // 减去指标名称和说明列

        // 生成上三角和下三角单元格ID
        for (var i = 0; i < indicatorCount; i++) {
            for (var j = i + 1; j < indicatorCount; j++) {
                upperTriangleCells.push(`cell-${i}-${j}`);
                lowerTriangleCells.push(`cell-${j}-${i}`);
            }
        }

        // 更新上三角矩阵单元格
        for (var i = 0; i < upperTriangleCells.length; i++) {
            var cellId = upperTriangleCells[i];
            var score = scores[i] || '1';
            $('#' + cellId).text(score);
        }

        // 更新下三角矩阵单元格（显示倒数）
        for (var i = 0; i < lowerTriangleCells.length; i++) {
            var cellId = lowerTriangleCells[i];
            var score = scores[i] || '1';
            var reciprocalValue = calculateReciprocal(score);
            $('#' + cellId).text(reciprocalValue);
        }
    }

    // 初始化时触发一次计算，确保所有倒数都正确显示
    function initMatrixCalculation() {
        // 等待指标内容更新后再触发计算
        setTimeout(function() {
            $('.matrix-input').each(function() {
                $(this).trigger('change');
            });
        }, 100);
    }

    // 计算按钮点击事件
    $('#save-matrix-btn').on('click', function() {
        // 收集表格数据
        var matrix = [];
        var indicatorNames = [];

        // 从矩阵表头获取指标名称
        $('.matrix-table thead th').each(function(index) {
            if (index > 0 && index < $(this).closest('tr').find('th').length - 1) {
                indicatorNames.push($(this).text());
            }
        });

        // 获取打分表数据
        var scoreInputs = $('.matrix-input');
        var scores = [];
        scoreInputs.each(function() {
            var inputValue = $(this).val().trim();
            if (inputValue.includes('/')) {
                var parts = inputValue.split('/');
                scores.push(parseFloat(parts[0]) / parseFloat(parts[1]));
            } else {
                scores.push(parseFloat(inputValue));
            }
        });

        // 构建矩阵
        var n = indicatorNames.length;
        matrix = [];
        var scoreIndex = 0;

        for (var i = 0; i < n; i++) {
            var row = [];
            for (var j = 0; j < n; j++) {
                if (i === j) {
                    row.push(1.0);
                } else if (i < j) {
                    row.push(scores[scoreIndex++] || 1.0);
                } else {
                    // 下三角矩阵，使用上三角的倒数
                    var reciprocalScore = scores[scoreIndex - (i - j)] || 1.0;
                    row.push(reciprocalScore > 0 ? 1.0 / reciprocalScore : 1.0);
                }
            }
            matrix.push(row);
        }

        // 调用后端API进行一致性检验
        $.ajax({
            url: '/evaluation/ahp/consistency/',
            type: 'POST',
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            data: JSON.stringify({
                matrix: matrix,
                indicator_names: indicatorNames
            }),
            success: function(response) {
                if (response.success) {
                    var consistency = response.data.consistency;
                    var cr = consistency.CR;
                    var isConsistent = cr < 0.1;

                    // 更新结果显示
                    var resultHtml = '<p class="card-text">';
                    resultHtml += 'λmax = [' + consistency.lambda_max.toFixed(3) + '] | ';
                    resultHtml += 'CI = [' + consistency.CI.toFixed(3) + '] | ';
                    resultHtml += 'RI = [' + consistency.RI.toFixed(2) + '] | ';
                    resultHtml += 'CR = [' + cr.toFixed(3) + '] ';

                    if (isConsistent) {
                        resultHtml += '<span class="text-success">一致性通过√</span>';
                    } else {
                        resultHtml += '<span class="text-danger">一致性未通过，请重新评分</span>';
                    }

                    resultHtml += '</p>';
                    $('#consistency-result').html(resultHtml);
                } else {
                    alert('一致性检验失败：' + response.error);
                }
            },
            error: function(xhr, status, error) {
                alert('请求失败：' + error);
            }
        });
    });

    // 清除重填按钮点击事件
    $('#clear-matrix-btn').on('click', function() {
        // 将所有矩阵输入框的值设为1
        $('.matrix-input').each(function() {
            $(this).val('1');
        });

        // 触发一次计算，确保下三角矩阵也显示为1
        $('.matrix-input').each(function() {
            $(this).trigger('change');
        });

        // 清空一致性检验结果
        $('#consistency-result').html('<p class="card-text">λmax = [计算中...] | CI = [计算中...] | RI = [计算中...] | CR = [计算中...]</p>');
    });

    // 上传Excel按钮点击事件
    $('#upload-excel-btn').on('click', function() {
        var fileInput = $('#excel-file')[0];
        if (fileInput.files.length === 0) {
            alert('请先选择Excel文件');
            return;
        }

        var file = fileInput.files[0];

        // 验证文件名
        var fileName = file.name;
        var baseName = fileName.substring(0, fileName.lastIndexOf('.'));
        if (baseName !== 'AHP评分表') {
            alert('只能上传名为"AHP评分表"的Excel文件');
            return;
        }

        var reader = new FileReader();

        reader.onload = function(e) {
            try {
                var data = new Uint8Array(e.target.result);
                var workbook = XLSX.read(data, { type: 'array' });

                // 根据当前路径获取对应的sheet索引
                function getSheetIndexByPath() {
                    var path = $('#current-path').text();
                    var pathParts = path.split(' > ');
                    var level3Indicator = pathParts[2] || '';
                    var level2Indicator = pathParts[1] || '';

                    // 映射表：指标名称 -> sheet索引
                    var sheetMap = {
                        '进给轴精度': 0,      // sheet1
                        '工作台精度': 1,      // sheet2
                        '主轴精度': 2,        // sheet3
                        '刀库精度': 3,        // sheet4
                        '位置精度': 4,        // sheet5
                        '加工精度': 7,        // sheet8
                        '主轴运动精度': 8,    // sheet9
                        '多轴联动精度': 9,    // sheet10
                        '传动精度': 10,       // sheet11
                        '热误差': 11,         // sheet12
                        '磨损精度': 12        // sheet13
                    };

                    // 优先匹配三级指标
                    if (sheetMap[level3Indicator] !== undefined) {
                        return sheetMap[level3Indicator];
                    }
                    // 再匹配二级指标
                    if (sheetMap[level2Indicator] !== undefined) {
                        return sheetMap[level2Indicator];
                    }
                    // 默认返回第一个sheet
                    return 0;
                }

                // 获取对应sheet索引
                var sheetIndex = getSheetIndexByPath();
                var sheetName = workbook.SheetNames[sheetIndex];
                var worksheet = workbook.Sheets[sheetName];

                // 转换为JSON
                var jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

                // 提取第二列数据（索引为1）
                var secondColumnData = [];
                for (var i = 0; i < jsonData.length; i++) {
                    if (jsonData[i].length > 1 && jsonData[i][1] !== undefined && jsonData[i][1] !== null) {
                        var value = jsonData[i][1];
                        if (typeof value === 'number' && value > 0) {
                            secondColumnData.push(value);
                        }
                    }
                }

                // 填充到上三角矩阵
                fillUpperTriangleMatrix(secondColumnData);

                alert('Excel数据上传成功，已填充到矩阵中');
            } catch (error) {
                alert('读取Excel文件失败：' + error.message);
            }
        };

        reader.onerror = function() {
            alert('文件读取失败');
        };

        reader.readAsArrayBuffer(file);
    });

    // 提交打分按钮点击事件
    $('#submit-matrix-btn').on('click', function() {
        // 先进行一致性检验
        var consistencyResult = $('#consistency-result').text();

        // 检查是否已经计算过一致性
        if (consistencyResult.includes('[计算中...]')) {
            alert('请先点击"计算"按钮进行一致性检验');
            return;
        }

        // 收集表格数据
        var matrix = [];
        var indicatorNames = [];

        // 从矩阵表头获取指标名称
        $('.matrix-table thead th').each(function(index) {
            if (index > 0 && index < $(this).closest('tr').find('th').length - 1) {
                indicatorNames.push($(this).text());
            }
        });

        // 获取打分表数据
        var scoreInputs = $('.matrix-input');
        var scores = [];
        scoreInputs.each(function() {
            var inputValue = $(this).val().trim();
            if (inputValue.includes('/')) {
                var parts = inputValue.split('/');
                scores.push(parseFloat(parts[0]) / parseFloat(parts[1]));
            } else {
                scores.push(parseFloat(inputValue));
            }
        });

        // 构建矩阵
        var n = indicatorNames.length;
        matrix = [];
        var scoreIndex = 0;

        for (var i = 0; i < n; i++) {
            var row = [];
            for (var j = 0; j < n; j++) {
                if (i === j) {
                    row.push(1.0);
                } else if (i < j) {
                    row.push(scores[scoreIndex++] || 1.0);
                } else {
                    // 下三角矩阵，使用上三角的倒数
                    var reciprocalScore = scores[scoreIndex - (i - j)] || 1.0;
                    row.push(reciprocalScore > 0 ? 1.0 / reciprocalScore : 1.0);
                }
            }
            matrix.push(row);
        }

        // 获取当前路径
        var path = $('#current-path').text();

        // 提交到数据库
        $.ajax({
            url: '/evaluation/ahp/submit/',
            type: 'POST',
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            data: JSON.stringify({
                matrix: matrix,
                indicator_names: indicatorNames,
                path: path,
                notes: path + '指标对比'
            }),
            success: function(response) {
                if (response.success) {
                    alert('提交成功！矩阵ID: ' + response.data.matrix_id + '\n\n' + response.message);
                } else {
                    alert('提交失败：' + response.error);
                }
            },
            error: function(xhr, status, error) {
                alert('请求失败：' + error);
            }
        });
    });

    // 填充上三角矩阵
    function fillUpperTriangleMatrix(data) {
        var currentTable = $('table.table-bordered');
        var inputElements = currentTable.find('.matrix-input');

        // 按顺序填充数据
        for (var i = 0; i < Math.min(data.length, inputElements.length); i++) {
            var inputElement = $(inputElements[i]);
            var value = data[i];

            // 设置输入框值
            inputElement.val(value.toString());
            // 触发倒数计算
            inputElement.trigger('change');
        }
    }
});