"""Classes for defining the evolutionary algorithm for modals, including specific mutations on modal languages."""

import random
import numpy as np

from altk.effcomm.optimization import Evolutionary_Optimizer, Mutation
from altk.language.language import Language

from modals.modal_measures import ModalComplexityMeasure, ModalInformativityMeasure
from modals.modal_language import ModalExpression, ModalLanguage
    
##############################################################################
# Modals-specific evolutionary algorithm mutations
##############################################################################

class Add_Modal(Mutation):

    def __init__(self):
        super().__init__()
    
    def mutate(self, language: ModalLanguage, expressions: list[ModalExpression]) -> Language:
        while True:
            new_expression = random.choice(expressions)

            # TODO: delete the below line to allow for synonymy
            language.has_expression(new_expression)

            if language.has_expression(new_expression):
                continue
            language.add_expression(new_expression)
            break
        return language

class Remove_Modal(Mutation):

    def __init__(self):
        super().__init__()

    def mutate(self, language: ModalLanguage, expressions=None) -> Language:
        """Removes a random modal from the list of expressions of a modal language.

        Dummy expressions argument to have the same function signature as super().mutate().
        """
        index = random.randint(0, language.size() - 1)
        language.pop(index)
        return language

class Remove_Bit(Mutation):

    def __init__(self):
        super().__init__()
    
    def mutate(self, language: ModalLanguage, expressions: list[ModalExpression]) -> Language:
        """Choose a random modal from the langauge and replace it with a modal that deletes one point from the semantic space. 
        
        Should increase informativeness.
        """
        # randomly select a modal
        for index in range(language.size()):
            arr = language.get_expressions().copy()[index].get_meaning().to_array()

            if np.count_nonzero(arr) == 0:
                raise ValueError('Array to replace in remove_bit cannot be all 0.')

            # randomly remove a bit
            argw = list(np.argwhere(arr))
            if len(argw) == 0:
                continue
            loc = random.choice(argw)
            row, col = loc
            arr[row, col] = 0

            # replace the modal
            if np.count_nonzero(arr) != 0:
                # Search for the correct expression
                for e in expressions:
                    arr_ = e.get_meaning().to_array()
                    if np.array_equal(arr, arr_):
                        new_expression = e

                # replace
                language.add_expression(new_expression)
                language.pop(index -1 )
                break
        return language        

class Interchange_Modal(Mutation):

    """Removes and then adds a random expresion.
    
    Requires creating Add_Modal and Remove_Modal mutations as instance attributes.
    """

    def __init__(self):
        super().__init__()
        self.add_modal = Add_Modal()
        self.remove_modal = Remove_Modal()

    def mutate(self, language: ModalLanguage, expressions: list[ModalExpression]) -> Language:
        """Removes and then adds a random expresion."""
        remove = self.remove_modal.mutate
        add = self.add_modal.mutate
        return remove(add(language, expressions))

##############################################################################
# Modals-specific optimizer
##############################################################################

class Modal_Evolutionary_Optimizer(Evolutionary_Optimizer):

    """A class for defining specific a implementation, e.g. mutations on modal expressions, of the evolutionary algorithm used for finding Pareto optimal languages.
    """

    def __init__(
        self, 
        comp_measure: ModalComplexityMeasure, 
        inf_measure: ModalInformativityMeasure,
        expressions: list[ModalExpression], 
        sample_size: int, 
        max_mutations: int, 
        generations: int, 
        lang_size: int, 
        processes: int
        ):
        """Initialize the optimizer with configurations and define the mutations on modal languages."""
        super().__init__(comp_measure, inf_measure, expressions, sample_size, max_mutations, generations, lang_size, processes)
        self.add = Add_Modal().mutate
        self.remove = Remove_Modal().mutate
        self.interchange = Interchange_Modal().mutate
        self.remove_bit = Remove_Bit().mutate
    
    def mutate(self, language: ModalLanguage, expressions: list[ModalExpression]) -> ModalLanguage:
        possible_mutations = [self.interchange, self.remove_bit]
        if language.size() < self.lang_size:
            possible_mutations.append(self.add)
        if language.size() > 1:
            possible_mutations.append(self.remove)

        mutation = random.choice(possible_mutations)
        return mutation(language, expressions)

