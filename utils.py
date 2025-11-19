import io
from datetime import datetime, timezone
import pandas as pd
from rapidfuzz import process, fuzz
from models import Faculty
from werkzeug.datastructures import FileStorage

# 정규화 헬퍼
def normalize_name(s: str) -> str:
    if not s:
        return ""
    s = str(s).strip()
    s = " ".join(s.split())  # 연속 공백 정리
    return s

# 엑셀 업로드(faculty) -> 내부 DB랑 완전 일치 매칭 후 채우기. 반환: BytesIO(엑셀)
def enrich_faculty_excel(file_storage: FileStorage, db_session) -> io.BytesIO:
    df = pd.read_excel(file_storage, engine="openpyxl")
    # 기대 컬럼: Korean_name (대소문자/스페이스 normalize 필요)
    if "Korean_name" not in df.columns and "korean_name" not in df.columns:
        # 시도: 첫번째 열을 Korean_name으로 간주
        df.columns = [c if i != 0 else "Korean_name" for i, c in enumerate(df.columns)]
    # ensure column
    df.rename(columns={col: ("Korean_name" if col.lower()=="korean_name" else col) for col in df.columns}, inplace=True)
    # 준비된 결과 컬럼
    out_cols = ["No", "Korean_name", "English_name", "Category", "Email"]
    out_rows = []
    faculties = {normalize_name(f.korean_name): f for f in db_session.query(Faculty).all()}
    for idx, row in df.iterrows():
        kname = normalize_name(row.get("Korean_name", ""))
        if not kname:
            english = ""
            category = ""
            email = ""
        else:
            f = faculties.get(kname)
            if f:
                english = f.english_name or ""
                category = f.category or ""
                email = f.email or ""
            else:
                english = ""
                category = ""
                email = ""
        out_rows.append({
            "No": idx+1,
            "Korean_name": kname,
            "English_name": english,
