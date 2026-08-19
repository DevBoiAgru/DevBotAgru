from typing import cast
from decimal import Decimal, InvalidOperation
import re
from .types import Token, Operand, Operator, OperatorTypes
from .errors import InvalidExpression, InputTooLong, ResultTooBig

class Calculator:
    def __init__(self) -> None:
        pass

    def tokenise(self, infix: str) -> list[Token]:
        # Safety stuff
        MAX_DIGIT_LENGTH = 255

        tokenised = []
        infix = infix.lower().replace("{", "(").replace("[", "(").replace("]", ")").replace("}", ")")

        # Verify balanced parantheses
        paranthesesStack = []
        for i in infix:
            if i == "(":
                paranthesesStack.append(1)
            elif i == ")":
                try:
                    paranthesesStack.pop()
                except IndexError:
                    raise InvalidExpression("Unbalanced parantheses in input expression")
        if len(paranthesesStack) != 0:
            raise InvalidExpression("Unbalanced parantheses in input expression")


        # Regex pattern ordered by specificity: decimals -> words/constants -> other non-whitespace
        pattern = r"(\d+\.\d+|\w+|\S)"
        rawTokenised: list[str] = re.findall(pattern, infix)

        for rawToken in rawTokenised:
            if len(rawToken) > MAX_DIGIT_LENGTH:
                raise InputTooLong(f"Number too long: {rawToken[:100]}")
            try:
                val = Decimal(rawToken)
                tokenised.append(Operand(val))
            except InvalidOperation:
                # Try parsing as a constant (pi, e)
                if rawToken == "pi" or rawToken == "e":
                    match rawToken:
                        case "pi":
                            tokenised.append(Operand(Decimal("3.141592653589793")))
                        case "e":
                            tokenised.append(Operand(Decimal("2.718281828459045")))
                else:
                    # Parse as operand
                    match rawToken:
                        case "+":
                            tokenised.append(Operator(OperatorTypes.ADD, 2))
                        case "-":
                            tokenised.append(Operator(OperatorTypes.SUBTRACT, 2))
                        case "*":
                            tokenised.append(Operator(OperatorTypes.MULTIPLY, 5))
                        case "/":
                            tokenised.append(Operator(OperatorTypes.DIVIDE, 5))
                        case "^":
                            tokenised.append(Operator(OperatorTypes.EXPONENT, 9, True))
                        case "sqrt":
                            tokenised.append(Operator(OperatorTypes.SQRT, 9, True))
                        case "(" | "{" | "[":
                            tokenised.append(Operator(OperatorTypes.BRACKET_OPEN, 9999))
                        case ")" | "]" | "]":
                            tokenised.append(Operator(OperatorTypes.BRACKET_CLOSE, 9999))
                        case _:
                            raise InvalidExpression(f"Unknown operand: {rawToken}")
                            
        return tokenised

    def infixToPostfix(self, infix: list[Token]) -> list[Token]:
        operatorStack: list[Operator] = []
        postfix: list[Token] = []

        for token in infix:
            if isinstance(token, Operand):
                postfix.append(token)
                continue

            # Token is an operator
            op = cast(Operator, token)

            # Open bracket
            if op.operator == OperatorTypes.BRACKET_OPEN:
                operatorStack.append(op)
                continue

            # Close bracket
            if op.operator == OperatorTypes.BRACKET_CLOSE:
                # Pop and push until open bracket is found
                while (
                    operatorStack
                    and operatorStack[-1].operator != OperatorTypes.BRACKET_OPEN
                ):
                    postfix.append(operatorStack.pop())

                if not operatorStack:
                    raise InvalidExpression("Unmatched closing paranthesis")

                # Remove the open bracket we found
                operatorStack.pop()
                continue

            # Regular operator
            while operatorStack:
                top = operatorStack[-1]

                if top.operator == OperatorTypes.BRACKET_OPEN:
                    break

                if top.precedence > op.precedence:
                    postfix.append(operatorStack.pop())
                    continue

                if top.precedence == op.precedence and not op.rightAssociative:
                    postfix.append(operatorStack.pop())
                    continue

                break

            operatorStack.append(op)

        # Empty the remaining stack
        while (operatorStack):
            postfix.append(operatorStack.pop())

        return postfix


    def evaluate(self, postfix: list[Token]) -> Decimal:

        # Safety stuff
        MAX_DIGITS = 100
        MAX_TOKENS = 1000

        if len(postfix) > MAX_TOKENS:
            raise InputTooLong("Expression too long")

        operandStack: list[Operand] = []

        for token in postfix:
            if isinstance(token, Operand):
                operandStack.append(token)

            else:
                # Token is an operator
                op = cast(Operator, token)
                if op.unary:
                    operand = operandStack.pop()
                    match op.operator:
                        case OperatorTypes.SQRT:
                            operandStack.append(Operand(operand.value.sqrt()))
                else:
                    b = operandStack.pop()
                    a = operandStack.pop()

                    match op.operator:
                        case OperatorTypes.ADD:
                            operandStack.append(Operand(a.value + b.value))
                        case OperatorTypes.SUBTRACT:
                            operandStack.append(Operand(a.value - b.value))
                        case OperatorTypes.MULTIPLY:
                            operandStack.append(Operand(a.value * b.value))
                        case OperatorTypes.DIVIDE:
                            operandStack.append(Operand(a.value / b.value))
                        case OperatorTypes.EXPONENT:
                            if a.value != 0 and b.value > 0:
                                estimated_digits = int(
                                    b.value * abs(a.value).ln() / Decimal(10)
                                ) + 1

                                if estimated_digits > MAX_DIGITS:
                                    raise ResultTooBig(f"Result too large. Estimated {estimated_digits} digits long.")
                            operandStack.append(Operand(a.value ** b.value))

        if len(operandStack) != 1:
            raise InvalidExpression("Operand stack has got than 1 elements during evalutaion. Invalid postfix")

        return operandStack[0].value


    def solve(self, expression: str) -> Decimal:
        infix = self.tokenise(expression)
        postfix = self.infixToPostfix(infix)
        result = self.evaluate(postfix)

        estimated_digits = int(abs(result).log10()) + 1

        if estimated_digits > 750:
            raise ResultTooBig(f"Result too large. Estimated {estimated_digits} digits long.")

        return result

if __name__ == "__main__":
    tokeniser = Calculator()

    expression = "10.59 * 5.54 - 3.78 + (10 + 20) - 5 + pi + e * sqrt(10 + 6)"
    # expression = "1*(2+3)/4"

    print(tokeniser.solve(expression))