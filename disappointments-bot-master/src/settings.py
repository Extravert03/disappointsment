import pathlib
import urllib.parse

from environs import Env

env = Env()
env.read_env()

SRC_DIR = pathlib.Path(__file__).parent
POINTS_AMOUNT: int = env.int('POINTS_AMOUNT')
TELEGRAM_BOT_TOKEN: str = env.str('TELEGRAM_BOT_TOKEN')
DATABASE = urllib.parse.urlparse(env.str('DATABASE_URL'))
DEBUG: bool = env.bool('DEBUG')

REPORT_FILE_PATH = './disappointments-report.xlsx'
