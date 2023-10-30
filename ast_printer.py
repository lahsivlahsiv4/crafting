import expr
import token

class AstPrinter(expr.ExprVisitor):
    def print_ast(self, expression : expr.Expr):
        return expression.accept(self)
    
    def visit_binary_expr(self, expr : expr.Binary):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)
    def visit_grouping_expr(self, expr : expr.Grouping):
        return self.parenthesize("group", expr.expression)
    def visit_literal_expr(self, expr : expr.Literal):
        return str(expr.value) if expr.value != None else "nil"
    def visit_unary_expr(self, expr : expr.Unary):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name : str, *expressions):
        res = "(" + name

        for expression in expressions:
            res += " " + expression.accept(self)
        
        res += ")"

        return res
    
if __name__ == "__main__":
    expression = expr.Binary(
        expr.Unary(
            token.Token(token.TokenType.MINUS, "-", None, 1),
            expr.Literal(123)
        ),
        token.Token(token.TokenType.STAR, "*", None, 1),
        expr.Grouping(
            expr.Literal(45.67)
        )
    )

    print(AstPrinter().print_ast(expression))