let isDetectionActive = false;

// 监听来自 popup.js 的消息
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if (request.action === 'startDetection') {
        isDetectionActive = true;
        startDetection();  // 启动检测
    } else if (request.action === 'stopDetection') {
        isDetectionActive = false;
        // 停止检测时可以添加一些操作，例如清除当前状态等
    }
});

// 每当检测开启时，自动抓取当前页面的源码并传递给模型
function startDetection() {
    if (isDetectionActive) {
        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
            if (tabs.length > 0) {
                const tab = tabs[0];
                const url = tab.url;
                console.log("开始爬取的 URL:", url);

                // 确保只爬取有效的网页 URL
                if (url && (url.startsWith("http://") || url.startsWith("https://"))) {
                    fetch('http://127.0.0.1:8000/predict', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ "url": url })
                    })
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`HTTP 错误! 状态码: ${response.status}`);
                            }
                            return response.json();
                        })
                        .then(data => {
                            console.log("API 返回的数据:", data);
                            // 向 popup.js 发送检测结果
                            chrome.runtime.sendMessage({ result: data });
                        })
                        .catch(error => {
                            console.error('请求错误:', error);
                            // 向 popup.js 发送错误信息
                            chrome.runtime.sendMessage({ result: { error: error.message } });
                        });
                } else {
                    console.log("无效的 URL，跳过检测:", url);
                    chrome.runtime.sendMessage({ result: { error: '无效的 URL，跳过检测' } });
                }
            }
        });
    }
}
