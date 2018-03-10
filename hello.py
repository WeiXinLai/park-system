from flask import Flask,request
import logging
import simplejson
from flask_sqlalchemy import SQLAlchemy
from easyiotsdk import EasyIoT

app = Flask(__name__)
app.debug = True
handler = logging.FileHandler('/home/BigWhile/flasky/log/uwsgi/hello.log')
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
    app.run()

