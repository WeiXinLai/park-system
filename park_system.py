from flask import Flask,request
import logging
import simplejson
from flask_sqlalchemy import SQLAlchemy
from easyiotsdk import EasyIoT
from nb_protocol import nb_protocol,get_data_field

app = Flask(__name__)
app.debug = True
handler = logging.FileHandler('/home/BigWhile/park-system/logs/uwsgi/park.log')
app.logger.addHandler(handler)
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:laiweixin@localhost:3306/test?charset=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True 
db = SQLAlchemy(app)


def db_init():
    db.create_all()


@app.route('/')
def index():
    return '<h1>Hello World!</h1>'


@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, {}!</h1>'.format(name)

@app.route('/login',methods=['POST','GET'])
def login():
    userName = request.form['username']
    app.logger.info(userName)
    return '<h1>hello, {}</h1>'.format(userName)

@app.route('/dev-batch-reg-result', methods=['POST'])
def DevBatchRegResult():
    rsp = request.get_data()
    rsp = simplejson.loads(rsp)
    app.logger.info(rsp)
    if isinstance(rsp,dict):
        if 'process' in rsp:
            app.logger.info("process:"+rsp['process'])
        else:
            app.logger.info("process not exist")
    else:
        app_logger("unreach service")
    return 'hello world'

@app.route('/report-dev-callback', methods=['POST'])
def RepDevCbk():
    rsp = request.get_data()
    rsp = simplejson.loads(rsp)
    app.logger.info('report-dev-callback')
    Entrancesonser = get_data_field(rsp, 'Entrancesonser')
    n1 = nb_protocol(Entrancesonser)
    c1 = n1.content_decode()
    if n1.data_flag and c1 is not None:
        app.logger.info(rsp)
        iot = EasyIoT('gzhxxxdev01', '!zyhGood3$$')
        iot.login()
        iot.common_method('urt-command', devSerial='863703031721561', method='DataDowncommand',params={'Entrancesonser':'111'})
    return 'hello,wp'

@app.route('/cmd-response-callback',methods=['POST'])
def CmdRspCbk():
    rsp = request.get_data()
    rsp = simplejson.loads(rsp)
    app.logger.info('cmd-response-callback')
    app.logger.info(rsp)
    return 'hello'


if __name__ == '__main__':
    #rsp1 = {"createTime": "2018-02-19 22:29:01", "serviceData": [{"serviceData": {"batteryLevel": 99},"serviceId": "Battery"}, {"serviceData": {"signalStrength": 79}, "serviceId": "Meter"}, {"serviceData": {"Entrancesonser": "01000000000d010100020400036c9003020001"},"serviceId": "Datamessage"}], "lastMessageTime": "2018-03-01 21:55:08", "devSerial": "863703031721561"} 
    #rsp2 = {'devSerial': '863703031721561', 'serviceData': [{'serviceData': {'batteryLevel': 99}, 'serviceId': 'Battery'}, {'serviceData': {'signalStrength': 79}, 'serviceId': 'Meter'}, {'serviceData': {'Entrancesonser': '0100000000040402ffff'}, 'serviceId': 'Datamessage'}], 'lastMessageTime': '2018-03-10 17:18:05', 'createTime': '2018-02-19 22:29:01'}

    #Entrancesonser = get_data_field(rsp2, 'Entrancesonser')
    #n1 = nb_protocol(Entrancesonser)
    #c1 = n1.content_decode()
    #if n1.data_flag and c1 is not None:
    #    print(c1)
    app.run()

