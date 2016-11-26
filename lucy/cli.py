import sys
from antlr4 import FileStream, CommonTokenStream
from lucy.antlr.LucyLexer import LucyLexer
from lucy.antlr.LucyParser import LucyParser


def main():
    input_stream = FileStream(sys.argv[1])
    lexer = LucyLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = LucyParser(token_stream)
    tree = parser.program()
