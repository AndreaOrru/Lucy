#!/bin/sh

cd lucy/parser
antlr4 -visitor -no-listener -Dlanguage=Python3 Lucy.g4
