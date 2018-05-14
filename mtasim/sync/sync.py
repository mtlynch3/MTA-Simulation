import math
import random
import statistics
from collections import deque
import numpy


class Station:

    def __init__(self, annual_ridership, num_track_beds, trash_threshold, cleaning_rate):
        # SHARED
        self.annual_ridership = annual_ridership
        self.num_track_beds = num_track_beds

        # SPECIFIC: demand sim
        self.trash_threshold = trash_threshold

        # SPECIFIC: baseline sim
        self.cleaning_rate = cleaning_rate
        self.next_scheduled_cleaning = 0.0

        # SHARED
        # (1.0/100000000) chosen to yield rate of approximately 1/5
        # i.e. 1 unit of trash arriving every five minutes at the BUSIEST stations
        self.trash_arrival_rate_scalar = 1.0/100000000
        self.trash_arrival_rate = self.trash_arrival_rate_scalar * annual_ridership
        # Choose fire_arrival_rate_scalar to yield approximately two fires per year at the busiest stations
        self.fire_arrival_rate_scalar = 1.0/1000000000

        # SHARED
        self.diverged = False
        self.next_fire_arrival_uniform = 0.0
        self.next_trash_arrival = 0.0
        self.next_fire_arrival_shared = 0.0

        # SHARED
        # Units: minutes
        self.time = 0.0
        self.maintenance_delay = 0.0

        # SPECIFIC: baseline sim
        self.aggregate_trash_baseline = 0
        self.num_cleanings_baseline = 0
        self.num_scheduled_cleanings = 0
        self.num_fires_baseline = 0
        self.next_fire_arrival_baseline = 0.0
        self.fire_arrival_rate_baseline = 0.0

        # SPECIFIC: demand sim
        self.aggregate_trash_alt = 0
        self.num_cleanings_alt = 0
        self.num_threshold_cleanings = 0
        self.num_fires_alt = 0
        self.next_fire_arrival_alt = 0.0
        self.fire_arrival_rate_alt = 0.0

    def initialize_simulation(self):
        # initialize time
        self.time = 0.0

        # initialize values for baseline sim
        self.aggregate_trash_baseline = 0
        self.num_cleanings_baseline = 0
        self.num_scheduled_cleanings = 0
        self.num_fires_baseline = 0

        # initialize values for alt sim
        self.aggregate_trash_alt = 0
        self.num_cleanings_alt = 0
        self.num_threshold_cleanings = 0
        self.num_fires_alt = 0

        # to be used for fire_arrivals
        self.next_fire_arrival_uniform = 0.0
        # initialize residual clocks
        self.next_trash_arrival = random.expovariate(self.trash_arrival_rate)
        self.next_fire_arrival_shared = math.inf
        self.next_fire_arrival_baseline = math.inf
        self.next_fire_arrival_alt = math.inf
        self.next_scheduled_cleaning = self.cleaning_rate

    def print_state(self):
        # TODO: Add alt stuff
        print("--------------------------------")
        print("Current Time: " + str(self.time))
        print("Aggregate Trash: " + str(self.aggregate_trash_baseline))
        print("Time until next trash: " + str(self.next_trash_arrival))
        print("Time until next cleaning: " + str(self.next_scheduled_cleaning))
        print("Time until next fire: " + str(self.next_fire_arrival_baseline))
        print("\nFire arrival rate: " + str(self.fire_arrival_rate_baseline))
        print("\nNumber of cleanings to date:" + str(self.num_cleanings_baseline))
        print("Number of scheduled cleanings to date:" + str(self.num_scheduled_cleanings))
        print("Number of fires to date:" + str(self.num_fires_baseline))
        print("--------------------------------\n\n")

    def recalculate_next_fire_arrival(self):
        # set fire arrival rate based on aggregate trash
        self.fire_arrival_rate_baseline = self.fire_arrival_rate_scalar * self.aggregate_trash_baseline
        # generate next_fire_arrival
        self.next_fire_arrival_uniform = numpy.random.uniform(0.0,1.0)
        # zn = (-1.0/self.fire_arrival_rate)*math.log(1-self.next_fire_arrival_uniform)
        # self.next_fire_arrival = random.expovariate(self.fire_arrival_rate)
        self.next_fire_arrival_baseline = (-1.0 / self.fire_arrival_rate_baseline) * math.log(1 - self.next_fire_arrival_uniform)

    def clean(self, fire):
        self.num_cleanings_baseline = self.num_cleanings_baseline + 1
        self.aggregate_trash_baseline = 0
        # Include some time delay for the cleaning and add to productivity loss
        # Should depend on if fire == True
        # increment self.time by amount of time for cleaning / fire repair
        if not fire:
            self.num_scheduled_cleanings = self.num_scheduled_cleanings + 1
            self.next_scheduled_cleaning = self.cleaning_rate
        self.next_trash_arrival = random.expovariate(self.trash_arrival_rate)
        self.next_fire_arrival_baseline = math.inf

    def simulate(self, end_time):
        # initialize start of simulation
        self.initialize_simulation()

        while (self.time < end_time):
            if self.next_trash_arrival == min(self.next_scheduled_cleaning, self.next_fire_arrival_baseline, self.next_trash_arrival):
                # print("********* Trash Arrives")
                time_elapsed = self.next_trash_arrival
                self.aggregate_trash_baseline = self.aggregate_trash_baseline + 1
                self.next_scheduled_cleaning = self.next_scheduled_cleaning - time_elapsed
                self.next_trash_arrival = random.expovariate(self.trash_arrival_rate)
                self.time = self.time + time_elapsed
                self.recalculate_next_fire_arrival()
            elif self.next_scheduled_cleaning == min(self.next_scheduled_cleaning, self.next_fire_arrival_baseline, self.next_trash_arrival):
                # print("********* Scheduled Cleaning")
                time_elapsed = self.next_scheduled_cleaning
                self.time = self.time + time_elapsed
                self.clean(False)
            else:  # next_fire_arrival is the min
                # self.print_state()
                # print("********* FIRE!!!")
                time_elapsed = self.next_fire_arrival_baseline
                self.time = self.time + time_elapsed
                self.num_fires_baseline = self.num_fires_baseline + 1
                self.clean(True)


print("Starting")
# s1 = Station(40000000, 2, 6000, 30240)
# s1 = Station(200000, 1, 6000, 30240)
s1 = Station(20000000, 1, 6000, 60000)
# s1 = Station(40000000, 1, 6000, 60000)
num_reps = 50
reps = []
for i in range(num_reps):
    s1.simulate(525600)
    s1.print_state()
    reps.append((s1.num_fires_baseline, s1.num_cleanings_baseline))
print()
print([x[0] for x in reps])
print(sum([x[0] for x in reps])/len([x[0] for x in reps]))
print(statistics.stdev([x[0] for x in reps]))

print([x[1] for x in reps])
print(sum([x[1] for x in reps])/len([x[1] for x in reps]))
print(statistics.stdev([x[1] for x in reps]))




