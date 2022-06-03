from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from . import data_add # 데이터 베이스 링크
import openpyxl # 엑셀파일 로드

# 신규 머신러닝에 필요한 패키지
import tensorflow as tf
import pickle
from .Intent import intent_predict
from .Ner import ner_predict

# 뉴스 스크레이핑에 필요한 패키지
import requests
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup as bs
import urllib
import urllib.request as ur

# ---------머신 러닝 파트 ------------
print('====================머신러닝 객체 생성 시작====================')

# 의도분류 모델 로딩
intent_model = tf.keras.models.load_model('static/best_model.h5')
print('의도 분류 모델 로딩 완료')

# 의도분류 토크나이저 로딩
with open('static/IntentTokenizer.pickle', 'rb') as handle:
    intent_tokenizer = pickle.load(handle)
print('의도 분류 토크나이저 로딩 완료')

# 개체명 인식 모델 로딩
ner_model = tf.keras.models.load_model('static/best_ner_model.h5')
print('개체명 인식 모델 로딩 완료')

# 개체명 인식 토크나이저 로딩
with open('static/src_tokenizer.pickle', 'rb') as handle:
    src_tokenizer = pickle.load(handle)
with open('static/tar_tokenizer.pickle', 'rb') as handle:
    tar_tokenizer = pickle.load(handle)
print('개체명 인식 토크나이저 로딩 완료')
print('----------머신러닝 객체 생성 완료----------')

# MYSQL과 링크 이용
db = data_add.link_in()
print('MYSQL 링크 완료')

# 답변테이블 부분 로드하기
wb = openpyxl.load_workbook('static/answertable.xlsx')
db_sheet = wb['datatable']

# 데이터베이스 초기화
data_add.reset_data(db)

# 데이터베이스 데이터 삽입
for row in db_sheet.iter_rows(min_row=2):
    data_add.insert_data(db, row)

print('답변 테이블 로드 완료')
print('챗봇이 사용자로부터 메시지 입력받을 준비 완료')
print('=========================================')

# 처음 접속시 메인 페이지 - 주간 동향 기술 포함
def chatbot_main(request):
    week_trend1, week_trend2, week_trend3 = week_trend_clipping()

    return render(
        request,
        'chatbot_app/chatbot_home.html',
        {'week_trend1': week_trend1, 'week_trend2': week_trend2, 'week_trend3': week_trend3}
    )


# 신규 머신러닝에 대한 챗봇 답변
@csrf_exempt
def chatanswer(request):
    context = {}

    print('==============================')
    print('챗봇 답변 준비')
    user_msg = request.GET['chattext']
    print('사용자 메시지: ', user_msg)

    user_msg = user_msg.upper()     # 영단어는 대문자로변경
    user_msg = user_msg.replace('?', '')    # 물음표는 의도분류 때 오류내서 제거

    news = None
    # 의도 분류 시작
    print('의도 분류 진행')
    if intent_predict(user_msg, intent_tokenizer, intent_model, 40):

        print('의도 분류 확인 완료')
        # 개체명 인식
        ner_word = ner_predict(user_msg,ner_model,src_tokenizer,tar_tokenizer,13)
        print('개체명 인식 완료: ', ner_word)

        # 답변 검색
        keyword, answer, answer_url = data_add.search_data(db, ner_word)
        print('답변 테이블에서 검색')

        if keyword == None:
            res1 = ner_word + "에 대한 답변입니다. <br>"
            res2 = "해당 정보를 찾을 수 없습니다.<br>"
            res3 = "다른 궁금하신 IT 정보를 물어보세요."
        else:
            res1 = keyword + "에 대한 답변입니다. <br>"
            res2 = answer
            res3 = answer_url

            # 구글 뉴스 크롤링
            news = gnews_clipping(keyword)

    # 의도가 안 맞는 것
    else:
        res1 = '궁금하신 IT 정보가 있으면 물어보세요'
        res2, res3 = '', ''

    # 챗봇 최종 답변
    context['res1'] = res1
    context['res2'] = res2
    context['res3'] = res3

    # 구글 뉴스 크롤링 결과 추가
    context['news'] = news

    # 웹 뉴스 크롤링 함수 넣기

    print('-----답변 완성하여 전송 시작-----')

    return JsonResponse(context, content_type=u"application/json; charset=utf-8")

