#!/usr/bin/env python
# encoding: utf-8

"""EasyIot平台Rest接口Python示例
1、需安装Python，下载地址：https://www.python.org/downloads/
2、需要安装requests，请使用：pip install requests 安装requests。
3、本示例主要演示在EasyIot平台“文档中心-平台API”中的登录、IOT平台查询、设备管理、业务管理几个接口
"""

import random
import string
import requests

OPT_RESULT_EXPLAIN = {
    '0': '操作成功',
    '1000': '数据库访问异常',
    '1001': '不合法的设备类型(产品型号)',
    '1002': '不合法的设备类别',
    '1003': '设备类型(产品型号)无绑定智能业务',
    '1004': '重复注册相同的设备',
    '1005': '未注册的设备',
    '1006': '未为非直连设备匹配到适合的设备连接点（例如未找到IOT平台）',
    '1007': '认证失败,请重新登录。错误原因：1、用户名或密码错误；2、Token校验失败或已过期。',
    '1008': '业务未在智能业务表注册',
    '1009': '业务在服务地址表中没有记录',
    '1010': '不合法的用户ID',
    '1014': '不合法的接口传参',
    '1015': '注册设备中的设备类型(产品型号)不属于该用户',
    '1016': '用户无操作该设备的权限',
    '1200': '设备控制命令错误',
    '1201': '命令commandId繁忙',
    '1400': '数据引擎服务异常',
    '1502': 'Session Id不合法',
    '1503': '不合法的请求体',
    '1504': '无法查询出与设备序列号相应的数据',
    '1505': '未找到可用的连接点Id',
    '1601': '请求头认证信息未正确填写',
    '1602': 'CallbackUrl 未配置',
    '40009': '编解码过程出现错误',
    '100000': 'IOT平台返回错误（IOTGateway模块返回的错误都映射成此错误码）',
    '100001': 'IOT平台http连接错误',
    '100101': '内部服务组件调用失败',
    '100102': '服务异常',
    '100103': '内部路由失败',
    '200000': '入口参数格式错误',
}

REST_COMMON_DATA = {
    'login': {
        'uri': 'server/',
        'rest_text': '登录鉴权接口',
        'method': 'POST'
    },
    'get-iotservers': {
        'uri': 'service-config/',
        'rest_text': 'IoT连接平台查询接口',
        'method': 'GET'
    },
    'get-iotservicemode': {
        'uri': 'service-config/',
        'rest_text': 'IoT平台业务模式查询接口',
        'method': 'GET'
    },
    'reg-device': {
        'uri': 'devices/',
        'rest_text': '注册设备接口',
        'method': 'POST'
    },
    'reg-device-batch': {
        'uri': 'devices/',
        'rest_text': '批量注册设备接口',
        'method': 'POST'
    },
    'update-device': {
        'uri': 'devices/',
        'rest_text': '更新设备接口',
        'method': 'PUT'
    },
    'query-device-allinfo': {
        'uri': 'devices/',
        'rest_text': '设备信息查询接口',
        'method': 'GET'
    },
    'del-device': {
        'uri': 'devices/',
        'rest_text': '删除设备接口',
        'method': 'DELETE'
    },
    'list-devtypes': {
        'uri': 'devices/',
        'rest_text': '查询所有可用设备类型(产品型号)接口',
        'method': 'GET'
    },
    'list-devices': {
        'uri': 'devices/',
        'rest_text': '查询用户所有设备接口',
        'method': 'GET'
    },
    'query-devType': {
        'uri': 'dev-manage/',
        'rest_text': '查询设备类型(产品型号)信息接口',
        'method': 'GET'
    },
    'urt-command': {
        'uri': 'dev-control/',
        'rest_text': '设备控制接口',
        'method': 'POST'
    },
    'subscribe-service-address': {
        'uri': '',
        'rest_text': '注册订阅地址接口',
        'method': 'POST'
    },
    'unsubscribe-service-address': {
        'uri': '',
        'rest_text': '取消订阅地址接口',
        'method': 'DELETE'
    },
    'query-subscribe-service-address': {
        'uri': '',
        'rest_text': '查询订阅地址接口',
        'method': 'GET'
    }
}


class OperateFailedException(Exception):
    """操作失败异常"""
    pass


class NotConnectToServerException(Exception):
    """未连接到服务器"""
    pass


class NotLoginException(Exception):
    """未登录"""
    pass


class UnknowRestError(KeyError):
    """未知的接口"""
    pass


