LDA #$00
count_up:
ADC #$01
BCC count_up
CLC

LDA #$FF
count_down:
SBC #$01
BNE count_down
BRK