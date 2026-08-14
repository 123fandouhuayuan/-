/**
 * visualization.js - 可视化分析页面JavaScript文件
 *
 * 功能说明:
 * - VisualizationDashboard类：管理机床综合得分分析的可视化展示
 * - 基于ECharts库实现柱状图、雷达图、柱状图等多种图表
 * - 支持精度分析、综合得分分析、五维度评分展示等功能
 * - 提供图表的tooltip格式化、数据交互、保存图片等工具功能
 *
 * 主要依赖:
 * - ECharts 5.4.3 (https://echarts.apache.org/)
 */

class VisualizationDashboard {
    // ============================================
    // 构造函数：初始化可视化仪表盘
    // 初始化图表实例、数据存储和管理员权限状态
    // ============================================
    constructor() {
        this.chartInstance = null;
        this.normalDistributionChartInstance = null;
        // 五个维度正态分布图表实例
        this.precisionNormalDistributionChartInstance = null;
        this.performanceNormalDistributionChartInstance = null;
        this.reliabilityNormalDistributionChartInstance = null;
        this.intelligenceNormalDistributionChartInstance = null;
        this.greenNormalDistributionChartInstance = null;
        this.currentData = [];
        this.isAdmin = this.getIsAdmin();
        this.init();
    }

    // ============================================
    // 获取当前用户是否为管理员
    // 从页面DOM元素中读取用户角色数据
    // ============================================
    getIsAdmin() {
        const userRoleData = document.getElementById('user-role-data');
        return userRoleData ? userRoleData.getAttribute('data-is-admin') === 'true' : false;
    }

    // ============================================
    // 异步初始化方法
    // 按顺序：加载ECharts库 -> 初始化图表 -> 设置事件监听 -> 加载初始数据
    // ============================================
    async init() {
        await this.loadECharts();
        this.initializeCharts();
        this.setupEventListeners();
        this.loadInitialData();
    }

