#-*- coding:utf-8 -*-
from datetime import datetime
import time

input1 = {"createTime": "2018-02-19 22:29:01", "serviceData": [{"serviceData": {"batteryLevel": 99},"serviceId": "Battery"}, {"serviceData": {"signalStrength": 79}, "serviceId": "Meter"}, {"serviceData": {"Entrancesonser": "01000000000d010100020400036c9003020001"},"serviceId": "Datamessage"}], "lastMessageTime": "2018-03-01 21:55:08", "devSerial": "863703031721561"}
#ignoreInput = {'devSerial': '863703031721561', 'serviceData': [{'serviceData': {'batteryLevel': 99}, 'serviceId': 'Battery'}, {'serviceData': {'signalStrength': 79}, 'serviceId': 'Meter'}, {'serviceData': {'Entrancesonser': '0100000000040402ffff'}, 'serviceId': 'Datamessage'}], 'lastMessageTime': '2018-03-10 17:18:05', 'createTime': '2018-02-19 22:29:01'}

#input2 = {"createTime": "2018-02-19 22:29:01","serviceData": [{"serviceData": {"batteryLevel": 99},"serviceId": "Battery"},{"serviceData": {"signalStrength": 79}, "serviceId": "Meter"}, {"serviceData": {"Entrancesonser": "02010000000d01010102041111111103020001"}, "serviceId": "Datamessage"}], "lastMessageTime": "2018-03-01 21:55:08", "devSerial": "863703031721561"}

#lastMessageTime = input['lastMessageTime']
#devSerial = input['devSerial']
#print lastMessageTime, devSerial

def get_data_field(input, data_field):
    serviceData_lst = input['serviceData']
    for serviceData_dict in serviceData_lst:
        for k in serviceData_dict['serviceData']:
            if k == data_field:
                mydata = {k:serviceData_dict['serviceData'][k]}
                return mydata

def max_2_power_num(num):
    result = num&(num-1)
    if result == 0:
        return num
    else:
        count=0
        while(num):
            num /= 2
            count = count+1
        return 2**count

