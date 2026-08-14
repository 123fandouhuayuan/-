var selectedMachineId = null;
var selectedReportType = 'single';
var currentStep = 1;

$(document).ready(function() {
    $('#machineSearch').on('input', filterMachines);
    $('#machineTypeFilter').on('change', filterMachines);
    $('#evalStatusFilter').on('change', filterMachines);
    
    function filterMachines() {
        var search = $('#machineSearch').val().toLowerCase();
        var type = $('#machineTypeFilter').val();
        var status = $('#evalStatusFilter').val();
        var visibleCount = 0;
        
        $('.machine-item').each(function() {
            var $item = $(this);
            var itemType = $item.data('type');
            var itemName = ($item.data('name') || '').toLowerCase();
            var itemStatus = $item.data('status');
            
            var matchSearch = !search || itemName.includes(search);
            var matchType = !type || itemType === type;
            var matchStatus = !status || itemStatus === status;
            
            if (matchSearch && matchType && matchStatus) {
                $item.show();
                visibleCount++;
            } else {
                $item.hide();
            }
        });
        
        $('#machineCount').text(visibleCount);
    }
    
    $('.machine-card').click(function() {
        $('.machine-card').removeClass('selected');
        $(this).addClass('selected');
        selectedMachineId = $(this).data('id');
        $('#nextToStep2').prop('disabled', false);
        
        var $item = $(this).closest('.machine-item');
        var machineName = $item.find('.machine-name').text();
        var machineModel = $item.find('.machine-meta span:first').text().replace('型号: ', '');
        
        $('#previewMachineModel').text(machineModel);
    });
    
    function goToStep(step) {
        $('.step-content').removeClass('active');
        $('#step' + step).addClass('active');
        
        $('.wizard-step').each(function() {
            var s = $(this).data('step');
            $(this).removeClass('active completed');
            if (s < step) {
                $(this).addClass('completed');
            } else if (s === step) {
                $(this).addClass('active');
            }
        });
        
        $('#wizardProgress').removeClass('progress-1 progress-2 progress-3 progress-4');
        $('#wizardProgress').addClass('progress-' + step);
        currentStep = step;
    }
    
    $('#nextToStep2').click(function() {
        goToStep(2);
    });
    
    $('#backToStep1').click(function() {
        goToStep(1);
    });
    
    $('.type-card').click(function() {
        $('.type-card').removeClass('selected');
        $(this).addClass('selected');
        selectedReportType = $(this).data('type');
        $('#nextToStep3').prop('disabled', false);
        
        var typeName = $(this).find('h6').text();
        $('#previewReportType').text(typeName);
    });
    
    $('#nextToStep3').click(function() {
        goToStep(3);
    });
    
    $('#backToStep2').click(function() {
        goToStep(2);
    });
    
    $('#reportFormat').change(function() {
        var format = $(this).val();
        var formatText = format === 'html' ? 'HTML 页面' : (format === 'pdf' ? 'PDF 文档' : 'Excel 表格');
        $('#previewFormat').text(formatText);
    });
    
    $('#generateReport').click(function() {
        var $btn = $(this);
        $btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-1"></i>生成中...');
        
        $.ajax({
            url: '/reports/api/generate/',
            method: 'POST',
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            contentType: 'application/json',
            data: JSON.stringify({
                machine_id: selectedMachineId,
                report_type: selectedReportType,
                report_format: $('#reportFormat').val(),
                report_title: $('#reportTitle').val(),
                include_summary: $('#includeSummary').is(':checked'),
                include_details: $('#includeDetails').is(':checked'),
                include_charts: $('#includeCharts').is(':checked'),
                include_recommendations: $('#includeRecommendations').is(':checked')
            }),
            success: function(response) {
                if (response.success) {
                    goToStep(4);
                    $('#generatedReportNumber').text(response.report_number);
                    $('#viewReportBtn').attr('href', response.redirect_url);
                } else {
                    alert(response.error || '生成报告失败');
                    if (response.need_evaluation) {
                        if (confirm('该机床尚未完成评价，是否前往评价页面？')) {
                            window.location.href = '/evaluation/wizard/';
                        }
                    }
                }
            },
            error: function() {
                alert('请求失败，请重试');
            },
            complete: function() {
                $btn.prop('disabled', false).html('<i class="fas fa-magic me-1"></i> 生成报告');
            }
        });
    });
    
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});