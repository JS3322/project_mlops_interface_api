from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select
from sqlalchemy.orm import sessionmaker
import html

app = FastAPI()

# 데이터베이스 설정 (실제 값으로 변경하세요)
DATABASE_URL = "postgresql+psycopg2://username:password@localhost:5432/mydatabase"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 테이블 정의
metadata = MetaData()
users_table = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('email', String),
)

@app.get("/", response_class=HTMLResponse)
def read_users():
    with SessionLocal() as session:
        stmt = select(users_table)
        result = session.execute(stmt)
        users = result.fetchall()

    # HTML 파일 읽기
    with open("templates/users.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    # 테이블 행 생성
    table_rows = ""
    for user in users:
        user_id = html.escape(str(user.id))
        user_name = html.escape(user.name)
        user_email = html.escape(user.email)
        table_rows += f"<tr><td>{user_id}</td><td>{user_name}</td><td>{user_email}</td></tr>"

    # HTML 콘텐츠에 테이블 행 삽입
    html_content = html_content.replace("{{ table_rows }}", table_rows)

    return HTMLResponse(content=html_content)




# <!DOCTYPE html>
# <html>
# <head>
#     <title>사용자 목록</title>
# </head>
# <body>
# <h1>사용자 목록</h1>
# <table border="1">
#     <tr>
#         <th>ID</th><th>이름</th><th>이메일</th>
#     </tr>
#     {{ table_rows }}
# </table>
# </body>
# </html>
