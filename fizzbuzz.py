def fizzbuzz(n: int) -> str:
    """Return 'Fizz' if n is divisible by 3, 'Buzz' if divisible by 5,
    'FizzBuzz' if divisible by both, otherwise the number as a string."""
    result = ''
    if n % 3 == 0:
        result += 'Fizz'
    if n % 5 == 0:
        result += 'Buzz'
    return result or str(n)


def main():
    for i in range(1, 101):
        print(fizzbuzz(i))


if __name__ == '__main__':
    main()