    // ============================================
    // 动态加载ECharts库
    // 优先从jsdelivr CDN加载，失败后使用cloudflare CDN作为备选
    // ============================================
    async loadECharts() {
        // 如果ECharts已经加载（同步加载），直接返回
        if (typeof echarts !== 'undefined') {
            return;
        }

        await new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = '/static/js/echarts.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    // ============================================
    // 初始化所有图表
    // ============================================
    initializeCharts() {
        this.initializeChart();
        this.initializeNormalDistributionChart();
        // 初始化五个维度的正态分布图表
        this.initializeDimensionNormalDistributionCharts();
    }

    // ============================================
    // 初始化五个维度的正态分布图表
    // 精度、性能、可靠性、智能化、绿色化
    // ============================================
    initializeDimensionNormalDistributionCharts() {
        this.initializePrecisionNormalDistributionChart();
        this.initializePerformanceNormalDistributionChart();
        this.initializeReliabilityNormalDistributionChart();
        this.initializeIntelligenceNormalDistributionChart();
        this.initializeGreenNormalDistributionChart();
    }

    // ============================================
    // 初始化精度得分正态分布图表
    // ============================================
    initializePrecisionNormalDistributionChart() {
        const chartDom = document.getElementById('precision-normal-distribution-container');
        if (!chartDom) return;

        this.precisionNormalDistributionChartInstance = echarts.init(chartDom);

        const option = {
            title: {
                text: '精度得分正态分布分析',
                left: 'center',
                top: 10,
                textStyle: {
                    fontSize: 18,
                    fontWeight: 'bold'
                }
            },
            tooltip: {
                trigger: 'item',
                formatter: function(params) {
                    if (params.seriesName === '正态分布曲线') {
                        return `得分: ${params.value[0].toFixed(2)}<br/>概率密度: ${params.value[1].toFixed(4)}`;
                    } else if (params.seriesName === '数据点分布') {
                        const data = params.data;
                        return `<strong>报告编号: ${data.report_number}</strong><br/>
                                机床型号: ${data.machine_model}<br/>
                                精度得分: ${data.value[0].toFixed(2)}<br/>
                                概率密度: ${data.value[1].toFixed(4)}`;
                    }
                    return '';
                }
            },
            legend: {
                data: ['正态分布曲线', '数据点分布'],
                top: 50,
                left: 'center'
            },
            grid: {
                left: '12%',
                right: '8%',
                bottom: '12%',
                top: '20%'
            },
            xAxis: {
                type: 'value',
                name: '精度得分',
                nameLocation: 'middle',
                nameGap: 35,
                min: 60,
                max: 100,
                axisLabel: {
                    formatter: '{value}'
                }
            },
            yAxis: {
                type: 'value',
                name: '概率密度',
                nameLocation: 'middle',
                nameGap: 55
            },
            series: []
        };

        this.precisionNormalDistributionChartInstance.setOption(option);
    }

    // ============================================
    // 初始化性能得分正态分布图表
    // ============================================
    initializePerformanceNormalDistributionChart() {
        const chartDom = document.getElementById('performance-normal-distribution-container');
        if (!chartDom) return;

        this.performanceNormalDistributionChartInstance = echarts.init(chartDom);

        const option = {
            title: {
                text: '性能得分正态分布分析',
                left: 'center',
                top: 10,
                textStyle: {
                    fontSize: 18,
                    fontWeight: 'bold'
                }
            },
            tooltip: {
                trigger: 'item',
                formatter: function(params) {
                    if (params.seriesName === '正态分布曲线') {
                        return `得分: ${params.value[0].toFixed(2)}<br/>概率密度: ${params.value[1].toFixed(4)}`;
                    } else if (params.seriesName === '数据点分布') {
                        const data = params.data;
                        return `<strong>报告编号: ${data.report_number}</strong><br/>
                                机床型号: ${data.machine_model}<br/>
                                性能得分: ${data.value[0].toFixed(2)}<br/>
                                概率密度: ${data.value[1].toFixed(4)}`;
                    }
                    return '';
                }
            },
            legend: {
                data: ['正态分布曲线', '数据点分布'],
                top: 50,
                left: 'center'
            },
            grid: {
                left: '12%',
                right: '8%',
                bottom: '12%',
                top: '20%'
            },
            xAxis: {
                type: 'value',
                name: '性能得分',
                nameLocation: 'middle',
                nameGap: 35,
                min: 60,
                max: 100,
                axisLabel: {
                    formatter: '{value}'
                }
            },
            yAxis: {
                type: 'value',
                name: '概率密度',
                nameLocation: 'middle',
                nameGap: 55
            },
            series: []
        };

        this.performanceNormalDistributionChartInstance.setOption(option);
    }

    // ============================================
    // 初始化可靠性得分正态分布图表
    // ============================================
    initializeReliabilityNormalDistributionChart() {
        const chartDom = document.getElementById('reliability-normal-distribution-container');
        if (!chartDom) return;

        this.reliabilityNormalDistributionChartInstance = echarts.init(chartDom);

        const option = {
            title: {
                text: '可靠性得分正态分布分析',
                left: 'center',
                top: 10,
                textStyle: {
                    fontSize: 18,
                    fontWeight: 'bold'
                }
            },
            tooltip: {
                trigger: 'item',
                formatter: function(params) {
                    if (params.seriesName === '正态分布曲线') {
                        return `得分: ${params.value[0].toFixed(2)}<br/>概率密度: ${params.value[1].toFixed(4)}`;
                    } else if (params.seriesName === '数据点分布') {
                        const data = params.data;
                        return `<strong>报告编号: ${data.report_number}</strong><br/>
                                机床型号: ${data.machine_model}<br/>
                                可靠性得分: ${data.value[0].toFixed(2)}<br/>
                                概率密度: ${data.value[1].toFixed(4)}`;
                    }
                    return '';
                }
            },
            legend: {
                data: ['正态分布曲线', '数据点分布'],
                top: 50,
                left: 'center'
            },
            grid: {
                left: '12%',
                right: '8%',
                bottom: '12%',
                top: '20%'
            },
            xAxis: {
                type: 'value',
                name: '可靠性得分',
                nameLocation: 'middle',
                nameGap: 35,
                min: 60,
                max: 100,
                axisLabel: {
                    formatter: '{value}'
                }
            },
            yAxis: {
                type: 'value',
                name: '概率密度',
                nameLocation: 'middle',
                nameGap: 55
            },
            series: []
        };

        this.reliabilityNormalDistributionChartInstance.setOption(option);
    }

    // ============================================
    // 初始化智能化得分正态分布图表
    // ============================================
    initializeIntelligenceNormalDistributionChart() {
        const chartDom = document.getElementById('intelligence-normal-distribution-container');
        if (!chartDom) return;

        this.intelligenceNormalDistributionChartInstance = echarts.init(chartDom);

        const option = {
            title: {
                text: '智能化得分正态分布分析',
                left: 'center',
                top: 10,
                textStyle: {
                    fontSize: 18,
                    fontWeight: 'bold'
                }
            },
            tooltip: {
                trigger: 'item',
                formatter: function(params) {
                    if (params.seriesName === '正态分布曲线') {
                        return `得分: ${params.value[0].toFixed(2)}<br/>概率密度: ${params.value[1].toFixed(4)}`;
                    } else if (params.seriesName === '数据点分布') {
                        const data = params.data;
                        return `<strong>报告编号: ${data.report_number}</strong><br/>
                                机床型号: ${data.machine_model}<br/>
                                智能化得分: ${data.value[0].toFixed(2)}<br/>
                                概率密度: ${data.value[1].toFixed(4)}`;
                    }
                    return '';
                }
            },
            legend: {
                data: ['正态分布曲线', '数据点分布'],
                top: 50,
                left: 'center'
            },
            grid: {
                left: '12%',
                right: '8%',
                bottom: '12%',
                top: '20%'
            },
            xAxis: {
                type: 'value',
                name: '智能化得分',
                nameLocation: 'middle',
                nameGap: 35,
                min: 60,
                max: 100,
                axisLabel: {
                    formatter: '{value}'
                }
            },
            yAxis: {
                type: 'value',
                name: '概率密度',
                nameLocation: 'middle',
                nameGap: 55
            },
            series: []
        };

        this.intelligenceNormalDistributionChartInstance.setOption(option);
    }

    // ============================================
    // 初始化绿色化得分正态分布图表
    // ============================================
    initializeGreenNormalDistributionChart() {
        const chartDom = document.getElementById('green-normal-distribution-container');
        if (!chartDom) return;

        this.greenNormalDistributionChartInstance = echarts.init(chartDom);

        const option = {
            title: {
                text: '绿色化得分正态分布分析',
                left: 'center',
                top: 10,
                textStyle: {
                    fontSize: 18,
                    fontWeight: 'bold'
                }
            },
            tooltip: {
                trigger: 'item',
                formatter: function(params) {
                    if (params.seriesName === '正态分布曲线') {
                        return `得分: ${params.value[0].toFixed(2)}<br/>概率密度: ${params.value[1].toFixed(4)}`;
                    } else if (params.seriesName === '数据点分布') {
                        const data = params.data;
                        return `<strong>报告编号: ${data.report_number}</strong><br/>
                                机床型号: ${data.machine_model}<br/>
                                绿色化得分: ${data.value[0].toFixed(2)}<br/>
                                概率密度: ${data.value[1].toFixed(4)}`;
                    }
                    return '';
                }
            },
            legend: {
                data: ['正态分布曲线', '数据点分布'],
                top: 50,
                left: 'center'
            },
            grid: {
                left: '12%',
                right: '8%',
                bottom: '12%',
                top: '20%'
            },
            xAxis: {
                type: 'value',
                name: '绿色化得分',
                nameLocation: 'middle',
                nameGap: 35,
                min: 60,
                max: 100,
                axisLabel: {
                    formatter: '{value}'
                }
            },
            yAxis: {
                type: 'value',
                name: '概率密度',
                nameLocation: 'middle',
                nameGap: 55
            },
            series: []
        };

        this.greenNormalDistributionChartInstance.setOption(option);
    }

    // ============================================
    // 初始化主柱状图（机床综合得分分析）
    // 配置：X轴为机床编号，Y轴为综合得分
    // 包含柱状图和趋势线两种系列
    // ============================================
    initializeChart() {
        const chartDom = document.getElementById('chart-container');
        if (!chartDom) return;

        this.chartInstance = echarts.init(chartDom);

        const option = {
            title: {
                text: '机床综合得分分析',
                left: 'center',
                top: 20,
                textStyle: {
                    fontSize: 18,
                    fontWeight: 'bold'
                }
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross'
                },
                formatter: this.formatTooltip.bind(this)
            },
            legend: {
                data: ['柱状图', '趋势线'],
                top: 60,
                left: 'center'
            },
            grid: {
                left: '60px',
                right: '40px',
                bottom: '60px',
                top: '80px',
                containLabel: false
            },
            toolbox: {
                feature: {
                    restore: { title: '重置' },
                    saveAsImage: { title: '保存图片' },
                    dataView: { title: '数据视图', readOnly: true }
                },
                right: 20,
                top: 20
            },
            xAxis: {
                type: 'category',
                data: [],
                name: '机床编号',
                nameLocation: 'middle',
                nameGap: 30,
                axisLabel: {
                    rotate: 45,
                    interval: 0,
                    fontSize: 10
                },
                axisLine: {
                    lineStyle: { color: '#333' }
                },
                axisTick: {
                    alignWithLabel: true
                }
            },
            yAxis: [
                {
                    type: 'value',
                    name: '综合得分',
                    position: 'left',
                    axisLabel: {
                        formatter: function(value) {
                            return value.toFixed(2) + '分';
                        }
                    },
                    axisLine: {
                        show: true,
                        lineStyle: { color: '#333' }
                    },
                    splitLine: {
                        show: true,
                        lineStyle: { type: 'dashed' }
                    },
                    min: function(value) {
                        return Math.max(0, value.min - 10);
                    },
                    max: function(value) {
                        return Math.min(100, value.max + 10);
                    }
                }
            ],
            series: [
                {
                    name: '柱状图',
                    type: 'bar',
                    data: [],
                    itemStyle: {
                        color: function(params) {
                            const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc'];
                            return colors[params.dataIndex % colors.length];
                        },
                        borderRadius: [4, 4, 0, 0]
                    },
                    label: {
                        show: true,
                        position: 'top',
                        formatter: '{c}',
                        fontSize: 10,
                        color: '#333'
                    },
                    emphasis: {
                        itemStyle: {
                            color: '#28a745',
                            shadowBlur: 10,
                            shadowColor: 'rgba(40, 167, 69, 0.5)'
                        }
                    }
                },
                {
                    name: '趋势线',
                    type: 'line',
                    data: [],
                    smooth: true,
                    lineStyle: {
                        color: '#dc3545',
                        width: 3,
                        type: 'solid'
                    },
                    itemStyle: {
                        color: '#dc3545'
                    },
                    symbol: 'circle',
                    symbolSize: 8,
                    emphasis: {
                        itemStyle: {
                            color: '#dc3545',
                            borderColor: '#fff',
                            borderWidth: 2,
                            shadowBlur: 10,
                            shadowColor: 'rgba(220, 53, 69, 0.5)'
                        }
                    },
                    label: {
                        show: false
                    }
                }
            ]
        };

        this.chartInstance.setOption(option);
    }

