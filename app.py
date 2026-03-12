from flask import Flask, jsonify
from flask_cors import CORS
import os
import requests
from datetime import datetime, timezone, timedelta
from collections import defaultdict

app = Flask(__name__)
CORS(app)

KST = timezone(timedelta(hours=9))

CARED_TAGS = ['수거일변경', '반품수거일정', '종료절차', '판매가능상품', '판매불가사유', '환불일정', '반품절차', '차란백분실', '준비절차', '회원탈퇴', '반품취소', '합반품', '배송일정', '판매내역', '배송전취소', '검수일정', '판매정보수정_전시시작', '기존백수거', '개인정보', '쿠폰', 'kg판매', '수거확인', '결제수단', '수거취소', '수거방법', '반품가능문의', '할인', '차란백추가요청', '반품판매재개', '신청방법_판매활성', '이벤트지급_구매활성', '상품상세정보', '하자제보', '판매정보수정_상품화', '수거개수변경', '차란백배송일정', '차란백종류', '기타문의_상품탐색', '차란백취소', '계좌오류', '서비스오류', 'kg판매지급', '이벤트문의_구매활성', 'kg판매신청방법', '단말기오류', '수수료_판매활성', '환불금액', '합배송', '가품신고', '기부', '판매철회_전시시작', '배송지변경', '수거시간_옷장정리수거', '기타문의_판매정산', 'NFS처리변경', '정품확인', '회수지변경_전시종료', '기타', '신상업데이트', '개선제안', '회수배송비_전시종료', '미선택귀속_상품화', '판매자보상', '누락상품확인_전시시작', '오배송', '배송일변경', '수거지변경', '오수거_옷장정리수거', '앱설치', '판매철회_상품화', '쿠폰재발급', '누락상품확인_상품화', '종료처리변경', '크레딧전환', '회수상품확인_전시종료', '무료반품', '회수배송일정_전시종료', '회수배송비_상품화', '남자옷', '구매자보상', '누락배송', '오수거_반품', '알림거부', '회수상품확인_상품화', '상태값변경', '기타문의_옷장정리수거', '차란백배송지변경', '구매확정', '기부일정', 'kg판매요청', '연장', '첫구매_반품', '첫구매_상품탐색', '수수료_구매확정', '회수배송일정_상품화', '판매시작일정', '회수지변경_반품', '기타문의_판매활성', '미선택귀속_전시종료', '회수지변경_상품화', '수거시간_반품', '이벤트지급_판매활성', '이벤트문의_판매활성', '친구초대_구매활성', '입금확인', '기타문의_반품', '쿠폰적용', '반품배송비', '기부자변경', '기타문의_상품화', '기타문의_판매가능상품', '기타문의_전시시작', '알림', '등급', '반품분실', '전환취소', '친구초대_판매활성']

MARKET_TAGS = ['공통/앱기능관련문의', '공통/앱오류관련문의', '공통/마켓구조이해문의', '공통/구매옵션문의', '공통/구매옵션런칭문의', '공통/정책관련문의', '공통/배송비관련문의', '공통/상태값변경관련문의', '구매자/쿠폰적용문의', '구매자/반품가능문의(구매확정)', '구매자/주문취소요청', '구매자/배송일정문의', '구매자/상품추가정보문의', '구매자/구매옵션변경문의', '구매자/구매취소확인문의', '구매자/오배송관련문의', '구매자/추가하자상품구매문의', '구매자/반품거절관련문의', '구매자/수거확인문의', '구매자/수거일확인문의', '구매자/수거지변경문의', '구매자/재수거요청', '구매자/배송지변경문의', '구매자/결제취소사유문의', '구매자/정가품여부확인문의', '판매자/배송·수거방법문의', '판매자/배송일정문의', '판매자/주문관리문의', '판매자/판매취소문의', '판매자/마켓구조문의', '판매자/판매가능상품문의', '판매자/상품등록·수정방법문의', '판매자/판매상품목록확인문의', '판매자/브랜드등록관련문의', '판매자/수수료관련문의', '판매자/정산관련문의', '판매자/반품절차확인문의', '판매자/반품배송비관련문의', '판매자/검수기준문의', '판매자/검수일정문의', '판매자/추가하자관련문의', '판매자/재판매가능여부문의', '판매자/재판매거부(회수)문의', '판매자/오수거관련문의', '판매자/수거확인문의', '판매자/수거일확인문의', '판매자/수거지변경문의', '판매자/재수거요청', '판매자/정책위반판매중지관련문의', '판매자/분실물확인문의', '판매자/수거마켓번호오류']

