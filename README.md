```markdown
# DLC operation

간단한 Flask 기반 앱으로 Faculty Email Finder 및 Course Modality DB 기능을 제공합니다.

요약 기능
- Faculty: 관리자(핀 필요) 엑셀 업로드로 교원 DB 갱신, 사용자 업로드 파일(Korean_name만 포함)을 내부 DB와 매칭하여 영문/카테고리/이메일을 채운 엑셀로 다운로드
- Course: 관리자(핀 필요) 엑셀 업로드로 수업방식 DB 갱신, 사용자는 검색(이름) → Apply(4자리 PIN 입력) → Reason 작성 및 저장 → 조회/취소 가능
- 퍼지 검색(Levenshtein 기반)을 이름 검색에 사용(rapidfuzz)
- Modified Date는 ISO8601로 DB에 저장. UI에선 "YYYY-MM-DD hh:mm:ss AM/PM"으로 표시

로컬 실행
1. Python 3.10+ 권장
2. 가상환경 생성 및 패키지 설치
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
3. 환경변수 설정(선택)
   export ADMIN_PIN=1205
   export FLASK_APP=app.py
4. 앱 실행
   flask run

GitHub 업로드
1. 새 리포지토리 생성 (예: KDISCHOOL/Distance-Learning-Committee-5)
2. 파일들을 커밋 후 푸시:
   git init
   git add .
   git commit -m "Initial DLC operation Flask app"
   git branch -M main
   git remote add origin https://github.com/YOURNAME/YOURREPO.git
   git push -u origin main

PythonAnywhere 배포 (단계별)
1. GitHub에 코드 푸시
2. PythonAnywhere 계정 생성(무료/유료)
3. PythonAnywhere 대시보드 -> Consoles -> Bash 콘솔 열기
4. Git으로 리포지토리 클론
   git clone https://github.com/YOURNAME/YOURREPO.git
5. 가상환경 생성
   mkvirtualenv dlc-venv --python=python3.10
6. 요구사항 설치
   pip install -r YOURREPO/requirements.txt
7. Web 탭으로 이동 -> "Add a new web app" -> Manual configuration -> Flask 선택
8. WSGI 설정: Open the WSGI configuration file과 프로젝트 경로를 추가
   예시 WSGI 변경:
     import sys
     path = '/home/yourusername/YOURREPO'
     if path not in sys.path:
         sys.path.insert(0, path)
     from app import create_app
     application = create_app()
9. Static files 경로 설정(필요시)
10. Reload web app
11. DB: SQLite 사용시 파일이 프로젝트 디렉토리에 생성됩니다. (더 큰 서비스면 MySQL/Postgres 고려)

주의/권장
- ADMIN_PIN 기본값은 0000로 설정해두었으나, 실제 운영시 더 강한 PIN/계정 기반 인증 사용 권장
- PIN은 row별로 해시로 저장합니다. 관리자 PIN은 env var로 관리하세요.
- 개인정보(이메일) 노출 정책을 확인하시고 필요시 로그인/권한 추가
- 운영 환경에선 HTTPS, 백업, 감사로그, 브루트포스 차단(핀 시도 제한) 추가 권장

다음 단계 제안
- WSGI 파일 샘플 (.wsgi) 생성 및 PythonAnywhere용 환경변수 설정 방법을 제가 만들어 드릴게요.
- 프론트엔드(모달/비동기)와 테스트 스크립트(유닛/통합) 추가 원하시면 바로 만들어 드립니다.
```
