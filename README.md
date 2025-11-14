# 🛍️ Deal-Hunter v2.1: 쇼핑몰 가격 추적 자동화

네이버, 쿠팡 등 JavaScript로 로드되는 쇼핑몰의 상품 가격을 추적하는 Python 자동화 스크립트입니다.

지정한 상품의 가격이 이전에 확인한 가격보다 낮아지거나, 설정한 '목표 가격'에 도달하면 알림을 보냅니다. (현재 v2.1 알림은 터미널 콘솔에 출력됩니다.)

## ✨ 주요 기능

* **Selenium 기반:** JavaScript가 많은 네이버, 쿠팡 등의 사이트도 안정적으로 추적
* **설정 파일 분리:** `config.json` 파일 수정만으로 추적할 상품을 쉽게 추가/삭제/관리
* **상태 저장:** `last_prices.json`에 마지막 가격을 저장하여 '가격 하락' 시점 감지

## 🚀 시작하기

### 1. 환경 준비

이 스크립트는 Python 3와 Chrome 브라우저가 필요합니다.

1.  이 저장소의 파일들을 다운로드합니다.
2.  터미널(명령 프롬프트)을 열고, 필요한 라이브러리를 설치합니다.

    ```bash
    pip install -r requirements.txt
    ```

### 2. 설정 (`config.json`)

`config.json` 파일을 열어 원하는 상품 정보를 입력합니다.

* `id`: 상품을 구별할 고유 ID (직접 만드세요)
* `name`: 알림 시 표시될 상품 이름 (직접 만드세요)
* `url`: 추적할 상품의 전체 URL
* `target_price`: 이 가격 이하가 되면 알림 (선택 사항)
* `css_selector`: **[가장 중요]** 상품 가격 정보가 담긴 HTML의 CSS 선택자.
* `stock_keyword`: "품절" 등 재고 없음 키워드

#### 💡 CSS 선택자(Selector) 찾는 팁

1.  Chrome에서 상품 페이지 열기
2.  가격 정보(예: "15,900원")에 마우스 오른쪽 클릭 > **[검사]**
3.  
4.  개발자 도구 창에서 해당 요소(예: `<span class="total-price">...`)를 찾아, 해당 요소에 마우스 오른쪽 클릭 > **[Copy]** > **[Copy selector]**
5.  복사된 선택자(예: `#contents > ... > span.total-price`)를 `css_selector` 값으로 붙여넣습니다.

### 3. 실행

터미널에서 스크립트를 실행합니다.

```bash
python deal_hunter_v2.0.py