    // ============================================
    // 格式化主图表的tooltip提示框内容
    // 显示机床ID、报告编号、型号、综合得分和计算时间
    // ============================================
    formatTooltip(params) {
        let result = '<div style="padding: 10px;">';
        params.forEach(function(item) {
            if (item.seriesName === '柱状图') {
                result += `
                    <div style="margin-bottom: 5px;">
                        <strong>${item.marker}${item.seriesName}</strong><br/>
                        机床ID：${item.data.machine_id}<br/>
                        报告编号：${item.data.report_number}<br/>
                        机床型号：${item.data.machine_model}<br/>
                        综合得分：<strong style="color: #28a745;">${item.data.value.toFixed(2)}</strong>分
                    </div>
                `;
            } else if (item.seriesName === '趋势线') {
                result += `
                    <div style="margin-bottom: 5px;">
                        <strong>${item.marker}${item.seriesName}</strong><br/>
                        得分：<strong style="color: #dc3545;">${item.value.toFixed(2)}</strong>分
                    </div>
                `;
            }
        });
        result += '</div>';
        return result;
    }

    setupEventListeners() {
        const machineTypeSelect = document.getElementById('machine-type-select');

        if (machineTypeSelect) {
            machineTypeSelect.addEventListener('change', (e) => {
                const selectedType = e.target.value;
                this.loadChartData(selectedType);
            });
        }

        window.addEventListener('resize', () => {
            if (this.chartInstance) {
                this.chartInstance.resize();
            }
            if (this.normalDistributionChartInstance) {
                this.normalDistributionChartInstance.resize();
            }
        });
    }

    async loadInitialData() {
        await this.loadChartData('machining_center');
    }

