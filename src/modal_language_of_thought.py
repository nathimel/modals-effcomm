import sys
import numpy as np
from nltk.tree import *
from nltk.grammar import *
from modal_meaning import Modal_Meaning, Modal_Meaning_Space

##############################################################################
# ExpressionTree
##############################################################################

class ExpressionTree:

    def __init__(self, node, children=[]):
        """
        Construct an expression tree (E.T.) wrapper for nltk Tree.
        The following are valid expression trees:
        - (Atom)
        - (Operator (E.T.) (E.T.))
        """

        # Addition is at least binary
        if node == Nonterminal("+"):
            if len(children) < 1:
                raise ValueError("Addition must have at least two operands: children={}"
                .format(children))
            elif len(children) == 1:
                self.tree_ = self.unwrap_singleton_sum(children)
                return

        # Multiplication is binary
        if node == Nonterminal("*") and len(children) != 2:
            raise ValueError("Multiplication must have exactly two operands: children={}"
            .format(children))

        # Negation is unary
        if node == Nonterminal("-") and len(children) != 1:
            raise ValueError("Negation must have exactly one operand: children={}"
            .format(children))

        if isinstance(node, Tree):
            # children doesn't make sense
            self.tree_ = node
            return

        children_ = [child.tree() if isinstance(child, ExpressionTree)
                    else child for child in children]
        
        self.tree_ = Tree(node=node, children=children_)

    def unwrap_singleton_sum(self, children)->Tree:
        """
        Addition is a n-ary for n >= 2. If n == 1, remove the addition
        operator, e.g.
            (+ (* (A ) (c ))) => (* (A ) (c ))
        """
        e, = children
        if isinstance(e, Tree):
            return e
        elif isinstance(e, ExpressionTree):
            return e.tree()
        else:
            return Tree(e, [])        
  
    def tree(self)->Tree:
        return self.tree_
    
    def __str__(self) -> str:
        return str(self.tree())
    
    def __eq__(self, other)->bool:
        return str(self.tree()) == str(other.tree())


##########################################################################
# Modal Language of Thought
##########################################################################

"""Class for defining representation language primitives and running a minimum description length algorithm.

    Example usage:
        >>> mlot = Modal_Language_of_Thought(space)
        >>> expressions = mlot.minimum_descriptions(meanings)
"""


