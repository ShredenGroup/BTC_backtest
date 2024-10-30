from os import path
import pathlib
import sys
class Config:
    def __init__(self):
      print('config module is loading')
      self.current_dict=pathlib.Path().resolve()
      self.btc_file=path.join(self.current_dict,'data','btc.csv')
      
    @staticmethod
    def arg()->str:
      arguments=sys.argv[1:]
      if len(arguments)>1:
          print('please enter only one stratergy')
          sys.exit(1)
      if len(arguments)==0:
          print('please enter at least one strategy arg')
          sys.exit(1)
      else:
         return arguments[0]