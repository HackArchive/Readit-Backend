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
            fresult.append(i[1].lower())

    def clean_list():
        fresult2=[]
        temp = []
        
        temp = " ".join(fresult).split('chapter')
        for i in temp:
            fresult2.append("chapter"+i)
  
        fresult2.pop(0)
            
        return fresult2

    formatted_data = clean_list()
    for i in formatted_data:
        result.append(i[0:40])

    for i in result:
        print(i)
        print("\n")
    return result