class Modal_Language_of_Thought:

    def __init__(self, meaning_space: Modal_Meaning_Space, operators: list[str]):
        self.forces = meaning_space.forces
        self.flavors = meaning_space.flavors
        self.operators = operators


    def minimum_lot_descriptions(self, meanings: list[Modal_Meaning])->list:
        """Runs a heuristic to estimate the shortest length description of modal meanings in a language of thought.

        This is useful for measuring the complexity of modals, and the langauges containing them.

        Args:
            meanings: a list of the Modal_Meanings

        Returns:
            descriptions: a list of descriptions of each meaning in the lot
        """
        arrs = [meaning.points_to_array() for meaning in meanings]
        r = [str(self.__joint_heuristic(arr)) for arr in arrs]
        return r

    def expression_complexity(self, ET: ExpressionTree)->int:
        """
        Returns the number of atoms in the expression,
        thus ignoring the complexity of operators and
        tree depth.
        """
        # return the number of leaves of the expression tree
        if self.__is_atom(ET):
            if self.__is_id(ET, "1") or self.__is_id(ET, "0"):
                return 1
            return 2
        return sum([self.expression_complexity(ExpressionTree(child)) for child in ET.tree()])

    #################################################################
    # Heuristic
    #################################################################

    def __heuristic(self, e: ExpressionTree, simple_operations: list, relative_operations: list,
            complement=False)->ExpressionTree:
        """A breadth first tree search of possible boolean formula reductions.

        Args:
            e: an ExpressionTree representing the DNF expression to reduce

            simple_operations: a list of functions from ExpressionTree to ExpressionTree

            relative_operations: a list of functions from ExpressionTree to ExpressionTree, parametrized by an atom.

        Returns: 
            shortest: the string representation of the shortest
        expression found.
        """

        atoms = [ExpressionTree("0"), ExpressionTree("1")] + [ExpressionTree(x) for x in self.forces] + [ExpressionTree(x) for x in self.flavors]

        to_visit = [e]
        shortest = e
        it = 0
        hard_ceiling = 2000 # Best solutions are likely before 1000 iterations

        while to_visit:
            if it == hard_ceiling:
                break
            next = to_visit.pop(0)

            children = [operation(next) for operation in simple_operations]
            children.extend(operation(next, atom) for operation in relative_operations for atom in atoms)

            to_visit.extend([child for child in children if child != next])
            it += 1

            if self.expression_complexity(next) < self.expression_complexity(shortest):
                shortest = next

        if complement and self.expression_complexity(shortest) != 1:
            return ExpressionTree(Nonterminal("-"), [shortest])

        return shortest

    def __joint_heuristic(self, arr: np.ndarray)->ExpressionTree:
        """
        Calls the boolean expression minimization heuristic twice, once
        to count 0s and once to count 1s. Returns the shorter result.

        Args:
            arr: a numpy array representing the meaning points a modal can express.

        Returns: 
            result: the ExpressionTree representing the shortest lot description
        """
        e = self.__array_to_dnf(arr)
        simple_operations = [
            self.__identity_a, 
            self.__identity_m, 
            self.__flavor_cover, 
            self.__force_cover
            ]
        relative_operations = [self.__distr_m_over_a]

        if 'negation' in self.operators:
            e_c = self.__array_to_dnf(arr, complement=True)        
            simple_operations.append(self.__sum_complement)
            results = [
                self.__heuristic(e, simple_operations, relative_operations),
                self.__heuristic(e_c, simple_operations, relative_operations, complement=True)]
            complexities = [self.expression_complexity(r) for r in results]
            
            result = results[np.argmin(complexities)]

        else:
            result = self.heuristic(e, simple_operations, relative_operations)

        return result


    ##########################################################################
    # Utility functions
    #########################################################################


    def __array_to_dnf(self, arr: np.ndarray, complement=False)->ExpressionTree:
        """
        Creates a Disjunctive Normal Form (Sum of Products)
        ExpressionTree of nonzero array entries.
        [[1,1,1],
        [1,1,1]]
        =>
        (+ (
            * Q_1 f_1) 
            (* Q_1 f_2) 
            (* Q_1 f_3) 
            (* Q_2 f_1) 
            (* Q_2 f_2) 
            (* Q_2 f_3)
            )
        """
        # Special case: 0
        if np.count_nonzero(arr) == 0:
            return ExpressionTree("0")
        if np.count_nonzero(arr) == (len(self.forces) * len(self.flavors)):
            return ExpressionTree("1")

        if not complement:
            argw = np.argwhere(arr)
            products = [ExpressionTree(
                node=Nonterminal("*"),
                children=[
                    ExpressionTree(self.forces[pair[0]]),
                    ExpressionTree(self.flavors[pair[1]])
                ])
            for pair in argw]
            return ExpressionTree(node=Nonterminal("+"), children=products)
        
        else:
            argw = np.argwhere(arr==0)
            products = [ExpressionTree(
                node=Nonterminal("*"), 
                children=[
                    ExpressionTree(self.forces[pair[0]]), 
                    ExpressionTree(self.flavors[pair[1]])])
            for pair in argw]
            negated_products = [
                ExpressionTree(
                    node=Nonterminal("-"),
                    children=[product],
                ) for product in products]
            return ExpressionTree(node=Nonterminal("+"), children=products)

    def __is_atom(self, ET: ExpressionTree)->bool:
        """
        Returns True if the input is a single atomic symbol, e.g. (x )
        """
        return (
            isinstance(ET, ExpressionTree)
            and not isinstance(ET.tree().label(), Nonterminal)
            and not [child for child in ET.tree()]
        )

    def __is_flavor_atom(self, ET: ExpressionTree)->bool:
        """
        Returns True if the input is a single flavor symbol, e.g.
        if flavors=['e', 'd', 'c'] and ET= ('e' )
        """
        return self.__is_atom(ET) and ET.tree().label() in self.flavors

    def __contains_id(self, ET: ExpressionTree, id: str)->bool:
        """
        Returns true if the identity ("1" or "0") or ExpressionTree wrapper
        is in the input ExpressionTree.
        Buffer function to prevent '==' overload incompatibility.
        """
        for child in ET.tree():
            if self.__is_id(child, id):
                return True
        return False

    def __is_id(self, child, id: str)->bool:
        """
        Checks if input is any of the identity versions.
        Buffer function to prevent '==' overload incompatibility.
        """
        # if isinstance(child, str) and child == id:
            # return True
        if isinstance(child, ExpressionTree) and ExpressionTree(id) == child:
            return True
        if isinstance(child, Tree) and Tree(id, []) == child:
            return True
        return False

    def __is_product_or_singleton(self, child)->bool:
        """
        Buffer to check if input is a Tree with multiplication as root,
        or a Tree containing a string as root and nothing else,
        or simply an atom.
        """
        return (
            (isinstance(child, Tree) and child.label() != Nonterminal("+"))
            or ((isinstance(child, ExpressionTree)) 
                and child.tree().label() != Nonterminal("+"))
        )


    ##########################################################################
    # Logical Inferences
    ##########################################################################

    ##########################################################################
    # Multiplication
    # 
    # Binary branching. This is because multiplication is a
    # binary operator, and iterated multiplication of more than 2 atoms is 
    # either redundant (idempotence) or results in 0, e.g.
    #     xyz = 0
    #     xxy = xy
    ##########################################################################

    def __identity_m(self, ET: ExpressionTree)->ExpressionTree:
        """
        Applies multiplicative identity.
            (* a b ... 1 ... c) => (* a b c)
            (* a 1) => (a)
        """
        if ET.tree().label() == Nonterminal("*") and self.__contains_id(ET, "1"):
            children = [child for child in ET.tree() if not self.__is_id(child, "1")]
            if children == []:
                return ExpressionTree(node="1", children=[])
            elif len(children) == 1:
                return ExpressionTree(node=children[0])
            else:
                return ExpressionTree(node=ET.tree().label(), children=children)

        # Recursive
        if [child for child in ET.tree()]:
            return ExpressionTree(node=ET.tree().label(), children=[
                # child if isinstance(child, str)
                self.__identity_m(ExpressionTree(child)) for child in ET.tree()]
            )
        return ET

    def __annihalator_m(ET: ExpressionTree)->ExpressionTree:
        """
        Applies multiplicative annihalation.
            (* a b ... 0 ...) => (0)
            (* 0) => 0
        """

        if ET.tree().label() != Nonterminal("*"):
            return ET
        if "0" in ET.tree():
            return ExpressionTree(node="0", children=[])

    ##########################################################################
    # Addition
    # 
    # At least binary branching. Will have at most the number of terms in 
    # the DNF of the array representation.
    ##########################################################################
    def __identity_a(self, ET: ExpressionTree)->ExpressionTree:
        """
        Applies additive identity law.
            (+ a b ... 0 ... c) => (+ a b c)
            (+ a 0) => (a)
            (+ 0) => (0)
        """
        if ET.tree().label() == Nonterminal("+") and self.__contains_id(ET, "0"):
            children = [child for child in ET.tree() if 
                        child not in ["0", ExpressionTree("0")]]
            if children == []:
                return ExpressionTree(node="0", children=[])
            else:
                return ExpressionTree(node=ET.tree().label(), children=children)

        # Recursive
        if [child for child in ET.tree()]:
            return ExpressionTree(node=ET.tree().label(), children=[
                # child if isinstance(child, str)
                self.__identity_a(ExpressionTree(child)) for child in ET.tree()]
            )
        return ET

    def __annihalator_a(ET: ExpressionTree)->ExpressionTree:
        """
        Applies additive annihalation. Holds in boolean algebra generally.
            (+ a b ... 1 ... c) => (1)
            (+ 1) => (1)
        """
        if ET.tree().label() != Nonterminal("+"):
            return ET
        if "1" in ET.tree():
            return ExpressionTree(node="1", children=[])

    def __flavor_cover(self, ET: ExpressionTree)->ExpressionTree:
        """
        Replace the sum of all flavors with multiplicative identity.
            \sum_{i=1}^{|flavors|}(flavor_i) = 1
        """
        # Unwrap atoms and check for array cover.
        if (ET.tree().label() == Nonterminal("+")
            and set(self.flavors) == set([
                ExpressionTree(child).tree().label() 
                for child in ET.tree() if self.__is_atom(ExpressionTree(child))])):
            return ExpressionTree("1")

        # Recursive
        elif [child for child in ET.tree()]:
            children = [child if self.__is_atom(child)
                        else self.__flavor_cover(ExpressionTree(child)) for child in ET.tree()]
            return ExpressionTree(node=ET.tree().label(), children=children)

        return ET

    def __force_cover(self, ET: ExpressionTree)->ExpressionTree:
        """
        Replace the sum of all forces with multiplicative identity.
            \sum_{i=1}^{|forces|}(force_i) = 1
        """
        if (ET.tree().label() == Nonterminal("+")
            and set(self.forces) == set([
                ExpressionTree(child).tree().label() 
                for child in ET.tree() if self.__is_atom(ExpressionTree(child))])):
            return ExpressionTree(node="1")
        
        # Recursive
        elif [child for child in ET.tree()]:
            children = [child if self.__is_atom(child)
                        else self.__force_cover(ExpressionTree(child)) for child in ET.tree()]
            return ExpressionTree(node=ET.tree().label(), children=children)

        return ET

    #################################################################
    # Distributivity
    #################################################################

    def __distr_m_over_a(self, ET: ExpressionTree, factor: ExpressionTree):
        """
        Factor out a term from a SOP.
        Reverses distributivity of multiplication over addition.
            (+ (* x y) (* x z)) => (* x (+ y z))
            (+ (* x y) (* x z) (* w v)) => (+ (* x (+ y z)) (* w v))

        Only applies the inference if reduces length, not for e.g.
            (+ (* x y) (* w v)) => (+ (* x y) (* w v))

        Because this function is parametrized by the atom to factor
        out, the minimization heuristic search tree branches for
        each possible atom factor that _shortens_ the expression, e.g.:

        xy + xz + wy + wa
            - branch x: x(y + z) + wy + wa  LEN 7
                - branch w: x(y + z) + w(y + a) LEN 6
            - branch y: y(x + w) + xz + wa  LEN 7
        """
        if ET.tree().label() != Nonterminal("+"):
            return ET
        factored_terms = [] # list of atoms
        remaining_terms = [] # list of trees
        for child in ET.tree():
            if self.__is_product_or_singleton(child):
                if factor.tree() in child:
                    factored_terms += [gc for gc in child if gc != factor.tree()]
                    continue
            remaining_terms.append(child)

        if len(factored_terms) < 2:
            return ET

        factors_tree = ExpressionTree(node=Nonterminal("+"), children=factored_terms)
        factored_tree = ExpressionTree(node=Nonterminal("*"), children=[factor, factors_tree])        
        if remaining_terms:
            children = [factored_tree] + remaining_terms
            return ExpressionTree(node=Nonterminal("+"), children=children)
        else:
            return factored_tree

    #################################################################
    # Complement
    #################################################################

    def __negation(ET: ExpressionTree)->ExpressionTree:
        """
        An operation, not an inference.
        Embed an expression under a negation operator.
            (x ) => (- (x ))
        """
        return ExpressionTree(node=Nonterminal("-"), children=[ET])

    def __shorten_expression(self, ET: ExpressionTree, atoms, others, atoms_c)->ExpressionTree:
        """
        Helper function to sum complement. 
        - atoms 
        a list of the expression tree's children that are atoms
        - others
        the list of the expression tree's children that are not atoms.    
        - atoms_c is a set of atoms: 1 - atoms. Replaces atoms if is shorter.
        """
        if not atoms_c:
            # Allow flavor cover to handle
            return ET

        if len(atoms_c) < len(atoms):
            # if shortens expression, use new sum of wrapped atoms.
            atoms = [ExpressionTree(atom)
                if not isinstance(atom, ExpressionTree)
                else atom for atom in atoms_c]

            comp = ExpressionTree(
                node=Nonterminal("-"),
                children=[ExpressionTree(
                    node=Nonterminal("+"), 
                    children=atoms)]
                )
            new_children = [comp] + others

            return ExpressionTree(
                node=ET.tree().label(),
                children=new_children
            )
        return ET

    def __sum_complement(self, ET: ExpressionTree)->ExpressionTree:
        """
        Reduces a sum to its complement if the complement is shorter, e.g.
        flavors= e, d, c
            (+ (e ) (d ) (* (E ) (c ))) => (+ (- (c )) (* (E )(c )))
        """
        # print("sum comp: ", ET)
        children = [child for child in ET.tree()]

        # Base case
        if not children:
            return ET

        # Base case
        if (ET.tree().label() == Nonterminal("+")):
            
            atoms = []
            others = []
            for child in children:
                if self.__is_atom(ExpressionTree(child)):
                    atoms.append(ExpressionTree(child).tree().label())
                else:
                    others.append(self.__sum_complement(ExpressionTree(child)))

            if atoms and (set(atoms) <= set(self.flavors)):
                atoms_c = list(set(self.flavors) - set(atoms))
                return self.__shorten_expression(ET, atoms, others, atoms_c)
            if atoms and (set(atoms) <= set(self.forces)):
                atoms_c = list(set(self.forces) - set(atoms))
                return self.__shorten_expression(ET, atoms, others, atoms_c)

            new_children = [ExpressionTree(atom) for atom in atoms] + others
            return ExpressionTree(
                node=ET.tree().label(),
                children=new_children
            )

        # Recurse
        if ((ET.tree().label() != Nonterminal("+"))
            or
            (not [child for child in children if self.is_atom(child)])):
            return ExpressionTree(
                node=ET.tree().label(),
                children=[self.__sum_complement(ExpressionTree(child)) for child in children]
            )

    #################################################################
    # End Logical Inferences
    #################################################################

##########################################################################
# End Class Modal Language of Thought
##########################################################################