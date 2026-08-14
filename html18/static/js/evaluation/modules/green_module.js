window.GreenModule = (function() {
    var METRICS_CONFIG = [
        { id: 'cutting-fluid', scoreKey: 'green_summary_cutting_fluid_score', weightedKey: 'green_summary_cutting_fluid_weighted', score: '切削液消耗_score', section: 'resource' },
        { id: 'lubricant', scoreKey: 'green_summary_lubricant_score', weightedKey: 'green_summary_lubricant_weighted', score: '润滑油消耗_score', section: 'resource' },
        { id: 'lightweight', scoreKey: 'green_summary_lightweight_score', weightedKey: 'green_summary_lightweight_weighted', score: '轻量化设计_total', section: 'resource' },
        { id: 'energy', scoreKey: 'green_summary_energy_score', weightedKey: 'green_summary_energy_weighted', score: '有效能量利用率_score', section: 'energy' },
        { id: 'workpiece', scoreKey: 'green_summary_workpiece_score', weightedKey: 'green_summary_workpiece_weighted', score: '工件比能_score', section: 'energy' },
        { id: 'volume', scoreKey: 'green_summary_volume_score', weightedKey: 'green_summary_volume_weighted', score: '体积比能_score', section: 'energy' },
        { id: 'standby', scoreKey: 'green_summary_standby_score', weightedKey: 'green_summary_standby_weighted', score: '待机能耗率_score', section: 'energy' },
        { id: 'idle', scoreKey: 'green_summary_idle_score', weightedKey: 'green_summary_idle_weighted', score: '空运转能耗率_score', section: 'energy' },
        { id: 'cutting', scoreKey: 'green_summary_cutting_score', weightedKey: 'green_summary_cutting_weighted', score: '切削能耗率_score', section: 'energy' },
        { id: 'cutting-energy', scoreKey: 'green_summary_cutting_energy_score', weightedKey: 'green_summary_cutting_energy_weighted', score: '切削能量能耗率_score', section: 'energy' }
    ];

    var SECTIONS = {
        resource: { name: '资源消耗指标', weightKey: 'green_section_resource_weight', totalScoreKey: 'green_section_resource_total', metrics: ['cutting-fluid', 'lubricant', 'lightweight'] },
        energy: { name: '能耗效率指标', weightKey: 'green_section_energy_weight', totalScoreKey: 'green_section_energy_total', metrics: ['energy', 'workpiece', 'volume', 'standby', 'idle', 'cutting', 'cutting-energy'] }
    };

    function getMetricsConfig() {
        return METRICS_CONFIG;
    }

    function getSections() {
        return SECTIONS;
    }

    function resetData() {
        localStorage.removeItem('green_summary_saved');
        localStorage.removeItem('green_summary_total_score');
        METRICS_CONFIG.forEach(function(metric) {
            localStorage.removeItem(metric.scoreKey);
            localStorage.removeItem(metric.weightedKey);
        });
        Object.keys(SECTIONS).forEach(function(key) {
            localStorage.removeItem(SECTIONS[key].weightKey);
            localStorage.removeItem(SECTIONS[key].totalScoreKey);
        });
        console.log('[绿色化模块] 评分汇总数据已重置');
    }

    function isGreenIndicator(level1Title) {
        return level1Title === '绿色化';
    }

    function saveScoreToLocal(score, machineId, machineInfo) {
        if (window.EvaluationUtils) {
            window.EvaluationUtils.saveScoreToLocal(
                'comprehensive_weight_results',
                'green_score',
                score,
                machineId,
                machineInfo
            );
        }
    }

    function init() {
        console.log('[绿色化模块] 初始化完成');
    }

    return {
        getMetricsConfig: getMetricsConfig,
        getSections: getSections,
        resetData: resetData,
        isGreenIndicator: isGreenIndicator,
        saveScoreToLocal: saveScoreToLocal,
        init: init
    };
})();
