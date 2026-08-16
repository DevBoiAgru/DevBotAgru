from decimal import Decimal

class OperatorTypes:
    ADD = 1
    SUBTRACT = 2
    MULTIPLY = 3
    DIVIDE = 4
    EXPONENT = 5
    SQRT = 6
    
    BRACKET_OPEN = 100
    BRACKET_CLOSE = 101

class Token:
    raw: str

    def __repr__(self) -> str:
        return self.raw

class Operand(Token):
    value: Decimal

    def __init__(self, val: Decimal) -> None:
        super().__init__()
        self.value = val
        self.raw = f"<VAL:{str(val)}>"

class Operator(Token):
    operator: int
    precedence: int
    rightAssociative: bool
    unary: bool

    def __init__(self, val: int, precedence: int, unary: bool = False, rightAssociative: bool = False) -> None:
        super().__init__()
        self.operator = val
        self.precedence = precedence
        self.unary = unary
        self.rightAssociative = rightAssociative

        reprName = ""

        match val:
            case OperatorTypes.ADD:
                reprName = "+"
            case OperatorTypes.SUBTRACT:
                reprName = "-"
            case OperatorTypes.MULTIPLY:
                reprName = "*"
            case OperatorTypes.DIVIDE:
                reprName = "/"
            case OperatorTypes.EXPONENT:
                reprName = "^"
            case OperatorTypes.SQRT:
                reprName = "sqrt"
            case OperatorTypes.BRACKET_OPEN:
                reprName = "("
            case OperatorTypes.BRACKET_CLOSE:
                reprName = ")"
        self.raw = f"<OP:{reprName}>"