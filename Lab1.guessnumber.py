import random

# Generate a random number between 1 and 20
num = random.randint(1, 20)
print("The random number between 1 and 20 has been generated.")

guessed = False
while not guessed:
    # Prompt the user to guess the number
    guess = int(input("Enter your guess: "))

    if guess < num:
        print("Your guess is too low. Try again.")
    elif guess > num:
        print("Your guess is too high. Try again.")
    else:
        print("Congratulations! You've guessed the number.")
        guessed = True

