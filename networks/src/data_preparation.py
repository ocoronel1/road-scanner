# -*- coding: future_fstrings -*-


from itertools import chain
import numpy as np
import pandas as pd
import os
from glob import glob
import params
from sklearn.model_selection import train_test_split


def get_first_folder_after_base(path, base):
  _path = path.replace(base, '', 1)
  folders = []
  while 1:
    _path, folder = os.path.split(_path)
    if _path == "/":
        return folder

def load_metadata(data_folder=params.DATA_FOLDER):
    '''
    Scans the file system to index the available files.
    Parses the file name to extract the metadata

    Args:
      data_folder: The path to the data folder

    Returns:
      The metadata DataFrame with a file system mapping of the data (images)
    '''
    base_path = os.path.join(os.getcwd(), data_folder)
    search_path = os.path.join(base_path, '**/*.jpg')
    file_system_scan = glob(search_path, recursive=True)

    files = [file for file in file_system_scan if os.path.getsize(file)]

    metadata = pd.DataFrame([{
        'path': file,
        'label': get_first_folder_after_base(file, base_path)} for file in files])

    return metadata


def preprocess_metadata(metadata,
                        scenic_folder=params.SCENIC_FOLDER,
                        non_scenic_folder=params.NON_SCENIC_FOLDER,
                        minimum_cases=params.MIN_CASES):
    '''
    Preprocessing of the metadata df.

    Args:
      metadata: The metadata DataFrame

    Returns:
      metadata: The preprocessed metadata DataFrame and the 
      valid labels.
    '''
    print(f'Total records:{len(metadata)}.')
    label_count = metadata.groupby('label').count()
    print(f'{label_count}')
    
    # TODO: make this label agnostic
    
    non_scenic = metadata[metadata['label'] == 'non-scenic']
    scenic = metadata[metadata['label'] == 'scenic']
    
    scenic_under = scenic.sample(min(len(scenic), len(non_scenic)))
    balanced_metadata = pd.concat([scenic_under, non_scenic], axis=0)
    
    print(f'Balancing data')
    label_count = balanced_metadata.groupby('label').count()
    print(f'{label_count}')

    print('Total records:{}.'.format((balanced_metadata.shape[0])))

    return balanced_metadata, list(balanced_metadata.label.unique())


def stratify_train_test_split(metadata):
    '''
    Creates a train/test stratification of the dataset

    Args:
      metadata: The metadata DataFrame

    Returns:
      train, valid: The stratified train/test DataFrames
    '''
    stratify = metadata['label']
    train, valid = train_test_split(metadata,
                                    test_size=0.25,
                                    random_state=2018,
                                    stratify=stratify)
    return train, valid


if __name__ == '__main__':
    metadata = load_metadata()
    metadata, labels = preprocess_metadata(metadata)
    train, valid = stratify_train_test_split(metadata)