def rsp_deal(func):
    """请求响应结果统一处理装饰器。

    :return: :dict/None: dict为请求成功后的响应结果，None为请求失败后处理结果
    :rtype: dict/None
    """

    def inner_func(self, *args, **kwargs):
        """装饰器"""
        rest_name = self.curr_rest
        if rest_name is None:
            rest_name = ''
        rsp = func(self, *args, **kwargs)
        if not isinstance(rsp, dict):
            raise NotConnectToServerException(rest_name+"未请求到服务器")
        if 'optResult' not in rsp:
            raise NotConnectToServerException(rest_name+"未请求到服务器")
        print(rest_name+"已请求到服务器")
        if rsp['optResult'] != '0':
            raise OperateFailedException(rest_name+"请求失败,返回码："+rsp['optResult']+
                                         ","+OPT_RESULT_EXPLAIN[rsp['optResult']])
        print(rest_name+"请求成功，返回："+str(rsp)+"\n")
        if 'accessToken' in rsp:
            self.access_token = rsp['accessToken']
        return rsp
    return inner_func


def before_invoke_check(func):
    """方法调用前检查是否已经登录"""

    def invoke_func(self, *args, **kwargs):
        """装饰器"""
        if self.access_token is None:
            raise NotLoginException('请先登录。')
        return func(self, *args, **kwargs)
    return invoke_func


RANDOM_NAME = lambda length: ''.join(random.choice(string.hexdigits) for _ in range(length))


