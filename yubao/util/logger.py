'''
    from: Ice9Coffee/HoshinoBot
'''
import logging
import os
import sys

os.makedirs('./logs', exist_ok=True)
_debug_log_file = os.path.expanduser('./logs/debug.log')
_info_log_file = os.path.expanduser('./logs/info.log')
_error_log_file = os.path.expanduser('./logs/error.log')
_critical_log_file = os.path.expanduser('./logs/critical.log')

formatter = logging.Formatter('[%(asctime)s %(name)s] %(levelname)s: %(message)s')

debug_handler = logging.FileHandler(_debug_log_file, encoding='utf8')
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(formatter)

info_handler = logging.StreamHandler(sys.stdout)
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(formatter)

info_handler_file = logging.FileHandler(_info_log_file, encoding='utf8')
info_handler_file.setLevel(logging.INFO)
info_handler_file.setFormatter(formatter)

error_handler = logging.FileHandler(_error_log_file, encoding='utf8')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

critical_handler = logging.FileHandler(_critical_log_file, encoding='utf8')
critical_handler.setLevel(logging.CRITICAL)
critical_handler.setFormatter(formatter)


def new_logger(name, debug=True):
    logger = logging.getLogger(name)
    logger.addHandler(debug_handler)
    logger.addHandler(info_handler)
    logger.addHandler(info_handler_file)
    logger.addHandler(error_handler)
    logger.addHandler(critical_handler)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    return logger