    async loadChartData(machineType) {
        this.toggleElement('loading-indicator', true);
        
        try {
            let data = [];
            
            // 所有用户统一从数据库加载数据
            const response = await fetch(`/visualization/api/comprehensive-weight-chart-data/?machine_type=${machineType}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const result = await response.json();
            
            if (result.success) {
                data = result.data;
            }
            
            if (data.length > 0) {
                this.currentData = data;
                this.updateChart(data);
                this.updateStatistics(data);
                this.updateNormalDistributionChart(data);
                // 更新五个维度的正态分布图表
                this.updateDimensionNormalDistributionCharts(data);
                this.toggleElement('chart-container', true);
                this.toggleElement('no-data-message', false);
                this.toggleElement('initial-message', false);
                this.toggleElement('stats-total', true);
                this.toggleElement('stats-average', true);
                this.toggleElement('stats-max', true);
                this.toggleElement('stats-min', true);
                this.toggleElement('normal-distribution-container', true);
                this.toggleElement('normal-distribution-no-data-message', false);
                
                setTimeout(() => {
                    if (this.normalDistributionChartInstance) {
                        this.normalDistributionChartInstance.resize();
                    }
                    // 调整五个维度图表尺寸
                    if (this.precisionNormalDistributionChartInstance) {
                        this.precisionNormalDistributionChartInstance.resize();
                    }
                    if (this.performanceNormalDistributionChartInstance) {
                        this.performanceNormalDistributionChartInstance.resize();
                    }
                    if (this.reliabilityNormalDistributionChartInstance) {
                        this.reliabilityNormalDistributionChartInstance.resize();
                    }
                    if (this.intelligenceNormalDistributionChartInstance) {
                        this.intelligenceNormalDistributionChartInstance.resize();
                    }
                    if (this.greenNormalDistributionChartInstance) {
                        this.greenNormalDistributionChartInstance.resize();
                    }
                }, 300);
            } else {
                this.toggleElement('chart-container', false);
                this.toggleElement('no-data-message', true);
                this.toggleElement('initial-message', false);
                this.updateStatistics([]);
                this.toggleElement('stats-total', false);
                this.toggleElement('stats-average', false);
                this.toggleElement('stats-max', false);
                this.toggleElement('stats-min', false);
                this.toggleElement('normal-distribution-container', false);
                this.toggleElement('normal-distribution-no-data-message', true);
                this.toggleElement('precision-normal-distribution-container', false);
                this.toggleElement('precision-normal-distribution-no-data-message', true);
                this.toggleElement('performance-normal-distribution-container', false);
                this.toggleElement('performance-normal-distribution-no-data-message', true);
                this.toggleElement('reliability-normal-distribution-container', false);
                this.toggleElement('reliability-normal-distribution-no-data-message', true);
                this.toggleElement('intelligence-normal-distribution-container', false);
                this.toggleElement('intelligence-normal-distribution-no-data-message', true);
                this.toggleElement('green-normal-distribution-container', false);
                this.toggleElement('green-normal-distribution-no-data-message', true);
            }
            
        } catch (error) {
            console.error('Failed to load chart data:', error);
            alert('加载数据失败，请稍后重试');
            this.toggleElement('chart-container', false);
            this.toggleElement('no-data-message', true);
            this.toggleElement('initial-message', false);
        } finally {
            this.toggleElement('loading-indicator', false);
        }
    }

    updateChart(data) {
        const sortedData = [...data].sort((a, b) => {
            const scoreA = a.comprehensive_score || a.total_score || 0;
            const scoreB = b.comprehensive_score || b.total_score || 0;
            return scoreA - scoreB;
        });

        const xAxisData = sortedData.map(item => item.report_number || '');
        const barData = sortedData.map(item => ({
            value: item.comprehensive_score || item.total_score || 0,
            report_number: item.report_number || '',
            machine_id: item.machine_id,
            machine_model: item.machine_model || item.machine_name || '',
            precision_score: item.precision_score || 0,
            performance_score: item.performance_score || 0,
            reliability_score: item.reliability_score || 0,
            intelligence_score: item.intelligence_score || 0,
            green_score: item.green_score || 0,
            total_weight: item.total_weight || 0,
            calculated_at: item.calculated_at || item.timestamp || '',
            version: item.version || 1
        }));

        const lineData = sortedData.map(item => item.comprehensive_score || item.total_score || 0);

        const minScore = Math.min(...sortedData.map(item => item.comprehensive_score || item.total_score || 0));
        const maxScore = Math.max(...sortedData.map(item => item.comprehensive_score || item.total_score || 0));

        this.chartInstance.setOption({
            xAxis: { data: xAxisData },
            yAxis: {
                min: Math.max(0, minScore - 10),
                max: Math.min(100, maxScore + 10)
            },
            series: [
                { data: barData },
                { data: lineData }
            ]
        }, {
            notMerge: false,
            lazyUpdate: false
        });
    }

    updateStatistics(data) {
        if (data.length === 0) {
            document.getElementById('total-machines').textContent = '0';
            document.getElementById('average-score').textContent = '0';
            document.getElementById('max-score').textContent = '0';
            document.getElementById('min-score').textContent = '0';
            return;
        }
        
        const scores = data.map(item => item.comprehensive_score || item.total_score || 0);
        const total = scores.length;
        const average = scores.reduce((sum, score) => sum + score, 0) / total;
        const max = Math.max(...scores);
        const min = Math.min(...scores);
        
        document.getElementById('total-machines').textContent = total;
        document.getElementById('average-score').textContent = average.toFixed(2);
        document.getElementById('max-score').textContent = max.toFixed(2);
        document.getElementById('min-score').textContent = min.toFixed(2);
    }

    toggleElement(elementId, show) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        if (show) {
            element.style.display = 'block';
            element.style.visibility = 'visible';
            
            if (elementId.includes('chart-container')) {
                setTimeout(() => {
                    if (this.chartInstance && elementId.includes('chart-container')) {
                        this.chartInstance.resize();
                    }
                }, 200);
            }
        } else {
            element.style.display = 'none';
            element.style.visibility = 'hidden';
        }
    }

    initializeNormalDistributionChart() {
        const chartDom = document.getElementById('normal-distribution-container');
        if (!chartDom) return;

        this.normalDistributionChartInstance = echarts.init(chartDom);

        const option = {
            title: {
                text: '机床综合得分正态分布分析',
                left: 'center',
                top: 10,
                textStyle: {
                    fontSize: 18,
                    fontWeight: 'bold'
                }
            },
            tooltip: {
                trigger: 'item',
                formatter: function(params) {
                    if (params.seriesName === '正态分布曲线') {
                        return `得分: ${params.value[0].toFixed(2)}<br/>概率密度: ${params.value[1].toFixed(4)}`;
                    } else if (params.seriesName === '数据点分布') {
                        const data = params.data;
                        return `<strong>报告编号: ${data.report_number}</strong><br/>
                                机床型号: ${data.machine_model}<br/>
                                综合得分: ${data.value[0].toFixed(2)}<br/>
                                概率密度: ${data.value[1].toFixed(4)}`;
                    }
                    return '';
                }
            },
            legend: {
                data: ['正态分布曲线', '数据点分布'],
                top: 50,
                left: 'center'
            },
            grid: {
                left: '12%',
                right: '8%',
                bottom: '12%',
                top: '20%'
            },
            xAxis: {
                type: 'value',
                name: '综合得分',
                nameLocation: 'middle',
                nameGap: 35,
                min: 60,
                max: 100,
                axisLabel: {
                    formatter: '{value}'
                }
            },
            yAxis: {
                type: 'value',
                name: '概率密度',
                nameLocation: 'middle',
                nameGap: 55
            },
            series: []
        };

        this.normalDistributionChartInstance.setOption(option);
    }

    updateNormalDistributionChart(data) {
        if (!this.normalDistributionChartInstance) {
            return;
        }

        if (data.length === 0) {
            this.toggleElement('normal-distribution-container', false);
            this.toggleElement('normal-distribution-no-data-message', true);
            return;
        }

        const scores = data.map(item => item.comprehensive_score || item.total_score || 0);
        const mean = scores.reduce((sum, score) => sum + score, 0) / scores.length;
        const variance = scores.reduce((sum, score) => sum + Math.pow(score - mean, 2), 0) / scores.length;
        const stdDev = Math.sqrt(variance);

        const normalCurveData = [];
        const scatterData = [];

        for (let x = 60; x <= 100; x += 0.5) {
            const y = (1 / (stdDev * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((x - mean) / stdDev, 2));
            normalCurveData.push([x, y]);
        }

        data.forEach(item => {
            const score = item.comprehensive_score || item.total_score || 0;
            if (score >= 60 && score <= 100) {
                const y = (1 / (stdDev * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((score - mean) / stdDev, 2));
                scatterData.push({
                    value: [score, y],
                    report_number: item.report_number || '',
                    machine_model: item.machine_model || item.machine_name || '',
                    machine_id: item.machine_id
                });
            }
        });

        const maxY = Math.max(...normalCurveData.map(point => point[1]));

        this.normalDistributionChartInstance.setOption({
            yAxis: {
                min: 0,
                max: maxY * 1.2
            },
            series: [
                {
                    name: '正态分布曲线',
                    type: 'line',
                    data: normalCurveData,
                    smooth: true,
                    lineStyle: {
                        color: '#1890ff',
                        width: 3
                    },
                    areaStyle: {
                        color: {
                            type: 'linear',
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
                                { offset: 1, color: 'rgba(24, 144, 255, 0.05)' }
                            ]
                        }
                    },
                    markLine: {
                        silent: true,
                        symbol: 'none',
                        data: [
                            { xAxis: mean, label: { formatter: `μ=${mean.toFixed(2)}`, position: 'end' } },
                            { xAxis: mean - stdDev, label: { formatter: 'μ-σ', position: 'end' } },
                            { xAxis: mean + stdDev, label: { formatter: 'μ+σ', position: 'end' } },
                            { xAxis: mean - 2 * stdDev, label: { formatter: 'μ-2σ', position: 'end' } },
                            { xAxis: mean + 2 * stdDev, label: { formatter: 'μ+2σ', position: 'end' } },
                            { xAxis: mean - 3 * stdDev, label: { formatter: 'μ-3σ', position: 'end' } },
                            { xAxis: mean + 3 * stdDev, label: { formatter: 'μ+3σ', position: 'end' } }
                        ],
                        lineStyle: {
                            color: '#1E6F9F',
                            width: 2,
                            type: 'dashed'
                        }
                    }
                },
                {
                    name: '数据点分布',
                    type: 'scatter',
                    data: scatterData,
                    symbolSize: 10,
                    itemStyle: {
                        color: '#fa8c16',
                        opacity: 0.7
                    }
                }
            ],
            graphic: [
                {
                    type: 'text',
                    left: '12%',
                    top: '3%',
                    style: {
                        text: `数据来源: ${data.length}台机床综合得分数据`,
                        fontSize: 12,
                        fill: '#999'
                    }
                },
                {
                    type: 'text',
                    left: '12%',
                    top: '6%',
                    style: {
                        text: `均值(μ): ${mean.toFixed(2)}, 标准差(σ): ${stdDev.toFixed(2)}`,
                        fontSize: 12,
                        fill: '#666'
                    }
                }
            ]
        }, {
            notMerge: false,
            lazyUpdate: false
        });
    }


    // 五个维度的正态分布图表
    updateDimensionNormalDistributionCharts(data) {
        this.updatePrecisionNormalDistributionChart(data);
        this.updatePerformanceNormalDistributionChart(data);
        this.updateReliabilityNormalDistributionChart(data);
        this.updateIntelligenceNormalDistributionChart(data);
        this.updateGreenNormalDistributionChart(data);
    }


    // 精度正态分布
    updatePrecisionNormalDistributionChart(data) {
        if (!this.precisionNormalDistributionChartInstance) {
            return;
        }

        if (data.length === 0) {
            this.toggleElement('precision-normal-distribution-container', false);
            this.toggleElement('precision-normal-distribution-no-data-message', true);
            return;
        }

        const scores = data.map(item => item.precision_score || 0).filter(score => score > 0);
        if (scores.length === 0) {
            this.toggleElement('precision-normal-distribution-container', false);
            this.toggleElement('precision-normal-distribution-no-data-message', true);
            return;
        }

        const mean = scores.reduce((sum, score) => sum + score, 0) / scores.length;
        const variance = scores.reduce((sum, score) => sum + Math.pow(score - mean, 2), 0) / scores.length;
        const stdDev = Math.sqrt(variance);

        const normalCurveData = [];
        const scatterData = [];

        for (let x = 60; x <= 100; x += 0.5) {
            const y = (1 / (stdDev * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((x - mean) / stdDev, 2));
            normalCurveData.push([x, y]);
        }

        data.forEach(item => {
            const score = item.precision_score || 0;
            if (score >= 60 && score <= 100) {
                const y = (1 / (stdDev * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((score - mean) / stdDev, 2));
                scatterData.push({
                    value: [score, y],
                    report_number: item.report_number || '',
                    machine_model: item.machine_model || item.machine_name || '',
                    machine_id: item.machine_id
                });
            }
        });

        const maxY = Math.max(...normalCurveData.map(point => point[1]));

        this.precisionNormalDistributionChartInstance.setOption({
            yAxis: {
                min: 0,
                max: maxY * 1.2
            },
            series: [
                {
                    name: '正态分布曲线',
                    type: 'line',
                    data: normalCurveData,
                    smooth: true,
                    lineStyle: {
                        color: '#17a2b8',
                        width: 3
                    },
                    areaStyle: {
                        color: {
                            type: 'linear',
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                { offset: 0, color: 'rgba(23, 162, 184, 0.3)' },
                                { offset: 1, color: 'rgba(23, 162, 184, 0.05)' }
                            ]
                        }
                    },
                    markLine: {
                        silent: true,
                        symbol: 'none',
                        data: [
                            { xAxis: mean, label: { formatter: `μ=${mean.toFixed(2)}`, position: 'end' } },
                            { xAxis: mean - stdDev, label: { formatter: 'μ-σ', position: 'end' } },
                            { xAxis: mean + stdDev, label: { formatter: 'μ+σ', position: 'end' } },
                            { xAxis: mean - 2 * stdDev, label: { formatter: 'μ-2σ', position: 'end' } },
                            { xAxis: mean + 2 * stdDev, label: { formatter: 'μ+2σ', position: 'end' } },
                            { xAxis: mean - 3 * stdDev, label: { formatter: 'μ-3σ', position: 'end' } },
                            { xAxis: mean + 3 * stdDev, label: { formatter: 'μ+3σ', position: 'end' } }
                        ],
                        lineStyle: {
                            color: '#138496',
                            width: 2,
                            type: 'dashed'
                        }
                    }
                },
                {
                    name: '数据点分布',
                    type: 'scatter',
                    data: scatterData,
                    symbolSize: 10,
                    itemStyle: {
                        color: '#ffc107',
                        opacity: 0.7
                    }
                }
            ],
            graphic: [
                {
                    type: 'text',
                    left: '12%',
                    top: '3%',
                    style: {
                        text: `数据来源: ${scores.length}台机床精度得分数据`,
                        fontSize: 12,
                        fill: '#999'
                    }
                },
                {
                    type: 'text',
                    left: '12%',
                    top: '6%',
                    style: {
                        text: `均值(μ): ${mean.toFixed(2)}, 标准差(σ): ${stdDev.toFixed(2)}`,
                        fontSize: 12,
                        fill: '#666'
                    }
                }
            ]
        }, {
            notMerge: false,
            lazyUpdate: false
        });

        this.toggleElement('precision-normal-distribution-container', true);
        this.toggleElement('precision-normal-distribution-no-data-message', false);
    }

    // ============================================
    // 更新性能得分正态分布图表
    // ============================================
    updatePerformanceNormalDistributionChart(data) {
        if (!this.performanceNormalDistributionChartInstance) {
            return;
        }

        if (data.length === 0) {
            this.toggleElement('performance-normal-distribution-container', false);
            this.toggleElement('performance-normal-distribution-no-data-message', true);
            return;
        }

        const rawScores = data.map(item => item.performance_score || 0).filter(score => score > 0);
        const scores = rawScores.map(score => 60 + 8 * score);
        if (scores.length === 0) {
            this.toggleElement('performance-normal-distribution-container', false);
            this.toggleElement('performance-normal-distribution-no-data-message', true);
            return;
        }

        const mean = scores.reduce((sum, score) => sum + score, 0) / scores.length;
        const variance = scores.reduce((sum, score) => sum + Math.pow(score - mean, 2), 0) / scores.length;
        const stdDev = Math.sqrt(variance);

        const normalCurveData = [];
        const scatterData = [];

        for (let x = 60; x <= 100; x += 0.4) {
            const y = (1 / (stdDev * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((x - mean) / stdDev, 2));
            normalCurveData.push([x, y]);
        }

        data.forEach(item => {
            const rawScore = item.performance_score || 0;
            if (rawScore >= 0 && rawScore <= 5) {
                const score = 60 + 8 * rawScore;
                const y = (1 / (stdDev * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((score - mean) / stdDev, 2));
                scatterData.push({
                    value: [score, y],
                    report_number: item.report_number || '',
                    machine_model: item.machine_model || item.machine_name || '',
                    machine_id: item.machine_id
                });
            }
        });

        const maxY = Math.max(...normalCurveData.map(point => point[1]));

        this.performanceNormalDistributionChartInstance.setOption({
            yAxis: {
                min: 0,
                max: maxY * 1.2
            },
            series: [
                {
                    name: '正态分布曲线',
                    type: 'line',
                    data: normalCurveData,
                    smooth: true,
                    lineStyle: {
                        color: '#007bff',
                        width: 3
                    },
                    areaStyle: {
                        color: {
                            type: 'linear',
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                { offset: 0, color: 'rgba(0, 123, 255, 0.3)' },
                                { offset: 1, color: 'rgba(0, 123, 255, 0.05)' }
                            ]
                        }
                    },
                    markLine: {
                        silent: true,
                        symbol: 'none',
                        data: [
                            { xAxis: mean, label: { formatter: `μ=${mean.toFixed(2)}`, position: 'end' } },
                            { xAxis: mean - stdDev, label: { formatter: 'μ-σ', position: 'end' } },
                            { xAxis: mean + stdDev, label: { formatter: 'μ+σ', position: 'end' } },
                            { xAxis: mean - 2 * stdDev, label: { formatter: 'μ-2σ', position: 'end' } },
                            { xAxis: mean + 2 * stdDev, label: { formatter: 'μ+2σ', position: 'end' } },
                            { xAxis: mean - 3 * stdDev, label: { formatter: 'μ-3σ', position: 'end' } },
                            { xAxis: mean + 3 * stdDev, label: { formatter: 'μ+3σ', position: 'end' } }
                        ],
                        lineStyle: {
                            color: '#0056b3',
                            width: 2,
                            type: 'dashed'
                        }
                    }
                },
                {
                    name: '数据点分布',
                    type: 'scatter',
                    data: scatterData,
                    symbolSize: 10,
                    itemStyle: {
                        color: '#28a745',
                        opacity: 0.7
                    }
                }
            ],
            graphic: [
                {
                    type: 'text',
                    left: '12%',
                    top: '3%',
                    style: {
                        text: `数据来源: ${scores.length}台机床性能得分数据`,
                        fontSize: 12,
                        fill: '#999'
                    }
                },
                {
                    type: 'text',
                    left: '12%',
                    top: '6%',
                    style: {
                        text: `均值(μ): ${mean.toFixed(2)}, 标准差(σ): ${stdDev.toFixed(2)}`,
                        fontSize: 12,
                        fill: '#666'
                    }
                }
            ]
        }, {
            notMerge: false,
            lazyUpdate: false
        });

        this.toggleElement('performance-normal-distribution-container', true);
        this.toggleElement('performance-normal-distribution-no-data-message', false);
    }

    // ============================================
    // 更新可靠性得分正态分布图表
    // ============================================
    updateReliabilityNormalDistributionChart(data) {
        if (!this.reliabilityNormalDistributionChartInstance) {
            return;
        }

        if (data.length === 0) {
            this.toggleElement('reliability-normal-distribution-container', false);
            this.toggleElement('reliability-normal-distribution-no-data-message', true);
            return;
        }

        const rawScores = data.map(item => item.reliability_score || 0).filter(score => score > 0);
        const scores = rawScores.map(score => 60 + 8 * score);
        if (scores.length === 0) {
            this.toggleElement('reliability-normal-distribution-container', false);
            this.toggleElement('reliability-normal-distribution-no-data-message', true);
            return;
        }

        const mean = scores.reduce((sum, score) => sum + score, 0) / scores.length;
        const variance = scores.reduce((sum, score) => sum + Math.pow(score - mean, 2), 0) / scores.length;
        const stdDev = Math.sqrt(variance);

        const normalCurveData = [];
        const scatterData = [];

        for (let x = 60; x <= 100; x += 0.4) {
            const y = (1 / (stdDev * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((x - mean) / stdDev, 2));
            normalCurveData.push([x, y]);
        }

        data.forEach(item => {
            const rawScore = item.reliability_score || 0;
            if (rawScore >= 0 && rawScore <= 5) {
                const score = 60 + 8 * rawScore;
                const y = (1 / (stdDev * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((score - mean) / stdDev, 2));
                scatterData.push({
                    value: [score, y],
                    report_number: item.report_number || '',
                    machine_model: item.machine_model || item.machine_name || '',
                    machine_id: item.machine_id
                });
            }
        });

        const maxY = Math.max(...normalCurveData.map(point => point[1]));

        this.reliabilityNormalDistributionChartInstance.setOption({
            yAxis: {
                min: 0,
                max: maxY * 1.2
            },
            series: [
                {
                    name: '正态分布曲线',
                    type: 'line',
                    data: normalCurveData,
                    smooth: true,
                    lineStyle: {
                        color: '#ffc107',
                        width: 3
                    },
                    areaStyle: {
                        color: {
                            type: 'linear',
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                { offset: 0, color: 'rgba(255, 193, 7, 0.3)' },
                                { offset: 1, color: 'rgba(255, 193, 7, 0.05)' }
                            ]
                        }
                    },
                    markLine: {
                        silent: true,
                        symbol: 'none',
                        data: [
                            { xAxis: mean, label: { formatter: `μ=${mean.toFixed(2)}`, position: 'end' } },
                            { xAxis: mean - stdDev, label: { formatter: 'μ-σ', position: 'end' } },
                            { xAxis: mean + stdDev, label: { formatter: 'μ+σ', position: 'end' } },
                            { xAxis: mean - 2 * stdDev, label: { formatter: 'μ-2σ', position: 'end' } },
                            { xAxis: mean + 2 * stdDev, label: { formatter: 'μ+2σ', position: 'end' } },
                            { xAxis: mean - 3 * stdDev, label: { formatter: 'μ-3σ', position: 'end' } },
                            { xAxis: mean + 3 * stdDev, label: { formatter: 'μ+3σ', position: 'end' } }
                        ],
                        lineStyle: {
                            color: '#d39e00',
                            width: 2,
                            type: 'dashed'
                        }
                    }
                },
                {
                    name: '数据点分布',
                    type: 'scatter',
                    data: scatterData,
                    symbolSize: 10,
                    itemStyle: {
                        color: '#dc3545',
                        opacity: 0.7
                    }
                }
            ],
            graphic: [
                {
                    type: 'text',
                    left: '12%',
                    top: '3%',
                    style: {
                        text: `数据来源: ${scores.length}台机床可靠性得分数据`,
                        fontSize: 12,
                        fill: '#999'
                    }
                },
                {
                    type: 'text',
                    left: '12%',
                    top: '6%',
                    style: {
                        text: `均值(μ): ${mean.toFixed(2)}, 标准差(σ): ${stdDev.toFixed(2)}`,
                        fontSize: 12,
                        fill: '#666'
                    }
                }
            ]
        }, {
            notMerge: false,
            lazyUpdate: false
        });

        this.toggleElement('reliability-normal-distribution-container', true);
        this.toggleElement('reliability-normal-distribution-no-data-message', false);
    }

    // ============================================
    // 更新智能化得分正态分布图表
    // ============================================
    updateIntelligenceNormalDistributionChart(data) {
        if (!this.intelligenceNormalDistributionChartInstance) {
            return;
        }

        if (data.length === 0) {
            this.toggleElement('intelligence-normal-distribution-container', false);
            this.toggleElement('intelligence-normal-distribution-no-data-message', true);
            return;
        }

        const scores = data.map(item => item.intelligence_score || 0).filter(score => score > 0);
        if (scores.length === 0) {
            this.toggleElement('intelligence-normal-distribution-container', false);
            this.toggleElement('intelligence-normal-distribution-no-data-message', true);
            return;
        }

        const mean = scores.reduce((sum, score) => sum + score, 0) / scores.length;
        const variance = scores.reduce((sum, score) => sum + Math.pow(score - mean, 2), 0) / scores.length;
        const stdDev = Math.sqrt(variance);

        const normalCurveData = [];
        const scatterData = [];

        for (let x = 60; x <= 100; x += 0.5) {
            const y = (1 / (stdDev * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((x - mean) / stdDev, 2));
            normalCurveData.push([x, y]);
        }

        data.forEach(item => {
            const score = item.intelligence_score || 0;
            if (score >= 60 && score <= 100) {
                const y = (1 / (stdDev * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((score - mean) / stdDev, 2));
                scatterData.push({
                    value: [score, y],
                    report_number: item.report_number || '',
                    machine_model: item.machine_model || item.machine_name || '',
                    machine_id: item.machine_id
                });
            }
        });

        const maxY = Math.max(...normalCurveData.map(point => point[1]));

        this.intelligenceNormalDistributionChartInstance.setOption({
            yAxis: {
                min: 0,
                max: maxY * 1.2
            },
            series: [
                {
                    name: '正态分布曲线',
                    type: 'line',
                    data: normalCurveData,
                    smooth: true,
                    lineStyle: {
                        color: '#6c757d',
                        width: 3
                    },
                    areaStyle: {
                        color: {
                            type: 'linear',
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                { offset: 0, color: 'rgba(108, 117, 125, 0.3)' },
                                { offset: 1, color: 'rgba(108, 117, 125, 0.05)' }
                            ]
                        }
                    },
                    markLine: {
                        silent: true,
                        symbol: 'none',
                        data: [
                            { xAxis: mean, label: { formatter: `μ=${mean.toFixed(2)}`, position: 'end' } },
                            { xAxis: mean - stdDev, label: { formatter: 'μ-σ', position: 'end' } },
                            { xAxis: mean + stdDev, label: { formatter: 'μ+σ', position: 'end' } },
                            { xAxis: mean - 2 * stdDev, label: { formatter: 'μ-2σ', position: 'end' } },
                            { xAxis: mean + 2 * stdDev, label: { formatter: 'μ+2σ', position: 'end' } },
                            { xAxis: mean - 3 * stdDev, label: { formatter: 'μ-3σ', position: 'end' } },
                            { xAxis: mean + 3 * stdDev, label: { formatter: 'μ+3σ', position: 'end' } }
                        ],
                        lineStyle: {
                            color: '#545b62',
                            width: 2,
                            type: 'dashed'
                        }
                    }
                },
                {
                    name: '数据点分布',
                    type: 'scatter',
                    data: scatterData,
                    symbolSize: 10,
                    itemStyle: {
                        color: '#fd7e14',
                        opacity: 0.7
                    }
                }
            ],
            graphic: [
                {
                    type: 'text',
                    left: '12%',
                    top: '3%',
                    style: {
                        text: `数据来源: ${scores.length}台机床智能化得分数据`,
                        fontSize: 12,
                        fill: '#999'
                    }
                },
                {
                    type: 'text',
                    left: '12%',
                    top: '6%',
                    style: {
                        text: `均值(μ): ${mean.toFixed(2)}, 标准差(σ): ${stdDev.toFixed(2)}`,
                        fontSize: 12,
                        fill: '#666'
                    }
                }
            ]
        }, {
            notMerge: false,
            lazyUpdate: false
        });

        this.toggleElement('intelligence-normal-distribution-container', true);
        this.toggleElement('intelligence-normal-distribution-no-data-message', false);
    }

    // ============================================
    // 更新绿色化得分正态分布图表
    // ============================================
    updateGreenNormalDistributionChart(data) {
        if (!this.greenNormalDistributionChartInstance) {
            return;
        }

        if (data.length === 0) {
            this.toggleElement('green-normal-distribution-container', false);
            this.toggleElement('green-normal-distribution-no-data-message', true);
            return;
        }

        const rawScores = data.map(item => item.green_score || 0).filter(score => score > 0);
        const scores = rawScores.map(score => 60 + 8 * score);
        if (scores.length === 0) {
            this.toggleElement('green-normal-distribution-container', false);
            this.toggleElement('green-normal-distribution-no-data-message', true);
            return;
        }

        const mean = scores.reduce((sum, score) => sum + score, 0) / scores.length;
        const variance = scores.reduce((sum, score) => sum + Math.pow(score - mean, 2), 0) / scores.length;
        const stdDev = Math.sqrt(variance);

        const normalCurveData = [];
        const scatterData = [];

        for (let x = 60; x <= 100; x += 0.4) {
            const y = (1 / (stdDev * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((x - mean) / stdDev, 2));
            normalCurveData.push([x, y]);
        }

        data.forEach(item => {
            const rawScore = item.green_score || 0;
            if (rawScore >= 0 && rawScore <= 5) {
                const score = 60 + 8 * rawScore;
                const y = (1 / (stdDev * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((score - mean) / stdDev, 2));
                scatterData.push({
                    value: [score, y],
                    report_number: item.report_number || '',
                    machine_model: item.machine_model || item.machine_name || '',
                    machine_id: item.machine_id
                });
            }
        });

        const maxY = Math.max(...normalCurveData.map(point => point[1]));

        this.greenNormalDistributionChartInstance.setOption({
            yAxis: {
                min: 0,
                max: maxY * 1.2
            },
            series: [
                {
                    name: '正态分布曲线',
                    type: 'line',
                    data: normalCurveData,
                    smooth: true,
                    lineStyle: {
                        color: '#343a40',
                        width: 3
                    },
                    areaStyle: {
                        color: {
                            type: 'linear',
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                { offset: 0, color: 'rgba(52, 58, 64, 0.3)' },
                                { offset: 1, color: 'rgba(52, 58, 64, 0.05)' }
                            ]
                        }
                    },
                    markLine: {
                        silent: true,
                        symbol: 'none',
                        data: [
                            { xAxis: mean, label: { formatter: `μ=${mean.toFixed(2)}`, position: 'end' } },
                            { xAxis: mean - stdDev, label: { formatter: 'μ-σ', position: 'end' } },
                            { xAxis: mean + stdDev, label: { formatter: 'μ+σ', position: 'end' } },
                            { xAxis: mean - 2 * stdDev, label: { formatter: 'μ-2σ', position: 'end' } },
                            { xAxis: mean + 2 * stdDev, label: { formatter: 'μ+2σ', position: 'end' } },
                            { xAxis: mean - 3 * stdDev, label: { formatter: 'μ-3σ', position: 'end' } },
                            { xAxis: mean + 3 * stdDev, label: { formatter: 'μ+3σ', position: 'end' } }
                        ],
                        lineStyle: {
                            color: '#1d2124',
                            width: 2,
                            type: 'dashed'
                        }
                    }
                },
                {
                    name: '数据点分布',
                    type: 'scatter',
                    data: scatterData,
                    symbolSize: 10,
                    itemStyle: {
                        color: '#20c997',
                        opacity: 0.7
                    }
                }
            ],
            graphic: [
                {
                    type: 'text',
                    left: '12%',
                    top: '3%',
                    style: {
                        text: `数据来源: ${scores.length}台机床绿色化得分数据`,
                        fontSize: 12,
                        fill: '#999'
                    }
                },
                {
                    type: 'text',
                    left: '12%',
                    top: '6%',
                    style: {
                        text: `均值(μ): ${mean.toFixed(2)}, 标准差(σ): ${stdDev.toFixed(2)}`,
                        fontSize: 12,
                        fill: '#666'
                    }
                }
            ]
        }, {
            notMerge: false,
            lazyUpdate: false
        });

        this.toggleElement('green-normal-distribution-container', true);
        this.toggleElement('green-normal-distribution-no-data-message', false);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new VisualizationDashboard();
});