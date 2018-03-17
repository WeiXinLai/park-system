# -*- coding: utf-8 -*- 
from flask import Flask,request
#import logging
import simplejson
#from flask_sqlalchemy import SQLAlchemy
from easyiotsdk import EasyIoT
from nb_protocol import nb_protocol,get_data_field
from mydatabase import User,Park,Inout
from __init__ import app,db
from common import create_service_id
from datetime import datetime

#app = Flask(__name__)
#app.debug = True
#handler = logging.FileHandler('/home/BigWhile/park-system/logs/uwsgi/park.log')
#app.logger.addHandler(handler)
#app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:laiweixin@localhost:3306/test?charset=utf8'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True 
#db = SQLAlchemy(app)


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
    app.logger.info(Entrancesonser)
    n1 = nb_protocol(Entrancesonser)
    c1 = n1.content_decode()
    app.logger.info(c1)
    if n1.data_flag and c1 is not None:
        if c1['inout_flag'] == 'in':
            tb_user = User.query.filter_by(unique_num=c1['unique_num'],lot_id=c1['lot_id']).first()
            if tb_user is None:#如果根据唯一编号和停车场id查询不到，说明是临时用户，因为临时用户没有停车场id
                tb_user = User.query.filter_by(unique_num=c1['unique_num']).first()
            user_type = tb_user.user_type
            park_num = tb_user.park_num
            tb_park = Park.query.filter_by(lot_id = c1['lot_id'], park_num=park_num, park_kind='perm').first()
            if tb_park is not None:
                date_end = tb_park.date_end
            app.logger.info(park_num)
            app.logger.info(user_type)
            if user_type == 'year' or user_type == 'month':
                 app.logger.info(date_end)
                 app.logger.info(tb_user.balance)
                 if date_end > datetime.now():
                     ret = dict()
                     ret['permit']=True
                     ret['park_num']= park_num
                     ret['user_type']= user_type
                     ret['date_end'] = date_end
                     ret['balance']=tb_user.balance
                     app.logger.info(ret)  
                 elif tb_user.balance > 0: #如果年月用户已到期，但用户余额大于0,且该停车场有临时车位也是可以放行    
                     p1 = Park.query.filter_by(lot_id=c1['lot_id'],park_kind='temp',park_state='available').first()
                     if p1 is not None:
                         ret = dict()
                         ret['permit']=True
                         ret['park_num']=p1.park_num
                         ret['user_type']='day'
                         ret['date_end']=date_end
                         ret['balance']=tb_user.balance
                         u1 = User.query.filter_by(unique_num = c1['unique_num']).first()
                         u1.user_type = 'day'
                         u1.lot_id = None
                         u1.park_num =None
                         db.session.add(u1)
                         db.session.commit()
                         app.logger.info('user type is year/month but exceed the date_end limit, but balance is enough and have temp park_num,so permit')
                         app.logger.info(ret)
                     else: 
                         ret=dict()
                         ret['permit']=False
                         ret['park_num']=None
                         ret['user_type']='day'
                         ret['date_end']=date_end
                         ret['balance']=tb_user.balance
                         app.logger.info('user type is year/month but exceed the date_end limit,and balance is enough but temp park is full so dispermit')
                         app.logger.info(ret)
                 else: #车位即过期且账户余额为零
                     ret = dict()
                     ret['permit']=False
                     ret['park_num']=None
                     ret['user_type']='day'
                     ret['date_end']=date_end
                     ret['balance']=tb_user.balance
                     app.logger.info('user type is year/month but exceed the date_end limit,and balance is not enough, so dispermit')
            elif user_type == 'day':
                 balance = User.query.filter_by(unique_num=c1['unique_num']).first().balance
                 app.logger.info(balance)
                 p1= Park.query.filter_by(lot_id = c1['lot_id'], park_kind ='temp', park_state='available').first()
                 if balance > 0 and p1 is not None:
                     ret = dict()
                     ret['permit']=True
                     ret['park_num']=p1.park_num
                     ret['user_type']=user_type
                     ret['balance']=tb_user.balance
                     ret['date_end']=None
                     app.logger.info("user is day and balance is enough and park is not full so permit")
                 else:
                     ret=dict()
                     ret['permit']=False
                     ret['park_num']=None
                     ret['balance']=tb_user.balance
                     ret['user_type']=user_type
                     ret['date_end']=None
                     app.logger.info("user_type is day but balance is not enougt or park is full")
                     app.logger.info(ret)
            if ret['permit']:
                service_id = create_service_id()
                app.logger.info(ret)
                i1 = Inout(service_id, c1['lot_id'], ret['park_num'], c1['unique_num'], ret['user_type'], datetime.now(),None,None)
                app.logger.info(i1)
                p1 = Park.query.filter_by(lot_id = c1['lot_id'], park_num = ret['park_num']).first()
                app.logger.info(p1)
                if ret['user_type']== 'day':
                    u1 = User.query.filter_by(unique_num = c1['unique_num']).first()
                    app.logger.info(u1)
                    u1.lot_id = c1['lot_id']
                    u1.park_num = ret['park_num']
                    db.session.add(u1)
                    db.session.commit()
                p1.park_state = 'unavailable'
                db.session.add_all([i1,p1])
                db.session.commit()
            app.logger.info("successful")         
        if c1['inout_flag'] == 'out':
            app.logger.info('out service')
            tb_user = User.query.filter_by(unique_num=c1['unique_num']).first()
            app.logger.info(tb_user.user_type)
            if tb_user.user_type == 'year' or tb_user.user_type == 'month':
                ret = dict()
                ret['permit'] = True
                ret['park_fee']=None
                ret['user_type']=tb_user.user_type
                ret['balance'] = tb_user.balance
                app.logger.info("user_type is year/month, permit")
            else:
                time_in = Inout.query.filter_by(unique_num = c1['unique_num'], lot_id = c1['lot_id'],time_out=None).first().time_in
                half_hour_num = round((datetime.now()-time_in).total_seconds()/1800) #表示多少个半小时
                park_fee = half_hour_num * 5 #暂定5元半小时
                if tb_user.balance < park_fee:
                    ret = dict()
                    ret['permit'] = False
                    ret['park_fee']=park_fee
                    ret['user_type']='day'
                    ret['balance']=tb_user.balance
                    app.logger.info('user_type is day but balance is not enough for park_fee so dispermit')
                else:
                    ret = dict()
                    ret['permit'] = True
                    ret['park_fee']=park_fee
                    ret['user_type']='day'
                    ret['balance'] = tb_user.balance
                    app.logger.info('user_type is day and balance is enough,permit')
            app.logger.info(ret)
            if ret['permit'] == True:
                in1 = Inout.query.filter_by(unique_num = c1['unique_num'], lot_id = c1['lot_id'], time_out=None).first()
                app.logger.info(in1)
                in1.time_out = datetime.now()
                in1.park_fee = ret['park_fee']
                park1 = Park.query.filter_by(lot_id = tb_user.lot_id, park_num = tb_user.park_num).first()
                app.logger.info(park1)
                park1.park_state = 'available'
                usr2 = User.query.filter_by(unique_num = c1['unique_num']).first()
                usr2.lot_id = None
                usr2.park_num = None
                db.session.add_all([in1,park1,usr2])
                db.session.commit()
            app.logger.info('successful')
                
            #app.logger.info(rsp)
            #iot = EasyIoT('gzhxxxdev01', '!zyhGood3$$')
            #iot.login()
            #iot.common_method('urt-command', devSerial='863703031721561', method='DataDowncommand',params={'Entrancesonser':'111'})
    return 'hello wp'

@app.route('/cmd-response-callback',methods=['POST'])
def CmdRspCbk():
    rsp = request.get_data()
    rsp = simplejson.loads(rsp)
    app.logger.info('cmd-response-callback')
    app.logger.info(rsp)
    return 'hello'


if __name__ == '__main__':
    app.run()

