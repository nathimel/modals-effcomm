"""Script to compute the IB theoretical bound."""

import scipy
import numpy as np

from modals.modal_meaning import ModalMeaningSpace, ModalMeaningPoint
from ib_measures import information_rate, expected_distortion, generate_kl_divergence, generate_meaning_distribution, DEFAULT_AGENT, DEFAULT_DECAY, DEFAULT_UTILITY

DEFAULT_NUM_ITER = 10


# default language for IB to interface with RSA
from modals.modal_language import ModalLanguage, ModalExpression, ModalMeaning



# reverse deterministic annealing algorithm (Zaslavsky & Tishby, 2019)
def get_curve(
    prior: np.ndarray,
    space: ModalMeaningSpace,
    max_lang_size: int,
    num_points: int = 1500,
    decay: float = DEFAULT_DECAY,
    utility: str = DEFAULT_UTILITY,
) -> np.ndarray:
    """
    Args:
        prior: array of shape `|meanings|`

        max_lang_size: int representing the maximum number of words a system can have. To support perfect informativity, should be greater than or equal to the number of meanings.

        num_points: int representing how many points to compute of the IB curve

        decay: parameter for meaning distribution p(u|m) generation

        utility: parameter for meaning distribution p(u|m) generation

    Returns:
        an array of shape `(num_points, 2)` representing the list of (comm_cost, complexity) points on the information plane.
    """
    init = np.eye(max_lang_size)

    kl_dist_mat = generate_kl_divergence(space, decay, utility)
    meanings = generate_meaning_distribution(space, decay, utility)

    EDKL = lambda encoder, decoder: expected_distortion(
        source=prior,
        encoder=encoder,
        decoder=decoder,
        kl_divergence=kl_dist_mat,
    )



    points = []
    complexity = lambda encoder: information_rate(source=prior, encoder=encoder)
    # comm_cost = lambda encoder: 

    logsp = np.logspace(2, 0, num=num_points)
    for beta in logsp:
        q_w_m = ib_method(
            p_x=prior,
            p_y_x=meanings,
            Z=max_lang_size,
            beta=beta,
            init=init,
            num_iter=100,
        )

        points.append(())

        init = q_w_m

# code belongs to Chen et. al. (2022) https://github.com/mahowak/deictic_adverbs/blob/master/run_ib_new.py
def ib_method(
    p_x, 
    p_y_x, 
    Z, 
    beta, 
    init, 
    num_iter=DEFAULT_NUM_ITER, 
    temperature = 1,
    ):
    """ Find encoder q(Z|X) to minimize J = I[X:Z] - beta * I[Y:Z].
    
    Args:
        p_x: array of shape `|X|` representing the source distribution, p(x)

        p_y_x: array of shape `(|X|, |Y|)` representing the conditional distribution over targets Y, given the value of the source variable X

        Z: int representing the size of the support of the representation variable, Z.

    Returns:
        an array of shape `(|X|, |Z|)`, representing the conditional distribution over representations Z given the source variable X.
    """
    # Support size of X
    X = p_x.shape[-1]

    # Support size of Y
    Y = p_y_x.shape[-1]

    # Randomly initialize the conditional distribution q(z|x)
    q_z_x = init #scipy.special.softmax(np.random.randn(X, Z), -1) # shape (X, Z)
    p_y_x = p_y_x[:, None, :] # shape (X, 1, Y)
    p_x = p_x[:, None] # shape (X, 1)

    # Blahut-Arimoto iteration to find the minimizing q(z|x)
    for _ in range(num_iter):
        q_xz = p_x * q_z_x # Joint distribution q(x,z), shape X x Z
        q_z = q_xz.sum(axis=0, keepdims=True) # Marginal distribution q(z), shape 1 x Z
        q_y_z = ((q_xz / q_z)[:, :, None] * p_y_x).sum(axis=0, keepdims=True) # Conditional decoder distribution q(y|z), shape 1 x Z x Y
        d = ( 
            scipy.special.xlogy(p_y_x, p_y_x)
            - scipy.special.xlogy(p_y_x, q_y_z) # negative KL divergence -D[p(y|x) || q(y|z)]
        ).sum(axis=-1) # expected distortion over Y; shape X x Z
        q_z_x = scipy.special.softmax((np.log(q_z) - beta*d)/temperature, axis=-1) # Conditional encoder distribution q(z|x) = 1/Z q(z) e^{-beta*d}

    return q_z_x