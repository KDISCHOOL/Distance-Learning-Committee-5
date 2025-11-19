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
            "Category": category,
            "Email": email
        })
    out_df = pd.DataFrame(out_rows, columns=out_cols)
    bio = io.BytesIO()
    out_df.to_excel(bio, index=False, engine="openpyxl")
    bio.seek(0)
    return bio

# 퍼지 검색 후보(rapidfuzz 사용)
def fuzzy_search_name(query: str, candidates: list, limit: int = 10):
    # candidates: list of strings
    if not query:
        return []
    results = process.extract(query, candidates, scorer=fuzz.WRatio, limit=limit)
    # results: list of tuples (candidate, score, index)
    return results

# Modified Date formatting (UI용)
def format_modified_date(dt):
    if not dt:
        return ""
    # Return localized string like "2025-07-15 10:29:16 AM"
    # Here we assume dt is UTC; front-end can convert if needed. We'll format in server local time for display.
    local = dt.astimezone() if dt.tzinfo else dt
    return local.strftime("%Y-%m-%d %I:%M:%S %p")

# Helper to parse course excel and merge into DB by Korean name
def import_course_excel(file_storage, db_session, CourseModality):
    df = pd.read_excel(file_storage, engine="openpyxl")
    # expected columns include Korean_name or Name
    name_col = None
    for c in df.columns:
        if c.lower() in ("Korean_name", "English_name"):
            name_col = c
            break
    if not name_col:
        # try first column
        name_col = df.columns[0]
    # For each row, normalize name, find existing by exact match on name, update or insert
    updated = 0
    inserted = 0
    for _, row in df.iterrows():
        raw_name = normalize_name(row.get(name_col, ""))
        if not raw_name:
            continue
        existing = db_session.query(CourseModality).filter_by(name=raw_name).first()
        if existing:
            # update known columns if present
            existing.year = int(row.get("Year")) if pd.notna(row.get("Year")) else existing.year
            existing.semester = row.get("Semester") or existing.semester
            existing.language = row.get("Language") or existing.language
            existing.course_title = row.get("Course Title") or existing.course_title
            existing.time_slot = row.get("Time Slot") or existing.time_slot
            existing.day = row.get("Day") or existing.day
            existing.time = row.get("Time") or existing.time
            existing.frequency_week = row.get("Frequency(Week)") or existing.frequency_week
            existing.course_format = row.get("Course format") or existing.course_format
            # password column might exist in excel
            pw = row.get("password")
            if pd.notna(pw):
                existing.set_pin(str(pw))
            db_session.add(existing)
            updated += 1
        else:
            cm = CourseModality(
                name=raw_name,
                year=int(row.get("Year")) if pd.notna(row.get("Year")) else None,
                semester=row.get("Semester"),
                language=row.get("Language"),
                course_title=row.get("Course Title"),
                time_slot=row.get("Time Slot"),
                day=row.get("Day"),
                time=row.get("Time"),
                frequency_week=row.get("Frequency(Week)"),
                course_format=row.get("Course format")
            )
            pw = row.get("password")
            if pd.notna(pw):
                cm.set_pin(str(pw))
            db_session.add(cm)
            inserted += 1
    db_session.commit()
    return {"updated": updated, "inserted": inserted}
