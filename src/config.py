from os import path
import pathlib
class Config:
    def __init__(self):
      print('config module is loading')
      self.current_dict=pathlib.Path().resolve()
      self.btc_file=path.join(self.current_dict,'data','btc_price.csv')
      