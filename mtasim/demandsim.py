import math
import random
import statistics
from collections import deque


class Station:

    def __init__(self, annual_ridership, num_track_beds, trash_threshold):
        self.annual_ridership = annual_ridership
        self.num_track_beds = num_track_beds

        self.trash_threshold = trash_threshold

        self.maintenance_delay = 0.0

        # (1.0/100000000) chosen to yield rate of approximately 1/5
        # i.e. 1 unit of trash arriving every five minutes at the BUSIEST stations
        self.trash_arrival_rate = (1.0/100000000) * annual_ridership

        self.fire_arrival_rate = 0.0

        # Units: minutes
        self.time = 0.0

        self.aggregate_trash = 0

        self.num_cleanings = 0
        self.num_threshold_cleanings = 0

        self.num_fires = 0

        self.next_trash_arrival = 0.0
        self.next_fire_arrival = 0.0

    def initialize_simulation(self):
        self.time = 0.0

        self.aggregate_trash = 0
        self.num_cleanings = 0
        self.num_threshold_cleanings = 0
        self.num_fires = 0

        self.next_trash_arrival = random.expovariate(self.trash_arrival_rate)
        self.next_fire_arrival = math.inf

    def print_state(self):
        print("--------------------------------")
        print("Current Time: " + str(self.time))
        print("Aggregate Trash: " + str(self.aggregate_trash))
        print("Time until next trash: " + str(self.next_trash_arrival))
        print("Time until next fire: " + str(self.next_fire_arrival))
        print("\nFire arrival rate: " + str(self.fire_arrival_rate))
        print("\nNumber of cleanings to date:" + str(self.num_cleanings))
        print("Number of threshold cleanings to date:" + str(self.num_threshold_cleanings))
        print("Number of fires to date:" + str(self.num_fires))
        print("--------------------------------\n\n")

    def recalculate_next_fire_arrival(self):
        # set fire arrival rate based on aggregate trash
        self.fire_arrival_rate = (1.0/1000000000) * self.aggregate_trash
        # generate next_fire_arrival
        self.next_fire_arrival = random.expovariate(self.fire_arrival_rate)

    def clean(self, fire):
        self.num_cleanings = self.num_cleanings + 1
        self.aggregate_trash = 0
        # Include some time delay for the cleaning and add to productivity loss
        # Should depend on if fire == True
        # increment self.time by amount of time for cleaning / fire repair
        if not fire:
            self.num_threshold_cleanings = self.num_threshold_cleanings + 1
        self.next_trash_arrival = random.expovariate(self.trash_arrival_rate)
        self.next_fire_arrival = math.inf

    def simulate(self, end_time):
        # initialize start of simulation
        self.initialize_simulation()

        while self.time < end_time:
            if self.next_trash_arrival == min(self.next_fire_arrival, self.next_trash_arrival):
                # print("********* Trash Arrives")
                time_elapsed = self.next_trash_arrival
                self.time = self.time + time_elapsed
                self.aggregate_trash = self.aggregate_trash + 1
                if self.aggregate_trash > self.trash_threshold:
                    self.clean(False)
                else:
                    self.next_trash_arrival = random.expovariate(self.trash_arrival_rate)
                    self.recalculate_next_fire_arrival()
            else:  # next_fire_arrival is the min
                # self.print_state()
                # print("********* FIRE!!!")
                time_elapsed = self.next_fire_arrival
                self.time = self.time + time_elapsed
                self.num_fires = self.num_fires + 1
                self.clean(True)


print("Starting")
threshold = 10000
# s1 = Station(40000000, 2, threshold)
# s1 = Station(200000, 1, threshold)
s1 = Station(20000000, 1, threshold)
# s1 = Station(40000000, 1, threshold)
num_reps = 50
reps = []
for i in range(num_reps):
    s1.simulate(525600)
    s1.print_state()
    reps.append((s1.num_fires, s1.num_cleanings))
print()
print([x[0] for x in reps])
print(sum([x[0] for x in reps])/len([x[0] for x in reps]))
print(statistics.stdev([x[0] for x in reps]))

print([x[1] for x in reps])
print(sum([x[1] for x in reps])/len([x[1] for x in reps]))
print(statistics.stdev([x[1] for x in reps]))




