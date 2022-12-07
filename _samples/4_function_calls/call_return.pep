BR Main
_UNIV:   .EQUATE 42
;
;******* void my_func()
x:       .BLOCK 2
mx:      .EQUATE 2
retVal:  .EQUATE 4
;
my_func: LDWA mx,s
         ADDA _UNIV,i
         STWA retVal,s
         RET	
;
;******* int main()
Main:    NOP1
         SUBSP 4,i
         DECI x,d
         LDWA x,d
         STWA 0,s
         CALL my_func
         DECO 2,s
         ADDSP 4,i
         STOP
         .END