window.ReliabilityModule = (function() {
    var _config = {
        moduleType: 'reliability',
        level1Title: '可靠性',
        sampleCount: 2
    };

    function getConfig() {
        return _config;
    }

    function isReliabilityIndicator(level1Title) {
        return level1Title === '可靠性';
    }

    function saveScoreToLocal(score, level, machineId, machineInfo) {
        if (window.EvaluationUtils) {
            window.EvaluationUtils.saveScoreToLocal(
                'comprehensive_weight_results',
                'reliability_score',
                score,
                machineId,
                machineInfo,
                { reliability_level: level }
            );
        }
    }

    function loadWeights() {
        console.log('[可靠性模块] 加载权重配置');
        var weights = {
            mtbf: 0.15,
            mttr: 0.10,
            availability: 0.15,
            fault_rate: 0.15,
            machining_consistency: 0.15,
            accuracy_retention: 0.15,
            mttff: 0.15
        };
        return weights;
    }

    function init() {
        console.log('[可靠性模块] 初始化完成');
    }

    return {
        getConfig: getConfig,
        isReliabilityIndicator: isReliabilityIndicator,
        saveScoreToLocal: saveScoreToLocal,
        loadWeights: loadWeights,
        init: init
    };
})();
