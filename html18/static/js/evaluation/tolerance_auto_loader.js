const ToleranceAutoLoader = {
    CACHE_KEY_MC: 'toleranceData_machining_center',
    CACHE_KEY_BM: 'toleranceData_boring_milling_machine',
    CACHE_TIMESTAMP_KEY: 'tolerance_cache_timestamp',
    CACHE_DURATION: 30 * 60 * 1000,
    TOLERANCE_PAGE_URL: '/evaluation/tolerance-management/',
    isLoaded: false,

    init: function() {
        console.log('[ToleranceAutoLoader] 初始化自动加载允差数据...');
        this.loadToleranceData();
    },

    loadToleranceData: function() {
        const cacheTimestamp = localStorage.getItem(this.CACHE_TIMESTAMP_KEY);
        const now = Date.now();

        if (cacheTimestamp && (now - parseInt(cacheTimestamp)) < this.CACHE_DURATION) {
            const mcData = localStorage.getItem(this.CACHE_KEY_MC);
            const bmData = localStorage.getItem(this.CACHE_KEY_BM);

            var mcCount = mcData ? Object.keys(JSON.parse(mcData)).length : 0;
            var bmCount = bmData ? Object.keys(JSON.parse(bmData)).length : 0;
            if (mcCount > 0 || bmCount > 0) {
                console.log('[ToleranceAutoLoader] 使用缓存的允差数据 (加工中心:', mcCount, '条, 镗铣床:', bmCount, '条)');
                this.isLoaded = true;
                this.notifyLoaded();
                return;
            }
        }

        console.log('[ToleranceAutoLoader] 缓存无效，从允差管理页面获取数据...');
        this.fetchFromTolerancePage();
    },

    fetchFromTolerancePage: function() {
        const self = this;
        const xhr = new XMLHttpRequest();
        xhr.open('GET', this.TOLERANCE_PAGE_URL, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    try {
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(xhr.responseText, 'text/html');
                        self.parseTolerancePage(doc);
                    } catch (e) {
                        console.error('[ToleranceAutoLoader] 解析允差管理页面失败:', e);
                        self.checkExistingCache();
                    }
                } else {
                    console.warn('[ToleranceAutoLoader] 获取允差管理页面失败，状态码:', xhr.status);
                    self.checkExistingCache();
                }
            }
        };
        xhr.onerror = function() {
            console.error('[ToleranceAutoLoader] 网络请求失败');
            self.checkExistingCache();
        };
        xhr.send();
    },

    parseTolerancePage: function(doc) {
        console.log('[ToleranceAutoLoader] 解析允差管理页面HTML...');
        const self = this;
        const machineTypes = ['machining_center', 'boring_milling_machine'];
        let totalSaved = 0;

        machineTypes.forEach(function(machineType) {
            const dataKey = 'toleranceData_' + machineType;
            const toleranceData = {};

            const allTables = doc.querySelectorAll('.tolerance-table[data-machine-type="' + machineType + '"]');
            console.log('[ToleranceAutoLoader] ' + machineType + ' 找到 ' + allTables.length + ' 个表格');

            if (allTables.length === 0) return;

            allTables.forEach(function(table) {
                const rows = table.querySelectorAll('tbody tr');

                rows.forEach(function(row) {
                    const firstCell = row.querySelector('td:first-child');
                    if (!firstCell) return;

                    const testItem = firstCell.textContent.trim().replace(/\s+/g, ' ');
                    if (!testItem) return;

                    const toleranceValues = row.querySelectorAll('.tolerance-value');
                    if (!toleranceValues.length) return;

                    var values = [];
                    toleranceValues.forEach(function(toleranceValue) {
                        var valueCells = toleranceValue.querySelectorAll('td');
                        if (valueCells.length > 1) {
                            // 表格结构：提取每个允差值
                            // 检查第一个td是否为空（标签行），如果为空则跳过
                            var firstCellIsEmpty = !valueCells[0].textContent.trim();
                            valueCells.forEach(function(cell, index) {
                                if (index === 0 && firstCellIsEmpty) {
                                    return;
                                }
                                var cellValue = cell.textContent.trim();
                                if (cellValue) {
                                    values.push(cellValue);
                                }
                            });
                        } else {
                            var cellValue = toleranceValue.textContent.trim();
                            if (cellValue) {
                                values.push(cellValue);
                            }
                        }
                    });

                    if (values.length > 0) {
                        toleranceData[testItem] = values.join(', ');
                    }
                });
            });

            if (Object.keys(toleranceData).length > 0) {
                localStorage.setItem(dataKey, JSON.stringify(toleranceData));
                console.log('[ToleranceAutoLoader] ' + machineType + ' 已保存 ' + Object.keys(toleranceData).length + ' 条数据');
                totalSaved += Object.keys(toleranceData).length;
            }
        });

        if (totalSaved > 0) {
            localStorage.setItem(self.CACHE_TIMESTAMP_KEY, Date.now().toString());
            console.log('[ToleranceAutoLoader] 从允差管理页面获取数据完成，共 ' + totalSaved + ' 条');
        } else {
            console.warn('[ToleranceAutoLoader] 未从允差管理页面获取到数据');
        }

        self.isLoaded = true;
        self.notifyLoaded();
    },

    checkExistingCache: function() {
        console.log('[ToleranceAutoLoader] 检查现有缓存数据');

        const mcDataStr = localStorage.getItem(this.CACHE_KEY_MC);
        const bmDataStr = localStorage.getItem(this.CACHE_KEY_BM);

        let mcData = {};
        let bmData = {};

        if (mcDataStr) {
            try {
                mcData = JSON.parse(mcDataStr);
            } catch (e) {}
        }

        if (bmDataStr) {
            try {
                bmData = JSON.parse(bmDataStr);
            } catch (e) {}
        }

        if (Object.keys(mcData).length > 0 || Object.keys(bmData).length > 0) {
            console.log('[ToleranceAutoLoader] 使用现有缓存数据 (加工中心:', Object.keys(mcData).length, '条, 镗铣床:', Object.keys(bmData).length, '条)');
        } else {
            console.log('[ToleranceAutoLoader] 无缓存数据');
        }

        this.isLoaded = true;
        this.notifyLoaded();
    },

    notifyLoaded: function() {
        const mcData = JSON.parse(localStorage.getItem(this.CACHE_KEY_MC) || '{}');
        const bmData = JSON.parse(localStorage.getItem(this.CACHE_KEY_BM) || '{}');

        console.log('[ToleranceAutoLoader] 允差数据加载完成 - 加工中心:', Object.keys(mcData).length, '条, 镗铣床:', Object.keys(bmData).length, '条');

        const event = new CustomEvent('toleranceDataLoaded', {
            detail: {
                machining_center: mcData,
                boring_milling_machine: bmData
            }
        });
        document.dispatchEvent(event);
    },

    getToleranceData: function(machineType) {
        const key = machineType === 'boring_milling_machine' ? this.CACHE_KEY_BM : this.CACHE_KEY_MC;
        return JSON.parse(localStorage.getItem(key) || '{}');
    },

    forceRefresh: function() {
        console.log('[ToleranceAutoLoader] 强制刷新允差数据');
        localStorage.removeItem(this.CACHE_TIMESTAMP_KEY);
        this.fetchFromTolerancePage();
    },

    clearCache: function() {
        console.log('[ToleranceAutoLoader] 清除所有允差数据缓存');
        localStorage.removeItem(this.CACHE_KEY_MC);
        localStorage.removeItem(this.CACHE_KEY_BM);
        localStorage.removeItem(this.CACHE_TIMESTAMP_KEY);
        console.log('[ToleranceAutoLoader] 缓存已清除');
    },

    getStatus: function() {
        const mcData = JSON.parse(localStorage.getItem(this.CACHE_KEY_MC) || '{}');
        const bmData = JSON.parse(localStorage.getItem(this.CACHE_KEY_BM) || '{}');
        const timestamp = localStorage.getItem(this.CACHE_TIMESTAMP_KEY);

        return {
            machining_center: {
                count: Object.keys(mcData).length,
                data: mcData
            },
            boring_milling_machine: {
                count: Object.keys(bmData).length,
                data: bmData
            },
            cache_timestamp: timestamp ? new Date(parseInt(timestamp)).toLocaleString() : '无'
        };
    }
};

document.addEventListener('DOMContentLoaded', function() {
    ToleranceAutoLoader.init();
});
