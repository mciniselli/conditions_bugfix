import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')

import gzip
import json
import re
import os
import sys
from dateutil.parser import isoparse
from model import Repository, Commit
import traceback

from subprocess import Popen, PIPE, STDOUT

from construct_processing import *

from utils.inputoutput import WriteFile, ReadFile

from utils.settings import init_global
import utils.settings as settings

from ctypes import *

from utils.progress import get_progress_value, read_progress_file, update_progress_bar

data_path = 'input'

sha_regex = '[0-9a-f]{6,40}'


def extract_data(fix_commit, num_processed, file_name, id_internal, id_row):

    try:
        repo = Repository(fix_commit.repository)
        #repo.test(fix_commit)
        repo.miner(fix_commit, fix_commit.repository, num_processed, file_name, id_internal, id_row)


    except Exception as e:
        logging.error(f'exception: {type(e).__name__} {e.args}')
        print(traceback.format_exc())
    finally:
        repo.cleanup()


def main(file_names):

    logging.info(f'files count: {len(file_names)}')

    if os.path.exists("result")==False:
        os.makedirs("result")

    tot_processed = 0
    tot = len(file_names)
    for i, file_name in enumerate(file_names):
        logging.info(f'{file_name} # {str(i + 1)} of {tot}')
        try:
            with open(os.path.join(data_path, file_name)) as f:

                index_start=get_progress_value(file_name)

                print("INDEX START: {}".format(index_start))

                for i, line in enumerate(f):

                    if i<=index_start:
                        continue

                    data=json.loads(line)

                    tot_processed += 1

                    extract_data(Commit(
                        hash=data['id_commit'],
                        repository=data['repo'],
                        message=data['message'],
                        api_url=data['URL'],
                        created_at=data['date_commit'],
                        before=data['before_api'],
                        after=data['after_api'],
                        changes=data['modifications'],

                    ), i+1, data['file_path'], data['id_internal'], i)
                    #sys.exit(0)

                    # update progress bar
                    update_progress_bar(file_name, i)

                logging.info(f'total processed commits: {tot_processed}')
        except Exception as file_error:
            logging.error(f'file exception: {type(file_error).__name__} {file_error.args}')
            print(traceback.format_exc())

    print('+++ DONE +++')


if __name__ == "__main__":

    init_global()

    file_names = [f for f in os.listdir(data_path) if f.endswith('.txt')]

    settings.file_list=file_names

    read_progress_file()

    main(file_names)