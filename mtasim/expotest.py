import math
import random
import statistics

rate = 20000000.0/100000000.0  # 0.2 arrivals of trash per minute
limit = 30240.0  # 30240 minutes = 3 weeks

def generate_three_weeks_of_trash():
    time = 0.0  # start time at 0
    num_arrivals = 0  # set number of arrivals to be zero at start
    interarrival_time = random.expovariate(rate)  # generate an initial interarrival time
    while time < limit:  # while three weeks have not yet elapsed
        time = time + interarrival_time  # advance clock by interarrival time
        num_arrivals = num_arrivals + 1  # increment number of arrivals
        interarrival_time = random.expovariate(rate)  # generate new interarrival time
    print(num_arrivals)  # print the total number of arrivals of trash in this three week period

for i in range(50):
    generate_three_weeks_of_trash()

print("Notice how steady/consistent the amount of trash generated in 3 weeks is / how little variance there is")