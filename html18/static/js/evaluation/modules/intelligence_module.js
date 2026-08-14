window.IntelligenceModule = (function() {
    var _config = {
        moduleType: 'intelligence',
        level1Title: '智能化',
        sampleCount: 2,
        levels: [
            { name: 'L1基础级', minScore: 0, maxScore: 4 },
            { name: 'L2规范级', minScore: 5, maxScore: 9 },
            { name: 'L3集成级', minScore: 10, maxScore: 14 },
            { name: 'L4优化级', minScore: 15, maxScore: 19 },
            { name: 'L5成长级', minScore: 20, maxScore: 25 }
        ]
    };

    function getConfig() {
        return _config;
    }

    function isIntelligenceIndicator(level1Title) {
        return level1Title === '智能化';
    }

    function calculateLevel(score) {
        for (var i = 0; i < _config.levels.length; i++) {
            if (score >= _config.levels[i].minScore && score <= _config.levels[i].maxScore) {
                return _config.levels[i].name;
            }
        }
        return 'L1基础级';
    }

    function saveScoreToLocal(score, level, machineId, machineInfo) {
        if (window.EvaluationUtils) {
            window.EvaluationUtils.saveScoreToLocal(
                'comprehensive_weight_results',
                'intelligence_score',
                score,
                machineId,
                machineInfo,
                { intelligence_level: level }
            );
        }
    }

    function init() {
        console.log('[智能化模块] 初始化完成');
    }

    return {
        getConfig: getConfig,
        isIntelligenceIndicator: isIntelligenceIndicator,
        calculateLevel: calculateLevel,
        saveScoreToLocal: saveScoreToLocal,
        init: init
    };
})();
