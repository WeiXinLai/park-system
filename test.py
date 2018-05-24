#-*- coding:utf-8 -*-
from __init__ import db
from mydatabase import User,Park,Inout
from datetime import datetime,timedelta
import time
import uuid

db.create_all()

u1 = User('11111111','user1','123456','717334756@qq.com','44528119960201242490','year',1,1,0)
u2 = User('22222222','user2','123456','717334756@qq.com','44528119960201242491','year',1,2,0)
u3 = User('33333333','user3','123456','717334756@qq.com','44528119960201242492','year',1,3,100)
u4 = User('44444444', 'user4','123456','717334756@qq.coom','44528119960201242493','year',1,4,100)
u5 = User('55555555', 'user5','123456','717334756@qq.coom','44528119960201242493','year',1,5,100)
u6 = User('66666666', 'user6','123456','717334756@qq.coom','44528119960201242493','month',1,6,100)
u7 = User('77777777', 'user7', '123445','717334856@qq.com', '445281199403245678', 'month', 1,7,0)
u8 = User('88888888', 'user8', '123445','717334856@qq.com', '445281199403245678', 'month', 1,8,0)
u9 = User('99999999', 'user9', '123445','717334856@qq.com', '445281199403245678', 'day', None, None, 100)
u10 = User('10000000', 'user10', '123445','717334856@qq.com', '445281199403245678', 'day', None, None, 100)
u11 = User('11000000', 'user11', '123445','717334856@qq.com', '445281199403245678', 'day', None, None, 0)
u12 = User('12000000', 'user12', '123445','717334856@qq.com', '445281199403245678', 'day', None, None, 0)

#u13 = User('13000000', 'user13', '123445','717334856@qq.com', '445281199403245678', 'day', None, None, 0)

now  = datetime.now()
next_month = now+ timedelta(days=30)
before_month = now - timedelta(days = 31)
before_day = now - timedelta(days = 1)
before_year = now - timedelta(days = 365)
next_year = now + timedelta(days = 365)
c1 = Park(1,1,1,'perm','available', now, next_year)
c2 = Park(2,1,2,'perm','available', now, next_year)
c3 = Park(3,1,3,'perm','available', now, next_year)
c4 = Park(4,1,4,'perm','available', now, next_year )
c5 = Park(5,1,5,'perm','available', before_year, before_day)
c6 = Park(6,1,6,'perm','available', before_month, before_day)
c7 = Park(7,1,7,'perm','available', before_month, before_day)
c8 = Park(8,1,8,'perm','available', before_month, before_day)
c9 = Park(9,1,9,'temp','available', None,None)
c10 = Park(10,1,10,'temp','available', None,None)

#c11 = Park(11,1,11,'temp','available',None,None)


#db.session.add_all([u1,u2,u3,u4,u5,u6,u7,u8,u9,u10,u11,u12,c1,c2,c3,c4,c5,c6,c7,c8,c9,c10])
#db.session.add_all([u13,c10])
#db.session.commit()

park_lst = Park.query.filter_by(lot_id = 1).all()
park_dict = dict()
for park_item in park_lst:
    park_dict[int(park_item.park_num)] = park_item.park_state
print park_dict


#if __name__ == '__main__':



