"""Configs for the run-1.
"""
from pathlib import Path

from nna.params import EXCERPT_LENGTH

PROJECT_NAME = 'megan'

#   DEFAULT values
default_config = {
    'batch_size': 58,
    'epochs': 1000,
    'patience': -1,
    'weight_decay': 0.001,
    'augmentadSize': 200,
    'CNNLayer_count': 1,
    'CNN_filters_1': 45,
    'CNN_filters_2': 64,
    'device': 0,
    # augmentation params
    'pitch_shift_n_steps': 2.2,
    'time_stretch_factor': 0.8,
    'noise_factor': 0.001,
    'roll_rate': 1.1,
    # ['pitch_shift':0,'time_stretch':1,'noise_factor':2, 'roll_rate':3]
    'aug_ID': 3,
    #     'lr': lr,
    #     'momentum': momentum,
}

TAXO_COUNT_LIMIT = 25
SAMPLE_LENGTH_LIMIT = 10

TAXONOMY_FILE_PATH = Path(
    '/home/enis/projects/nna/src/nna/assets/taxonomy/taxonomy.yaml')

src_path = '/scratch/enis/data/nna/labeling/megan/AudioSamplesPerSite/'
MEGAN_LABELED_FILES_INFO_PATH = src_path + 'meganLabeledFiles_wlenV1.txt'
resources_folder = ('/scratch/enis/archive/' +
                    'forks/cramer2020icassp/resources/')
CSV4MEGAN_EXCELL_CLEANED  = (resources_folder + 'Sheet1(1).csv')
IGNORE_FILES = set([
    'S4A10268_20190610_103000_bio_anth.wav',  # has two topology bird/plane
])


EXCERPT_LENGTH = 10


EXCELL_NAMES2CODE = {
        'anth': '0.0.0',
        'auto': '0.1.0',
        'bio': '1.0.0',
        'bird': '1.1.0',
        'bug': '1.3.0',
        'dgs': '1.1.7',
        'flare': '0.4.0',
        'fox': '1.2.4',
        'geo': '2.0.0',
        'grouse': '1.1.8',
        'loon': '1.1.3',
        'mam': '1.2.0',
        'plane': '0.2.0',
        'ptarm': '1.1.8',
        'rain': '2.1.0',
        'seab': '1.1.5',
        'silence': '3.0.0',
        'songbird': '1.1.10',
        'unknown': 'X.X.X',
        'water': '2.2.0',
        'x': 'X.X.X',
    }