"""
test_classifier: tests a classification data science project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""
from __future__ import annotations
import dataclasses
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import pandas as pd
import numpy as np
import sklearn.datasets

import amicus
from amicus import project
from amicus import simplify


def test_project():
    cancer_data = sklearn.datasets.load_breast_cancer()
    df = pd.DataFrame(
        data = np.c_[cancer_data['data'], cancer_data['target']],
        columns = np.append(cancer_data['feature_names'], ['target']))
    # Stores the pandas dataframe in an amicus Dataset wrapper to allow easy
    # access to both amicus and pandas methods.
    dataset = simplify.Dataset.from_dataframe(df = df)
    # Converts label to boolean type to correct numpy default above.
    dataset.change_datatype(columns = 'target', datatype = 'boolean')
    project = amicus.Project.create(
        name = 'wisconsin_cancer_project',
        settings = pathlib.Path('tests') / 'cancer_settings.ini',
        data = dataset,
        automatic = False)
    project.execute()
    print('test project workflow', project.workflow)
    print('test workflow paths', len(project.workflow.paths))
    print('test workflow endpoints', str(project.workflow.endpoints))
    print('test workflow roots', str(project.workflow.roots))
    return


if __name__ == '__main__':
    test_project()