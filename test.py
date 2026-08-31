from gpu import GPU


def test_vector_add():
    """Vector add: C[i] = A[i] + B[i]"""
    gpu = GPU(num_cores=2, threads_per_block=4)

    program = [
        0b0101000011011110,  # MUL R0, %blockIdx, %blockDim
        0b0011000000001111,  # ADD R0, R0, %threadIdx
        0b1001000100000000,  # CONST R1, #0
        0b1001001000001000,  # CONST R2, #8
        0b1001001100010000,  # CONST R3, #16
        0b0011010000010000,  # ADD R4, R1, R0
        0b0111010001000000,  # LDR R4, R4
        0b0011010100100000,  # ADD R5, R2, R0
        0b0111010101010000,  # LDR R5, R5
        0b0011011001000101,  # ADD R6, R4, R5
        0b0011011100110000,  # ADD R7, R3, R0
        0b1000000001110110,  # STR R7, R6
        0b1111000000000000,  # RET
    ]

    data = [0, 1, 2, 3, 4, 5, 6, 7,
            0, 1, 2, 3, 4, 5, 6, 7]

    gpu.load_program(program)
    gpu.load_data(data)
    result, cycles = gpu.run(num_threads=8)

    expected = [0, 2, 4, 6, 8, 10, 12, 14]
    actual = result[16:24]
    passed = actual == expected
    print(f"Vector Add:    {'PASS' if passed else 'FAIL'} ({cycles} cycles)")
    if not passed:
        print(f"  Expected: {expected}")
        print(f"  Got:      {actual}")
    return passed


def test_elementwise_mul():
    """Element-wise multiply: C[i] = A[i] * B[i]"""
    gpu = GPU(num_cores=2, threads_per_block=4)

    program = [
        0b0101000011011110,  # MUL R0, %blockIdx, %blockDim
        0b0011000000001111,  # ADD R0, R0, %threadIdx
        0b1001000100000000,  # CONST R1, #0
        0b1001001000001000,  # CONST R2, #8
        0b1001001100010000,  # CONST R3, #16
        0b0011010000010000,  # ADD R4, R1, R0
        0b0111010001000000,  # LDR R4, R4
        0b0011010100100000,  # ADD R5, R2, R0
        0b0111010101010000,  # LDR R5, R5
        0b0101011001000101,  # MUL R6, R4, R5
        0b0011011100110000,  # ADD R7, R3, R0
        0b1000000001110110,  # STR R7, R6
        0b1111000000000000,  # RET
    ]

    data = [1, 2, 3, 4, 5, 6, 7, 8,
            2, 3, 4, 5, 6, 7, 8, 9]

    gpu.load_program(program)
    gpu.load_data(data)
    result, cycles = gpu.run(num_threads=8)

    expected = [2, 6, 12, 20, 30, 42, 56, 72]
    actual = result[16:24]
    passed = actual == expected
    print(f"Elem Multiply: {'PASS' if passed else 'FAIL'} ({cycles} cycles)")
    if not passed:
        print(f"  Expected: {expected}")
        print(f"  Got:      {actual}")
    return passed


def test_mul_accum():
    """Multiply-accumulate: C[i] = A[i] * 2 + B[i]"""
    gpu = GPU(num_cores=2, threads_per_block=4)

    program = [
        0b0101000011011110,  # MUL R0, %blockIdx, %blockDim
        0b0011000000001111,  # ADD R0, R0, %threadIdx
        0b1001000100000000,  # CONST R1, #0        (A base)
        0b1001001000001000,  # CONST R2, #8        (B base)
        0b1001001100010000,  # CONST R3, #16       (C base)
        0b1001010000000010,  # CONST R4, #2        (constant 2)
        0b0011010100010000,  # ADD R5, R1, R0      (&A[i])
        0b0111010101010000,  # LDR R5, R5          (A[i])
        0b0101010101010100,  # MUL R5, R5, R4      (A[i] * 2)
        0b0011011000100000,  # ADD R6, R2, R0      (&B[i])
        0b0111011001100000,  # LDR R6, R6          (B[i])
        0b0011011101010110,  # ADD R7, R5, R6      (A[i]*2 + B[i])
        0b0011100000110000,  # ADD R8, R3, R0      (&C[i])
        0b1000000010000111,  # STR R8, R7
        0b1111000000000000,  # RET
    ]

    data = [1, 2, 3, 4, 5, 6, 7, 8,
            10, 20, 30, 40, 50, 60, 70, 80]

    gpu.load_program(program)
    gpu.load_data(data)
    result, cycles = gpu.run(num_threads=8)

    expected = [12, 24, 36, 48, 60, 72, 84, 96]
    actual = result[16:24]
    passed = actual == expected
    print(f"Multiply-Acc:  {'PASS' if passed else 'FAIL'} ({cycles} cycles)")
    if not passed:
        print(f"  Expected: {expected}")
        print(f"  Got:      {actual}")
    return passed


