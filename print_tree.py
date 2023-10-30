import expr
import Token
import textwrap
import lox
import stmt

class AstPrinter(expr.ExprVisitor, stmt.StmtVisitor):
    def __init__(self):
        self.ncount = 1
        self.dot_header = [textwrap.dedent("""\
        digraph astgraph {
          node [shape=circle, fontsize=12, fontname="Courier", height=.1];
          ranksep=.3;
          edge [arrowsize=.5]

        """)]
        self.dot_body = []
        s = '  node{} [label="{}"]\n'.format(self.ncount, "Program")
        self.dot_body.append(s)
        self.ncount += 1
        self.dot_footer = ['}']

    def print_ast(self, stmt : stmt.Stmt):
        stmt.accept(self)
    
    def visit_binary_expr(self, expr : expr.Binary):
        s = '  node{} [label="{}"]\n'.format(self.ncount, "Binary " + expr.operator.lexeme)
        self.dot_body.append(s)
        expr._num = self.ncount
        self.ncount += 1

        expr.left.accept(self)
        expr.right.accept(self)

        for child_node in (expr.left, expr.right):
            s = '  node{} -> node{}\n'.format(expr._num, child_node._num)
            self.dot_body.append(s) 

    def visit_grouping_expr(self, expr : expr.Grouping):
        s = '  node{} [label="{}"]\n'.format(self.ncount, "group")
        self.dot_body.append(s)
        expr._num = self.ncount
        self.ncount += 1

        expr.expression.accept(self)

        for child_node in ([expr.expression]):
            s = '  node{} -> node{}\n'.format(expr._num, child_node._num)
            self.dot_body.append(s) 

    def visit_literal_expr(self, expr : expr.Literal):
        s = '  node{} [label="{}"]\n'.format(self.ncount, "Literal " + str(expr.value) if expr.value != None else "nil")
        self.dot_body.append(s)
        expr._num = self.ncount
        self.ncount += 1

    def visit_variable_expr(self, expr):
        s = '  node{} [label="{}"]\n'.format(self.ncount, "Expr Var " + str(expr.name.lexeme))
        self.dot_body.append(s)
        expr._num = self.ncount
        self.ncount += 1

    def visit_assign_expr(self, expr):
        s = '  node{} [label="{}"]\n'.format(self.ncount, "Assign expr " + expr.name.lexeme)
        self.dot_body.append(s)
        expr._num = self.ncount
        self.ncount += 1

        expr.value.accept(self)

        for child_node in ([expr.value]):
            s = '  node{} -> node{}\n'.format(expr._num, child_node._num)
            self.dot_body.append(s) 

    def visit_unary_expr(self, expr : expr.Unary):
        s = '  node{} [label="{}"]\n'.format(self.ncount, "Unary " + expr.operator.lexeme)
        self.dot_body.append(s)
        expr._num = self.ncount
        self.ncount += 1

        expr.right.accept(self)

        for child_node in ([expr.right]):
            s = '  node{} -> node{}\n'.format(expr._num, child_node._num)
            self.dot_body.append(s) 

    def visit_var_stmt(self, stmt):
        s = '  node{} [label="{}"]\n'.format(self.ncount, "Var Stmt (Assign)" + stmt.name.lexeme)
        self.dot_body.append(s)
        stmt._num = self.ncount
        self.ncount += 1

        stmt.initializer.accept(self)

        if stmt.initializer:
            for child_node in ([stmt.initializer]):
                s = '  node{} -> node{}\n'.format(stmt._num, child_node._num)
                self.dot_body.append(s) 

    def visit_print_stmt(self, stmt):
        s = '  node{} [label="{}"]\n'.format(self.ncount, "Print Stmt " )
        self.dot_body.append(s)
        stmt._num = self.ncount
        self.ncount += 1

        stmt.expression.accept(self)

        for child_node in ([stmt.expression]):
            s = '  node{} -> node{}\n'.format(stmt._num, child_node._num)
            self.dot_body.append(s) 

    def visit_expression_stmt(self, stmt):
        s = '  node{} [label="{}"]\n'.format(self.ncount, "Expression Stmt " + stmt.name.lexeme)
        self.dot_body.append(s)
        stmt._num = self.ncount
        self.ncount += 1

        stmt.expression.accept(self)

        for child_node in ([stmt.expression]):
            s = '  node{} -> node{}\n'.format(stmt._num, child_node._num)
            self.dot_body.append(s) 

    def visit_block_stmt(self, block_stmt : stmt.Block):
        s = '  node{} [label="{}"]\n'.format(self.ncount, "Block Stmt " )
        self.dot_body.append(s)
        block_stmt._num = self.ncount
        self.ncount += 1

        for statement in block_stmt.statements:
           statement.accept(self)

        for child_node in block_stmt.statements:
            s = '  node{} -> node{}\n'.format(block_stmt._num, child_node._num)
            self.dot_body.append(s) 

    def gendot(self):
        return ''.join(self.dot_header + self.dot_body + self.dot_footer)

    
if __name__ == "__main__":
    expression = expr.Binary(
        expr.Unary(
            Token.Token(Token.TokenType.MINUS, "-", None, 1),
            expr.Literal(123)
        ),
        Token.Token(Token.TokenType.STAR, "*", None, 1),
        expr.Grouping(
            expr.Literal(45.67)
        )
    )

    ast_inst = AstPrinter()
    statments = lox.vishal_ast("{var y=100; print(y);}")
    for stmt in statments:
        ast_inst.print_ast(stmt)
        s = '  node{} -> node{}\n'.format(1, stmt._num)
        ast_inst.dot_body.append(s) 
    print(ast_inst.gendot())
