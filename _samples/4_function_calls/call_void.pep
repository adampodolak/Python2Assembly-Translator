
BR Main 
_UNIV:   .EQUATE 42
;
;******* void my_func()
mValue:       .EQUATE 0
mResult:      .EQUATE 2
;
my_func: SUBSP 4,i
         DECI mValue,s
         LDWA mValue,s
         ADDA _UNIV,i
         STWA mResult,s
         DECO mResult,s
         RET	
;
;******* int main()
Main:    NOP1
         CALL my_func
         STOP
         .END