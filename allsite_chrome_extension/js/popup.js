var list_regexs;
var detail_regexs;

function httpRequest(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            callback(xhr.responseText);
        }
    };
    xhr.send();
}

function showRegexs(result) {
    result = JSON.parse(result);
    list_regexs = JSON.parse(result).list_regexs;
    detail_regexs = JSON.parse(result).detail_regexs;
    // list_regexs= [{"regex":"list-","weight":"1"},{"regex":"index","weight":"1"},{"regex":"aaaa","weight":"1"}];
    var table = '<table id=regexs_tab><tr><th>分类(列表/详情)</th><th>正则表达式</th><th>权重</th><th>采用</th></tr>';
    for (var i in list_regexs) {
        table += '<tr>';
        table += '<td><input type=text size=2 value=list></td>';
        table += '<td><input type=text size=15 value=' + list_regexs[i].regex + '></td>';
        table += '<td><input type=text size=2 value=' + list_regexs[i].weight + '></td>';
        table += '<td>use</td>';
        table += '</tr>';
    }
    for (var i in detail_regexs) {
        table += '<tr>';
        table += '<td><input type=text size=2 value=detail></td>';
        table += '<td><input type=text size=15 value=' + detail_regexs[i].regex + '></td>';
        table += '<td><input type=text size=2 value=' + detail_regexs[i].weight + '></td>';
        table += '<td>use</td>';
        table += '</tr>';
    }
    table += '</table>';
    document.getElementById('regexs').innerHTML = table;
}

function getChangedRegexs() {
    console.log('getChangedRegexs() start');
    var regex_type = [];
    $("#regexs_tab tr td:nth-child(1) input").each(function () {
        regex_type.push($(this).val());
    });

    var regexs = [];
    $("#regexs_tab tr td:nth-child(2) input").each(function () {
        regexs.push($(this).val());
    });
    var regexs_parten = regexs.join('|');

    var weight = [];
    $("#regexs_tab tr td:nth-child(3) input").each(function () {
        weight.push($(this).val());
    });

    list_regexs = [];
    detail_regexs = [];
    for(var i=0; i<regex_type.length;i++){
        if(regex_type[i]=='list'){
            list_regexs.push({regex:regexs[i],weight:weight[i]});
        }else{
            detail_regexs.push({regex:regexs[i],weight:weight[i]});
        }
    }
    console.log(list_regexs);
    console.log(detail_regexs);
    console.log('getChangedRegexs() end');
}

function onlineRegexsChange(e) {
    console.log('onlineRegexsChange');
    getChangedRegexs();
    var message = {opt: "change", list_regexs: list_regexs, detail_regexs: detail_regexs};
    console.log(message);
    chrome.tabs.query({active: true, currentWindow: true}, function (tabs) {
        for (var i = tabs.length - 1; i >= 0; i--) {
            chrome.tabs.sendMessage(tabs[0].id, message);
        }
    });
}

var url = 'http://127.0.0.1:2000/regexs/list';
httpRequest(url, showRegexs);

document.body.onchange = onlineRegexsChange;
