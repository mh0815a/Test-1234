counter = 10
while counter > 0: 
    counter = counter - 1
    with open("some_file.txt", "a") as f: 
        f.write(f"Counter is now: {counter}\n")

with open("some_file.txt", "r") as f: 
    content = f.read()
    print(content)