class nb_protocol:
    def __init__(self, data):
        self.data = data
        self.protocol_decode()
        self.data_flag = True
    def protocol_decode(self):
        Entrancesonser = self.data['Entrancesonser']
        self.protocol_num = Entrancesonser[:2]
        self.device_type = Entrancesonser[2:4]
        data_len = Entrancesonser[4:12]
        self.data_len = int( Entrancesonser[4:12],16)*2 #将字符串表示的十六进制转换成十进制,乘以2后转换成字节单位
        self.protocol_content = Entrancesonser[12:12+self.data_len]
        return {'protocol_num':self.protocol_num, 'device_type':self.device_type, 'data_len':self.data_len,'protocol_content':self.protocol_content}
    def content_decode(self):
        if self.protocol_content[:2]=='04':
            self.data_flag = False
        if self.data_flag and (self.protocol_num == '01' and self.device_type == '00')or(self.protocol_num == '02' and self.device_type =='01'):
            len1 = int(self.protocol_content[2:4],16)*2
            if self.protocol_content[4:4+len1]=='00':
                self.inout_flag = 'in'
            elif self.protocol_content[4:4+len1]=='01':
                self.inout_flag = 'out'
            len2 = int(self.protocol_content[6+len1:8+len1],16)*2
            self.unique_num = self.protocol_content[8+len1:8+len1+len2]
            len3 = int(self.protocol_content[10+len1+len2:12+len1+len2],16)*2
            self.lot_id = self.protocol_content[12+len1+len2:12+len1+len2+len3]
            return {'inout_flag':self.inout_flag, 'unique_num':self.unique_num,'lot_id':int(self.lot_id,16) }

    def content_encode(self, content_dict):
        if self.inout_flag == 'in':
            permit = content_dict['permit']
            park_num = int(content_dict['park_num'])
            balance = int(content_dict['balance'])
            user_type = content_dict['user_type']
            date_end = content_dict['date_end']
            if permit:
                permit_str = '01'+'01'+'01'
            else:
                permit_str = '01'+'01'+'00'
            print("permit:"+permit_str)
            if park_num is not None:
                park_num_type = '02'
                park_num_len = len(hex(park_num)[2:])
                park_num_len = max_2_power_num(park_num_len)
                if park_num_len == 1:
                    park_num_val = hex(park_num)[2:].zfill(2)
                else:
                    park_num_val = hex(park_num)[2:].zfill(park_num_len)
                if park_num_len == 1:
                    park_num_len = str(park_num_len).zfill(2)
                else:
                    park_num_len = str(park_num_len/2).zfill(2)
                park_num_str = park_num_type+park_num_len+park_num_val
            else:
                park_num_str = '02'+'00'
            print("park_num:"+park_num_str)
            balance_type = '03'
            balance_len = len(hex(balance)[2:])
            balance_len = max_2_power_num(balance_len)
            if balance_len == 1:
                balance_val = hex(balance)[2:].zfill(2)
            else:
                balance_val = hex(balance)[2:].zfill(balance_len)
            if balance_len == 1:
                balance_len = str(balance_len).zfill(2)
            else:
                balance_len = str(balance_len/2).zfill(2)
            balance_str = balance_type + balance_len + balance_val
            print("balance:"+balance_str)
            if user_type == 'day':
                user_type_str = '04'+'01'+'00'
            elif user_type == 'month':
                user_type_str = '04'+'01'+'01'
            else:
                user_type_str = '04'+'01'+'02'
            print("user_type:"+user_type_str)

            if date_end is not None:
                date_end_type = '05'
                date_end_stamp = int(time.mktime(date_end.timetuple()))
                date_end_len =len(hex(date_end_stamp)[2:])
                date_end_len = max_2_power_num(date_end_len)
                if date_end_len == 1:
                    date_end_val = hex(date_end_stamp)[2:].zfill(2)
                else:
                    date_end_val = hex(date_end_stamp)[2:].zfill(date_end_len)
                if date_end_len == 1:
                    date_end_len = str(date_end_len).zfill(2)
                else:
                    date_end_len = str(date_end_len/2).zfill(2)
                date_end_str = date_end_type+date_end_len+date_end_val
            print("date_end:"+date_end_str)
            self.content_str = permit_str+park_num_str+balance_str+user_type_str+date_end_str
            return self.content_str
        elif self.inout_flag == 'out':
            permit = content_dict['permit']
            user_type = content_dict['user_type']
            balance = int(content_dict['balance'])
            park_fee = content_dict['park_fee'] 
            if permit == True:
                permit_str = '01'+'01'+'01'
            else:
                permit_str = '01'+'01'+'00'
            print("permit:"+permit_str)
            if user_type == 'day':
                user_type_str = '02'+'01'+'00'
            elif user_type == 'month':
                user_type_str = '02'+'01'+'01'
            else:
                user_type_str = '02'+'01'+'02'
            print("user_type:"+user_type_str)
            balance_type = '03'
            balance_len = len(hex(balance)[2:])
            balance_len = max_2_power_num(balance_len)
            if balance_len == 1:
                balance_val = hex(balance)[2:].zfill(2)
            else:
                balance_val = hex(balance)[2:].zfill(balance_len)
            if balance_len == 1:
                balance_len = str(balance_len).zfill(2)
            else:
                balance_len = str(balance_len/2).zfill(2)
            balance_str = balance_type + balance_len + balance_val
            print("balance:"+balance_str)
     
            if park_fee is not None:
                park_fee_type = '04'
                park_fee_len = len(hex(park_fee)[2:])
                park_fee_len = max_2_power_num(park_fee_len)
                if park_fee_len == 1:
                    park_fee_val = hex(park_fee)[2:].zfill(2)
                else:
                    park_fee_val = hex(park_fee)[2:].zfill(park_fee_len)
                if park_fee_len == 1:
                    park_fee_len = str(park_fee_len).zfill(2)
                else:
                    park_fee_len = str(park_fee_len/2).zfill(2)
                park_fee_str = park_fee_type+park_fee_len+park_fee_val
            else:
                park_fee_str = '04'+'01'+'00'
            print("park_fee:"+park_fee_str)
            self.content_str = permit_str+user_type_str+balance_str+park_fee_str
            return self.content_str
                
    def protocol_encode(self):
        if self.inout_flag == 'in':
            down_protocol_num = '01'
            down_protocol_len = len(self.content_str)/2
            down_protocol_len = hex(down_protocol_len)[2:].zfill(8)
            down_protocol_content = self.content_str
            down_protocol = down_protocol_num+down_protocol_len+down_protocol_content
            return down_protocol

        elif self.inout_flag == 'out':
            down_protocol_num = '02'
            down_protocol_len = len(self.content_str)/2
            down_protocol_len = hex(down_protocol_len)[2:].zfill(8)
            down_protocol_content = self.content_str
            down_protocol = down_protocol_num + down_protocol_len + down_protocol_content
            return down_protocol

#mydata1 = get_data_field(input1, 'Entrancesonser')
#n1 = nb_protocol(mydata1)
#print n1.protocol_decode()
#print n1.content_decode()
#content_dict = {'permit':True, 'park_num':1L, 'user_type':'day','balance':int(100.0),'date_end':datetime.now()}
#print content_dict
#print "content:"+n1.content_encode(content_dict)
#print "protocol:"+n1.protocol_encode()


#mydata2 = get_data_field(ignoreInput, 'Entrancesonser')
#n2 = nb_protocol(mydata2)
#print(n2.protocol_decode())
#print(n2.content_decode())


#mydata3 = get_data_field(input2, 'Entrancesonser')
#n3 = nb_protocol(mydata3)
#print(n3.protocol_decode())
#print(n3.content_decode())
#content_dict = {'permit':True, 'park_fee':15,'user_type':'day','balance':100}
#print "content:"+n3.content_encode(content_dict)
#print "protocol:"+n3.protocol_encode()




