; Programa de teste da micro-CPU (versao final) - usa todas as instrucoes
; Sintaxe: ADD RA, RB, RD  (RD = RA + RB)   |  ADD RA, valor, RD  (RD = RA + valor)
;          MOV valor, RD   |  MOV RA, RD     |  CMP RA, RB  |  JMP end  |  JMP RA
;          JZ RA, end      |  JE end         |  RST
; "Armadilha" = instrucao que NUNCA deve executar; se executar, aparece F no display.

00: MOV 7, R0          ; R0 = 7
01: MOV 3, R1          ; R1 = 3
02: ADD R0, R1, R2     ; R2 = 7 + 3 = 10 (A)
03: SUB R0, R1, R3     ; R3 = 7 - 3 = 4
04: MUL R1, R3, R3     ; R3 = 3 x 4 = 12 (C)
05: DIV R2, R1, R2     ; R2 = 10 / 3 = 3
06: ADD R0, 2, R0      ; R0 = 7 + 2 = 9
07: SUB R0, 4, R0      ; R0 = 9 - 4 = 5
08: MUL R0, 3, R1      ; R1 = 5 x 3 = 15 (F)
09: DIV R1, 4, R1      ; R1 = 15 / 4 = 3
10: JMP R3             ; salta para o endereco guardado em R3 (12)
11: MOV 15, R2         ; armadilha
12: MOV R3, R0         ; R0 = R3 = 12 (C)
13: CMP R1, R2         ; 3 = 3 -> flag "igual" = 1 (LEDR9 acende)
14: JE 16              ; flag = 1 -> salta
15: MOV 15, R3         ; armadilha
16: MOV 0, R3          ; R3 = 0
17: JZ R3, 19          ; R3 = 0 -> salta
18: MOV 15, R2         ; armadilha
19: MOV 3, R1          ; laco: R1 = 3
20: JZ R1, 23          ; sai do laco quando R1 = 0
21: SUB R1, 1, R1      ; R1 = R1 - 1
22: JMP 20             ; volta para o teste
23: CMP R1, R2         ; 0 x 3 -> flag "igual" = 0 (LEDR9 apaga)
24: JE 15              ; flag = 0 -> NAO salta
25: JZ R2, 15          ; R2 = 3 -> NAO salta
26: RST                ; zera tudo e recomeca do endereco 0
