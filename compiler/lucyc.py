#!/usr/bin/env python3

import sys
from antlr4 import *
from llvmlite import ir
from LucyLexer import LucyLexer
from LucyParser import LucyParser
from LucyVisitor import LucyVisitor


class SymbolTable:
    def __init__(self):
        self._symbols = [dict()]

    def push_frame(self, symbols=None):
        symbols = dict() if symbols is None else symbols
        self._symbols.append(symbols)

    def pop_frame(self):
        self._symbols.pop()

    def resolve(self, ide):
        for frame in reversed(self._symbols):
            try:
                return frame[ide]
            except KeyError:
                pass
        raise IndexError

    def bind(self, ide, ptr):
        self._symbols[-1][ide] = ptr


class CodeGenerator(LucyVisitor):
    def __init__(self):
        self.types = {
            'Void': ir.VoidType(),
            'Int':  ir.IntType(32),
        }
        self.module  = ir.Module()
        self.symbols = SymbolTable()

    def new_var(self, typ, ide, val=None):
        ptr = self.builder.alloca(typ, name=ide)
        self.symbols.bind(ide, ptr)
        if val is not None:
            self.builder.store(val, ptr)

    def new_func(self, typ, ide):
        self.func = ir.Function(self.module, typ, name=ide)
        self.symbols.bind(ide, self.func)

    def new_block(self):
        block = self.func.append_basic_block(name='.entry')
        self.builder = ir.IRBuilder(block)

    def visitVarDecl(self, ctx):
        typ = ctx.typ().getText()
        ide = ctx.ID().getText()
        self.new_var(self.types[typ], ide)
        if ctx.expr():
            self.visitAssign(ctx)

    def visitFuncDecl(self, ctx):
        ide = ctx.ID().getText()
        try:
            ret_typ = ctx.typ().getText()
        except AttributeError:
            ret_typ = 'Void'

        try:
            params = ctx.params().param()
            param_types = [self.types[x.typ().getText()] for x in params]
            param_names = [x.ID().getText()              for x in params]
        except AttributeError:
            param_types = []
            param_names = []

        func_typ = ir.FunctionType(self.types[ret_typ], param_types)
        self.new_func(func_typ, ide)

        self.symbols.push_frame()
        self.new_block()

        for arg, typ, name in zip(self.func.args, param_types, param_names):
            arg.name = name
            self.new_var(typ, name, arg)

        self.visit(ctx.block())
        self.symbols.pop_frame()

        if not self.builder.block.is_terminated and func_typ == self.types['Void']:
            self.builder.ret_void()

    def visitBlock(self, ctx):
        self.symbols.push_frame()

        for child in ctx.children:
            self.visit(child)

        self.symbols.pop_frame()

    def visitRet(self, ctx):
        try:
            self.builder.ret(self.visit(ctx.expr()))
        except AttributeError:
            if self.func.return_value.type == self.types['Void']:
                self.builder.ret_void()
            else:
                raise Exception("Function must return a value.")

    def visitAssign(self, ctx):
        ide = ctx.ID().getText()
        try:
            ptr = self.symbols.resolve(ide)
            val = self.visit(ctx.expr())
            if ptr.type.pointee != val.type:
                raise Exception("Type mismatch in assignment.")
            return self.builder.store(val, ptr)
        except IndexError:
            raise Exception("Undeclared identifier in assignment.")

    def visitParensExpr(self, ctx):
        return self.visit(ctx.expr())

    def visitCallExpr(self, ctx):
        ide = ctx.ID().getText()
        try:
            func = self.symbols.resolve(ide)
            if not isinstance(func, ir.Function):
                raise Exception("Trying to call non-function.")

            try:
                params = [self.visit(x) for x in ctx.exprList().expr()]
            except AttributeError:
                params = []
            if len(params) != len(func.args):
                raise Exception("Wrong number of parameters in call.")

            for param, arg in zip(params, func.args):
                if param.type != arg.type:
                    raise Exception("Wrong type of parameter.")
            return self.builder.call(func, params)
        except IndexError:
            raise Exception("Undeclared identifier in expression.")

    def visitMinusExpr(self, ctx):
        return self.builder.neg(self.visit(ctx.expr()))

    def visitMulDivExpr(self, ctx):
        op  = ctx.op.text
        lhs = self.visit(ctx.expr(0))
        rhs = self.visit(ctx.expr(1))
        if op == '*':
            return self.builder.mul(lhs, rhs)
        else:
            return self.builder.sdiv(lhs, rhs)

    def visitAddSubExpr(self, ctx):
        op  = ctx.op.text
        lhs = self.visit(ctx.expr(0))
        rhs = self.visit(ctx.expr(1))
        if op == '+':
            return self.builder.add(lhs, rhs)
        else:
            return self.builder.sub(lhs, rhs)

    def visitIdExpr(self, ctx):
        ide = ctx.ID().getText()
        try:
            ptr = self.symbols.resolve(ide)
            return self.builder.load(ptr)
        except IndexError:
            raise Exception("Undeclared identifier in expression.")

    def visitIntExpr(self, ctx):
        integer = ctx.INT().getText()
        return ir.Constant(self.types['Int'], int(integer))


if __name__ == '__main__':
    inputs  = FileStream(sys.argv[1])
    lexer   = LucyLexer(inputs)
    tokens  = CommonTokenStream(lexer)
    parser  = LucyParser(tokens)
    tree    = parser.program()
    codegen = CodeGenerator()
    codegen.visit(tree)
    print(codegen.module)
