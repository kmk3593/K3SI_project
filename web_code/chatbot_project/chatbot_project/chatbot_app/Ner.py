from konlpy.tag import Mecab
from .Reform import *
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np

#새로운 문장에 대해 개체명을 예측하는 함수
def ner_predict(sentence,ner_model,src_tokenizer,tar_tokenizer,max_len):
    print('---------개체명 인식 함수 실행----------')
    m = Mecab()
    print('MEcab 생성 완료')

    word_to_index = src_tokenizer.word_index
    index_to_word = src_tokenizer.index_word
    ner_to_index = tar_tokenizer.word_index
    index_to_ner = tar_tokenizer.index_word
    index_to_ner[0] = 'PAD'

    new_sentence = m.morphs(sentence)
    print('형태소 분리:', new_sentence)

    stopwords = ['을', '를', '이', '가', '은', '는', '의']  # 불용어 지정
    new_sentence = [word for word in new_sentence if not word in stopwords]
    print('불용어제거:', new_sentence)

    new_encoded = []
    for w in new_sentence:
        try:
            new_encoded.append(word_to_index.get(w, 1))
        except KeyError:
            new_encoded.append(word_to_index['OOV'])

    print('정수 인코딩 결과:', new_encoded)

    new_padded = pad_sequences([new_encoded], padding="post", value=0, maxlen=max_len)
    print('패딩: ', new_padded)

    p = ner_model(np.array([new_padded[0]]))
    print('개체명 예측 완료')
    p = np.argmax(p, axis=-1)
    print("{:15}||{}".format("단어", "예측값"))
    print(30 * "-")
    w_list = []
    t_list = ()
    v_list = []
    for w, pred in zip(new_sentence, p[0]):
        print("{:15}: {:5}".format(w, index_to_ner[pred]))
        t_list = (w, index_to_ner[pred])
        v_list.append(t_list)
    print(v_list)
    print('-' * 30 + '\n')
    print('형태소 개체명 예측 완료')

    i = 0
    while i < len(v_list):
        if v_list[i][1]=="B_DATA" or v_list[i][1] == "I_DATA":
            w_list.append(v_list[i][0])
        i = i+1
    w_list = "".join(w_list)
    print('키워드 생성완료:', w_list)
    print('-----------개체명 인식 함수 반환---------')
    return w_list

