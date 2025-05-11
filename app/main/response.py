# -*- coding: utf-8 -*-

class ApiResponse:
    """
    响应对象类, 用于封装 API 接口的响应信息
    
    该类提供了将响应信息转换为字典的方法, 便于在 API 接口中返回统一格式的数据
    """

    def __init__(self, code, message, data=None):
        """
        初始化响应对象

        :param code: 响应状态码, 用于表示接口的执行结果状态
        :param message: 响应消息, 用于向调用方提供执行结果的描述信息
        :param data: 响应数据, 包含接口返回的具体业务数据, 默认为 None
        """
        self.code = code
        self.message = message
        self.data = data

    def to_dict(self):
        """
        将响应对象转换为字典

        :return: 包含响应信息的字典, 格式为 {"code": 状态码, "message": 消息, "data": 数据}
        """
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }
