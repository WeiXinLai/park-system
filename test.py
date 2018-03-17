#-*- coding:utf-8 -*-
from __init__ import db
from mydatabase import User,Park,Inout
from datetime import datetime,timedelta
import uuid

db.create_all()

u1 = User('11111111','BigWhile','123456','717334756@qq.com','44528119960201242490','year',1,1,0)
u2 = User('22222222','BigYellow','123456','717334756@qq.com','44528119960201242491','month',1,2,100)
u3 = User('33333333','BigBlack','123456','717334756@qq.com','44528119960201242492','month',1,3,100)
u4 = User('44444444', 'BigBlue','123456','717334756@qq.coom','44528119960201242493','month',1, 4,0)
u5 = User('55555555', 'BigRed','123456','717334756@qq.coom','44528119960201242493','day',1,5,100)
u6 = User('66666666', 'SmallBlue','123456','717334756@qq.coom','44528119960201242493','day',None, None,100)
u7 = User('77777777', 'middleWhile', '123445','717334856@qq.com', '445281199403245678', 'day', None, None, 100)
now  = datetime.now()
next_month = now+ timedelta(days=30)
before_month = now - timedelta(days = 31)
before_day = now - timedelta(days = 1)
hour = (now-before_day).total_seconds()/3600
hour = round(hour)



next_year = now + timedelta(days = 365)
c1 = Park(1,1,1,'perm','available', now, next_year)
c2 = Park(2,1,2,'perm','available', before_month, before_day)#需要一个临时车位
c3 = Park(3,1,3,'perm','available',before_month, before_day)#没有临时车位了
c4 = Park(4,1,4,'perm','available', before_month, before_day)#用户账户小于零
c5 = Park(5,1,5,'temp','available',None,None)
c6 = Park(6,1,6,'temp','available',None,None)
c7 = Park(7,1,7,'temp','available', None,None)
db.session.add_all([u7,c7])
db.session.commit()
#p1 = Park.query.filter_by(lot_id = 1, park_num = 1).first()
#p1.park_state = 'available'
#db.session.add(p1)
#db.session.commit()
#db.session.add_all([u1,u2,u3,u4,u5,u6,c1,c2,c3,c4,c5,c6])
#db.session.commit()

#i1 = Inout('11111111111',1,1,'11111111','perm',datetime.now(),None,None)
#db.session.add(i1)
#db.session.commit()




#if __name__ == '__main__':



