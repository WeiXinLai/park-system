#-*- coding:utf-8 -*-

input1 = {"createTime": "2018-02-19 22:29:01", "serviceData": [{"serviceData": {"batteryLevel": 99},"serviceId": "Battery"}, {"serviceData": {"signalStrength": 79}, "serviceId": "Meter"}, {"serviceData": {"Entrancesonser": "01000000000d010100020400036c9003020001"},"serviceId": "Datamessage"}], "lastMessageTime": "2018-03-01 21:55:08", "devSerial": "863703031721561"}
ignoreInput = {'devSerial': '863703031721561', 'serviceData': [{'serviceData': {'batteryLevel': 99}, 'serviceId': 'Battery'}, {'serviceData': {'signalStrength': 79}, 'serviceId': 'Meter'}, {'serviceData': {'Entrancesonser': '0100000000040402ffff'}, 'serviceId': 'Datamessage'}], 'lastMessageTime': '2018-03-10 17:18:05', 'createTime': '2018-02-19 22:29:01'}

input2 = {"createTime": "2018-02-19 22:29:01","serviceData": [{"serviceData": {"batteryLevel": 99},"serviceId": "Battery"},{"serviceData": {"signalStrength": 79}, "serviceId": "Meter"}, {"serviceData": {"Entrancesonser": "02010000000d01010102041111111103020001"}, "serviceId": "Datamessage"}], "lastMessageTime": "2018-03-01 21:55:08", "devSerial": "863703031721561"}

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
    


#mydata1 = get_data_field(input1, 'Entrancesonser')
#n1 = nb_protocol(mydata1)
#print (n1.protocol_decode())
#print (n1.content_decode())


#mydata2 = get_data_field(ignoreInput, 'Entrancesonser')
#n2 = nb_protocol(mydata2)
#print(n2.protocol_decode())
#print(n2.content_decode())


#mydata3 = get_data_field(input2, 'Entrancesonser')
#n3 = nb_protocol(mydata3)
#print(n3.protocol_decode())
#print(n3.content_decode())




