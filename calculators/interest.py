import math
principal = input("How much money do you currently have in the bank?")
rate = input("What is your interest rate?")
time = input("Over how many years is the interest compounded?")
actual_principal = float(principal)
actual_rate = float(rate)
actual_time = int(time)

#TODO: Calculate the total amount and print the result

A = math.pow((1 + actual_rate) , actual_time)
B = actual_principal*A


print(B)