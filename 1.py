n = int(input("Введите число: "))

sequence = []
num = 1

while len(sequence) < n:
    for i in range(num):
        if len(sequence) < n:
            sequence.append(num)
    num += 1

print(''.join(map(str, sequence)))