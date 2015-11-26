grammar Lucy;


//////////////
//  Parser  //
//////////////

program:
    (varDecl | funcDecl)* ;

varDecl:
    ID ':' typ ('=' expr)? ';' ;

funcDecl:
    ID '(' params? ')' ('->' typ)? block ;

typ:
    'Int' ;

params:
    param (',' param)* ;

param:
    ID ':' typ ;

expr
    : ID '(' exprList? ')'      # CallExpr
    | '-' expr                  # MinusExpr
    | expr op=('*' | '/') expr  # MulDivExpr
    | expr op=('+' | '-') expr  # AddSubExpr
    | ID                        # IdExpr
    | INT                       # IntExpr
    | '(' expr ')'              # ParensExpr
    | assign                    # AssignExpr
    ;

exprList:
    expr (',' expr)* ;

block:
    '{' stmt* '}' ;

stmt
    : varDecl
    | block
    | assign ';'
    | ret
    | expr   ';' ;

assign:
    ID '=' expr ;

ret:
    'return' expr? ';' ;


/////////////
//  Lexer  //
/////////////

ID:
    Letter (Letter | Digit)* ;

INT:
    Digit+ ;

fragment Digit:
    [0-9] ;

fragment Letter:
    [a-zA-Z] ;

SPACE:
    [ \t\n\r]+ -> skip ;

COMMENT:
    '//' ~[\r\n]* -> skip ;