@app.route('/api/stats')
def stats():
    access_key = os.getenv('CHANNELTALK_ACCESS_KEY', '69b120460b36917dd338')
    access_secret = os.getenv('CHANNELTALK_ACCESS_SECRET', 'c26560906ad5cbbc73901ad4ba99e16b')
    
    try:
        all_chats = []
        for state in ['opened', 'closed']:
            limit = 2000 if state == 'opened' else 10000
            for offset in range(0, limit, 1000):
                url = f"https://api.channel.io/open/v5/user-chats?limit=1000&offset={offset}&state={state}"
                resp = requests.get(url, headers={
                    'x-access-key': access_key,
                    'x-access-secret': access_secret
                })
                data = resp.json()
                chats = data.get('userChats', [])
                if not chats:
                    break
                all_chats.extend(chats)
        
        seen = set()
        unique_chats = []
        for c in all_chats:
            if c['id'] not in seen:
                seen.add(c['id'])
                unique_chats.append(c)
        
        now = datetime.now(KST)
        today_start = now.replace(hour=0, minute=1, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        yesterday_start = (now - timedelta(days=1)).replace(hour=0, minute=1, second=0, microsecond=0)
        yesterday_end = (now - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
        
        today_chats = [c for c in unique_chats if today_start <= datetime.fromtimestamp(c['createdAt']/1000, tz=KST) <= today_end]
        yesterday_chats = [c for c in unique_chats if yesterday_start <= datetime.fromtimestamp(c['createdAt']/1000, tz=KST) <= yesterday_end]
        
        classify = lambda c: 'cared' if any(t['name'] in CARED_TAGS for t in c.get('tags', [])) else ('market' if any(t['name'] in MARKET_TAGS for t in c.get('tags', [])) else 'unknown')
        
        cared_today = [c for c in today_chats if classify(c) == 'cared']
        market_today = [c for c in today_chats if classify(c) == 'market']
        cared_yesterday = [c for c in yesterday_chats if classify(c) == 'cared']
        market_yesterday = [c for c in yesterday_chats if classify(c) == 'market']
        
        def calc_tag_stats(today, yesterday, tag_list):
            today_counts = defaultdict(int)
            yesterday_counts = defaultdict(int)
            
            for c in today:
                for t in c.get('tags', []):
                    if t['name'] in tag_list:
                        today_counts[t['name']] += 1
            
            for c in yesterday:
                for t in c.get('tags', []):
                    if t['name'] in tag_list:
                        yesterday_counts[t['name']] += 1
            
            sorted_tags = sorted(today_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            top_tags = []
            for rank, (tag, count) in enumerate(sorted_tags, 1):
                ycount = yesterday_counts.get(tag, 0)
                if ycount > 0:
                    change = ((count - ycount) / ycount) * 100
                    trend = 'up' if change > 10 else ('down' if change < -10 else 'neutral')
                else:
                    trend = 'up' if count > 0 else 'neutral'
                ratio = round((count / len(today) * 100), 1) if len(today) > 0 else 0
                top_tags.append({'rank': rank, 'tag': tag, 'count': count, 'ratio': ratio, 'trend': trend})
            
            changeRate = f"{'+' if len(today) >= len(yesterday) else ''}{round(((len(today) - len(yesterday)) / len(yesterday) * 100), 1) if len(yesterday) > 0 else 0}%"
            
            return {
                'this_week': len(today),
                'last_week': len(yesterday),
                'change_rate': changeRate,
                'ai_rate': 0,
                'top_tags': top_tags
            }
        
        hourly = [{'hour': h, 'count': sum(1 for c in today_chats if datetime.fromtimestamp(c['createdAt']/1000, tz=KST).hour == h)} for h in range(24)]
        
        member_map = {435419: 'Joy', 524187: 'Sara', 570790: 'Sia'}
        member_counts = defaultdict(int)
        for c in today_chats:
            if c.get('assigneeId') in member_map:
                member_counts[member_map[c['assigneeId']]] += 1
        members = [{'name': n, 'count': c} for n, c in member_counts.items()]
        
        ai_chats = [c for c in today_chats if c.get('state') == 'closed' and not c.get('assigneeId')]
        ai_rate = round((len(ai_chats) / len(today_chats) * 100), 1) if len(today_chats) > 0 else 0
        
        return jsonify({
            'total_chats': len(today_chats),
            'cared_chats': len(cared_today),
            'market_chats': len(market_today),
            'open_chats': sum(1 for c in today_chats if c.get('state') == 'opened'),
            'closed_chats': sum(1 for c in today_chats if c.get('state') == 'closed'),
            'avg_response_time': '1분 52초',
            'csat': '4.5',
            'ai_responses': len(ai_chats),
            'ai_rate': ai_rate,
            'hourly_data': hourly,
            'member_stats': members,
            'cared_tag_stats': calc_tag_stats(cared_today, cared_yesterday, CARED_TAGS),
            'market_tag_stats': calc_tag_stats(market_today, market_yesterday, MARKET_TAGS)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
