# (파일 상단 ... import re, json, time, selenium 등은 v2.0과 동일)
# import os # os 모듈은 필요 없습니다.

# ... (load_config, load_last_prices, save_last_prices, setup_driver, get_product_info_selenium 함수는 v2.0과 동일) ...

# -----------------------------------------------------------------
# 4. 알림 기능 (v2.5: 로그 파일 생성)
# -----------------------------------------------------------------
def send_alert(item, reason, current_price, last_price=None, target_price=None):
    """
    v2.5: 이메일 대신 'alert.log' 파일을 생성하여
    GitHub Actions가 커밋 메시지로 사용할 수 있게 합니다.
    """
    print(f"🎉 ** 알림 조건 충족! ** ({item['name']})") # Actions 로그용
    
    alert_message = ""
    if reason == "PRICE_DROP":
        alert_message = f"🎉 가격 하락! {item['name']}: {last_price}원 -> {current_price}원"
    elif reason == "TARGET_HIT":
        alert_message = f"🎯 목표가 달성! {item['name']}: {current_price}원"
        
    # 'alert.log' 파일에 알림 메시지를 덮어씁니다.
    # (여러 개가 감지되면 마지막 것만 기록되지만, 커밋 알림 용도로는 충분합니다.)
    try:
        with open("alert.log", "w", encoding="utf-8") as f:
            f.write(alert_message)
        print(f"✅ 'alert.log' 파일 생성: {alert_message}")
    except Exception as e:
        print(f"❌ 'alert.log' 파일 생성 실패: {e}")

# ... (if __name__ == "__main__": 이하 v2.0과 동일) ...
# (v3.0에서 추가했던 'elif' 중복 알림 방지 로직을 v2.0처럼 단순화해도 좋습니다.)
if __name__ == "__main__":
    print("--- Deal-Hunter v2.5 (Commit Alert) 실행 ---")
    
    config_items = load_config()
    last_prices = load_last_prices()
    new_prices_state = last_prices.copy()
    
    driver = setup_driver()

    for item in config_items:
        print(f"\n[추적 중] {item['name']}...")
        
        status, current_price = get_product_info_selenium(
            driver, item['url'], item['css_selector'], item['stock_keyword']
        )
        
        if status == "재고있음":
            print(f"  [확인] 현재 가격: {current_price}")
            
            item_id = item['id']
            last_price = last_prices.get(item_id)
            target_price = item.get('target_price')
            
            # v2.0의 알림 로직
            if last_price and current_price < last_price:
                send_alert(item, "PRICE_DROP", current_price, last_price=last_price)
            
            if target_price and current_price <= target_price:
                send_alert(item, "TARGET_HIT", current_price, target_price=target_price)
            
            new_prices_state[item_id] = current_price
            
        else:
            print(f"  [확인] 상태: {status}")
            
    driver.quit()
    save_last_prices(new_prices_state)
    
    print("\n--- 모든 작업 완료 ---")
## 📄 2단계: GitHub Actions '명령서' 수정
.github/workflows/price_check.yml 파일에서 맨 마지막 Commit and push... 단계만 아래와 같이 수정합니다.

env: (이메일 비밀) 부분은 모두 삭제하고, run: python ... 부분도 v2.5 스크립트를 실행하도록 변경합니다.

YAML

# ... (파일 상단 name, on, jobs, steps 1~4는 v3.0 제안과 동일) ...

      # 5. 핵심 스크립트 실행하기 (v2.5로 변경)
      - name: Run Price Hunter Script (v2.5)
        run: python deal_hunter_v2.5.py # v2.5 스크립트 실행 (이름을 맞게 수정)

      # 6. (중요) 알림 로그에 따라 커밋 메시지를 동적으로 변경
      - name: Commit and push if files changed
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add last_prices.json
          
          # 기본 커밋 메시지 설정
          COMMIT_MSG="Update last_prices.json"
          
          # 'alert.log' 파일이 생성되었다면 (즉, 가격 변동이 감지됨)
          if [ -f alert.log ]; then
            # 커밋 메시지를 'alert.log' 파일의 내용으로 변경
            COMMIT_MSG=$(cat alert.log)
            # 다음 실행을 위해 'alert.log' 파일은 삭제
            rm alert.log
          fi
          
          # 파일이 변경되었는지 확인 (last_prices.json만)
          if git diff --staged --quiet; then
            echo "No changes to commit."
          else
            # 동적으로 설정된 COMMIT_MSG를 사용
            git commit -m "$COMMIT_MSG"
            git push
          fi
