# -*- coding:UTF-8 -*-
'''
    自定义模块功能异常
'''
class ModuleException(BaseException):
    """ Common base class for all non-exit exceptions. """

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass

    @staticmethod  # known case of __new__
    def __new__(*args, **kwargs):  # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        pass