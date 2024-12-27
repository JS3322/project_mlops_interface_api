<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <title>{% block title %}{% endblock %}</title>
  <style>
    /* 기본 페이지 스타일 */
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
      position: relative; /* 새로고침 버튼 절대배치용 */
      color: #fff;
    }

    /* 우측 상단 새로고침 버튼 */
    .refresh-btn {
      position: absolute;
      top: 20px;
      right: 20px;
      z-index: 999; /* 버튼이 뒤로 깔리지 않도록 */
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

    /* 반투명(글라스) 스타일 컨테이너 */
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
      vertical-align: middle; /* 버튼이 행 중앙에 오도록 */
    }
    th {
      background-color: rgba(255, 255, 255, 0.2);
    }
    tbody tr:hover {
      background-color: rgba(255, 255, 255, 0.1);
    }

    /* 활성화된 모델(배경 깜빡임) */
    @keyframes blinkBlue {
      0%   { background-color: rgba(0, 123, 255, 0.3); }
      50%  { background-color: rgba(0, 123, 255, 0.1); }
      100% { background-color: rgba(0, 123, 255, 0.3); }
    }
    tr.activated {
      animation: blinkBlue 1.2s infinite alternate;
    }

    /* 버튼 영역 (Activate + Deactivate) */
    .btn-wrapper {
      width: 120px;        /* 고정 너비 */
      display: flex;       /* flex 레이아웃 */
      justify-content: space-between;
      position: relative;
      overflow: hidden;    /* Deactivate 버튼이 사라질 때 내용 숨김 */
    }

    /* 공통 버튼 스타일 */
    .activate-btn, .deactivate-btn {
      flex: 1 1 auto;            /* flex 영역 */
      margin: 0 2px;             /* 버튼 간격 */
      border: none;
      border-radius: 5px;
      font-weight: bold;
      cursor: pointer;
      color: #fff;
      background-color: rgba(255, 255, 255, 0.2);
      transition: all 0.3s ease;
      text-align: center;
      white-space: nowrap;
    }
    .activate-btn:hover, .deactivate-btn:hover {
      background-color: rgba(255, 255, 255, 0.4);
    }

    /* 비활성화 상태(row가 activated가 아님)일 때 -> Deactivate 버튼 숨기기 */
    .btn-wrapper:not(.activated) .deactivate-btn {
      width: 0;
      margin: 0;
      opacity: 0;
      pointer-events: none;
    }

    /* 비활성화 상태일 때 -> Activate 버튼이 전체 폭 사용 */
    .btn-wrapper:not(.activated) .activate-btn {
      width: 100%;
      margin: 0; 
    }

    /* 활성화 상태(row가 activated)일 때 -> 두 버튼 반반 */
    .btn-wrapper.activated .activate-btn,
    .btn-wrapper.activated .deactivate-btn {
      width: 50%;
      margin: 0 2px; /* 버튼간 간격 */
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