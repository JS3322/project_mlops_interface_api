<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
  table {
    border-collapse: collapse;
    width: 500px;
    table-layout: fixed;
    position: relative;
  }

  td {
    border: 1px solid #ccc;
    width: 50px;
    height: 30px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    position: relative;
    vertical-align: middle;
    padding:0;
  }

  input.cell-input {
    width: 100%;
    height: 100%;
    border: none;
    text-align: right;
    padding: 0 2px;
    box-sizing: border-box;
    background: transparent;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  /* 포커스 되었을 때 사용할 클래스 (동적으로 추가/삭제 예정) */
  .expanded-input {
    position: absolute;
    z-index: 999;
    background: #fff;
    border: 1px solid #333;
    box-sizing: border-box;
    padding: 0 4px;
    width: auto;
    min-width: 150px;
    /* 필요하다면 폰트 사이즈나 라인하이트 조정 가능 */
  }
</style>
</head>
<body>

<table id="myTable">
  <tbody>
    <tr>
      <td><input class="cell-input" type="text" value="123.4567"></td>
      <td><input class="cell-input" type="text" value="12.34"></td>
      <td><input class="cell-input" type="text" value="0.999999"></td>
      <td><input class="cell-input" type="text" value="45.6789"></td>
      <td><input class="cell-input" type="text" value="1000.00"></td>
      <td><input class="cell-input" type="text" value="3.14159265"></td>
      <td><input class="cell-input" type="text" value="9999.99"></td>
      <td><input class="cell-input" type="text" value="23.4567"></td>
      <td><input class="cell-input" type="text" value="5678.1234"></td>
      <td><input class="cell-input" type="text" value="0.12"></td>
    </tr>
    <tr>
      <td><input class="cell-input" type="text" value="9876.5432"></td>
      <td><input class="cell-input" type="text" value="10.0001"></td>
      <td><input class="cell-input" type="text" value="0.00001"></td>
      <td><input class="cell-input" type="text" value="123.4"></td>
      <td><input class="cell-input" type="text" value="500.2"></td>
      <td><input class="cell-input" type="text" value="1.1"></td>
      <td><input class="cell-input" type="text" value="2.2345"></td>
      <td><input class="cell-input" type="text" value="333.3333"></td>
      <td><input class="cell-input" type="text" value="1234.5678"></td>
      <td><input class="cell-input" type="text" value="44.44"></td>
    </tr>
  </tbody>
</table>

<script>
  const table = document.getElementById('myTable');

  table.addEventListener('focusin', function(e) {
    const target = e.target;
    if (target.classList.contains('cell-input')) {
      expandInput(target);
    }
  });

  table.addEventListener('focusout', function(e) {
    const target = e.target;
    if (target.classList.contains('cell-input')) {
      // 입력 종료 시 원래 위치 복귀
      collapseInput(target);
    }
  });

  function expandInput(inputEl) {
    // 현재 셀 위치 계산
    const td = inputEl.parentNode;
    const tableRect = table.getBoundingClientRect();
    const tdRect = td.getBoundingClientRect();

    // document.body에 임시로 복제해서 붙여넣어 크게 표시하는 방식
    // 또는 테이블 내 position:absolute를 활용할 수도 있음
    const originalStyle = {
      position: inputEl.style.position,
      left: inputEl.style.left,
      top: inputEl.style.top,
      width: inputEl.style.width,
      zIndex: inputEl.style.zIndex
    };
    inputEl.dataset.originalStyle = JSON.stringify(originalStyle);

    inputEl.classList.add('expanded-input');

    // 테이블 상대 좌표
    let left = tdRect.left - tableRect.left;
    let top = tdRect.top - tableRect.top;

    // 위치 지정
    inputEl.style.position = 'absolute';
    inputEl.style.left = left + 'px';
    inputEl.style.top = top + 'px';
    inputEl.style.width = 'auto';
    inputEl.select(); // 전체 값 선택 (편집 편의성 상승)
  }

  function collapseInput(inputEl) {
    // 원래 스타일 복구
    const originalStyle = JSON.parse(inputEl.dataset.originalStyle);
    inputEl.style.position = originalStyle.position;
    inputEl.style.left = originalStyle.left;
    inputEl.style.top = originalStyle.top;
    inputEl.style.width = originalStyle.width;
    inputEl.style.zIndex = originalStyle.zIndex;
    inputEl.classList.remove('expanded-input');
    delete inputEl.dataset.originalStyle;
  }
</script>

</body>
</html>




<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>2x10 Table with Overflow Tooltip</title>
<style>
  table {
    border-collapse: collapse;
    width: 500px; /* 전체 테이블 폭 고정 예시 */
    table-layout: fixed; /* 셀 너비 고정 */
    position: relative; /* tooltip positioning을 위해 */
  }

  td {
    border: 1px solid #ccc;
    width: 50px; /* 각 셀의 너비 고정 예시 */
    height: 30px; /* 각 셀의 높이 고정 예시 */
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    position: relative;
    vertical-align: middle;
  }

  input {
    width: 100%;
    height: 100%;
    border: none;
    padding: 0 2px;
    box-sizing: border-box;
    text-align: right;
    background: transparent;
    font-size: 14px;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  /* hover 또는 클릭 시 표시될 tooltip 스타일 */
  .tooltip {
    position: absolute;
    background: #fff;
    border: 1px solid #333;
    padding: 5px;
    white-space: nowrap;
    font-size: 14px;
    display: none;
    z-index: 999;
    box-shadow: 0px 0px 5px rgba(0,0,0,0.3);
  }

  /* tooltip 화살표 모양 추가 (선택사항) */
  .tooltip::before {
    content: "";
    position: absolute;
    border: 5px solid transparent;
    border-right-color: #333;
    left: -10px;
    top: 50%;
    transform: translateY(-50%);
  }

</style>
</head>
<body>

<table id="myTable">
  <tbody>
    <!-- 2행 10열 -->
    <tr>
      <td><input type="text" value="123.4567"></td>
      <td><input type="text" value="12.34"></td>
      <td><input type="text" value="0.999999"></td>
      <td><input type="text" value="45.6789"></td>
      <td><input type="text" value="1000.00"></td>
      <td><input type="text" value="3.14159265"></td>
      <td><input type="text" value="9999.99"></td>
      <td><input type="text" value="23.4567"></td>
      <td><input type="text" value="5678.1234"></td>
      <td><input type="text" value="0.12"></td>
    </tr>
    <tr>
      <td><input type="text" value="9876.5432"></td>
      <td><input type="text" value="10.0001"></td>
      <td><input type="text" value="0.00001"></td>
      <td><input type="text" value="123.4"></td>
      <td><input type="text" value="500.2"></td>
      <td><input type="text" value="1.1"></td>
      <td><input type="text" value="2.2345"></td>
      <td><input type="text" value="333.3333"></td>
      <td><input type="text" value="1234.5678"></td>
      <td><input type="text" value="44.44"></td>
    </tr>
  </tbody>
</table>

<div class="tooltip" id="tooltip"></div>

<script>
  const table = document.getElementById('myTable');
  const tooltip = document.getElementById('tooltip');

  let currentTd = null;

  // 셀 클릭 시 tooltip 표시
  table.addEventListener('click', function(e) {
    const target = e.target;
    if (target.tagName.toLowerCase() === 'input') {
      showTooltip(target);
    } else {
      hideTooltip();
    }
  });

  // 마우스 아웃 시 tooltip 숨김(원한다면 유지하거나 클릭 시만 닫도록 변경 가능)
  table.addEventListener('mouseleave', hideTooltip);

  // tooltip 보여주는 함수
  function showTooltip(inputEl) {
    const value = inputEl.value;
    tooltip.textContent = value;
    tooltip.style.display = 'block';

    // tooltip 위치 계산
    const td = inputEl.parentNode;
    const tableRect = table.getBoundingClientRect();
    const tdRect = td.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();

    // 기본적으로 td 오른쪽에 표시
    let left = tdRect.right - tableRect.left + 5;
    let top = tdRect.top - tableRect.top + (tdRect.height/2 - tooltipRect.height/2);

    // 만약 오른쪽 공간이 부족하다면 왼쪽으로 표시
    if (left + tooltipRect.width > tableRect.width) {
      left = tdRect.left - tableRect.left - tooltipRect.width - 5;
      tooltip.style.removeProperty('transform'); // 화살표 방향 변경하려면 추가 조정 필요
    }

    // 위/아래 공간 체크(기본적으로 수직 중앙정렬)
    // 만약 위로 더 올라갈 공간이 없다면 아래쪽으로 내려가기
    if (top < 0) {
      top = 0;
    } else if (top + tooltipRect.height > tableRect.height) {
      top = tableRect.height - tooltipRect.height;
    }

    tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';
  }

  function hideTooltip() {
    tooltip.style.display = 'none';
  }
</script>

</body>
</html>
