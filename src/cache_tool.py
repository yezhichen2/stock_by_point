# coding=utf-8

import functools
import hashlib
import json
import pickle
import re
import redis

#from lvn_public import CTX

cache_rds = redis.StrictRedis.from_url("redis://localhost/4")


def api_cache(ex=300, mgr_key=""):
    """
    Api方法结果缓存， Api方法参数要求是简单的类型， 装饰器排列在最底层
    :param ex: T-int, 设置过期时间
    :param mgr_key: T-string, 管理键eval表达式
    :example:

    @xxx
    @rds_api_cache(ex=60)
    def api_method(self):
    """

    def wrapper(func):

        @functools.wraps(func)
        def _d(*args, **kwargs):

            def _get_params_key():
                _args = args[1:]
                _kwargs = {}
                _kwargs.update(kwargs)

                for index, _arg in enumerate(_args):
                    _kwargs["_arg_%d" % index] = _arg

                pkey_name = json.dumps(_kwargs, sort_keys=True)
                pn_bytes = pkey_name.encode("utf-8")
                pn_key = "{}{}".format(hashlib.md5(pn_bytes).hexdigest(), hashlib.sha256(pn_bytes).hexdigest())
                return pn_key

            def _mk_func_name_key():

                find = re.findall("(?:function|method)\s(\w+\.\w+)", "%s" % func)
                func_name = find[0]

                _params_key = _get_params_key()

                func_name_key = "api_cache_" + func_name
                _mgr_key = "[mgr_key-%s]" % eval(mgr_key, {"args": args, "kwargs": kwargs}) if mgr_key else ""
                _func_key = func_name_key + _mgr_key + ":" + _params_key

                return _func_key

            func_key = _mk_func_name_key()
            dumps_data = cache_rds.get(func_key)

            if dumps_data is None:
                rs = func(*args, **kwargs)
                dumps_data = pickle.dumps(rs)
                cache_rds.set(func_key, dumps_data, ex=ex)

                return rs

            rs = pickle.loads(dumps_data)
            return rs

        return _d

    return wrapper


def delete_api_cache_key(method_name, mgr_key=""):
    """
    删除缓存
    :param method_name:
    :param mgr_key:
    :return:
    """
    if not isinstance(method_name, str):
        find = re.findall("(?:function|method)\s(\w+\.\w+)", "%s" % method_name)
        method_name = find[0]

    target_key_name = "api_cache_%s%s*" % (method_name, "\[mgr_key-%s\]" % mgr_key if mgr_key else "")

    for key_name in cache_rds.scan_iter(target_key_name):
        cache_rds.delete(key_name)

