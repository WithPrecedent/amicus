"""
analyst.steps
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0) 

Contents:

"""
from __future__ import annotations
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import numpy as np
import pandas as pd
import sklearn
import amicus


@dataclasses.dataclass
class Model(amicus.project.Step):
    """Wrapper for a Technique.

    An instance will try to return attributes from 'contents' if the attribute 
    is not found in the Step instance. 

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an 
            amicus instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        contents (Technique): stored Technique instance used by the 'implement' 
            method.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'implement' method is called. Defaults to an empty dict.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be at the end of a parallel workflow structure. Defaults to 
            True.
                                                
    """    
    name: str = 'model'
    contents: amicus.project.Technique = None
    iterations: Union[int, str] = 1
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = True





model_options = {
    'classify': {
        'adaboost': Tool(
            name = 'adaboost',
            module = 'sklearn.ensemble',
            algorithm = 'AdaBoostClassifier',
            transform_method = None),
        'baseline_classifier': Tool(
            name = 'baseline_classifier',
            module = 'sklearn.dummy',
            algorithm = 'DummyClassifier',
            required = {'strategy': 'most_frequent'},
            transform_method = None),
        'logit': Tool(
            name = 'logit',
            module = 'sklearn.linear_model',
            algorithm = 'LogisticRegression',
            transform_method = None),
        'random_forest': Tool(
            name = 'random_forest',
            module = 'sklearn.ensemble',
            algorithm = 'RandomForestClassifier',
            transform_method = None),
        'svm_linear': Tool(
            name = 'svm_linear',
            module = 'sklearn.svm',
            algorithm = 'SVC',
            required = {'kernel': 'linear', 'probability': True},
            transform_method = None),
        'svm_poly': Tool(
            name = 'svm_poly',
            module = 'sklearn.svm',
            algorithm = 'SVC',
            required = {'kernel': 'poly', 'probability': True},
            transform_method = None),
        'svm_rbf': Tool(
            name = 'svm_rbf',
            module = 'sklearn.svm',
            algorithm = 'SVC',
            required = {'kernel': 'rbf', 'probability': True},
            transform_method = None),
        'svm_sigmoid': Tool(
            name = 'svm_sigmoid ',
            module = 'sklearn.svm',
            algorithm = 'SVC',
            required = {'kernel': 'sigmoid', 'probability': True},
            transform_method = None),
        'tensorflow': Tool(
            name = 'tensorflow',
            module = 'tensorflow',
            algorithm = None,
            default = {
                'batch_size': 10,
                'epochs': 2},
            transform_method = None),
        'xgboost': Tool(
            name = 'xgboost',
            module = 'xgboost',
            algorithm = 'XGBClassifier',
            # data_dependent = 'scale_pos_weight',
            transform_method = None)},
    'cluster': {
        'affinity': Tool(
            name = 'affinity',
            module = 'sklearn.cluster',
            algorithm = 'AffinityPropagation',
            transform_method = None),
        'agglomerative': Tool(
            name = 'agglomerative',
            module = 'sklearn.cluster',
            algorithm = 'AgglomerativeClustering',
            transform_method = None),
        'birch': Tool(
            name = 'birch',
            module = 'sklearn.cluster',
            algorithm = 'Birch',
            transform_method = None),
        'dbscan': Tool(
            name = 'dbscan',
            module = 'sklearn.cluster',
            algorithm = 'DBSCAN',
            transform_method = None),
        'kmeans': Tool(
            name = 'kmeans',
            module = 'sklearn.cluster',
            algorithm = 'KMeans',
            transform_method = None),
        'mean_shift': Tool(
            name = 'mean_shift',
            module = 'sklearn.cluster',
            algorithm = 'MeanShift',
            transform_method = None),
        'spectral': Tool(
            name = 'spectral',
            module = 'sklearn.cluster',
            algorithm = 'SpectralClustering',
            transform_method = None),
        'svm_linear': Tool(
            name = 'svm_linear',
            module = 'sklearn.cluster',
            algorithm = 'OneClassSVM',
            transform_method = None),
        'svm_poly': Tool(
            name = 'svm_poly',
            module = 'sklearn.cluster',
            algorithm = 'OneClassSVM',
            transform_method = None),
        'svm_rbf': Tool(
            name = 'svm_rbf',
            module = 'sklearn.cluster',
            algorithm = 'OneClassSVM,',
            transform_method = None),
        'svm_sigmoid': Tool(
            name = 'svm_sigmoid',
            module = 'sklearn.cluster',
            algorithm = 'OneClassSVM',
            transform_method = None)},
    'regress': {
        'adaboost': Tool(
            name = 'adaboost',
            module = 'sklearn.ensemble',
            algorithm = 'AdaBoostRegressor',
            transform_method = None),
        'baseline_regressor': Tool(
            name = 'baseline_regressor',
            module = 'sklearn.dummy',
            algorithm = 'DummyRegressor',
            required = {'strategy': 'mean'},
            transform_method = None),
        'bayes_ridge': Tool(
            name = 'bayes_ridge',
            module = 'sklearn.linear_model',
            algorithm = 'BayesianRidge',
            transform_method = None),
        'lasso': Tool(
            name = 'lasso',
            module = 'sklearn.linear_model',
            algorithm = 'Lasso',
            transform_method = None),
        'lasso_lars': Tool(
            name = 'lasso_lars',
            module = 'sklearn.linear_model',
            algorithm = 'LassoLars',
            transform_method = None),
        'ols': Tool(
            name = 'ols',
            module = 'sklearn.linear_model',
            algorithm = 'LinearRegression',
            transform_method = None),
        'random_forest': Tool(
            name = 'random_forest',
            module = 'sklearn.ensemble',
            algorithm = 'RandomForestRegressor',
            transform_method = None),
        'ridge': Tool(
            name = 'ridge',
            module = 'sklearn.linear_model',
            algorithm = 'Ridge',
            transform_method = None),
        'svm_linear': Tool(
            name = 'svm_linear',
            module = 'sklearn.svm',
            algorithm = 'SVC',
            required = {'kernel': 'linear', 'probability': True},
            transform_method = None),
        'svm_poly': Tool(
            name = 'svm_poly',
            module = 'sklearn.svm',
            algorithm = 'SVC',
            required = {'kernel': 'poly', 'probability': True},
            transform_method = None),
        'svm_rbf': Tool(
            name = 'svm_rbf',
            module = 'sklearn.svm',
            algorithm = 'SVC',
            required = {'kernel': 'rbf', 'probability': True},
            transform_method = None),
        'svm_sigmoid': Tool(
            name = 'svm_sigmoid ',
            module = 'sklearn.svm',
            algorithm = 'SVC',
            required = {'kernel': 'sigmoid', 'probability': True},
            transform_method = None),
        'xgboost': Tool(
            name = 'xgboost',
            module = 'xgboost',
            algorithm = 'XGBRegressor',
            # data_dependent = 'scale_pos_weight',
            transform_method = None)}}
