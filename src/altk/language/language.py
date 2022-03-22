"""Classes for modeling languages as form-meaning mappings, most important among them the Language and Expression classes.

The base object of altk is a Language. This is intended to model a language scientifically (especially parts of its semantics) and to enable various use cases. Most notably, experiments such as analyses of efficient communication, learnability, automatic corpus generation for ML probing, etc.
"""

from abc import abstractmethod


class Language:

    """Minimally contains Expression objects."""

    def __init__(self, expressions=None):
        self.__expressions = list()
        self.set_expressions(expressions)
        raise NotImplementedError()
    
    def set_expressions(self, expressions):
        self.__expressions = expressions
    def get_expressions(self):
        return self.__expressions
    expressions=property(get_expressions, set_expressions)

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __eq__(self, __o: object) -> bool:
        pass
    
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
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __eq__(self, __o: object) -> bool:
        pass
