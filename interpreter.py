from typing import List

import expr
import Token
import lox
import stmt
import environment

class RuntimeError(Exception):
    def __init__(self, token, message):
        super().__init__(message)
        self.token = token

class Interpreter(expr.ExprVisitor, stmt.StmtVisitor):
    env : environment.Environment

    def __init__(self):
        self.env = environment.Environment()

    def visit_block_stmt(self, statement : stmt.Block):
        self.execute_block(statement.statements, environment.Environment(self.env))

    def execute_block(self, statements : List[stmt.Stmt], env : environment.Environment):
        previous = self.env

        try:
            self.env = env

            for statement in statements:
                self.execute(statement)
        finally:
            self.env = previous
    
    def visit_logical_expr(self, expression : expr.Logical):
        left = self.evaluate(expression.left)

        if expression.operator.token_type == Token.TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left
        
        return self.evaluate(expression.right)
    
    def visit_while_stmt(self, stmt : stmt.While):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
    
    def visit_if_stmt(self, statement : stmt.If):
        if self.is_truthy(self.evaluate(statement.condition)):
            self.execute(statement.then_branch)
        elif statement.else_branch != None:
            self.execute(statement.else_branch)

    def visit_expression_stmt(self, stmt):
        self.evaluate(stmt.expression)

    def visit_print_stmt(self, stmt):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
    
    def visit_var_stmt(self, stmt):
        value = None

        if stmt.initializer != None:
            value = self.evaluate(stmt.initializer)

            self.env.define(stmt.name.lexeme, value)
    
    def visit_assign_expr(self, expr):
        value = self.evaluate(expr.value)

        self.env.assign(expr.name, value)
        return value

    def evaluate(self, expression : expr.Expr):
        return expression.accept(self)
    
    def interpret(self, statements : List[stmt.Stmt]):
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeError as e:
            lox.runtime_error(e)
    
    def execute(self, statement : stmt.Stmt):
        statement.accept(self)

    def stringify(self, obj) -> str:
        return "nil" if obj == None else str(obj)
    
    def visit_binary_expr(self, expr : expr.Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        _type = expr.operator.token_type

        if _type == Token.TokenType.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) - float(right)

        if _type == Token.TokenType.PLUS:

            if type(left) == float and type(right) == float:
                return float(left) + float(right)

            if type(left) == str and type(right) == str:
                return str(left) + str(right)
            
            raise RuntimeError(expr.operator, "Operands must be two numbers or two strings.")

        if _type == Token.TokenType.SLASH:
            self.check_number_operands(expr.operator, left, right)
            return float(left) / float(right)

        if _type == Token.TokenType.STAR:
            self.check_number_operands(expr.operator, left, right)
            return float(left) * float(right)

        if _type == Token.TokenType.GREATER:
            self.check_number_operands(expr.operator, left, right)
            return float(left) > float(right)

        if _type == Token.TokenType.GREATER_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)

        if _type == Token.TokenType.LESS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) < float(right)

        if _type == Token.TokenType.LESS_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)
        

        if _type == Token.TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)

        if _type == Token.TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)

    def visit_grouping_expr(self, expr : expr.Grouping):
        return self.evaluate(expr.expression)

    def visit_literal_expr(self, expr : expr.Literal):
        return expr.value

    def visit_unary_expr(self, expr : expr.Unary):
        right = self.evaluate(expr.right)

        if expr.operator.token_type == Token.TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return - float(right)
        elif expr.operator.token_type == Token.TokenType.BANG:
            return not self.is_truthy(right)
        
        raise Exception("Unreachable")

    def visit_variable_expr(self, expr):
        return self.env.get(expr.name)

    def is_truthy(self, obj) -> bool:
        return obj != None and obj != False
    
    def is_equal(self, a, b):
        return a == b
    
    def check_number_operand(self, operator : Token.Token, operand):
        if type(operand) != float:
            raise RuntimeError(operator, "Operand must be a number.")
    
    def check_number_operands(self, operator : Token.Token, left, right):
        if type(left) != float or type(right) != float:
            raise RuntimeError(operator, "Operands must be numbers.")