gpu_options = {
    'classify': {
        'forest_inference': Tool(
            name = 'forest_inference',
            module = 'cuml',
            algorithm = 'ForestInference',
            transform_method = None),
        'random_forest': Tool(
            name = 'random_forest',
            module = 'cuml',
            algorithm = 'RandomForestClassifier',
            transform_method = None),
        'logit': Tool(
            name = 'logit',
            module = 'cuml',
            algorithm = 'LogisticRegression',
            transform_method = None)},
    'cluster': {
        'dbscan': Tool(
            name = 'dbscan',
            module = 'cuml',
            algorithm = 'DBScan',
            transform_method = None),
        'kmeans': Tool(
            name = 'kmeans',
            module = 'cuml',
            algorithm = 'KMeans',
            transform_method = None)},
    'regressor': {
        'lasso': Tool(
            name = 'lasso',
            module = 'cuml',
            algorithm = 'Lasso',
            transform_method = None),
        'ols': Tool(
            name = 'ols',
            module = 'cuml',
            algorithm = 'LinearRegression',
            transform_method = None),
        'ridge': Tool(
            name = 'ridge',
            module = 'cuml',
            algorithm = 'RidgeRegression',
            transform_method = None)}}
self.contents['model'] = model_options[
    self.idea['analyst']['model_type']]
if self.idea['general']['gpu']:
    self.contents['model'].update(
        gpu_options[idea['analyst']['model_type']])
return self.contents










# def make_tensorflow_model(step: 'Technique', parameters: dict) -> None:
#     algorithm = None
#     return algorithm


#    def _downcast_features(self, dataset):
#        dataframes = ['x_train', 'x_test']
#        number_types = ['uint', 'int', 'float']
#        feature_bits = ['64', '32', '16']
#        for data in dataframes:
#            for column in data.columns.keys():
#                if (column in dataset.floats
#                        or column in dataset.integers):
#                    for number_type in number_types:
#                        for feature_bit in feature_bits:
#                            try:
#                                data[column] = data[column].astype()


#    def _set_feature_types(self):
#        self.type_interface = {'boolean': tensorflow.bool,
#                               'float': tensorflow.float16,
#                               'integer': tensorflow.int8,
#                               'string': object,
#                               'categorical': CategoricalDtype,
#                               'list': list,
#                               'datetime': datetime64,
#                               'timedelta': timedelta}


#    def _tensor_flow_model(self):
#        from keras.models import Sequential
#        from keras.layers import Dense, Dropout, Activation, Flatten
#        classifier = Sequential()
#        classifier.add(Dense(units = 6, kernel_initializer = 'uniform',
#            activation = 'relu', input_dim = 30))
#        classifier.add(Dense(units = 6, kernel_initializer = 'uniform',
#            activation = 'relu'))
#        classifier.add(Dense(units = 1, kernel_initializer = 'uniform',
#            activation = 'sigmoid'))
#        classifier.compile(optimizer = 'adam',
#                           loss = 'binary_crossentropy',
#                           metrics = ['accuracy'])
#        return classifier
#        model = Sequential()
#        model.add(Activation('relu'))
#        model.add(Activation('relu'))
#        model.add(Dropout(0.25))
#        model.add(Flatten())
#        for layer_size in self.parameters['dense_layer_sizes']:
#            model.add(Dense(layer_size))
#            model.add(Activation('relu'))
#        model.add(Dropout(0.5))
#        model.add(Dense(2))
#        model.add(Activation('softmax'))
#        model.compile(loss = 'categorical_crossentropy',
#                      optimizer = 'adadelta',
#                      metrics = ['accuracy'])
#        return model



# def make_torch_model(step: 'Technique', parameters: dict) -> None:
#     algorithm = None
#     return algorithm


# def make_stan_model(step: 'Technique', parameters: dict) -> None:
#     algorithm = None
#     return algorithm
