n = int(input())

result = 0

while n > 0:
    while n > 1:
        result = result + 1
        n = n - 1
    result = result + 1
    n = n - 1

print(result)