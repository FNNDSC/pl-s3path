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
    VERSION = '0.1.1'
    MAX_NUMBER_OF_WORKERS = 1  # Override with integer value
    MIN_NUMBER_OF_WORKERS = 1  # Override with integer value
    MAX_CPU_LIMIT = ''  # Override with millicore value as string, e.g. '2000m'
    MIN_CPU_LIMIT = ''  # Override with millicore value as string, e.g. '2000m'
    MAX_MEMORY_LIMIT = ''  # Override with string, e.g. '1Gi', '2000Mi'
    MIN_MEMORY_LIMIT = ''  # Override with string, e.g. '1Gi', '2000Mi'
    MIN_GPU_LIMIT = 0  # Override with the minimum number of GPUs, as an integer, for your plugin
    MAX_GPU_LIMIT = 0  # Override with the maximum number of GPUs, as an integer, for your plugin

    # Fill out this with key-value output descriptive info (such as an output file path
    # relative to the output dir) that you want to save to the output meta file when
    # called with the --saveoutputmeta flag
    OUTPUT_META_DICT = {'prefix': ''}

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

        self.add_argument('--prefix', dest='prefix', type=str, optional=False,
                          help='prefix string for the cloud objects')


    def generateBucket(self, age):
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

            # is patient is more than 100 years old, assume something is not correct
            if patient_age_in_days > 36425:
                patient_age_in_days = -1
                series_date_valid = False

            print(str(patient_age_in_days) + ' days from series')
        except ValueError:
            series_date_valid = False
            print('Invalid SeriesDate or PatientBirthDate found')

        if not series_date_valid:
            try:
                study_datetime = datetime.datetime.strptime(study_date, '%Y%m%d')
                patient_birth_date_dateiime = \
                    datetime.datetime.strptime(patient_birth_date, '%Y%m%d')
                delta_from_series = study_datetime - patient_birth_date_dateiime
                patient_age_in_days = delta_from_series.days

                # is patient is more than 100 years old, assume something is not correct
                if patient_age_in_days > 36425:
                    patient_age_in_days = -1
                    study_date_valid = False

                print(str(patient_age_in_days) + ' days from study')
            except ValueError:
                study_date_valid = False
                print('Invalid SeriesDate or PatientBirthDate found')

        # compute patient age in days from patient age
        if not study_date_valid:
            try:
                # will just make it the dumb/fast way
                # 17M = 17* 364.25 / 12 days
                # 2Y = 2 * 364.25 days
                patient_age_reference = patient_age[-1].lower()
                patient_age_reference_scale = 1.
                if patient_age_reference == 'y':
                    patient_age_reference_scale = 364.25
                elif patient_age_reference == 'm':
                    patient_age_reference_scale = 364.25 / 12.

                patient_age_value = float(patient_age[:-1])
                patient_age_in_days = int(patient_age_value * patient_age_reference_scale)
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

        patient_age_in_days = \
            self.computeAge(study_date, series_date, patient_birth_date, patient_age)
        print(patient_age_in_days)

        patient_bucket = self.generateBucket(patient_age_in_days)
        print(patient_bucket)

        cloud_path = os.path.join(options.prefix, patient_bucket)
        # add cloud path to output.meta.json
        self.OUTPUT_META_DICT['prefix'] = cloud_path
        print(cloud_path)
        print('Done.')

# ENTRYPOINT
if __name__ == "__main__":
    app = S3Path()
    app.launch()
