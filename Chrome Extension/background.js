let nowConUrl = null;
let lastResult = null;

function updateCurrentSite(callback) {
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    if (tabs.length > 0) {
      const newUrl = tabs[0].url;
      if (newUrl !== nowConUrl) {
        nowConUrl = newUrl;

        // API 호출
        fetch(`https://safeweb-flask.vercel.app/api/check_url?url=${encodeURIComponent(nowConUrl)}`)
          .then(response => response.json())
          .then(data => {
            lastResult = {
              now_con_url: data.user_url || "N/A",
              score: data.score || "N/A",
              good: data.good || "N/A",
            };
            //console.log("[Background] API 결과:", lastResult);
            if (callback) callback(true); // 호출 완료 알림
          })
          .catch(error => {
            //console.error("[Background] API 요청 실패:", error);
            lastResult = null;
            if (callback) callback(false); // 호출 실패 알림
          });
      } else if (callback) {
        callback(true); // URL이 동일한 경우에도 성공 알림
      }
    }
  });
}

chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  if (message.action === "getPopupData") {
    sendResponse(lastResult);
    return true;
  } else if (message.action === "updateCurrentSite") {
    updateCurrentSite((success) => {
      sendResponse({ success });
    });
    return true; // 비동기 응답 처리
  }
});

chrome.tabs.onActivated.addListener((activeInfo) => {
  chrome.tabs.get(activeInfo.tabId, (tab) => {
    if (tab.url !== nowConUrl) {
      updateCurrentSite();
    }
  });
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url) {
    updateCurrentSite();
  }
});
