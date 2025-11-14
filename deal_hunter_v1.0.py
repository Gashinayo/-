import requests
from bs4 import BeautifulSoup
import json
import time
import re

# 설정/상태 파일명
CONFIG_FILE = "config.json"
STATE_FILE = "last_prices.json"

# HTTP 요청 시 헤더 (봇 차단 우회용)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# -----------------------------------------------------------------
# 1. 파일 관리 기능
# -----------------------------------------------------------------
def load_config():
    """설정 파일(config.json)을 읽어옴"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ '{CONFIG_FILE}'을 찾을 수 없습니다. 기본 양식으로 새로 생성합니다.")
        # 기본 양식 생성
        sample_config = [{
            "id": "item001", "name": "상품명", "url": "상품URL",
            "target_price": 10000, "css_selector": "가격 CSS 선택자",
            "stock_keyword": "품절"
        }]
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2)
        return sample_config

def load_last_prices():
    """이전 가격 상태 파일(last_prices.json)을 읽어옴"""
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {} # 파일이 없으면 빈 딕셔너리 반환

def save_last_prices(prices_state):
    """현재 가격을 상태 파일에 저장"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(prices_state, f, indent=2)

# -----------------------------------------------------------------
# 2. 핵심 기능: 스크래핑 및 분석
# -----------------------------------------------------------------
def get_product_info(url, css_selector, stock_keyword):
    """
    URL에 접속하여 가격과 재고 정보를 가져옵니다.
    (이 함수가 v1.0의 핵심입니다)
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status() # 오류가 있으면 예외 발생
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. 재고 확인 (키워드 기반)
        if stock_keyword and soup.find(string=lambda text: stock_keyword in text):
            return "품절", None
            
        # 2. 가격 정보 추출 (CSS 선택자 기반)
        price_element = soup.select_one(css_selector)
        
        if not price_element:
            return "가격정보없음", None

        # 가격 텍스트에서 숫자만 추출 (예: "50,000원" -> 50000)
        price_text = price_element.get_text()
        price_digits = re.sub(r"[^\d\.]", "", price_text) # 숫자와 소수점만 남김
        
        if price_digits:
            return "재고있음", float(price_digits)
            
    except requests.exceptions.RequestException as e:
        print(f"  [오류] {url} 접속 실패: {e}")
        return "접속오류", None
    except Exception as e:
        print(f"  [오류] 데이터 분석 실패: {e}")
        return "분석오류", None
        
    return "정보없음", None

# -----------------------------------------------------------------
# 3. 알림 기능 (v1.0: 단순 출력)
# -----------------------------------------------------------------
def send_alert(item, reason, current_price, last_price=None, target_price=None):
    """알림을 보냅니다. (v1.0은 print로 대체)"""
    print("="*40)
    print(f"🎉 ** 가격 변동 알림 ** 🎉")
    print(f"상품: {item['name']}")
    
    if reason == "PRICE_DROP":
        print(f"사유: 가격 하락! ({last_price} -> {current_price})")
    elif reason == "TARGET_HIT":
        print(f"사유: 목표 가격 달성! ({current_price} <= {target_price})")
    
    print(f"링크: {item['url']}")
    print("="*40)

# -----------------------------------------------------------------
# v1.0 실행 (Main)
# -----------------------------------------------------------------
if __name__ == "__main__":
    print("--- Deal-Hunter v1.0 (자동화 양식) 실행 ---")
    
    config_items = load_config()
    last_prices = load_last_prices()
    
    new_prices_state = last_prices.copy() # 현재 상태를 저장할 새 딕셔너리

    for item in config_items:
        print(f"\n[추적 중] {item['name']}...")
        
        status, current_price = get_product_info(item['url'], item['css_selector'], item['stock_keyword'])
        
        if status == "재고있음":
            print(f"  [확인] 현재 가격: {current_price}")
            
            item_id = item['id']
            last_price = last_prices.get(item_id)
            target_price = item.get('target_price')
            
            # 알림 조건 1: 이전 가격보다 저렴해짐
            if last_price and current_price < last_price:
                send_alert(item, "PRICE_DROP", current_price, last_price=last_price)
            
            # 알림 조건 2: 목표 가격에 도달함
            if target_price and current_price <= target_price:
                send_alert(item, "TARGET_HIT", current_price, target_price=target_price)
            
            # 새 가격 정보 업데이트
            new_prices_state[item_id] = current_price
            
        else:
            print(f"  [확인] 상태: {status}")
            
    # 모든 작업 완료 후, 최신 가격 정보를 파일에 저장
    save_last_prices(new_prices_state)
    
    print("\n--- 모든 작업 완료. 1분 후 다시 시작합니다. ---")
    # (실제 자동화 시에는 이 스크립트를 1시간에 1번씩 실행하도록 스케줄링)