def test_matmul_2x2():
    """2x2 matrix multiply: C = A * B (unrolled, 2 cores x 2 threads)"""
    gpu = GPU(num_cores=2, threads_per_block=2)

    # A = [[1,2],[3,4]], B = [[5,6],[7,8]]
    # C = [[19,22],[43,50]]
    #
    # blockIdx = row, threadIdx = col
    # A[row][k] at addr: row*2 + k
    # B[k][col] at addr: k*2 + col
    # C[row][col] at addr: row*2 + col + 8 (output offset)
    #
    # C[row][col] = A[row][0]*B[0][col] + A[row][1]*B[1][col]

    program = [
        0b1001000100000010,  # CONST R1, #2
        0b0101000011010001,  # MUL R0, %blockIdx, R1      ; R0 = row*2
        0b0111001000000000,  # LDR R2, R0                 ; R2 = A[row][0]
        0b1001000100000001,  # CONST R1, #1
        0b0011001100000001,  # ADD R3, R0, R1             ; R3 = row*2+1
        0b0111001100110000,  # LDR R3, R3                 ; R3 = A[row][1]
        0b1001000100000100,  # CONST R1, #4               ; B base
        0b0011010000011111,  # ADD R4, R1, R15            ; R4 = 4+col
        0b0111010001000000,  # LDR R4, R4                 ; R4 = B[0][col]
        0b1001000100000110,  # CONST R1, #6               ; B[1][0] base
        0b0011010100011111,  # ADD R5, R1, R15            ; R5 = 6+col
        0b0111010101010000,  # LDR R5, R5                 ; R5 = B[1][col]
        0b0101011000100100,  # MUL R6, R2, R4             ; R6 = A[row][0]*B[0][col]
        0b0101011100110101,  # MUL R7, R3, R5             ; R7 = A[row][1]*B[1][col]
        0b0011100001100111,  # ADD R8, R6, R7             ; R8 = C[row][col]
        0b1001000100001000,  # CONST R1, #8               ; C base
        0b0011100100001111,  # ADD R9, R0, R15            ; R9 = row*2+col
        0b0011100100011001,  # ADD R9, R1, R9             ; R9 = 8+row*2+col
        0b1000000010011000,  # STR R9, R8                 ; C[row][col] = R8
        0b1111000000000000,  # RET
    ]

    data = [1, 2, 3, 4,     # A
            5, 6, 7, 8,     # B
            0, 0, 0, 0,     # C (output)
            0, 0, 0, 0]

    gpu.load_program(program)
    gpu.load_data(data)
    result, cycles = gpu.run(num_threads=4)

    expected = [19, 22, 43, 50]
    actual = result[8:12]
    passed = actual == expected
    print(f"2x2 MatMul:   {'PASS' if passed else 'FAIL'} ({cycles} cycles)")
    if not passed:
        print(f"  Expected: {expected}")
        print(f"  Got:      {actual}")
    return passed


