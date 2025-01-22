chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log("[Content Script] 메시지 수신:", message);
  if (message.action === "triggerAlert" && message.result) {
    const { score } = message.result;
    console.log("[Content Script] 받은 점수:", score);

    if (score <= 50) {
      alert("이 사이트는 피싱의 위험이 있을 수 있습니다. 더 자세한 정보를 원하시면 SafeWeb 아이콘을 클릭하세요.");
    }
    sendResponse({ success: true });
  }
});