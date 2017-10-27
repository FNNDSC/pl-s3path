#                                                            _
# S3 Path ds app
#
# (c) 2016 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#



import datetime
import json
import os
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
            '--seriesUIDS',
            dest='series_uids',
            type=str,
            default=',',
            optional=True,
            help='Series UIDs to be retrieved')

    def generateKey(self, age):
        ageList = [
            -1,
            0,
            14,
            60,
            165,
            240,
            285,
            330,
            405,
            480,
            555,
            615,
            660,
            720,
            900,
            99999,
        ]
        # default age range
        from_age = ageList[0]
        to_age = ageList[1]
    
        previous = 0
        for item in ageList:
            if (age - previous >= 0) and (age - item < 0):
                from_age = previous
                to_age = item
                break
            previous = item
    
        return str(from_age) + '_' + str(to_age)

    def computeAge(self, study_date, series_date, patient_birth_date, patient_age):
        series_date_valid = True
        study_date_valid = True
        patient_age_valid = True
        print('StudyDate ' + study_date)
        print('SeriesDate ' + series_date)
        print('PatientBirthDate ' + patient_birth_date)
        print('PatientAge ' + patient_age)
    
        patient_age_in_days = -1
 
        # compute patient age in days from series date and patient birthdate
        try:
            series_datetime = datetime.datetime.strptime(series_date, '%Y%m%d')
            patient_birth_date_dateiime = datetime.datetime.strptime(patient_birth_date, '%Y%m%d')
            delta_from_series = series_datetime - patient_birth_date_dateiime
            patient_age_in_days = delta_from_series.days

            if patient_age_in_days > 3615:
                patient_age_in_days = -1
                series_date_valid = False

            print(str(patient_age_in_days) + ' days from series')
        except ValueError:
            series_date_valid = False
            print('Invalid SeriesDate or PatientBirthDate found')
    
        if not series_date_valid:
            try:
                study_datetime = datetime.datetime.strptime(study_date, '%Y%m%d')
                patient_birth_date_dateiime = datetime.datetime.strptime(patient_birth_date, '%Y%m%d')
                delta_from_series = study_datetime - patient_birth_date_dateiime
                patient_age_in_days = delta_from_series.days

                if patient_age_in_days > 3615:
                    patient_age_in_days = -1
                    study_date_valid = False
    
                print(str(patient_age_in_days) + ' days from study')
            except ValueError:
                study_date_valid = False
                print('Invalid SeriesDate or PatientBirthDate found')
    
        # compute patient age in days from patient age
        if not study_date_valid:
            try:
                patient_age_reference = patient_age[-1].lower()
                patient_age_value = patient_age[-3:-1]
                age_datetime = datetime.datetime.strptime(patient_age_value, '%' + patient_age_reference)
                age_datetime_base = datetime.datetime.strptime('00', '%' + patient_age_reference)
                delta_from_age = age_datetime - age_datetime_base
                patient_age_in_days = delta_from_age.days
                print(str(patient_age_in_days) + ' days from age')
            except ValueError:
                print('Invalid PatientAge found')

        return patient_age_in_days

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """


        # create dummy series file with all series
        series_file = os.path.join(options.inputdir, 'results.json')

        # uids to be fetched from success.txt
        uids = options.series_uids.split(',')
        uids_set = set(uids)

        # parser series file
        data_file = open(series_file, 'r')
        data = json.load(data_file)
        data_file.close()
        series_data = data['query']['data']
        filtered_uids = [
            series for series in series_data if str(series['uid']['value']) in uids_set]
        
        first_series = filtered_uids[0]

        patient_birth_date = first_series['PatientBirthDate']['value']
        patient_age = first_series['PatientAge']['value']
        series_date = first_series['SeriesDate']['value']
        study_date = first_series['StudyDate']['value']

        patient_age_in_days = self.computeAge(study_date, series_date, patient_birth_date, patient_age)
        print(patient_age_in_days)
        print('Done.')

# ENTRYPOINT
if __name__ == "__main__":
    app = S3Path()
    app.launch()
