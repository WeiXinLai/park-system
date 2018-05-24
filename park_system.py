# -*- coding: utf-8 -*- 
from flask import Flask,request,render_template
#import logging
import simplejson
#from flask_sqlalchemy import SQLAlchemy
from easyiotsdk import EasyIoT
from nb_protocol import nb_protocol,get_data_field
from mydatabase import User,Park,Inout
from __init__ import app,db
from common import create_service_id
from datetime import datetime
from gpcharts import figure
from flask import Response 
from collections import OrderedDict
import json
import random
 
#app = Flask(__name__)
#app.debug = True
#handler = logging.FileHandler('/home/BigWhile/park-system/logs/uwsgi/park.log')
#app.logger.addHandler(handler)
#app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:laiweixin@localhost:3306/test?charset=utf8'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True 
#db = SQLAlchemy(app)


@app.route('/lot_id/<num>')
def index(num):
    park_lst = Park.query.filter_by(lot_id = int(num)).all()
    park_dict = dict()
    for park_item in park_lst:
        park_dict[int(park_item.park_num)] = park_item.park_state
    app.logger.info(park_dict)
    park_dict = {1:"available",2:"unavailable",3:"unavailable",4:"available",5:"available",6:"unavailable",7:"unavailable",8:"available",9:"available",10:"unavailable",11:"unavailable",12:"available",13:"available",14:"unavailable",15:"unavailable",16:"available",17:"available",18:"unavailable",19:"unavailable",20:"available",21:"available",22:"unavailable",23:"unavailable",24:"available",25:"available",26:"unavailable",27:"unavailable",28:"available"}
    return render_template('index.html',lot_id = num, park_dict = park_dict)


@app.route('/')
def user():
    return render_template('test1.html')

def get_random_data():
    date = dict()
    month = OrderedDict()
    for i in range(7):
        date[str(i+1)] = random.randint(1,24)
    for i in range(5):
        month[str(i+1)+'月'] = random.randint(1,744)
    datas = dict()
    #sorted(month.items(), key=lambda e:e[0], reverse=True)
    datas['date'] = date
    datas['month'] = month
    return datas


@app.route('/getdata/<park_num>',methods=['GET','POST'])
def getdata(park_num):
    #datas = {"date":{"1":10, "2":22,"3":10}, "month":{"1月":220,"2月":559,"3月":660}}
    datas = get_random_data()
    content = json.dumps(datas)
    app.logger.info(content)
    resp = Response(content)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

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

