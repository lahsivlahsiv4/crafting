from typing import List, Any

import LoxCallable
import stmt
import environment
import interpreter as Interpreter

class LoxFunction(LoxCallable.LoxCallable):
    declaration : stmt.Function
    closure : environment.Environment

    def __init__(self, declaration : stmt.Function, closure : environment.Environment):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, arguments : List[Any]) -> Any:
        env = environment.Environment(self.closure)

        for i, param in enumerate(self.declaration.params):
            env.define(param.lexeme, arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, env)
        except Interpreter.Return as e:
            return e.value

    def arity(self) -> int:
        return len(self.declaration.params)
    
    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"