# 구글 뉴스 웹 크롤링
def gnews_clipping(keyword):

    news_limit = 5

    base_url = "https://news.google.com"

    # 키워드를 받아서 URL 코드로 변환
    keyword_url = urllib.parse.quote(keyword)

    # 구글 뉴스 검색어 URL변환
    url = base_url + "/search?q=" + keyword_url + "&hl=ko&gl=KR&ceid=KR%3Ako"

    resp = requests.get(url)
    html_src = resp.text
    soup = BeautifulSoup(html_src, 'html.parser')

    news_items = soup.select('div[class="xrnccd"]')

    links = [];     titles = [];     contents = [];     agencies = []; reporting_dates = [];   reporting_times = [];

    if len(news_items) < 5:
        news_limit = len(news_items)

    for item in news_items[:news_limit]:
        link = item.find('a', attrs={'class': 'VDXfz'}).get('href')
        news_link = base_url + link[1:]
        links.append(news_link)

        print(news_link)

        news_title = item.find('a', attrs={'class': 'DY5T1d'}).getText()
        titles.append(news_title)

        print(news_title)

        news_agency = item.find('a', attrs={'class': 'wEwyrc AVN2gc uQIVzc Sksgp'}).text
        agencies.append(news_agency)

        news_reporting = item.find('time', attrs={'class': 'WW6dff uQIVzc Sksgp'})

        if news_reporting is not None:
            news_reporting_datetime = news_reporting.get('datetime').split('T')
            news_reporting_date = news_reporting_datetime[0]
        else:
            news_reporting_date = ''

        reporting_dates.append(news_reporting_date)


    result = {'link': links, 'title': titles, 'agency': agencies, 'date': reporting_dates}
    print(result['title'])
    print(result['agency'])
    print(result['date'])
    print(result['link'])

    return result

# 주간 동향 크롤링
def week_trend_clipping():

    weak_trend1 = []
    weak_trend2 = []
    weak_trend3 = []
    # 주간동향 첫번째 url
    trend_url1 = 'https://www.itfind.or.kr/publication/regular/weeklytrend/weekly/list.do'
    soup = bs(ur.urlopen(trend_url1).read(), 'html.parser')

    weak_trend1_title = soup.find('h3', {"class": "icon1"})
    weak_trend1_title = weak_trend1_title.text.replace('\r', '').replace('\n', '').replace('\xa0', '').replace('원문보기',
                                                                                                               '').lstrip().rstrip()
    weak_trend1_title = weak_trend1_title.replace('00:00:00.0', '')
    weak_trend1.append(weak_trend1_title)
    print(weak_trend1_title)

    # 주간 동향 소제목들 출력
    for i in soup.find_all('div', {"class": "periodical"}):
        for j in i.find_all('h4'):
            sub_title = j.text.replace('\r', '').replace('\n', '').lstrip().rstrip()
            weak_trend1.append(sub_title)
            print(sub_title)

    weak_trend1.append(trend_url1)

    # 주간 동향 두번째 url
    trend_url2 = 'https://www.itfind.or.kr/publication/regular/weeklytrend/weekly/list.do?selectedId=1196'
    soup = bs(ur.urlopen(trend_url2).read(), 'html.parser')

    weak_trend2_title = soup.find('h3', {"class": "icon1"})
    weak_trend2_title = weak_trend2_title.text.replace('\r', '').replace('\n', '').replace('\xa0', '').replace('원문보기',
                                                                                                               '').lstrip().rstrip()
    weak_trend2_title = weak_trend2_title.replace('00:00:00.0', '')
    weak_trend2.append(weak_trend2_title)
    print(weak_trend2_title)

    # 주간 동향 두번째 소제목들 출력
    for i in soup.find_all('div', {"class": "periodical"}):
        for j in i.find_all('h4'):
            sub_title = j.text.replace('\r', '').replace('\n', '').lstrip().rstrip()
            weak_trend2.append(sub_title)
            print(sub_title)

    weak_trend2.append(trend_url2)

    # 주간동향 세번째 url
    trend_url3 = 'https://www.itfind.or.kr/publication/regular/weeklytrend/weekly/list.do?selectedId=1195'
    soup = bs(ur.urlopen(trend_url3).read(), 'html.parser')

    weak_trend3_title = soup.find('h3', {"class": "icon1"})
    weak_trend3_title = weak_trend3_title.text.replace('\r', '').replace('\n', '').replace('\xa0', '').replace('원문보기',
                                                                                                               '').lstrip().rstrip()
    weak_trend3_title = weak_trend3_title.replace('00:00:00.0 ', '')
    weak_trend3.append(weak_trend3_title)
    print(weak_trend3_title)

    # 주간 동향 세번째 소제목들 출력
    for i in soup.find_all('div', {"class": "periodical"}):
        for j in i.find_all('h4'):
            sub_title = j.text.replace('\r', '').replace('\n', '').lstrip().rstrip()
            weak_trend3.append(sub_title)
            print(sub_title)

    weak_trend3.append(trend_url3)

    return weak_trend1, weak_trend2, weak_trend3
