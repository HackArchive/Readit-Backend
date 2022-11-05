import easyocr
import re

def read_data(filepath):
    reader = easyocr.Reader(['en'])
    raw_data = reader.readtext(filepath)
    fresult = []
    result = []
    for i in raw_data:
        try:
            int(i[1])
        except:
            # print(i[1])
            fresult.append(i[1].lower())

    def clean_list():
        fresult2=[]
        temp = []
        # for i in fresult:
            # chap_keyword = i.split(' ')
            # if chap_keyword[0] != 'chapter':
            #     temp.append(i)
            # else:
            #     fresult2.append(" ".join(temp))
            #     temp.clear()
        # fresult_temp = " ".join(fresult)
        # if re.search(r'chapter',fresult_temp):
        temp = " ".join(fresult).split('chapter')
        for i in temp:
            # print(i)
            fresult2.append("chapter"+i)
        # else:
        #     fresult2 = fresult
        fresult2.pop(0)
            
        return fresult2

    # for i in fresult:
    #     chap_keyword = i.split(' ')
    #     if chap_keyword[0] == 'chapter':
    # result = clean_list()
            # break
        # else: 
            # continue
    formatted_data = clean_list()
    for i in formatted_data:
        result.append(i[0:40])

    for i in result:
        print(i)
        print("\n")
    return result
read_data("demo2.jpg")