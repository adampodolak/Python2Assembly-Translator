;Call_param.py:

BR Main
_UNIV:   .EQUATE 42
;
;******* void my_func()
result:  .EQUATE 0
x:       .BLOCK 2
mx:      .EQUATE 4
;
my_func: SUBSP 2,i
         LDWA mx,s
         ADDA _UNIV,i
         STWA result,s
         DECO result,s
         ADDSP 2,i
         RET	
;
;******* int main()
Main:    NOP1
         SUBSP 2,i
         DECI x,d
         LDWA x,d
         STWA 0,s
         CALL my_func
         ADDSP 2,i
         STOP
         .END