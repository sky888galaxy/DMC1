// 获取开关按钮
const toggleSwitch = document.getElementById('toggleSwitch');

// 监听开关状态变化
toggleSwitch.addEventListener('change', function () {
    if (this.checked) {
        // 发送消息到 background.js 开始检测
        chrome.runtime.sendMessage({ action: 'startDetection' });
        document.getElementById('result').innerHTML = '<div class="loading">正在检测...</div>';
    } else {
        // 发送消息到 background.js 停止检测
        chrome.runtime.sendMessage({ action: 'stopDetection' });
        document.getElementById('result').innerHTML = '<div class="status">检测已停止</div>';
    }
});

// 接收来自 background.js 的结果并更新显示
chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
    console.log("popup.js 收到的数据:", message);

    const resultContainer = document.getElementById('result');

    if (message.result && message.result.predictions) {
        const results = message.result.predictions;

        let output = '';

        // 检查是否有恶意代码
        const hasMaliciousCode = results.some(item => item.prediction === 'Malicious');
        if (!hasMaliciousCode) {
            // 如果没有恶意代码，显示网站安全
            output += `<div class="status safe">✅ 网站安全：无恶意代码</div>`;
        } else {
            // 如果发现恶意代码，列出所有恶意代码
            output += '<div class="status warning">⚠️ 发现潜在的恶意代码：</div>';
            results.forEach((item, index) => {
                output += `第 ${index + 1} 段代码预测结果: ${item.prediction}<br>`;
                if (item.prediction === 'Malicious') {
                    output += `⚠️ 恶意代码:<br><code>${item.malicious_code}</code><br><br>`;
                }
            });
        }

        // 显示信息泄露风险
        if (message.result.leaks_detected) {
            output += `<div class="status warning">⚠️ 发现信息泄露风险：</div><code>${message.result.leaks.join(', ')}</code><br><br>`;
        }

        // 显示漏洞扫描结果
        if (message.result.vulnerabilities && message.result.vulnerabilities.length > 0) {
            output += `<div class="status error">❌ 发现漏洞：</div><ul>`;
            message.result.vulnerabilities.forEach(vuln => {
                output += `<li>${vuln}</li>`;
            });
            output += `</ul>`;
        }

        resultContainer.innerHTML = output;
    } else if (message.result && message.result.error) {
        resultContainer.innerHTML = `<div class="status error">❌ 错误：${message.result.error}</div>`;
    } else {
        resultContainer.innerHTML = '<div class="status">❓ 没有返回可用的数据</div>';
    }
});

