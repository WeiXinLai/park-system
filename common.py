from datetime import datetime
import random


def create_service_id():
    nowTime = datetime.now().strftime('%Y%m%d%H%M%S')
    randomNum = random.randint(0,999)
    if randomNum < 10:
        randomNum = str(00)+str(randomNum)
    elif randomNum >=10 and randomNum <= 99:
        randomNum = str(0)+str(randomNum)
    uniqueNum = str(nowTime)+str(randomNum)
    return uniqueNum 

if __name__ == '__main__':
    for i in range(10):
        print create_service_id()

