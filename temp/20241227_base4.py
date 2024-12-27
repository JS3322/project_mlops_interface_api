<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <title>{% block title %}{% endblock %}</title>
  <style>
    body {
      margin: 0; 
      padding: 0;
      font-family: sans-serif;
      background: linear-gradient(135deg, #2c3e50, #4ca1af) fixed;
    }
    .container {
      max-width: 900px;
      margin: 40px auto;
      padding: 20px;
      box-sizing: border-box;
      color: #fff;
      position: relative; /* Refresh버튼 위치용 */
    }

    /* 우측 상단 새로고침 버튼 */
    .refresh-btn {
      position: absolute;
      top: 0;
      right: 0;
      margin: 20px;
      background-color: rgba(255, 255, 255, 0.2);
      border: none;
      border-radius: 5px;
      color: #fff;
      padding: 8px 12px;
      cursor: pointer;
      font-weight: bold;
      transition: background-color 0.2s ease;
    }
    .refresh-btn:hover {
      background-color: rgba(255, 255, 255, 0.4);
    }

    /* 반투명(글라스) 컨테이너 */
    .glass-container {
      background-color: rgba(255, 255, 255, 0.2);
      backdrop-filter: blur(10px);
      border-radius: 10px;
      box-shadow: 0 0 10px rgba(0,0,0,0.2);
      padding: 20px;
      box-sizing: border-box;
    }

    /* 테이블 스타일 */
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
    }
    th, td {
      text-align: left;
      padding: 10px;
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: #fff;
    }
    th {
      background-color: rgba(255, 255, 255, 0.2);
    }
    tbody tr:hover {
      background-color: rgba(255, 255, 255, 0.1);
    }

    /* 활성화된 모델(배경 깜빡임) */
    @keyframes blinkBlue {
      0% {
        background-color: rgba(0, 123, 255, 0.3);
      }
      50% {
        background-color: rgba(0, 123, 255, 0.1);
      }
      100% {
        background-color: rgba(0, 123, 255, 0.3);
      }
    }
    tr.activated {
      animation: blinkBlue 1.2s infinite alternate;
    }

    /* 버튼 래퍼: Activate + Deactivate 버튼의 총 너비를 동일하게 유지 */
    .btn-wrapper {
      width: 120px; /* 원하는 고정 너비 */
      display: inline-block;
      position: relative;
    }

    /* 두 버튼 모두, 이 래퍼 안에서 절대 위치 */
    .activate-btn,
    .deactivate-btn {
      position: absolute;
      top: 0;
      left: 0;
      height: 32px; 
      box-sizing: border-box;
      border: none;
      border-radius: 5px;
      font-weight: bold;
      cursor: pointer;
      transition: width 0.3s ease, opacity 0.3s ease;
      color: #fff;
      background-color: rgba(255, 255, 255, 0.2);
    }
    .activate-btn:hover,
    .deactivate-btn:hover {
      background-color: rgba(255, 255, 255, 0.4);
    }

    /* 비활성화(Deactivate) 버튼: 초기 상태는 width=0, opacity=0 => 안 보임 */
    .deactivate-btn {
      width: 0;
      opacity: 0;
      pointer-events: none; /* 클릭 막기 */
    }

    /* 단일 버튼(미활성화 상태) => Activate 버튼이 전체 폭 사용 */
    .btn-wrapper:not(.activated) .activate-btn {
      width: 120px;
      opacity: 1;
    }

    /* 활성화 상태 => 두 버튼 모두 반띵 */
    .btn-wrapper.activated .activate-btn {
      width: 58px; 
      opacity: 1;
    }
    .btn-wrapper.activated .deactivate-btn {
      width: 58px;
      left: 62px; /* Activate버튼 뒤로 이동(간격 4px) */
      opacity: 1;
      pointer-events: auto; 
    }
  </style>
</head>
<body>
  <div class="container">
    <button class="refresh-btn" id="refreshBtn">새로고침</button>
    {% block content %}{% endblock %}
  </div>
</body>
</html>