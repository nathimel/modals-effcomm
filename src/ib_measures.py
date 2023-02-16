import numpy as np

from modals.modal_language import ModalLanguage, ModalMeaningSpace
from altk.effcomm.agent import Speaker, Listener, LiteralSpeaker
from modals.modal_measures import half_credit, indicator

DEFAULT_DECAY = 1e-1
DEFAULT_UTILITY = "half_credit"

##############################################################################
# Converting from languages to IB quantities
##############################################################################

# TODO: Move this to altk!
class BayesianListener(Listener):
    """A Bayesian reciever chooses an interpretation according to p(meaning | word), where

        P(meanings | words) = P(meanings | words) * P(meanings) / P(words)

    Furthermore, we sometimes require that each word w is deterministically interpreted as meaning \hat{m} as follows:

        \hat{m}_{w}(u) = sum_m [ p(m|w) * m(u) ]

    """

    def __init__(self, speaker: Speaker, prior: np.ndarray, name: str = None):
        weights = bayes(speaker.normalized_weights(), prior)
        super().__init__(speaker.language, weights=weights, name=name)

def deterministic_decoder(decoder: np.ndarray, meaning_distributions: np.ndarray) -> np.ndarray:
    """Compute \hat{m}_{w}(u) = sum_m [ p(m|w) * m(u) ]

    Args:
        decoder: array of shape `(|words|, |meanings|)`

        meaning_distributions: array of shape `(|meanings|, |meanings|)`
    
    Returns:
        array of shape `(|words|, |meanings|)` representing the 'optimal' deterministic decoder
    """
    return marginalize(decoder, meaning_distributions)

def ib_complexity(
    language: ModalLanguage, 
    prior: np.ndarray, 
    ) -> float:
    """Compute the encoder complexity of a language."""
    return information_rate(
        source=prior,
        encoder=language_to_ib_encoder_decoder(
            language,
            )["encoder"],
    )

def ib_comm_cost(
    language: ModalLanguage, 
    prior: np.ndarray, 
    decay: float,
    utility: str,
    ) -> float:
    """Compute the expected KL-divergence betweeen speaker and listener meanings for a language.
    
    Args:
        language: the ModalLanguage to measure

        prior: communicative need distribution

        decay: parameter for meaning distribution p(u|m) generation

        utility: parameter for meaning distribution p(u|m) generation

    Returns:
        the communicative cost, E[D[M || \hat{M}]] in bits.
    """
    system = language_to_ib_encoder_decoder(language, prior)
    encoder = system["encoder"]
    decoder = system["decoder"]

    meanings = generate_meaning_distributions(space, decay, utility)
    space = language.universe
    
    return expected_distortion_ib(
        source=prior,
        encoder=encoder,
        encoder_meanings=meanings,
        decoder_meanings=deterministic_decoder(decoder, meanings),
    )

def language_to_ib_encoder_decoder(
    language: ModalLanguage, 
    prior: np.ndarray,
    ) -> dict[str, np.ndarray]:
    """Convert a ModalLanguage, a mapping of words to meanings, to IB encoder, q(w|m) and IB decoder q(m|w).
    
    Args:
        language: the lexicon from which to infer a speaker (encoder).

        prior: communicative need distribution
    
    Returns:
        a dict of the form 
        {
            "encoder": np.ndarray of shape `(|meanings|, |words|)`,
            "decoder": np.ndarray of shape `(|words|, |meanings|)`,
        }
    """
    # In the IB framework, the encoder is a literal speaker and the decoder is a bayes optimal listener.
    speaker = LiteralSpeaker(language)
    listener = BayesianListener(speaker, prior)
    return {
        "encoder": speaker.normalized_weights(),
        "decoder": listener.normalized_weights(),
    }

def ib_encoder_to_decoder(
    encoder: np.ndarray,
    prior: np.ndarray,
    space: ModalMeaningSpace,
) -> np.ndarray:
    speaker = LiteralSpeaker(ModalLanguage.default_language_from_space(space))
    speaker.weights = encoder
    listener = BayesianListener(speaker, prior)
    return listener.normalized_weights()

def generate_meaning_distributions(
    space: ModalMeaningSpace, 
    decay: float = DEFAULT_DECAY, 
    utility: str = DEFAULT_UTILITY,
    ) -> np.ndarray:
    """Generate a conditional distribution over world states given meanings, p(u|m), for each meaning.

    Args:
        space: the ModalMeaningSpace on which meanings are defined

        decay: a float in [0,1]. controls informativity, by decaying how much probability mass is assigned to perfect recoveries. As decay approaches 0, only perfect recovery is rewarded (which overrides any partial credit structure built into the utility/cost function). As decay approaches 1, the worst guesses become most likely.

        utility: {'indicator', 'half_credit'} whether to reward only perfect recovery of meaning points, or whether to give half credit for a correctly guessed axis of meaning (a force or a flavor).
    
    Returns:
        p_u_m: an array of shape `(|space.referents|, |space.referents|)`
    """

    cost = lambda x, y: 1 -  {"half_credit": half_credit, "indicator": indicator}[utility](x,y)
    
    # construct p(u|m) for each meaning
    meaning_distributions = np.array(
        [[decay ** cost(m, u) for u in space.referents] for m in space.referents]
    )
    # each row sums to 1.0
    np.seterr(divide="ignore", invalid="ignore")
    meaning_distributions = np.nan_to_num(meaning_distributions / meaning_distributions.sum(axis=1, keepdims=True))

    return meaning_distributions