class EasyIoT(object):
    """本示例运行主类"""


    def __init__(self, username, password):

        """类实例初始化需传递用户名username和密码password两个参数"""

        self.username = username
        self.password = password
        self.access_token = None
        self.curr_rest = None

    def combine_uri(self, uri):
        """拼接完整的请求URL。

        :param uri：变化的URI
        :return: :str: 返回完整的请求URL，如：https://www.easy-iot.cn/idev/3rdcap/server/login
        :rtype: str
        """

        return 'https://www.easy-iot.cn/idev/3rdcap/' + uri

    @rsp_deal
    def common_requests(self, method, uri, args=None, headers=None, timeout=60):
        """统一请求处理函数

        :param method:请求方式，POST/PUT/GET/DELETE.
        :param uri:请求地址uri.
        :param args:请求体内容.
        :param headers:请求头内容.
        :param timeout:请求超时时间.
        :return: :dict: 返回请求响应结果，包含返回码optResult及响应内容(具体视接口而定)
        :rtype dict
        """
        if not uri.endswith('login'):
            headers = {
                'serverID':self.username,
                'accessToken':self.access_token
            }

        if method in ['GET', 'DELETE']:
            result = requests.request(method, self.combine_uri(uri), params=args,
                                      headers=headers, timeout=timeout)
            return result.json()
        elif method in ['PUT', 'POST']:
            result = requests.request(method, self.combine_uri(uri), json=args,
                                      headers=headers, timeout=timeout)
            return result.json()
        else:
            print("请填写正确的请求方式.")

    def login(self):
        """登录鉴权接口"""

        self.curr_rest = '登录鉴权接口'
        # 登录请求uri
        uri = 'server/login'
        # 请求体
        request_body = {
            'serverId':self.username,
            'password':self.password
        }
        # 发送请求
        return self.common_requests('POST', uri, request_body)

    @before_invoke_check
    def get_iotservers(self):
        """IoT连接平台查询接口"""

        self.curr_rest = 'IoT连接平台查询接口'
        uri = 'service-config/get-iotservers'
        return self.common_requests('GET', uri, {})

    @before_invoke_check
    def get_iotservicemode(self, iot_server_id):
        """IoT平台业务模式查询接口

        :param iot_server_id:指定IOT平台连接点,为方便测试，默认为通过'IoT连接平台查询接口'获取的连接点列表的第一个连接点
        """

        if iot_server_id is None:
            return
        self.curr_rest = 'IoT平台业务模式查询接口'
        uri = 'service-config/get-iotservicemode'
        request_body = {
            'iotserverId':iot_server_id
        }
        return self.common_requests('GET', uri, request_body)

    @before_invoke_check
    def reg_device(self, device):
        """注册设备接口

        :param device: 设备基本信息
        """

        self.curr_rest = '注册设备接口'
        uri = 'devices/reg-device'
        return self.common_requests('POST', uri, device)

    @before_invoke_check
    def reg_device_batch(self, devices):
        """批量注册设备接口

        :param devices: 设备基本信息列表
        """

        self.curr_rest = '批量注册设备接口'
        uri = 'devices/reg-device-batch'
        request_body = {
            'devices': devices
        }
        return self.common_requests('POST', uri, request_body)

    @before_invoke_check
    def update_device(self, device):
        """更新设备接口

        :param device: 要更新的设备基本信息
        """

        self.curr_rest = '更新设备接口'
        uri = 'devices/update-device'
        return self.common_requests('PUT', uri, device)

    @before_invoke_check
    def query_device_allinfo(self, dev_serial):
        """设备信息查询接口

        :param dev_serial: 设备序列号
        """

        self.curr_rest = '设备信息查询接口'
        uri = 'devices/query-device-allinfo'
        request_body = {
            'devSerial': dev_serial
        }
        return self.common_requests('GET', uri, request_body)

    @before_invoke_check
    def del_device(self, dev_serial):
        """删除设备接口

        :param dev_serial: 设备序列号
        """

        self.curr_rest = '删除设备接口'
        uri = 'devices/del-device'
        request_body = {
            'devSerial': dev_serial
        }
        return self.common_requests('DELETE', uri, request_body)

    @before_invoke_check
    def list_devtypes(self):
        """查询所有可用设备类型(产品型号)接口

        """

        self.curr_rest = '查询所有可用设备类型(产品型号)接口'
        uri = 'devices/list-devtypes'
        request_body = {
            'serverID': self.username
        }
        return self.common_requests('GET', uri, request_body)

    @before_invoke_check
    def query_devtype(self, dev_type):
        """查询设备类型(产品型号)信息接口

        :param dev_type: 设备类型(产品型号)
        """

        self.curr_rest = '查询设备类型(产品型号)信息接口'
        uri = 'dev-manage/query-devType'
        request_body = {
            'devType': dev_type
        }
        return self.common_requests('GET', uri, request_body)

    @before_invoke_check
    def list_devices(self):
        """查询用户所有设备接口

        """

        self.curr_rest = '查询用户所有设备接口'
        uri = 'devices/list-devices'
        request_body = {
            'serverID': self.username
        }
        return self.common_requests('GET', uri, request_body)

    @before_invoke_check
    def urt_command(self, dev_serial, method, params):
        """设备控制接口，你可以通过该接口对指定设备下发指令，指令内容格式请参考设备所属设备类型(产品型号)中的自定义指令\n

        :param dev_serial:设备序列号\n
        :param method:设备类型(产品型号)中自定义指令的指令ID\n
        :param params:设备类型(产品型号)中自定义指令的消息参数，如开关控制switch,params={'switch': 'ON'}
        """

        self.curr_rest = '设备控制接口'
        uri = 'dev-control/urt-command'
        request_body = {
            'devSerial': dev_serial,
            'method': method,
            'params': params
        }

        return self.common_requests('POST', uri, request_body)

    @before_invoke_check
    def subscribe_service_address(self, callback_url):
        '''注册订阅地址接口，第三方注册成功后，设备数据上报及指令响应都会通过该订阅地址通知

        :param callback_url:要注册的订阅地址
        '''

        self.curr_rest = '注册订阅地址接口'
        uri = 'subscribe-service-address'
        request_body = {
            'callbackUrl': callback_url
        }
        return self.common_requests('POST', uri, request_body)

    @before_invoke_check
    def unsubscribe_service_address(self):
        '''取消订阅地址接口

        '''

        self.curr_rest = '取消订阅地址接口'
        uri = 'unsubscribe-service-address'
        return self.common_requests('DELETE', uri)

    @before_invoke_check
    def query_subscribe_service_address(self):
        '''查询订阅地址接口

        '''

        self.curr_rest = '查询订阅地址接口'
        uri = 'query-subscribe-service-address'
        return self.common_requests('GET', uri)

    def common_method(self, rest, **kwargs):
        """统一调用接口\n
        :param rest:接口URL最后一个'/'后的uri\n
        :param kwargs:关键字变量可变参数，接收接口请求参数
        """
        if rest not in REST_COMMON_DATA:
            raise UnknowRestError('未知接口')
        rest_data = REST_COMMON_DATA[rest]
        self.curr_rest = rest_data['rest_text']
        uri = rest_data['uri']+rest
        method = rest_data['method']
        return self.common_requests(method, uri, kwargs)