@app.route('/report-dev-callback01', methods=['POST','GET'])
def Test01():
    #rsp = request.get_data()
    #rsp = simplejson.loads(rsp)
    #app.logger.info('/report-dev-callback')
    iot = EasyIoT('gzhxxxdev01', '!zyhGood3$$')
    iot.login()
    iot.common_method('urt-command', devSerial='863703031721561', method='command',params={'Park':'010000001201010102010103010004010205045c8fb401'})
    return "hi buddy!"

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
        ret = dict()
        if c1['inout_flag'] == 'in':
            tb_user = User.query.filter_by(unique_num=c1['unique_num'],lot_id=c1['lot_id']).first()
            if tb_user is None:#如果根据唯一编号和停车场id查询不到，说明是临时用户，因为临时用户没有停车场id
                tb_user = User.query.filter_by(unique_num=c1['unique_num']).first()
            user_type = tb_user.user_type
            park_num = tb_user.park_num
            tb_park = Park.query.filter_by(lot_id = c1['lot_id'], park_num=park_num, park_kind='perm').first()
            if tb_park is not None:
                date_end = tb_park.date_end
            if user_type == 'year' or user_type == 'month':
                 if date_end > datetime.now():
                     ret['permit']=True
                     ret['park_num']= park_num
                     ret['user_type']= user_type
                     ret['date_end'] = date_end
                     ret['balance']=tb_user.balance
                     app.logger.info('user type is year/month,permit')  
                 elif tb_user.balance > 0: #如果年月用户已到期，但用户余额大于0,且该停车场有临时车位也是可以放行    
                     p1 = Park.query.filter_by(lot_id=c1['lot_id'],park_kind='temp',park_state='available').first()
                     if p1 is not None:
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
                         app.logger.info('user type is year/month and exceed the date_end limit and balance is enough and have temp park_num,so permit')
                     else: 
                         ret['permit']=False
                         ret['park_num']=None
                         ret['user_type']='day'
                         ret['date_end']=date_end
                         ret['balance']=tb_user.balance
                         app.logger.info('user type is year/month and exceed the date_end limit and balance is enough, but temp park is full, so forbid')
                 else: #车位即过期且账户余额为零
                     ret['permit']=False
                     ret['park_num']=None
                     ret['user_type']='day'
                     ret['date_end']=date_end
                     ret['balance']=tb_user.balance
                     app.logger.info('user type is year/month and exceed the date_end limit but balance is not enough, so forbid')
            elif user_type == 'day':
                 balance = User.query.filter_by(unique_num=c1['unique_num']).first().balance
                 p1= Park.query.filter_by(lot_id = c1['lot_id'], park_kind ='temp', park_state='available').first()
                 if balance > 0 and p1 is not None:
                     ret['permit']=True
                     ret['park_num']=p1.park_num
                     ret['user_type']=user_type
                     ret['balance']=tb_user.balance
                     ret['date_end']=None
                     app.logger.info("user type is day and balance is enough and park is not full, so permit")
                 else:
                     ret['permit']=False
                     ret['park_num']=None
                     ret['balance']=tb_user.balance
                     ret['user_type']=user_type
                     ret['date_end']=None
                     app.logger.info("user type is day but balance is not enougt or park is full,so forbid")
            app.logger.info(ret)
            if ret['permit']:
                service_id = create_service_id()
                i1 = Inout(service_id, c1['lot_id'], ret['park_num'], c1['unique_num'], ret['user_type'], datetime.now(),None,None)
                p1 = Park.query.filter_by(lot_id = c1['lot_id'], park_num = ret['park_num']).first()
                if ret['user_type']== 'day':
                    u1 = User.query.filter_by(unique_num = c1['unique_num']).first()
                    u1.lot_id = c1['lot_id']
                    u1.park_num = ret['park_num']
                    db.session.add(u1)
                    db.session.commit()
                p1.park_state = 'unavailable'
                db.session.add_all([i1,p1])
                db.session.commit()
            app.logger.info("successful")         
        if c1['inout_flag'] == 'out':
            tb_user = User.query.filter_by(unique_num=c1['unique_num']).first()
            if tb_user.user_type == 'year' or tb_user.user_type == 'month':
                ret['permit'] = True
                ret['park_fee']=0
                ret['user_type']=tb_user.user_type
                ret['balance'] = tb_user.balance
                app.logger.info("user_type is year/month, permit")
            else:
                time_in = Inout.query.filter_by(unique_num = c1['unique_num'], lot_id = c1['lot_id'],time_out=None).first().time_in
                half_hour_num = round((datetime.now()-time_in).total_seconds()/1800) #表示多少个半小时
                park_fee = half_hour_num * 5 #暂定5元半小时
                if tb_user.balance < park_fee:
                    ret['permit'] = False
                    ret['park_fee']=park_fee
                    ret['user_type']='day'
                    ret['balance']=tb_user.balance
                    app.logger.info('user_type is day but balance is not enough for park_fee so dispermit')
                else:
                    ret['permit'] = True
                    ret['park_fee']=park_fee
                    ret['user_type']='day'
                    ret['balance'] = tb_user.balance
                    app.logger.info('user_type is day and balance is enough,permit')
            app.logger.info(ret)
            if ret['permit'] == True:
                in1 = Inout.query.filter_by(unique_num = c1['unique_num'], lot_id = c1['lot_id'], time_out=None).first()
                in1.time_out = datetime.now()
                in1.park_fee = ret['park_fee']
                park1 = Park.query.filter_by(lot_id = tb_user.lot_id, park_num = tb_user.park_num).first()
                park1.park_state = 'available'
                usr2 = User.query.filter_by(unique_num = c1['unique_num']).first()
                if usr2.user_type == 'day':
                    usr2.lot_id = None
                    usr2.park_num = None
                db.session.add_all([in1,park1,usr2])
                db.session.commit()
            app.logger.info('successful')
        n1.content_encode(ret)
        down_protocol = n1.protocol_encode()
        app.logger.info("down_protocol:"+down_protocol)        
        #iot = EasyIoT('gzhxxxdev01', '!zyhGood3$$')
        #iot.login()
        #iot.common_method('urt-command', devSerial='863703031721561', method='DataDowncommand',params={'Entrancesonser':down_protocol})
    return 'hello wp'

@app.route('/cmd-response-callback',methods=['POST'])
def CmdRspCbk():
    rsp = request.get_data()
    rsp = simplejson.loads(rsp)
    app.logger.info('cmd-response-callback')
    app.logger.info(rsp)
    return 'hello'


if __name__ == '__main__':
    print get_random_data()
    app.run()

