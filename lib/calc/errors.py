
class CalculatorError(ValueError):
    pass

class InvalidExpression(CalculatorError):
    pass

class ResultTooBig(CalculatorError):
    pass

class InputTooLong(CalculatorError):
    pass
