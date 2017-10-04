#                                                            _
# Pacs query app
#
# (c) 2016 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#



import os
import json
import time
import shutil
import subprocess

# import the Chris app superclass
from chrisapp.base import ChrisApp

class S3Path(ChrisApp):
    '''
    Create file out.txt witht the directory listing of the directory
    given by the --dir argument.
    '''
    AUTHORS = 'FNNDSC (dev@babyMRI.org)'
    SELFPATH = os.path.dirname(__file__)
    SELFEXEC = os.path.basename(__file__)
    EXECSHELL = 'python3'
    TITLE = 'S3 Path'
    CATEGORY = ''
    TYPE = 'ds'
    DESCRIPTION = 'An app to adapt pl-pacsquery output to pl-s3retrieve input'
    DOCUMENTATION = 'http://wiki'
    LICENSE = 'Opensource (MIT)'
    VERSION = '0.1'

    def define_parameters(self):
        """ Define parameters """
        self.add_argument(
            '--seriesFile',
            dest='series_file',
            type=str,
            default='',
            optional=True,
            help='Location of the file containing the series description.')

        self.add_argument(
            '--seriesUIDS',
            dest='series_uids',
            type=str,
            default=',',
            optional=True,
            help='Series UIDs to be retrieved')

    def run(self, options):
        """ Run plugin """
        # create dummy series file with all series
        series_file = os.path.join(options.inputdir, 'success.txt')
        if options.series_file != '':
            series_file = options.series_file

        # uids to be fetched from success.txt
        uids = options.series_uids.split(',')
        uids_set = set(uids)

        # parser series file
        data_file = open(series_file, 'r')
        data = json.load(data_file)
        data_file.close()
        filtered_uids = [
            series for series in data['data'] if str(series['uid']['value']) in uids_set]

        print('Done.')

# ENTRYPOINT
if __name__ == "__main__":
    app = S3Path()
    app.launch()
