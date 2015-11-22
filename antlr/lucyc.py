#!/usr/bin/env python3

import sys
from antlr4 import *
from llvmlite import ir
from LucyLexer import LucyLexer
from LucyParser import LucyParser
from LucyVisitor import LucyVisitor


class CodeGenerator(LucyVisitor):
    def __init__(self):
        void_func = ir.FunctionType(ir.VoidType(), tuple())
        
        self.module  = ir.Module()
        self.main    = ir.Function(self.module, void_func, name='main')
        self.block   = self.main.append_basic_block(name='begin')
        self.builder = ir.IRBuilder(self.block)

        self.symbols = dict()

    def visitProgram(self, ctx):
        for child in ctx.children:
            self.visit(child)
        self.builder.ret_void()

    def visitDecl(self, ctx):
        ide = ctx.ID().getText()
        ptr = self.builder.alloca(ir.IntType(32), name=ide)
        self.symbols[ide] = ptr

    def visitAssign(self, ctx):
        ide = ctx.ID().getText()
        try:
            ptr = self.symbols[ide]
            self.builder.store(self.visit(ctx.expr()), ptr)
        except IndexError:
            raise Exception("Undeclared identifier in assignment.")

    def visitParensExpr(self, ctx):
        return self.visit(ctx.expr())

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
            ptr = self.symbols[ide]
            return self.builder.load(ptr)
        except IndexError:
            raise Exception("Undeclared identifier in expression.")

    def visitIntExpr(self, ctx):
        integer = ctx.INT().getText()
        return ir.Constant(ir.IntType(32), int(integer))


if __name__ == '__main__':
    inputs  = FileStream(sys.argv[1])
    lexer   = LucyLexer(inputs)
    tokens  = CommonTokenStream(lexer)
    parser  = LucyParser(tokens)
    tree    = parser.program()
    codegen = CodeGenerator()
    codegen.visit(tree)
    print(codegen.module)
