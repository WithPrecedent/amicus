"""
analyst.algorithms
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    
    
"""
from __future__ import annotations
import copy
import dataclasses
import functools
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import numpy as np
import pandas as pd
import scipy
import sklearn

import amicus


    'scale': {
        'gauss': Tool(
            name = 'gauss',
            module = None,
            algorithm = 'Gaussify',
            default = {'standardize': False, 'copy': False},
            selected = True,
            required = {'rescaler': 'standard'}),
        'maxabs': Tool(
            name = 'maxabs',
            module = 'sklearn.preprocessing',
            algorithm = 'MaxAbsScaler',
            default = {'copy': False},
            selected = True),
        'minmax': Tool(
            name = 'minmax',
            module = 'sklearn.preprocessing',
            algorithm = 'MinMaxScaler',
            default = {'copy': False},
            selected = True),
        'normalize': Tool(
            name = 'normalize',
            module = 'sklearn.preprocessing',
            algorithm = 'Normalizer',
            default = {'copy': False},
            selected = True),
        'quantile': Tool(
            name = 'quantile',
            module = 'sklearn.preprocessing',
            algorithm = 'QuantileTransformer',
            default = {'copy': False},
            selected = True),
        'robust': Tool(
            name = 'robust',
            module = 'sklearn.preprocessing',
            algorithm = 'RobustScaler',
            default = {'copy': False},
            selected = True),
        'standard': Tool(
            name = 'standard',
            module = 'sklearn.preprocessing',
            algorithm = 'StandardScaler',
            default = {'copy': False},
            selected = True)},
    'split': {
        'group_kfold': Tool(
            name = 'group_kfold',
            module = 'sklearn.model_selection',
            algorithm = 'GroupKFold',
            default = {'n_splits': 5},
            runtime = {'random_state': 'seed'},
            selected = True,
            fit_method = None,
            transform_method = 'split'),
        'kfold': Tool(
            name = 'kfold',
            module = 'sklearn.model_selection',
            algorithm = 'KFold',
            default = {'n_splits': 5, 'shuffle': False},
            runtime = {'random_state': 'seed'},
            selected = True,
            required = {'shuffle': True},
            fit_method = None,
            transform_method = 'split'),
        'stratified': Tool(
            name = 'stratified',
            module = 'sklearn.model_selection',
            algorithm = 'StratifiedKFold',
            default = {'n_splits': 5, 'shuffle': False},
            runtime = {'random_state': 'seed'},
            selected = True,
            required = {'shuffle': True},
            fit_method = None,
            transform_method = 'split'),
        'time': Tool(
            name = 'time',
            module = 'sklearn.model_selection',
            algorithm = 'TimeSeriesSplit',
            default = {'n_splits': 5},
            runtime = {'random_state': 'seed'},
            selected = True,
            fit_method = None,
            transform_method = 'split'),
        'train_test': Tool(
            name = 'train_test',
            module = 'sklearn.model_selection',
            algorithm = 'ShuffleSplit',
            default = {'test_size': 0.33},
            runtime = {'random_state': 'seed'},
            required = {'n_splits': 1},
            selected = True,
            fit_method = None,
            transform_method = 'split')},
    'encode': {
        'backward': Tool(
            name = 'backward',
            module = 'category_encoders',
            algorithm = 'BackwardDifferenceEncoder',
            data_dependent = {'cols': 'categoricals'}),
        'basen': Tool(
            name = 'basen',
            module = 'category_encoders',
            algorithm = 'BaseNEncoder',
            data_dependent = {'cols': 'categoricals'}),
        'binary': Tool(
            name = 'binary',
            module = 'category_encoders',
            algorithm = 'BinaryEncoder',
            data_dependent = {'cols': 'categoricals'}),
        'dummy': Tool(
            name = 'dummy',
            module = 'category_encoders',
            algorithm = 'OneHotEncoder',
            data_dependent = {'cols': 'categoricals'}),
        'hashing': Tool(
            name = 'hashing',
            module = 'category_encoders',
            algorithm = 'HashingEncoder',
            data_dependent = {'cols': 'categoricals'}),
        'helmert': Tool(
            name = 'helmert',
            module = 'category_encoders',
            algorithm = 'HelmertEncoder',
            data_dependent = {'cols': 'categoricals'}),
        'james_stein': Tool(
            name = 'james_stein',
            module = 'category_encoders',
            algorithm = 'JamesSteinEncoder',
            data_dependent = {'cols': 'categoricals'}),
        'loo': Tool(
            name = 'loo',
            module = 'category_encoders',
            algorithm = 'LeaveOneOutEncoder',
            data_dependent = {'cols': 'categoricals'}),
        'm_estimate': Tool(
            name = 'm_estimate',
            module = 'category_encoders',
            algorithm = 'MEstimateEncoder',
            data_dependent = {'cols': 'categoricals'}),
        'ordinal': Tool(
            name = 'ordinal',
            module = 'category_encoders',
            algorithm = 'OrdinalEncoder',
            data_dependent = {'cols': 'categoricals'}),
        'polynomial': Tool(
            name = 'polynomial_encoder',
            module = 'category_encoders',
            algorithm = 'PolynomialEncoder',
            data_dependent = {'cols': 'categoricals'}),
        'sum': Tool(
            name = 'sum',
            module = 'category_encoders',
            algorithm = 'SumEncoder',
            data_dependent = {'cols': 'categoricals'}),
        'target': Tool(
            name = 'target',
            module = 'category_encoders',
            algorithm = 'TargetEncoder',
            data_dependent = {'cols': 'categoricals'}),
        'woe': Tool(
            name = 'weight_of_evidence',
            module = 'category_encoders',
            algorithm = 'WOEEncoder',
            data_dependent = {'cols': 'categoricals'})},
    'mix': {
        'polynomial': Tool(
            name = 'polynomial_mixer',
            module = 'sklearn.preprocessing',
            algorithm = 'PolynomialFeatures',
            default = {
                'degree': 2,
                'interaction_only': True,
                'include_bias': True}),
        'quotient': Tool(
            name = 'quotient',
            module = None,
            algorithm = 'QuotientFeatures'),
        'sum': Tool(
            name = 'sum',
            module = None,
            algorithm = 'SumFeatures'),
        'difference': Tool(
            name = 'difference',
            module = None,
            algorithm = 'DifferenceFeatures')},
    'cleave': {
        'cleaver': Tool(
            name = 'cleaver',
            module = 'amicus.analyst.algorithms',
            algorithm = 'Cleaver')},
    'sample': {
        'adasyn': Tool(
            name = 'adasyn',
            module = 'imblearn.over_sampling',
            algorithm = 'ADASYN',
            default = {'sampling_strategy': 'auto'},
            runtime = {'random_state': 'seed'},
            fit_method = None,
            transform_method = 'fit_resample'),
        'cluster': Tool(
            name = 'cluster',
            module = 'imblearn.under_sampling',
            algorithm = 'ClusterCentroids',
            default = {'sampling_strategy': 'auto'},
            runtime = {'random_state': 'seed'},
            fit_method = None,
            transform_method = 'fit_resample'),
        'knn': Tool(
            name = 'knn',
            module = 'imblearn.under_sampling',
            algorithm = 'AllKNN',
            default = {'sampling_strategy': 'auto'},
            runtime = {'random_state': 'seed'},
            fit_method = None,
            transform_method = 'fit_resample'),
        'near_miss': Tool(
            name = 'near_miss',
            module = 'imblearn.under_sampling',
            algorithm = 'NearMiss',
            default = {'sampling_strategy': 'auto'},
            runtime = {'random_state': 'seed'},
            fit_method = None,
            transform_method = 'fit_resample'),
        'random_over': Tool(
            name = 'random_over',
            module = 'imblearn.over_sampling',
            algorithm = 'RandomOverSampler',
            default = {'sampling_strategy': 'auto'},
            runtime = {'random_state': 'seed'},
            fit_method = None,
            transform_method = 'fit_resample'),
        'random_under': Tool(
            name = 'random_under',
            module = 'imblearn.under_sampling',
            algorithm = 'RandomUnderSampler',
            default = {'sampling_strategy': 'auto'},
            runtime = {'random_state': 'seed'},
            fit_method = None,
            transform_method = 'fit_resample'),
        'smote': Tool(
            name = 'smote',
            module = 'imblearn.over_sampling',
            algorithm = 'SMOTE',
            default = {'sampling_strategy': 'auto'},
            runtime = {'random_state': 'seed'},
            fit_method = None,
            transform_method = 'fit_resample'),
        'smotenc': Tool(
            name = 'smotenc',
            module = 'imblearn.over_sampling',
            algorithm = 'SMOTENC',
            default = {'sampling_strategy': 'auto'},
            runtime = {'random_state': 'seed'},
            data_dependent = {
                'categorical_features': 'categoricals_indices'},
            fit_method = None,
            transform_method = 'fit_resample'),
        'smoteenn': Tool(
            name = 'smoteenn',
            module = 'imblearn.combine',
            algorithm = 'SMOTEENN',
            default = {'sampling_strategy': 'auto'},
            runtime = {'random_state': 'seed'},
            fit_method = None,
            transform_method = 'fit_resample'),
        'smotetomek': Tool(
            name = 'smotetomek',
            module = 'imblearn.combine',
            algorithm = 'SMOTETomek',
            default = {'sampling_strategy': 'auto'},
            runtime = {'random_state': 'seed'},
            fit_method = None,
            transform_method = 'fit_resample')},
    'reduce': {
        'kbest': Tool(
            name = 'kbest',
            module = 'sklearn.feature_selection',
            algorithm = 'SelectKBest',
            default = {'k': 10, 'score_func': 'f_classif'},
            selected = True),
        'fdr': Tool(
            name = 'fdr',
            module = 'sklearn.feature_selection',
            algorithm = 'SelectFdr',
            default = {'alpha': 0.05, 'score_func': 'f_classif'},
            selected = True),
        'fpr': Tool(
            name = 'fpr',
            module = 'sklearn.feature_selection',
            algorithm = 'SelectFpr',
            default = {'alpha': 0.05, 'score_func': 'f_classif'},
            selected = True),
        'custom': Tool(
            name = 'custom',
            module = 'sklearn.feature_selection',
            algorithm = 'SelectFromModel',
            default = {'threshold': 'mean'},
            runtime = {'estimator': 'algorithm'},
            selected = True),
        'rank': Tool(
            name = 'rank',
            module = 'amicus.critic.rank',
            algorithm = 'RankSelect',
            selected = True),
        'rfe': Tool(
            name = 'rfe',
            module = 'sklearn.feature_selection',
            algorithm = 'RFE',
            default = {'n_features_to_select': 10, 'step': 1},
            runtime = {'estimator': 'algorithm'},
            selected = True),
        'rfecv': Tool(
            name = 'rfecv',
            module = 'sklearn.feature_selection',
            algorithm = 'RFECV',
            default = {'n_features_to_select': 10, 'step': 1},
            runtime = {'estimator': 'algorithm'},
            selected = True)}}
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

 