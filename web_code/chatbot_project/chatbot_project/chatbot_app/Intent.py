from konlpy.tag import Mecab
from .Reform import *
from tensorflow.keras.preprocessing.sequence import pad_sequences

def intent_predict(new_sentence,tokenizer,model,max_len):
    print('----------의도 분류 함수 실행----------')
    m = Mecab()
    print('mecab 생성 완료')

    stopwords = ['을','를','이','가','은','는','의']   #불용어 지정
    print('불용어 지정')

    new_sentence = m.morphs(new_sentence)
    print('형태소 분리:', new_sentence)

    new_sentence = [word for word in new_sentence if not word in stopwords]
    print('불용어 제거 완료')

    encoded = tokenizer.texts_to_sequences([new_sentence])
    print('정수 인코딩:', encoded)

    pad_new = pad_sequences(encoded, maxlen = max_len)
    print('패딩: ', pad_new)

    score = float(model(pad_new))
    print('스코어 예측:', score)

    if score > 0.5:
        print('질문 확인')
        print('-' * 10)
        return 1    #질문
    else:
        print('일반 문장 확인')
        print('-'*10)
        return 0    #일반문장


