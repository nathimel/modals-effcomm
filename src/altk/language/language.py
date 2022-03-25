"""Classes for modeling languages as form-meaning mappings, most important among them the Language and Expression classes.

The base object of altk is a Language. This is intended to model a language scientifically (especially parts of its semantics) and to enable various use cases. Most notably, experiments such as analyses of efficient communication, learnability, automatic corpus generation for ML probing, etc.
"""

from abc import abstractmethod
    
class Expression:

    """Minimally contains a form and a meaning."""

    def __init__(self, form=None, meaning=None):
        self.__form = None
        self.__meaning = None
        self.set_form(form)
        self.set_meaning(meaning)
    
    def set_form(self,form):
        self.__form = form
    def get_form(self):
        return self.__form
    form=property(get_form, set_form)

    def set_meaning(self, meaning):
        self.__meaning = meaning
    def get_meaning(self):
        return self.__meaning
    meaning=property(get_meaning, set_meaning)

    @abstractmethod
    def yaml_rep(self):
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass
    @abstractmethod
    def __eq__(self, __o: object) -> bool:
        pass
    @abstractmethod
    def __hash__(self) -> int:
        pass


class Language:

    """Minimally contains Expression objects."""

    def __init__(self, expressions: list[Expression]):
        self.set_expressions(expressions)
    
    def set_expressions(self, expressions: list[Expression]):
        if not expressions:
            raise ValueError("list of Expressions must not be empty.")        
        self.__expressions = expressions
    def get_expressions(self):
        return self.__expressions
    expressions=property(get_expressions, set_expressions)

    def has_expression(self, expression: Expression) -> bool:
        """Whether the language has the expression"""
        return expression in self.get_expressions()

    def add_expression(self, expression: Expression):
        """Add an expression to the list of expressions in a language."""
        self.set_expressions(self.get_expressions() + [expression])

    def size(self) -> int:
        """Returns the length of the list of expressions in a language."""
        return len(self.get_expressions())

    def pop(self, index: int) -> Expression:
        """Removes an expression at the specified index of the list of expressions, and returns it."""
        if not self.size():
            raise Exception("Cannot pop expressions from an empty language.")
        expressions = self.get_expressions()
        popped = expressions.pop(index)
        self.set_expressions(expressions)
        return popped
    
    def is_natural(self) -> bool:
        """Whether a language represents a human natural language."""
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __eq__(self, __o: object) -> bool:
        pass
    
    @abstractmethod
    def __hash__(self) -> int:
        return self.get_expressions().__hash__()

    def __eq__(self, __o: object) -> bool:
        return self.get_expressions() == __o.get_expressions()