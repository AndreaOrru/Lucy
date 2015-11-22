grammar Lucy;


//////////////
//  Parser  //
//////////////

program:
    stmt* ;

stmt
    : typ ID ';'       # Decl
    | ID '=' expr ';'  # Assign
    ;

typ:
    'Int' ;

expr
    : '-' expr                  # MinusExpr
    | expr op=('*' | '/') expr  # MulDivExpr
    | expr op=('+' | '-') expr  # AddSubExpr
    | ID                        # IdExpr
    | INT                       # IntExpr
    | '(' expr ')'              # ParensExpr
    ;


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
