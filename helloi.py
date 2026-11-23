counter = 5
while counter <= 1000:
 
    fizz = counter % 3 == 0 
    buzz = counter % 5 == 0 
    fizzbuzz = fizz and buzz

    if fizz and buzz: 
        print(str(counter) + " fizzbuzz")
    elif fizz:
        print(str(counter) + "fizz")
    elif buzz:
        print(str(counter) + " buzz") 

    counter = counter + 1


def run_fizzbuzz(start, end):
    counter = start
    while counter <= end:
 
        fizz = counter % 3 == 0 
        buzz = counter % 5 == 0 
        fizzbuzz = fizz and buzz

        if fizz and buzz: 
            print(str(counter) + " fizzbuzz")
        elif fizz:
            print(str(counter) + "fizz")
        elif buzz:
            print(str(counter) + " buzz") 

    counter = counter + 1



