#                                                            _
# S3 Path ds app
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
    Compute the path of a DICOM series stored in Amazon S3 and save it to the output meta
    JSON file with the key 's3path'
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

    # Fill out this with key-value output descriptive info (such as an output file path
    # relative to the output dir) that you want to save to the output meta file when
    # called with the --saveoutputmeta flag
    OUTPUT_META_DICT = {}

    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        """
        self.add_argument(
            '--seriesFile',
            dest='series_file',
            type=ChrisApp.path,
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
        """
        Define the code to be run by this plugin app.
        """
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

        print(filtered_uids)
        print('Done.')

# ENTRYPOINT
if __name__ == "__main__":
    app = S3Path()
    app.launch()
