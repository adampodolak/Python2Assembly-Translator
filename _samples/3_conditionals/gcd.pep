         BR      program 
a:      .BLOCK 2 
b:      .BLOCK 2
program: DECI a,d
         DECI b,d
test:    LDWA a,d
         CPWA b, d
         BREQ end_w
body:    LDWA a,d
         CPWA b,d
         BRLE else_b
if_b:    LDWA a,d
         SUBA b,d
         STWA a,d
         BR test
else_b:  LDWA b,d
         SUBA a,d
         STWA b,d
         BR test
end_w:   DECO a,d
         .END
         