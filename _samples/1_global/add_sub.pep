                BR program
UNIV:          .BLOCK 2
variable:       .BLOCK 2
value:          .BLOCK 2
result:         .BLOCK 2
; Top Level instructions
tl:             NOP1
                DECI value,d
                LDWA 42,i
                STWA _UNIV,d
                LDWA value,d
                ADDA _UNIV,d
                STWA result,d
                LDWA 3,i
                STWA variable,d
                LDWA result,d
                SUBA variable,d
                STWA result,d
                LDWA result,d
                SUBA 1,i
                STWA result,d
                DECO result,d
                .END