# 가상환경 활성화된 상태에서
pip list | grep -E "Flask|SQLAlchemy|rapidfuzz|pandas"
Flask            2.2.5
Flask-SQLAlchemy 3.0.4
pandas           2.1.1
SQLAlchemy       1.4.54
(venv) 11:58 ~/Distance-Learning-Committee-5 (main)$ "
Flask            2.2.5
Flask-SQLAlchemy 3.0.4
pandas           2.1.1
SQLAlchemy       1.4.54
(venv) 11:58 ~/Distance-Learning-Committee-5 (main)$ 
> 
> # 프로젝트 루트에서 (venv 활성화된 상태)
python -c "from app import create_app; app=create_app(); from models import db; with app.app_context(): db.create_all(); print('DB created')"
bash: syntax error near unexpected token `('
(venv) 12:00 ~/Distance-Learning-Committee-5 (main)$ python -c 'from app import create_app; app=create_app(); from models import db; with app.app_context(): db.create_all(); print("DB created")'
  File "<string>", line 1
    from app import create_app; app=create_app(); from models import db; with app.app_context(): db.create_all(); print("DB created")
                                                                         ^^^^
SyntaxError: invalid syntax
(venv) 12:02 ~/Distance-Learning-Committee-5 (main)$ 
(venv) 12:02 ~/Distance-Learning-Committee-5 (main)$ cat > create_db.py <<'PY'
from app import create_app
app = create_app()
from models import db
with app.app_context():
    db.create_all()
print("DB created")
PY
python create_db.py
# 필요하면 삭제
rm create_db.py
Traceback (most recent call last):
  File "/home/Learninginnovation/Distance-Learning-Committee-5/create_db.py", line 1, in <module>
    from app import create_app
  File "/home/Learninginnovation/Distance-Learning-Committee-5/app.py", line 4, in <module>
    from utils import enrich_faculty_excel, normalize_name, fuzzy_search_name, format_modified_date, import_course_excel
  File "/home/Learninginnovation/Distance-Learning-Committee-5/utils.py", line 45
    out_rows.append({
                    ^
SyntaxError: '{' was never closed
(venv) 12:02 ~/Distance-Learning-Committee-5 (main)$ 
(venv) 12:03 ~/Distance-Learning-Committee-5 (main)$ pwd
ls -la
/home/Learninginnovation/Distance-Learning-Committee-5
total 68
drwxrwxr-x 7 Learninginnovation registered_users  4096 Nov 19 12:02 .
drwxrwxr-x 7 Learninginnovation registered_users  4096 Nov 19 11:35 ..
drwxrwxr-x 8 Learninginnovation registered_users  4096 Nov 19 11:35 .git
-rw-rw-r-- 1 Learninginnovation registered_users   154 Nov 19 11:35 .gitignore
-rw-rw-r-- 1 Learninginnovation registered_users  2981 Nov 19 11:35 README.md
drwxrwxr-x 2 Learninginnovation registered_users  4096 Nov 19 12:02 __pycache__
-rw-rw-r-- 1 Learninginnovation registered_users 11502 Nov 19 11:35 app.py
-rw-rw-r-- 1 Learninginnovation registered_users   504 Nov 19 11:35 config.py
-rw-rw-r-- 1 Learninginnovation registered_users  2229 Nov 19 11:35 models.py
-rw-rw-r-- 1 Learninginnovation registered_users   158 Nov 19 11:51 requirements.txt
-rw-rw-r-- 1 Learninginnovation registered_users   105 Nov 19 11:35 run.sh
drwxrwxr-x 3 Learninginnovation registered_users  4096 Nov 19 11:35 static
drwxrwxr-x 2 Learninginnovation registered_users  4096 Nov 19 11:35 templates
-rw-rw-r-- 1 Learninginnovation registered_users  1867 Nov 19 11:35 utils.py
drwxrwxr-x 5 Learninginnovation registered_users  4096 Nov 19 11:47 venv
(venv) 12:03 ~/Distance-Learning-Committee-5 (main)$ 
(venv) 12:03 ~/Distance-Learning-Committee-5 (main)$ which python
echo $VIRTUAL_ENV
python -V
/home/Learninginnovation/Distance-Learning-Committee-5/venv/bin/python
/home/Learninginnovation/Distance-Learning-Committee-5/venv
Python 3.10.12
(venv) 12:03 ~/Distance-Learning-Committee-5 (main)$ 
