import pandas as pd 
from pathlib import Path
import sys
import os
class DB_processor():
    @staticmethod
    def read_csv(path:Path)->pd.DataFrame:
        P=Path(path)
        path_check=P.exists()
        if not path_check:
            print('path is not valid')
            sys.exit(1)
        df=pd.read_csv(path)
        print('Successfully read csv file and return df')
        return df