

class Response:
    """
    响应对象类,用于封装API接口的响应信息
    """

    def __init__(self, code, message, data=None):
        """
        初始化响应对象

        :param code: 响应状态码
        :param msg: 响应消息
        :param data: 响应数据,默认为None
        """
        self.code = code
        self.message = message
        self.data = data

    def to_dict(self):
        """
        将响应对象转换为字典

        :return: 包含响应信息的字典
        """
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }
