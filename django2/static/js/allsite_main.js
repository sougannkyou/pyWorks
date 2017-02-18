var THEME = 'shine';

function ajaxError(err) {
    $('#test').text('hubPageRank-ajax error:' + err);
}
// ------------------ getDashBoardCnt  ------------------
setInterval(function () {
    $.ajax({
        url: '/allsite/dashBoardCnt/',
        type: 'get',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err);
            $('#domainCnt').text(0);
            $('#hubPageCnt').text(0);
            $('#detailCnt').text(0);
            $('#newDoaminCnt').text(0);
        },
        success: function (data, textStatus) {
            $('#domainCnt').text(data["domain_cnt"]);
            $('#hubPageCnt').text(data["hubPage_cnt"]);
            $('#detailCnt').text(data["detail_cnt"]);
            $('#newDoaminCnt').text(data["new_doamin_cnt"]);
        }
    });
}, 600000);

// -------------- detail_trend ------------------
function detailTrendFunc(THEME) {
    $.ajax({
        url: '/allsite/drawDetailTrend/',
        type: 'get',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err);
        },
        success: function (data, textStatus) {
            var myChart = echarts.init(document.getElementById("detail_trend"), THEME);
            var option = {
                title: {
                    text: ''
                },
                tooltip: {
                    trigger: 'axis'
                },
                legend: {
                    data: ['前天', '昨天', '今天']
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14',
                        '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']
                },
                yAxis: {
                    type: 'value'
                },
                series: [
                    {
                        name: '前天',
                        type: 'line',
                        stack: '前天采集量',
                        data: data['beforeYesterday']
                    },
                    {
                        name: '昨天',
                        type: 'line',
                        stack: '昨天采集量',
                        data: data['yesterday']
                    },
                    {
                        name: '今天',
                        type: 'line',
                        stack: '今天采集量',
                        data: data['today']
                    }
                ]
            };
            myChart.setOption(option);
        }
    });
}
detailTrendFunc(THEME);


// ------------------ hubPage_trend  ------------------
function hubPageTrendFunc(THEME) {
    $.ajax({
        url: '/allsite/drawHubPageTrend/',
        type: 'get',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err);
        },
        success: function (data, textStatus) {
            var myChart = echarts.init(document.getElementById("hubPage_trend"), THEME);
            var option = {
                title: {
                    text: '     扫描周期：' + data['period'] + ' 小时'
                },
                tooltip: {
                    trigger: 'axis'
                },
                legend: {
                    data: ['今天']
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15',
                        '16', '17', '18', '19', '20', '21', '22', '23', '24']
                },
                yAxis: {
                    type: 'value'
                },
                series: [
                    {
                        name: '今日',
                        type: 'line',
                        stack: '扫描量',
                        data: data['hubPageTrend']
                    }]
            };
            myChart.setOption(option);
        }
    });
}
hubPageTrendFunc(THEME);

// ------------------ newDomain ------------------
function newDomainOpt(THEME, opt) {
    $.ajax({
        url: '/allsite/drawNewDomain/',
        type: 'POST',
        data: {opt: opt},
        // contentType: "application/json; charset=UTF-8",
        dataType: "json",
        error: function (xhr, err) {
            ajaxError(err);
        },
        success: function (data, textStatus) {
            $('#newDomain').remove();
            $('#newDomainParent').html('<div id="newDomain" style="width:100%;height:250px;"></div>');
            // var timeList = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16",
            //     "17", "18", "19", "20", "21", "22", "23", "24"];
            // var domainCnt = [500, 420, 360, 200, 500, 600, 800, 500, 420, 360, 700, 500, 400, 600, 500, 420, 360,
            //     200, 500, 600, 400, 500, 420, 360];
            var obj = document.getElementById('newDomain');
            var myChart = echarts.init(obj, THEME);
            var option = {
                color: ['#39BCD1'],
                title: {
                    text: ''
                },
                tooltip: {},
                legend: {
                    data: ['新站数']
                },
                xAxis: {
                    data: data['timeList']
                },
                yAxis: {},
                series: [{
                    name: '新站数',
                    barWidth: 10,
                    type: 'bar',
                    data: data['domainCnt']
                }]
            };
            myChart.setOption(option);
        }
    });
}

function reDrawNewDoamin(t) {
    var THEME = '';
    newDomainOpt(THEME, t);
}

// ------------------ domain_rank ------------------
function domainRankFunc(THEME) {
    $.ajax({
        url: '/allsite/drawDomainRank/',
        type: 'get',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err);
        },
        success: function (data, textStatus) {
            var myChart = echarts.init(document.getElementById('domain_rank'), THEME);

            var option = {
                color: ['#39BCD1'],
                title: {
                    text: ''
                },
                tooltip: {},
                legend: {
                    data: ['已入库', '未入库']
                },
                xAxis: {
                    data: ["No.1", "No.2", "No.3", "No.4", "No.5", "No.6", "No.7", "No.8", "No.9", "No.10"]
                },
                yAxis: {},
                series: [{
                    name: '已入库',
                    stack: '总量',
                    barWidth: 10,
                    type: 'bar',
                    data: data["domainRankUsed"]
                }, {
                    name: '未入库',
                    stack: '总量',
                    barWidth: 10,
                    type: 'bar',
                    data: data["domainRankUnUsed"]
                }]
            };
            myChart.setOption(option);
        }
    });
}
domainRankFunc(THEME);

// ------------------ hubPage_rank ------------------
function hubPageRankFunc(THEME) {
    $.ajax({
        url: '/allsite/drawHubPageRank/',
        type: 'get',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err);
        },
        success: function (data, textStatus) {

            var myChart = echarts.init(document.getElementById('hubPage_rank'), THEME);
            var option = {
                color: ['#348017'],
                title: {
                    text: ''
                },
                tooltip: {},
                legend: {
                    data: ['采集详情页数']
                },
                xAxis: {
                    data: ["No.1", "No.2", "No.3", "No.4", "No.5", "No.6", "No.7", "No.8", "No.9", "No.10"]
                },
                yAxis: {},
                series: [{
                    name: '采集详情页数',
                    stack: '总量',
                    barWidth: 10,
                    type: 'bar',
                    data: data["hubPageRank"]
                }]
            };
            myChart.setOption(option);
        }
    });
}
hubPageRankFunc(THEME);

// ------------------ redis_monitor ------------------
function redisMonitorFunc(THEME) {
    var myChart = echarts.init(document.getElementById("redis_monitor"), THEME);

    var base = 1;
    var hour = [];

    var data = [0];
    var now = base;

    function addData(shift) {
        hour.push(now);
        data.push(Math.random() * 60);

        if (shift) {
            hour.shift();
            data.shift();
        }
        if (now > 23) {
            now = 1;
        } else {
            now = now + 1;
        }
    }

    for (var i = 1; i < 24; i++) {
        addData();
    }

    var option = {
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: hour
        },
        yAxis: {
            boundaryGap: [0, '50%'],
            type: 'value',
            max: 100
        },
        series: [
            {
                name: 'redis',
                type: 'line',
                smooth: true,
                symbol: 'none',
                stack: 'a',
                areaStyle: {
                    normal: {}
                },
                data: data
            }
        ]
    };

    setInterval(function () {
        addData(true);
        myChart.setOption({
            xAxis: {
                data: hour
            },
            series: [{
                name: 'redis',
                data: data
            }]
        });
    }, 1800);

    if (option && typeof option === "object") {
        myChart.setOption(option, true);
    }
}
redisMonitorFunc(THEME);

// ------------------ crawlTime_part ------------------
function crawlTimePart(THEME) {
    $.ajax({
        url: '/allsite/drawCrawlTimePart/',
        type: 'get',
        contentType: "application/json; charset=UTF-8",
        error: function (xhr, err) {
            ajaxError(err);
        },
        success: function (data, textStatus) {
            var myChart = echarts.init(document.getElementById('crawlTime_part'), THEME);
            var option = {
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                legend: {
                    orient: 'vertical',
                    height: '240px',
                    x: 'left',
                    data: ['0-1分钟', '1-2分钟', '2-5分钟', '5-15分钟',
                        '15-30分钟', '30-60分钟', '60-120分钟', '120-240分钟', '超过240分钟']
                },
                series: [
                    {
                        name: '采集时间差',
                        type: 'pie',
                        radius: '80%',
                        center: ['50%', '50%'],
                        data: [
                            {value: data['0-1'], name: '0-1分钟'},
                            {value: data['1-2'], name: '1-2分钟'},
                            {value: data['2-5'], name: '2-5分钟'},
                            {value: data['5-15'], name: '5-15分钟'},
                            {value: data['15-30'], name: '15-30分钟'},
                            {value: data['30-60'], name: '30-60分钟'},
                            {value: data['60-120'], name: '60-120分钟'},
                            {value: data['120-240'], name: '120-240分钟'},
                            {value: data['>240'], name: '超过240分钟'}
                        ],
                        itemStyle: {
                            normal: {
                                label: {show: false},
                                labelLine: {
                                    show: false
                                }
                            }
                        }
                    }
                ],
                color: ['#073f01', '#075f01', '#07a001', '#0fc005', '#20e010', '#b04020', '#800f05', '#5f0701', '#2f0000']
            };
            myChart.setOption(option);
        }
    });

}
crawlTimePart(THEME);

// ------------------ detail_diff  ------------------
function detailDiffFunc(THEME) {
    var myChart = echarts.init(document.getElementById("detail_diff"), THEME);
    var option = {
        title: {
            text: '     扫描周期：20.6 小时'
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['今天']
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']
        },
        yAxis: {
            type: 'value'
        },
        series: [
            {
                name: '今日',
                type: 'line',
                stack: '扫描量',
                data: [120, 132, 133, 134, 150, 200, 210, 220, 232, 233, 235, 260, 261, 262, 277, 278, 280, 290, 310, 330, 340, 350, 360]
            }]
    };
    myChart.setOption(option);
}
detailDiffFunc(THEME);