def test_branch_loop():
    """Branch + loop: fill data[i] = i for i in 0..4 using CMP + BRn"""
    gpu = GPU(num_cores=1, threads_per_block=1)

    program = [
        0b1001000000000000,  # CONST R0, #0           ; counter = 0
        0b1001000100000001,  # CONST R1, #1           ; increment
        0b1001001000000101,  # CONST R2, #5           ; limit
        0b1001001100000000,  # CONST R3, #0           ; write addr
        # LOOP (addr 4):
        0b1000000000110000,  # STR R3, R0             ; data[addr] = counter
        0b0011001100110001,  # ADD R3, R3, R1         ; addr++
        0b0011000000000001,  # ADD R0, R0, R1         ; counter++
        0b0010000000000010,  # CMP R0, R2             ; compare counter, limit
        0b0001100000000100,  # BRn LOOP (addr 4)      ; if counter < limit, goto LOOP
        0b1111000000000000,  # RET
    ]

    data = [0] * 16

    gpu.load_program(program)
    gpu.load_data(data)
    result, cycles = gpu.run(num_threads=1)

    expected = [0, 1, 2, 3, 4]
    actual = result[0:5]
    passed = actual == expected
    print(f"Branch Loop:  {'PASS' if passed else 'FAIL'} ({cycles} cycles)")
    if not passed:
        print(f"  Expected: {expected}")
        print(f"  Got:      {actual}")
    return passed


def test_matmul_4x4():
    """4x4 matrix multiply: C = A * B using CMP + BRn loop.
       4 cores, 4 threads per block (blockIdx=row, threadIdx=col).
       A = [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]]
       B = identity matrix
       Expected: C = A"""
    gpu = GPU(num_cores=4, threads_per_block=4)

    program = [
        # Setup (addr 0-6)
        0b1001000100000001,  # CONST R1, #1            ; k increment
        0b1001001000000100,  # CONST R2, #4            ; N
        0b1001001100000000,  # CONST R3, #0            ; baseA
        0b1001010000010000,  # CONST R4, #16           ; baseB
        0b1001010100100000,  # CONST R5, #32           ; baseC
        0b1001100000000000,  # CONST R8, #0            ; acc = 0
        0b1001100100000000,  # CONST R9, #0            ; k = 0
        # LOOP (addr 7)
        0b0101011011010010,  # MUL R6, R13, R2         ; row * N
        0b0011011001101001,  # ADD R6, R6, R9          ; + k
        0b0011011001100011,  # ADD R6, R6, R3          ; + baseA
        0b0111011001100000,  # LDR R6, R6              ; A[row][k]
        0b0101011110010010,  # MUL R7, R9, R2          ; k * N
        0b0011011101111111,  # ADD R7, R7, R15         ; + col
        0b0011011101110100,  # ADD R7, R7, R4          ; + baseB
        0b0111011101110000,  # LDR R7, R7              ; B[k][col]
        0b0101101001100111,  # MUL R10, R6, R7         ; A[row][k] * B[k][col]
        0b0011100010001010,  # ADD R8, R8, R10         ; acc += ...
        0b0011100110010001,  # ADD R9, R9, R1          ; k++
        0b0010000010010010,  # CMP R9, R2              ; k < N?
        0b0001100000000111,  # BRn LOOP (addr 7)
        # Store result (addr 20-24)
        0b0101011011010010,  # MUL R6, R13, R2         ; row * N
        0b0011011001101111,  # ADD R6, R6, R15         ; + col
        0b0011011001100101,  # ADD R6, R6, R5          ; + baseC
        0b1000000001101000,  # STR R6, R8              ; C[row][col] = acc
        0b1111000000000000,  # RET
    ]

    A = [1, 2, 3, 4,
         5, 6, 7, 8,
         9, 10, 11, 12,
         13, 14, 15, 16]

    B = [1, 0, 0, 0,
         0, 1, 0, 0,
         0, 0, 1, 0,
         0, 0, 0, 1]

    data = A + B + [0] * 16

    gpu.load_program(program)
    gpu.load_data(data)
    result, cycles = gpu.run(num_threads=16)

    expected = A[:]
    actual = result[32:48]
    passed = actual == expected
    print(f"4x4 MatMul:   {'PASS' if passed else 'FAIL'} ({cycles} cycles)")
    if not passed:
        print(f"  Expected: {expected}")
        print(f"  Got:      {actual}")
    return passed


if __name__ == "__main__":
    results = []
    results.append(test_vector_add())
    results.append(test_elementwise_mul())
    results.append(test_mul_accum())
    results.append(test_matmul_2x2())
    results.append(test_branch_loop())
    results.append(test_matmul_4x4())

    print()
    if all(results):
        print(f"All {len(results)} tests passed!")
    else:
        print(f"{sum(results)}/{len(results)} tests passed")
