window.PerformanceModule = (function() {
    var METRICS_CONFIG = [
        { id: 'dispersion', scoreKey: 'perf_summary_dispersion_score', weightedKey: 'perf_summary_dispersion_weighted', score: '加工分散性_score', section: 'machining' },
        { id: 'efficiency', scoreKey: 'perf_summary_efficiency_score', weightedKey: 'perf_summary_efficiency_weighted', score: 'overallEfficiencyResult', section: 'machining' },
        { id: 'static-stiffness', scoreKey: 'perf_summary_static_stiffness_score', weightedKey: 'perf_summary_static_stiffness_weighted', score: 'staticStiffnessResult', section: 'stiffness' },
        { id: 'spindle', scoreKey: 'perf_summary_spindle_score', weightedKey: 'perf_summary_spindle_weighted', score: '主轴_score', section: 'operation' },
        { id: 'noise', scoreKey: 'perf_summary_noise_score', weightedKey: 'perf_summary_noise_weighted', score: '噪声_score', section: 'operation' },
        { id: 'current-stability', scoreKey: 'perf_summary_current_stability_score', weightedKey: 'perf_summary_current_stability_weighted', score: 'current_stability_score', section: 'operation' },
        { id: 'thermal-deformation', scoreKey: 'perf_summary_thermal_deformation_score', weightedKey: 'perf_summary_thermal_deformation_weighted', score: 'thermal_deformation_score', section: 'operation' },
        { id: 'spindle-load', scoreKey: 'perf_summary_spindle_load_score', weightedKey: 'perf_summary_spindle_load_weighted', score: 'spindle_load_score', section: 'load' },
        { id: 'max-load', scoreKey: 'perf_summary_max_load_score', weightedKey: 'perf_summary_max_load_weighted', score: 'max_load_score', section: 'load' },
        { id: 'vibration-resistance', scoreKey: 'perf_summary_vibration_resistance_score', weightedKey: 'perf_summary_vibration_resistance_weighted', score: 'vibration_resistance_score', section: 'load' }
    ];

    var SECTIONS = {
        machining: { name: '加工性能', weightKey: 'perf_section_machining_weight', totalScoreKey: 'perf_section_machining_total', metrics: ['dispersion', 'efficiency'] },
        stiffness: { name: '机床刚度', weightKey: 'perf_section_stiffness_weight', totalScoreKey: 'perf_section_stiffness_total', metrics: ['static-stiffness'] },
        operation: { name: '运行性能', weightKey: 'perf_section_operation_weight', totalScoreKey: 'perf_section_operation_total', metrics: ['spindle', 'noise', 'current-stability', 'thermal-deformation'] },
        load: { name: '负荷能力', weightKey: 'perf_section_load_weight', totalScoreKey: 'perf_section_load_total', metrics: ['spindle-load', 'max-load', 'vibration-resistance'] }
    };

    function getMetricsConfig() {
        return METRICS_CONFIG;
    }

    function getSections() {
        return SECTIONS;
    }

    function resetData() {
        localStorage.removeItem('perf_summary_saved');
        localStorage.removeItem('perf_summary_total_score');
        METRICS_CONFIG.forEach(function(metric) {
            localStorage.removeItem(metric.scoreKey);
            localStorage.removeItem(metric.weightedKey);
        });
        Object.keys(SECTIONS).forEach(function(key) {
            localStorage.removeItem(SECTIONS[key].weightKey);
            localStorage.removeItem(SECTIONS[key].totalScoreKey);
        });
        console.log('[性能模块] 评分汇总数据已重置');
    }

    function isPerformanceIndicator(level1Title) {
        return level1Title === '性能';
    }

    function saveScoreToLocal(score, machineId, machineInfo) {
        if (window.EvaluationUtils) {
            window.EvaluationUtils.saveScoreToLocal(
                'comprehensive_weight_results',
                'performance_score',
                score,
                machineId,
                machineInfo
            );
        }
    }

    function init() {
        console.log('[性能模块] 初始化完成');
    }

    return {
        getMetricsConfig: getMetricsConfig,
        getSections: getSections,
        resetData: resetData,
        isPerformanceIndicator: isPerformanceIndicator,
        saveScoreToLocal: saveScoreToLocal,
        init: init
    };
})();
