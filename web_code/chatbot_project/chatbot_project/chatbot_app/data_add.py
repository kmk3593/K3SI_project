import pymysql
import openpyxl
from . import DatabaseConfig as dbconfig

def link_in():
    db = pymysql.connect(
        host= dbconfig.DB_HOST,
        user= dbconfig.DB_USER,
        passwd= dbconfig.DB_PASSWORD,
        db= dbconfig.DB_NAME,
        charset='utf8'
    )
    return db

def link_out(db):
    if db is not None:
        db.close()

def data_add(db,sheet):
    reset_data(db)
    for row in sheet.iter_rows(min_row=2):
        insert_data(db,row)

def insert_data(db, xls_row): #데이터 추가 코드
    print(xls_row)
    id, keyword, answer, answer_url, search = xls_row

    if id is None:
        return
    sql = '''
        INSERT answertable(id, keyword, answer, answer_url, search) values(%d, '%s', '%s', '%s', '%s')
    ''' % (id.value, keyword.value, answer.value, answer_url.value, search.value)

    sql = sql.replace("'None'", "Null")

    with db.cursor() as cursor:
        cursor.execute(sql)
        db.commit()

def reset_data(db): # 초기화 코드(reset_data-> insert_data 순으로 작동
    sql ='''
        truncate `answertable`
    '''
    with db.cursor() as cursor:
        cursor.execute(sql)


def search_data(db, word): #데이터 찾고 출력 함수
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        sql='''
            select * from answertable where search = "%s"
        ''' % word
        cursor.execute(sql)
        data = cursor.fetchone()
        if data == None:
            return None, None, None
        else:
            result = data
            return result['keyword'], result['answer'], result['answer_url'] # 키워드와 답변 표현
