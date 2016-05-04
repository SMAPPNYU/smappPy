"""
Module for cross-validation related functionality.

SMaPP Lab @ NYU
"""

import numpy as np
from random import shuffle
from sklearn.cross_validation import StratifiedShuffleSplit
from collections import Counter

def grouped_stratified_train_test_split(y, x, group_by=None, test_size=0.33, group_labeler=None, return_indices=False, **kwargs):
    """
    Split arrays or matrices into random training and test subsets. Subsets will contain equal proportions of each label in `y`.
    Based on StratifiedShuffleSplit from sklearn.cross_validation.

    if `group_by` is an iterable of length `len(y)`, indices with the same `group_by[i]` will be kept together in either the training or the test set.

    if `group_labeler` is a callable, it will be used to assign a label to a group of labels. The default is `lambda labels: int(np.round(np.average(labels)))`
    

    --------
    Example:

     X = np.array([[1, 2], [3, 4], [1, 4], [3, 1], [1, 4], [3, 1], [1, 4], [3, 1], [1, 4], [3, 1], [1, 4], [3, 1]])
     y = np.array([0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1])
     id = np.array([1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6])

     x_train, x_test, y_train, y_test = grouped_stratified_train_test_split(y,X,id)

    """

    if not group_labeler:
        group_labeler = lambda labels: int(np.round(np.average(labels)))

    group_indices = dict()
    group_labels = dict()
    for i,(label, group) in enumerate(zip(y, group_by)):
        if not group in group_labels:
            group_labels[group] = list()
            group_indices[group] = list()
        group_indices[group].append(i)
        group_labels[group].append(label)
    groups, labels = zip(*{ group: group_labeler(labels) for group, labels in group_labels.items() }.items())

    sss = StratifiedShuffleSplit(labels, 1, test_size=test_size, **kwargs)

    group_train_indices, group_test_indices = list(sss)[0]
    test_groups = [groups[i] for i in group_test_indices]
    train_groups = [groups[j] for j in group_train_indices]

    test_indices = [idx for group in test_groups for idx in group_indices[group]]
    train_indices = [idx for group in train_groups for idx in group_indices[group]]
    if return_indices:
        return train_indices, test_indices
    else:
        return x[train_indices], x[test_indices], y[train_indices], y[test_indices]

def coherence_score(X,y):
    """
    Compute the coherence of the sample X, Y, where some examples x_i == x_j but y_i != y_j, this will be less than 100%.

    ------------
    Example:

     X = np.array([[0, 1],[0, 1],[0, 2],[0, 2],[1, 1],[1, 1]])
     Y = np.arange(6)

     coherence_score(X, Y)
    """

    # make a frozen copy of X, so that its rows can be hashable
    x = X.copy()
    x.flags.writeable = False

    rows_labels = dict()
    for i in range(len(x)):
        row = x[i]
        key = hash(row.data)
        if not key in rows_labels:
            rows_labels[key] = list()
        rows_labels[key].append(y[i])
    coherences = [Counter(labels).most_common()[0][1] / float(len(labels)) for key,labels in rows_labels.items()]
    return np.average(coherences)
