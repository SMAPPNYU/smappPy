"""
Math functions useful for smapp tasks

@auth dpb
@date 7/08/2014
"""

import numpy as np
import scipy as sp

def kl_divergence(p,q):
    """
    Kullback-Leibler divergence 
    (http://en.wikipedia.org/wiki/Kullback-Leibler_divergence)
    AKA information divergence, information gain, relative entropy
    A "directed divergence between two distributions."

    Parameters p and q must be array-like objects (numpy arrays)

    NOTE: scipy.stats.entropy given two distributions purportedly computes KL
    divergence, and will normalize both distributions if they do not sum to 1.
    Tested, scipy.stats.entropy produces exactly same results.
    """
    return np.sum(np.where(p!=0, p * np.log(p/q), 0))

def js_divergence(p, q):
    """
    Jensen-Shannon divergence, symmetric divg. based on KL divergence
    (http://en.wikipedia.org/wiki/Jensen-Shannon_divergence)
    AKA information radius, total divergence to the average

    Parameters p and q must be array-like objects (numpy arrays).
    """
    m = .5 * (p+q)
    return .5 * (kl_divergence(p,m) + kl_divergence(q,m))

def js_distance(p, q):
    """
    Jensen-Shannon distance (square root of divergence)

    Parameters p and q must be array-like objects (numpy arrays).
    """
    return np.sqrt(js_divergence(p,q))

def log_loss(actual, predicted, epsilon=1e-15):
    """
    Calculates and returns the log loss (error) of a set of predicted probabilities
    (hint: see sklearn classifier's predict_proba methods).

    Source: https://www.kaggle.com/wiki/LogarithmicLoss
    
    In plain English, this error metric is typically used where you have to predict 
    that something is true or false with a probability (likelihood) ranging from 
    definitely true (1) to equally true (0.5) to definitely false(0).

    Note: also see (and use) scikitlearn: 
    http://scikit-learn.org/stable/modules/generated/sklearn.metrics.log_loss.html#sklearn.metrics.log_loss
    """
    predicted = sp.maximum(epsilon, predicted)
    predicted = sp.minimum(1-epsilon, predicted)
    ll = sum(actual*sp.log(predicted) + sp.subtract(1,actual)*sp.log(sp.subtract(1,predicted)))
    ll = ll * -1.0/len(actual)
    return ll


