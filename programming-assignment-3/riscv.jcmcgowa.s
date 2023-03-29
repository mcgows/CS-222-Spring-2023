    addi sp, x0, 1024
    jal ra, main

f1:
    addi    sp, sp, -16 # reserve 4 words on the stack
    sw      ra, 12(sp)  # save ra in mem[sa+12]
    sw      s0, 8(sp)   # save fp (s0) in mem[sp+8]
    addi    s0, sp, 16  # s0 <- sp + 16

    sw      a0, -12(s0) # save a0 in mem[s0-12]
    lw      a0, -12(s0) # load a0 from mem[s0-12]
    addi    a0, x0, 23  # a1 <- 0 + 23 : this is i
    sw      a0, -16(s0) # save i
    lw      a0, -16(s0) # load i
    lw      a1, -12(s0) # load p
    add     a0, a0, a1  # a0 <- a0 + a1 
    sw      a0, -16(s0) # store a0 in mem[s0-16]
    lw      a0, -16(s0) # load a0 from mem[s0-16]

    lw      s0, 8(sp)   # restore s0
    lw      ra, 12(sp)  # restore ra
    addi    sp, sp, 16  # restore the stack pointer
    jalr    x0, ra, 0   # return (jump to ra)

f2:
    addi    sp, sp, -16 # reserve 4 words on the stack
    sw      ra, 12(sp)  # save ra in mem[sa+12]
    sw      s0, 8(sp)   # save fp (s0) in mem[sp+8]
    addi    s0, sp, 16  # s0 <- sp + 16

    sw      a0, -12(s0) # save p1
    lw      a0, -12(s0) # load p1

    sw      a1, -16(s0) # save p2
    lw      a1, -16(s0) # load p2

    blt     a1, a0, L1  # branch if p1 > p2
    blt     a0, a1, L2  # branch if p2 > p1
    jal     x0, L3
    
    L1:
        addi    a0, x0, 1
        jal     x0, L4

    L2:
        addi    a0, x0, -1
        jal     x0, L4

    L3:
        addi    a0, x0, 0

    L4:
        lw      s0, 8(sp)   # restore s0
        lw      ra, 12(sp)  # restore ra
        addi    sp, sp, 16  # restore the stack pointer
        jalr    x0, ra, 0   # return (jump to ra)


f3:
    addi    sp, sp, -32     # reserve 4 words on the stack
    sw      ra, 28(sp)      # save ra in mem[sa+28]
    sw      s0, 24(sp)      # save fp (s0) in mem[sp+24]
    addi    s0, sp, 32      # s0 <- sp + 32
    sw      a0, -12(s0)     # v, on the stack
    sw      a1, -16(s0)     # n, on the stack
    blt     a1, x0, error   # error if n <= 0
    addi    a0, x0, 0       # put 0 in a0
    sw      a0, -20(s0)     # i = 0, on the stack

    lw      a2, -12(s0)     # load v addr into a2
    add     a0, a0, a2      # load v addr + offset for v[0]
    lw      a0, 0(a0)       # max = v[0]
    sw      a0, -24(s0)     # save max on the stack

    loop:
        lw      a0, -20(s0)             # load i
        lw      a1, -16(s0)             # load n
        beq     a0, a1, done            # branch if i == n
        lw      a1, -12(s0)             # load v
        slli    a0, a0, 2               # compute index by i * 4
        add     a0, a0, a1              # computer mem addr
        lw      a2, 0(a0)               # load v[i]
        lw      a0, -24(s0)             # load max
        blt     a0, a2, greater-than    # branch if max < curr
    loop-return-from-greater:
        lw      a0, -20(s0)             # load i
        addi    a0, a0, 1               # increment i
        sw      a0, -20(s0)             # save i
        jal     x0, loop

    greater-than:
        sw      a2, -24(s0)             # save v[i] to max memory 
        jal     x0, loop-return-from-greater

    error:
        ERROR   x0

    done:
        lw      a0, -24(s0)     # loads the return val
        lw      s0, 24(sp)
        lw      ra, 28(sp)
        addi    sp, sp, 32
        jalr    x0, ra, 0



main:
    # call f3
    addi a0, x0, 200
    addi a1, x0, 4
    sw      a1, 0(a0)
    sw      x0, 4(a0)
    sw      x0, 8(a0)
    sw      x0, 12(a0)

    add a2, a1, a1
    sw      a2, 16(a0)

    addi    a1, x0, 5
    jal     ra, f3
    