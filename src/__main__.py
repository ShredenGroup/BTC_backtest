from .config import Config
from .db_processor import DB_processor
def main():
    config=Config()
    BTC_df=DB_processor.read_csv(config.btc_file)
    print(BTC_df.head())
main()