from altk.language.language import Expression

##############################################################################
# Expression
##############################################################################
class Modal_Expression(Expression):

    """A container for modal forms, meanings and other data.
    
        It is useful to additionally store the modal's shortest LoT description, as well as the complexity associated with this description. For semantic universals formulated in at the level of individual modal lexical items, e.g. the Independence of Force and Flavors, satisfaction of such universals is also stored.

        Example usage:
            
            e = Modal_Expression('might', {'weak+epistemic'}, '(* (weak ) (epistemic ))')
    """

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
    