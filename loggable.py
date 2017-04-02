import logging
import inspect

logging.basicConfig(level=logging.INFO)


class Loggable:
    @classmethod
    def format_msg(cls,msg):
        return cls.__name__ + ':' + inspect.getouterframes(inspect.currentframe(), 2)[1][3] + ': ' + msg

    @classmethod
    def dbg(cls, msg='', *args, **kwargs):
        msg = cls.format_msg(msg)
        logging.debug(msg, *args, **kwargs)

    @classmethod
    def info(cls, msg='', *args, **kwargs):
        msg = cls.format_msg(msg)
        logging.info(msg, *args, **kwargs)