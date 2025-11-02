

try:
    a = input("Введите число: ")
    number = int(a)
    if 100 <= number <= 999 and number%2==0 and number%3==0:
        print(f"✓ Число {number} подходит")
    else:
        print(f"✗ Число {number} не подходит под условия")
except ValueError:
    print("✗ Это не целое число test")


