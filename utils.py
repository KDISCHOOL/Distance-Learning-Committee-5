(venv) 12:03 ~/Distance-Learning-Committee-5 (main)$ cat > utils.py <<'PY'
(위에 있는 전체 utils.py 내용 붙여넣기)
PY
(venv) 12:06 ~/Distance-Learning-Committee-5 (main)$ python -m py_compile utils.py
# 에러가 없으면 아무 출력도 없이 종료(0)
  File "utils.py", line 1
    (위에 있는 전체 utils.py 내용 붙여넣기)
     ^^^^^^^^^^^^^
SyntaxError: invalid syntax. Perhaps you forgot a comma?
(venv) 12:06 ~/Distance-Learning-Committee-5 (main)$ cat > utils.py <<'PY'
(venv) 12:06 ~/Distance-Learning-Committee-5 (main)$ cat > utils.py <<'PY'
import iotime import datetime, timezone
from datetime import datetime, timezone
import pandas as pdrt process, fuzz
from rapidfuzz import process, fuzz
from models import Facultyes import FileStorage
from werkzeug.datastructures import FileStorage
# 정규화 헬퍼
# 정규화 헬퍼_name(s: str) -> str:
def normalize_name(s: str) -> str:
    if not s:n ""
        return ""rip()
    s = str(s).strip()it())  # 연속 공백 정리
    s = " ".join(s.split())  # 연속 공백 정리
    return s
# 엑셀 업로드(faculty) -> 내부 DB랑 완전 일치 매칭 후 채우기. 반환: BytesIO(엑셀)
# 엑셀 업로드(faculty) -> 내부 DB랑 완전 일치 매칭 후 채우기. 반환: BytesIO(엑셀)
def enrich_faculty_excel(file_storage: FileStorage, db_session) -> io.BytesIO:
    df = pd.read_excel(file_storage, engine="openpyxl")ze 필요)
    # 기대 컬럼: Korean_name (대소문자/스페이스 normalize 필요) df.columns:
    if "Korean_name" not in df.columns and "korean_name" not in df.columns:
        # 시도: 첫번째 열을 Korean_name으로 간주ame" for i, c in enumerate(df.columns)]
        df.columns = [c if i != 0 else "Korean_name" for i, c in enumerate(df.columns)]
    # ensure columnns={col: ("Korean_name" if col.lower()=="korean_name" else col) for col in df.columns}, inplace=True)
    df.rename(columns={col: ("Korean_name" if col.lower()=="korean_name" else col) for col in df.columns}, inplace=True)
    # 준비된 결과 컬럼"Korean_name", "English_name", "Category", "Email"]
    out_cols = ["No", "Korean_name", "English_name", "Category", "Email"]
    out_rows = []normalize_name(f.korean_name): f for f in db_session.query(Faculty).all()}
    faculties = {normalize_name(f.korean_name): f for f in db_session.query(Faculty).all()}
    for idx, row in df.iterrows():.get("Korean_name", ""))
        kname = normalize_name(row.get("Korean_name", ""))
        if not kname: ""
            english = """
            category = ""
            email = ""
        else: = faculties.get(kname)
            f = faculties.get(kname)
            if f:nglish = f.english_name or ""
                english = f.english_name or ""
                category = f.category or ""
                email = f.email or ""
            else:nglish = ""
                english = """
                category = ""
                email = ""
        out_rows.append({
            "No": idx+1,": kname,
            "Korean_name": kname,sh,
            "English_name": english,
            "Category": category,
            "Email": email
        }) = pd.DataFrame(out_rows, columns=out_cols)
    out_df = pd.DataFrame(out_rows, columns=out_cols)
    bio = io.BytesIO()o, index=False, engine="openpyxl")
    out_df.to_excel(bio, index=False, engine="openpyxl")
    bio.seek(0)
    return bio
# 퍼지 검색 후보(rapidfuzz 사용)
# 퍼지 검색 후보(rapidfuzz 사용), candidates: list, limit: int = 10):
def fuzzy_search_name(query: str, candidates: list, limit: int = 10):
    # candidates: list of strings
    if not query:
        return []cess.extract(query, candidates, scorer=fuzz.WRatio, limit=limit)
    results = process.extract(query, candidates, scorer=fuzz.WRatio, limit=limit)
    # results: list of tuples (candidate, score, index)
    return results
# Modified Date formatting (UI용)
# Modified Date formatting (UI용)
def format_modified_date(dt):
    if not dt: ""
        return ""lized string like "2025-07-15 10:29:16 AM"
    # Return localized string like "2025-07-15 10:29:16 AM"eded. We'll format in server local time for display.
    # Here we assume dt is UTC; front-end can convert if needed. We'll format in server local time for display.
    local = dt.astimezone() if dt.tzinfo else dt)
    return local.strftime("%Y-%m-%d %I:%M:%S %p")
# Helper to parse course excel and merge into DB by Korean name
# Helper to parse course excel and merge into DB by Korean namey):
def import_course_excel(file_storage, db_session, CourseModality):
    df = pd.read_excel(file_storage, engine="openpyxl")
    # expected columns include Korean_name or Name
    name_col = Noneumns:
    for c in df.columns:("korean_name", "name
        if c.lower() in ("korean_name", "name
> 
> 
