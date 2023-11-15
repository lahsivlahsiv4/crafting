from typing import List, Any
from enum import Enum, auto

import LoxCallable
import stmt
import environment
import interpreter as Interpreter


class FunctionType(Enum):
    NONE        = auto()
    FUNCTION    = auto()
    INITIALIZER = auto()
    METHOD      = auto()

class LoxFunction(LoxCallable.LoxCallable):
    declaration : stmt.Function
    closure : environment.Environment
    is_initializer : bool

    def __init__(self, declaration : stmt.Function, closure : environment.Environment, is_initializer : bool):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def call(self, interpreter, arguments : List[Any]) -> Any:
        env = environment.Environment(self.closure)

        for i, param in enumerate(self.declaration.params):
            env.define(param.lexeme, arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, env)
        except Interpreter.Return as e:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return e.value
        
        if self.is_initializer:
            return self.closure.get_at(0, "this")
    
    def bind(self, instance):
        env = environment.Environment(self.closure)
        env.define("this", instance)
        return LoxFunction(self.declaration, env, self.is_initializer)

    def arity(self) -> int:
        return len(self.declaration.params)
    
    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"