document.addEventListener("DOMContentLoaded", () => {
    // 팝업이 열릴 때 updateCurrentSite 호출 요청
    chrome.runtime.sendMessage({ action: "updateCurrentSite" }, (response) => {
      if (response && response.success) {
        console.log("[Popup] updateCurrentSite 호출 성공");
  
        // 데이터 요청
        chrome.runtime.sendMessage({ action: "getPopupData" }, (response) => {
          if (response) {
            const { score, now_con_url, good } = response;
  
            // 데이터 표시
            document.getElementById("now_con_url").innerText = `${now_con_url}`;
            document.getElementById("score").innerText = `${score}점`;
            document.getElementById("good").innerText = `${good}`;
  
            // 점수에 따른 색상 변경
            const scoreElement = document.getElementById("score");
            const explain = document.getElementById("description");
            if (score == 100) {
              scoreElement.style.color = "#36E6B6";
              scoreElement.style.backgroundImage = "linear-gradient(to right, #38fabc, #42acfc)";
              scoreElement.style.webkitBackgroundClip = "text";
              scoreElement.style.color = "transparent";
              explain.innerText = `해당 사이트는 안전한 사이트로\n안심하셔도 됩니다.`;
            } else if (score >= 70) {
              scoreElement.style.color = "#42acfc";
              explain.innerText = `해당 사이트는 피싱 사이트로 의심되지 않습니다.`;
            } else if (score == 60) {
              scoreElement.style.color = "#FEE667";
              explain.innerText = `해당 사이트는 위험 사이트로 의심되지는 않지만\n 주의가 필요합니다.`;
            } else {
              scoreElement.style.color = "#FF6961";
              explain.innerText = `해당 사이트는 위험 사이트로 의심됩니다.`;
            }
          } else {
            document.getElementById("score").innerText = "데이터를 가져올 수 없습니다.";
            document.getElementById("description").innerText = "데이터를 표기할 수 없습니다.";
          }
        });
      } else {
        console.error("[Popup] updateCurrentSite 호출 실패");
      }
    });
  });