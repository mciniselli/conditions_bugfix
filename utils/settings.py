import logging
from datetime import datetime

def init_global():  # initialization of all global variables

    global global_id
    global_id = 0

    global result_name

    date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    result_name = "result/result_{}.txt".format(date)

    global files_list

    files_list = list()

    global logger
    logger = logging.getLogger('LOGGER')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('debug.log', 'w+', 'utf-8')
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