def generate_kl_divergence(
    encoder_meanings: np.ndarray, 
    decoder_meanings: np.ndarray,
    ) -> np.ndarray:
    """Generate a distortion matrix for the speaker and listener meanings using KL divergence of their meaning distributions.
    
    Returns:
        an array of size `(|meanings|, |meanings|)` representing the pairwise KL divergence D[m || \hat{m}] for each speaker meaning distribution with each listener meaning distribution.
    """

    return np.array(
        [[DKL(m, m_) for m in encoder_meanings] for m_ in decoder_meanings]
    )


##############################################################################
# Converting from languages to IB quantities
##############################################################################

def information_rate(source: np.ndarray, encoder: np.ndarray) -> float:
    """Complexity, I(X;Xhat)"""
    pXY = joint(pY_X=encoder, pX=source)
    return MI(pXY=pXY)


def expected_distortion_ib(
    source: np.ndarray,
    encoder: np.ndarray,
    encoder_meanings: np.ndarray,
    decoder_meanings: np.ndarray,
) -> float:
    """Communicative cost, E[DKL[M || \hat{M}]] = 

        sum_m sum_w p(m) q(w|m) D[m || \hat{m}_w]

    where \hat{m}_w = sum_m p(m|w)m(u)

    Args:
        source: p(M) of shape `|meanings|`

        encoder: q(w | m) of shape `(|meanings|, |words|)`

        encoder_meanings: M of shape (`|meanings|, |meanings|)`

        decoder_meanings: \hat{M} of shape `(|words|, |meanings|)`
    
    Returns:
        the expected KL divergence
    """
    total = 0
    for i, p_meaning in enumerate(source):
        for j, p_word in enumerate(encoder):
            total += (
                p_meaning *
                p_word *
                DKL(encoder_meanings[i], decoder_meanings[j])
            )

    # alternatively, we might do
    expected_dkl = float(np.sum(
        np.diag(source) @ encoder * (decoder_meanings @ encoder_meanings)
        ))
    if expected_dkl != total:
        print("warning, difference in edkl values:")
        print(total)        
        print(expected_dkl)

    return total

# will never get used because deterministic bayesian listener is optimal, but this method is more general, so I'm keeping for now.
def expected_distortion(
    source: np.ndarray, 
    encoder: np.ndarray, 
    decoder: np.ndarray,
    kl_divergence: np.ndarray,
) -> float:
    """Communicative cost, E[DKL[M || \hat{M}]] = 
    
        sum_m p(m) sum_w q(w|m) sum_m' r(m'|w) D_KL[m, m']
    
    where q is the encoder, and r the decoder.

    Args:
        source: array of shape `|meanings|` p(m) the cognitive source / communicative need distribution, i.e. prior distribution over meanings.

        encoder: array of shape `(|meanings|, |words|)`. Represents conditional probability distribution q(w|m), i.e. an RSA speaker.

        decoder: array of shape `(|words|, |meanings|)`. Represents conditional probability distribution q(m|w), i.e. an RSA listener.

        kl_divergence: array of shape `(|meanings|, |meanings|)`. Represents a distortion matrix of KL divergences between speaker and listener meanings.

    Returns:
        a float representing the expected KL divergence between encoder and decoder representations.
    """
    return float(np.sum(np.diag(source) @ encoder @ decoder * kl_divergence))


##############################################################################
# Helper functions for measuring information-theoretic quantities. Code credit belongs to N. Zaslavsky: https://github.com/nogazs/ib-color-naming/blob/master/src/tools.py
##############################################################################

import numpy as np
from scipy.special import logsumexp

PRECISION = 1e-16

# === DISTRIBUTIONS ===

def marginal(pXY, axis=1):
    """:return pY (axis = 0) or pX (default, axis = 1)"""
    return pXY.sum(axis)


def conditional(pXY):
    """:return  pY_X """
    pX = pXY.sum(axis=1, keepdims=True)
    return np.where(pX > PRECISION, pXY / pX, 1 / pXY.shape[1])


def joint(pY_X, pX):
    """:return  pXY """
    return pY_X * pX[:, None]


def marginalize(pY_X, pX):
    """:return  pY """
    return pY_X.T @ pX


def bayes(pY_X, pX):
    """:return pX_Y """
    pXY = joint(pY_X, pX)
    pY = marginalize(pY_X, pX)
    return np.where(pY > PRECISION, pXY.T / pY, 1 / pXY.shape[0])


def softmax(dxy, beta=1, axis=None):
    """:return
        axis = None: pXY propto exp(-beta * dxy)
        axis = 1: pY_X propto exp(-beta * dxy)
        axis = 0: pX_Y propto exp(-beta * dxy)
    """
    log_z = logsumexp(-beta * dxy, axis, keepdims=True)
    return np.exp(-beta * dxy - log_z)


# INFORMATIONAL MEASURES

def xlogx(v):
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(v > PRECISION, v * np.log2(v), 0)


def H(p, axis=None):
    """ Entropy """
    return -xlogx(p).sum(axis=axis)


def MI(pXY):
    """ mutual information, I(X;Y) """
    return H(pXY.sum(axis=0)) + H(pXY.sum(axis=1)) - H(pXY)


def DKL(p, q, axis=None):
    """ KL divergences, D[p||q] """
    return (xlogx(p) - np.where(p > PRECISION, p * np.log2(q + PRECISION), 0)).sum(axis=axis)
