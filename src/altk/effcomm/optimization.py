"""Classes and functions for generating languages that optimize the simplicity/informativeness trade-off, e.g. via an iterative evolutionary algorithm."""

import copy
import pygmo
import random
import math
from tqdm import tqdm
from pathos.multiprocessing import ProcessPool
from altk.effcomm.complexity import Complexity_Measure
from altk.effcomm.informativity import Informativity_Measure

from altk.language.language import Expression, Language

class Evolutionary_Optimizer:

    def __init__(
        self, 
        comp_measure: Complexity_Measure, 
        inf_measure: Informativity_Measure,
        expressions: list[Expression],
        sample_size: int, 
        max_mutations: int, 
        generations: int, 
        lang_size: int, 
        processes: int,
        ):
        """Initialize the evolutionary algorithm configurations.

        Args: 
            - comp_measure:   a Complexity_Measure object

            - inf_measure:    an Informativity_Measure object

            - expressions:    a list of expressions from which to apply mutations to languages.

            - sample_size:  the size of the population at every generation.

            - max_muatations:   between 1 and this number of mutations will be applied to a subset of the population at the end of each generation.

            - generations:  how many iterations to run the evolutionary algorithm for.

            - lang_size:    between 1 and this number of expressions comprise a language.

            - proceses:     for multiprocessing.ProcessPool, e.g. 6.
        """
        self.comp_measure = comp_measure
        self.inf_measure = inf_measure
        self.expressions = expressions

        self.sample_size = sample_size
        self.max_mutations = max_mutations
        self.generations = generations
        self.lang_size = lang_size
        self.processes = processes

        self.dominating_languages = None
        self.explored_languages = None

    def fit(self, seed_population: list[Language]) -> tuple:
        """Computes the Pareto frontier, a set languages which cannot be both more simple and more informative.
        
        Uses pygmo's nondominated_front method for computing a population's best solutions to a multi-objective optimization problem.

        Args:
            - seed_population:      a list of languages representing the population at generation 0 of the algorithm.

        Returns: 
            - dominating_languages:     a list of the Pareto optimal languages

            - explored_languages:       a list of all the languages explored during the evolutionatry algorithm.
        """
        batch_complexity = self.comp_measure.batch_complexity
        batch_comm_cost = self.inf_measure.batch_communicative_cost

        pool = ProcessPool(nodes=self.processes)

        languages = seed_population
        explored_languages = []

        for gen in tqdm(range(self.generations)):
            # Measure each generation
            # complexity = pool.map(batch_complexity, languages) # for some reason pool hates me
            # comm_cost = pool.map(batch_comm_cost, languages)

            complexity = batch_complexity(languages)
            comm_cost = batch_comm_cost(languages)

            # measurements = [(cost, comp) for cost, comp in zip(comm_cost, complexity)]
            explored_languages.extend(languages)

            # Calculate dominating individuals
            dominating_indices = pygmo.non_dominated_front_2d(list(zip(comm_cost, complexity)))
            dominating_languages = [languages[i] for i in dominating_indices]

            # Mutate dominating individuals
            languages = self.sample_mutated(dominating_languages, self.sample_size, self.expressions)
        
        return (dominating_languages, explored_languages)

    def sample_mutated(self, languages: list[Language], amount: int, expressions: list[Expression]) -> list[Language]:
        '''
        Arguments: 
            - languages:   dominating languages of a generation 
            - amount:      sample_size.
            expressions: the list of expressions
        Returns:
            - mutated_languages: a new population of languages of size=sample_size
        '''
        amount -= len(languages)
        amount_per_lang = int(math.floor(amount / len(languages)))
        amount_random = amount % len(languages)

        mutated_languages = []

        for language in languages:
            for i in range(amount_per_lang):
                num_mutations = random.randint(1, self.max_mutations)
                mutated_language = copy.deepcopy(language)
                for j in range(num_mutations):
                    mutated_language = self.mutate(mutated_language, expressions)
                mutated_languages.append(mutated_language)

        # Ensure the number of languages per generation is constant
        for i in range(amount_random):
            language = random.choice(languages)
            mutated_languages.append(self.mutate(language, expressions))

        mutated_languages.extend(languages)

        return mutated_languages    

    def mutate(self, language: Language, expressions: list[Expression]) -> Language:
        raise NotImplementedError()

##############################################################################
# Mutation
##############################################################################

    """Classes for defining mutations used by an Evolutionary_Optimizer."""

class Mutation:

    def __init__(self):
        pass

    def mutate(self, language: Language, expressions: list[Expression]) -> Language:
        raise NotImplementedError()
