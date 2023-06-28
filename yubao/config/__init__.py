import yaml
import os
from yubao.util.logger import new_logger

class Config:
    '''该类用于设置一些辅助的方法'''
    logger = new_logger("config",debug=True)

    config_file = os.path.join(os.path.dirname(__file__), 'config.yaml')
    def __init__(self) -> None:
        self.logger.debug('实例化Config')
        pass

    def read_config(self) -> dict:
        '''读取配置'''
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        self.logger.debug(f'已载入配置{self.config_file}')
        return config