def main_test():
    """主测试函数，使用说明：在调用除登录接口外的接口时请先登录；请一步一步地测试。"""

    # 实例化主类
    iot = EasyIoT('gzhxxxdev01', '!zyhGood3$$')

    # 1、登录
    iot.login()

    # 2、获取IOT平台连接点
    rsp = iot.get_iotservers()

    # 3、根据IOT连接点查询业务模式
    # 选择某个连接点，这里取'第2步'结果的第一个
    iot_list = rsp['iotserverList']
    server_id = iot_list[0]['id']
    rsp = iot.get_iotservicemode(server_id)
    mode = rsp['serviceModeList'][0]['serviceMode']

    # 4、查询用户所有设备类型(产品型号)
    rsp = iot.list_devtypes()
    dev_type = rsp['devTypes'][0]

    # 为方便下面接口测试，请不要注释前4步

    # 13、注册订阅地址
    callback_url = 'http://47.106.13.101:83'
    iot.subscribe_service_address(callback_url)

    # 14、查询订阅地址
    iot.query_subscribe_service_address()

    # 5、注册设备
    # devSerial随机生成，deviceType取'第4步'结果的第一个，connectPointId取'第2步'结果的第一个,serviceMode取'第3步'结果的第一个
    # dev_serial = 'Test_'+RANDOM_NAME(4)
    # device_info = {
    #    'devSerial': dev_serial,
    #    'name': dev_serial,
    #    'deviceType': dev_type,
    #    'connectPointId': server_id,
    #    'serviceMode': mode
    #}
    # rsp = iot.reg_device(device_info)

    # 6、批量注册设备
    #devices = []
    #for i in range(3):
    #    device_info = {
    #        'devSerial': 'Test_'+str(i),
    #        'name': 'Test_'+str(i),
    #        'deviceType': dev_type,
    #        'connectPointId': server_id,
    #        'serviceMode': mode
    #    }
    #    devices.append(device_info)
    #iot.reg_device_batch(devices)

    # 7、更新设备
    #dev_serial = '863703031721561'
    # device_info = {
    #     'devSerial': dev_serial,
    #     'name': 'update_'+dev_serial,
    #     'longitude': '113.259933',
    #     'latitude': '23.143843'
    # }
    # iot.update_device(device_info)

    # 8、查询指定设备信息
    # iot.query_device_allinfo(dev_serial)

    # 9、设备控制
    # 指令内容格式请参考设备所属设备类型(产品型号)中的自定义指令
    # method:设备类型(产品型号)中自定义指令的指令ID,params:设备类型(产品型号)中自定义指令的消息参数，如开关控制switch,params={'switch': 'ON'}
    # method = 'DataDowncommand'
    # params = {'Entrancesonser':'allen'}
    # iot.urt_command(dev_serial, method, params)
    # 10、查询所有可用设备
    # iot.list_devices()

    # 11、查询指定设备类型(产品型号)信息
    # iot.query_devtype(dev_type)

    # 12、删除指定设备
    # iot.del_device(dev_serial)

    # 14、取消订阅地址
    # iot.unsubscribe_service_address()

    # 通过以上的调试，相信你已经对这些接口有了一定的了解，接下来可以使用较为通用的方法调试

    # 登录,其他接口的调用请先登录
    #iot.login()

    # IOT连接平台
    # iot.common_method('get-iotservers')

    # 业务模式查询
    # iot.common_method('get-iotservicemode', iotserverId='')

    # 查询用户所有设备类型(产品型号)
    # iot.common_method('list-devtypes', serverID=iot.username)

    # 注册设备
    # dev_serial = 'Test_'+RANDOM_NAME(4)
    # iot.common_method('reg-device', devSerial=dev_serial, name=dev_serial,
    #                   deviceType='', connectPointId='', serviceMode='')

    # 批量注册设备
    # devices = []
    # for i in range(3):
    #     device_info = {
    #         'devSerial': '',
    #         'name': '',
    #         'deviceType': '',
    #         'connectPointId': '',
    #         'serviceMode': ''
    #     }
    #     devices.append(device_info)
    # iot.common_method('reg-device-batch', devices=devices)

    # 更新设备接口
    # iot.common_method('update-device', devSerial=dev_serial, name='update_'+dev_serial,
    #                   longitude='113.259933', latitude='23.143843')

    # 设备信息查询接口
    # iot.common_method('query-device-allinfo', devSerial=dev_serial)

    # 删除设备
    # iot.common_method('del-device', devSerial=dev_serial)

    # 查询用户所有设备
    # iot.common_method('list-devices', serverID=iot.username)

    # 查询设备类型(产品型号)信息
    # iot.common_method('query-devType', devType='')

    # 设备控制
    #iot.common_method('urt-command', devSerial='', method='', params={})
    #iot.common_method('urt-command', devSerial='863703031721561', method='DataDowncommand', params={'Entrancesonser':'111'})
    iot.common_method('urt-command', devSerial='863703031721561', method='command',params={'Park':'111'})
    
    # 注册订阅
    # iot.common_method('subscribe-service-address', callbackUrl='')

    # 取消订阅
    # iot.common_method('unsubscribe-service-address')

    # 查询订阅地址
    # iot.common_method('query-subscribe-service-address')


if __name__ == '__main__':
    main_test()
