import altk
from altk.language.syntax import Form
from altk.language.language import Expression

##############################################################################
# Forms
##############################################################################

class Modal_Form(Form):
    """Modals are given forms identified with their shortest LoT expressions.
    
    Example usage for hypothetical 'mought': 
        >>> form = "(+ (* (weak ) (epistemic ) ) (* (strong ) (deontic ) ) )"
        >>> modal_form = Modal_Form(form)

    """
    def __init__(self, form):
        self.__form = str()
        self.set_form(form)
    
    def set_form(self, f):
        self.__form = f
    def get_form(self):
        return self.__form
    form=property(get_form, set_form)

    def __str__(self):
        return str(self.__form)

class Natural_Language_Modal_Form(Modal_Form):

    """Natural language modals additionally store their actual linguistic forms.

    Examples for English 'might': 
        >>> lot_form = "(* (weak ) (epistemic ))"
        >>> actual_form = "might"
        >>> might = Natural_Language_Modal_Form(lot_form, actual_form)
    """

    def __init__(self, form, natural_form):
        super().__init__(form)
        self.__natural_form = str()
        self.set_natural_form(natural_form)

    def set_natural_form(self, f):
        self.__natural_form = f
    def get_natural_form(self):
        return self.__natural_form
    natural_form=property(get_natural_form, set_natural_form)


##############################################################################
# Expression
##############################################################################
class Modal_Expression(Expression):

    """A container for modal forms and meanings."""

    def __init__(self, form, meaning, lot_expression):
        super().__init__(form, meaning)
        self.__lot_expression = str()
        self.set_lot_expression(lot_expression)
    
    def set_lot_expression(self, e):
        self.__lot_expression = e
    def get_lot_expression(self):
        return self.__lot_expression

    def __str__(self) -> str:
        return "Modal_Expression: [\nform={0}\nmeaning={1}\nlot_expression={2}]".format(self.get_form(), self.get_meaning(), self.get_lot_expression())
    