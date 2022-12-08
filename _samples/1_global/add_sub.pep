         BR      program     
UNIV:    .WORD 42
value:       .BLOCK 2
result:  .BLOCK 2
variable: .WORD 3
one: .WORD 1
program: DECI value,d
         LDWA UNIV,d
         ADDA value,d
         SUBA variable, d
         SUBA one,d
         STWA result,d
         DECO result,d
         .ENDa
