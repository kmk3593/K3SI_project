#mecab의 parse함수는 str형식의 형태소 분석 결과를 내놓습니다.
#따라서 이것을 pos형태로 변환시켜줄 필요가 있습니다.
#첫 번째 형태소를 저장하고, 탭을 읽고, 품사를 저장합니다.
#그 후 개행문자까지 읽고
#다시 첫 번째 형태소, 탭 무시, 품사, 개행까지 읽고
#이것을 연속된 EOS를 읽을 때까지 반복합니다.

#while을 EOS만날 때가지 반복실행합니다.
#'E'인지 확인합니다.
# 다음 형태소를 읽고 'O'인지 확인합니다.
# 'EO가 나오면 마지막 종결 변수를 써서 S인지 확인합니다.
#이 세 조건을 만족하면 함수를 종료시킵니다.
def reform_to_pos(a):       #parse형태의 분석결과를 [(word,pos),(word1,pos1)] 형태로 바꿔주는 함수
    pos_list=[]             #(형태소,품사)의 리스트
    word=[]                 #형태소를 담는 변수
    pos=[]                  #품사를 담는 변수
    i=0                     #인덱스
    while True:
        e = a[i]
        n = a[i+1]
        d = a[i+2]
        if e=='E' and n=='O' and d=='S':        #EOS에 도달하면 작업을 멈춥니다.
            break
        while a[i] != '\t':                       #형태소만 추출
            word.append(a[i])                   #원소를 리스트에 추가
            i = i+1
        w = ''.join(word)                       #리스트에 추가된 원소들을 병합 후 w에 저장
        word=[]                                 #word리스트 초기화
        i=i+1                                   #인덱스 증가
        while a[i]!=',':                        #품사정보를 다 읽을 때까지
            pos.append(a[i])                    #현재 원소를 pos리스트에 추가
            i=i+1                               #인덱스 증가
        p = ''.join(pos)                        #pos에 있는 원소 병합하여 p에 저장
        pos=[]                                  #pos 리스트 초기화
        i=i+1                                   #인덱스 증가
        pos_list.append((w,p))                  #w와 p를 튜플로 만들어 pos_list에 추가
        while a[i]!='\n':                       #마지막 원소까지 인덱스 증가
            i=i+1
        i=i+1                                   #다음 줄의 인덱스로 이동
    return pos_list

def morphs(a):
    word_list = []
    word = []
    i = 0

    while True:
        e = a[i]
        n = a[i + 1]
        d = a[i + 2]
        if e == 'E' and n == 'O' and d == 'S':  # EOS에 도달하면 작업을 멈춥니다.
            break

        while a[i] != '\t':  # 형태소만 추출
            word.append(a[i])  # 원소를 리스트에 추가
            i = i+1
        w = ''.join(word)  # 리스트에 추가된 원소들을 병합 후 w에 저장
        word = []  # word리스트 초기화
        word_list.append(w)
        while a[i] != '\n':                       #마지막 원소까지 인덱스 증가
            i = i+1
        i = i+1
    return word_list





