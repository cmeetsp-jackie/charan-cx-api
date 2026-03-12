# 차란 CX API 서버

## 배포 방법

### Render.com (추천)
1. https://render.com 접속
2. "New +" → "Web Service"
3. GitHub 연결: `cmeetsp-jackie/charan-cx-api`
4. 자동으로 배포됨 (5분)

배포 완료 후 URL을 프론트엔드에 연결하면 끝!

## 로컬 테스트
```bash
pip install -r requirements.txt
python app.py
# http://localhost:8000/api/stats
```
