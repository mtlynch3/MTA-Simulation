# NOTE: WIP: NOT FUNCTIONAL

import math
import random
import statistics
from collections import deque


class Station:

    def __init__(self, annual_ridership, num_track_beds, trash_threshold, cleaning_rate):
        self.trash_arrival_rate_scalar = 1.0/100000000
        self.fire_arrival_rate_scalar = 1.0/1000000000

        self.annual_ridership = annual_ridership
        self.num_track_beds = num_track_beds

        self.trash_threshold = trash_threshold

        self.cleaning_rate = cleaning_rate
        self.next_scheduled_cleaning = 0.0
        self.num_scheduled_cleanings = 0

        self.maintenance_delay = 0.0

        # (1.0/100000000) chosen to yield rate of approximately 1/5
        # i.e. 1 unit of trash arriving every five minutes at the BUSIEST stations
        self.trash_arrival_rate = self.trash_arrival_rate_scalar * (annual_ridership/num_track_beds)

        # Units: minutes
        self.time = 0.0




        self.aggregate_trash = [0, 0]
        # self.aggregate_trash = 0

        self.fire_arrival_rate = [0.0, 0.0]
        # self.fire_arrival_rate = 0.0

        self.num_cleanings = [0, 0]
        # self.num_cleanings = 0

        self.num_fires = [0, 0]
        # self.num_fires = 0

        self.diverged = False
        self.shared_next_trash_arrivals = deque()
        self.next_trash_arrival = [0.0, 0.0]
        self.next_fire_arrival = [0.0, 0.0]
        # self.next_trash_arrival = 0.0
        # self.next_fire_arrival = 0.0

    def initialize_simulation(self):
        self.time = 0.0

        self.aggregate_trash = [0, 0]
        self.num_cleanings = [0, 0]
        self.num_scheduled_cleanings = 0
        self.num_fires = [0, 0]

        self.diverged = False
        self.shared_next_trash_arrivals = deque()

        tt = random.expovariate(self.trash_arrival_rate)
        self.next_trash_arrival = [tt, tt]
        self.next_fire_arrival = [math.inf, math.inf]
        self.next_scheduled_cleaning = self.cleaning_rate

    def print_state(self):
        for i in range(2):
            print(("Periodic " if i == 0 else "Demand ") + "--------------------------------")
            print("Current Time: " + str(self.time))
            print("Aggregate Trash: " + str(self.aggregate_trash[i]))
            print("Time until next trash: " + str(self.next_trash_arrival[i]))
            print("Time until next cleaning: " + str(self.next_scheduled_cleaning))
            print("Time until next fire: " + str(self.next_fire_arrival[i]))
            print("\nFire arrival rate: " + str(self.fire_arrival_rate[i]))
            print("\nNumber of cleanings to date:" + str(self.num_cleanings[i]))
            print("Number of scheduled cleanings to date:" + str(self.num_scheduled_cleanings))
            print("Number of fires to date:" + str(self.num_fires[i]))
            print("--------------------------------\n\n")

    def recalculate_next_fire_arrival(self, s):
        # set fire arrival rate based on aggregate trash
        self.fire_arrival_rate[s] = self.fire_arrival_rate_scalar * self.aggregate_trash[s]
        # generate next_fire_arrival
        # TODO: MAKE SURE YOU USE THE SAME GENERATED RV'S FOR EACH SIM FOR NEXT_FIRE_ARRIVAL, IF POSSIBLE
        self.next_fire_arrival[s] = random.expovariate(self.fire_arrival_rate[s])

    def clean(self, s, fire):
        self.num_cleanings[s] = self.num_cleanings[s] + 1
        self.aggregate_trash[s] = 0
        # Include some time delay for the cleaning and add to productivity loss
        # Should depend on if fire == True
        # increment self.time by amount of time for cleaning / fire repair
        if not fire and s == 0:
            self.num_scheduled_cleanings = self.num_scheduled_cleanings + 1
            self.next_scheduled_cleaning = self.cleaning_rate
        self.next_trash_arrival[s] = random.expovariate(self.trash_arrival_rate)
        self.next_fire_arrival[s] = math.inf

    def dual_trash_arrival(self):
        # print("********* Trash Arrives")
        time_elapsed = self.next_trash_arrival[0]
        self.time = self.time + time_elapsed
        aggregate_trash = self.aggregate_trash[0]
        self.aggregate_trash[0] = aggregate_trash + 1
        self.aggregate_trash[1] = aggregate_trash + 1
        # DONT FORGET TO ADD THRESHOLD CHECK
        self.next_scheduled_cleaning = self.next_scheduled_cleaning - time_elapsed
        next_trash_arrival = random.expovariate(self.trash_arrival_rate)
        self.next_trash_arrival[0] = next_trash_arrival
        self.recalculate_next_fire_arrival(0)
        if self.aggregate_trash[1] > self.trash_threshold:
            self.diverged = True
            self.threshold_cleaning()
        self.next_trash_arrival[1] = next_trash_arrival
        self.recalculate_next_fire_arrival(1)

    def trash_arrival(self, s):
        # DONT FORGET TO ADD THRESHOLD CHECK
        # print("********* Trash Arrives")
        time_elapsed = self.next_trash_arrival
        self.aggregate_trash = self.aggregate_trash + 1
        self.next_scheduled_cleaning = self.next_scheduled_cleaning - time_elapsed
        self.next_trash_arrival = random.expovariate(self.trash_arrival_rate)
        self.time = self.time + time_elapsed
        self.recalculate_next_fire_arrival()

    def simulate(self, end_time):
        # initialize start of simulation
        self.initialize_simulation()

        while self.time < end_time:
            if self.diverged:
                min_time = min(self.next_scheduled_cleaning, self.next_fire_arrival[0], self.next_trash_arrival[0], self.next_fire_arrival[1], self.next_trash_arrival[1])
                if self.next_trash_arrival[0] == min_time:
                    # process trash arrive for sim 0
                    pass
                elif self.next_trash_arrival[1] == min_time:
                    # process trash arrival for sim 1
                    pass
                elif self.next_scheduled_cleaning == min_time:
                    # process scheduled cleaning for sim 0
                    pass
                elif self.next_fire_arrival[0] == min_time:
                    # process fire arrival for sim 0
                    pass
                else: #  self.next_fire_arrival[1] == min_time?
                    # process fire arrival for sim 1
                    pass
            else:
                min_time = min(self.next_scheduled_cleaning, self.next_fire_arrival[0], self.next_trash_arrival[0])
                if self.next_trash_arrival[0] == min_time:
                    # process trash arrival for both sims
                    self.dual_trash_arrival()
                elif self.next_scheduled_cleaning[0] == min_time:
                    # set to diverged
                    # process scheduled cleaning
                    pass
                else:  # self.next_fire_arrival[0] == min_time?
                    # process fire for both sims
                    pass

        while self.time < end_time:
            if self.next_trash_arrival == min(self.next_scheduled_cleaning, self.next_fire_arrival, self.next_trash_arrival):
                # print("********* Trash Arrives")
                time_elapsed = self.next_trash_arrival
                self.aggregate_trash = self.aggregate_trash + 1
                self.next_scheduled_cleaning = self.next_scheduled_cleaning - time_elapsed
                self.next_trash_arrival = random.expovariate(self.trash_arrival_rate)
                self.time = self.time + time_elapsed
                self.recalculate_next_fire_arrival()
            elif self.next_scheduled_cleaning == min(self.next_scheduled_cleaning, self.next_fire_arrival, self.next_trash_arrival):
                # print("********* Scheduled Cleaning")
                time_elapsed = self.next_scheduled_cleaning
                self.time = self.time + time_elapsed
                self.clean(False)
            else:  # next_fire_arrival is the min
                # self.print_state()
                # print("********* FIRE!!!")
                time_elapsed = self.next_fire_arrival
                self.time = self.time + time_elapsed
                self.num_fires = self.num_fires + 1
                self.clean(True)


print("Starting")
# s1 = Station(40000000, 2, 6000, 30240)
# s1 = Station(200000, 1, 6000, 30240)
# s1 = Station(200000, 1, 6000, 250000)
s1 = Station(40000000, 1, 6000, 60000)
num_reps = 50
reps = []
for i in range(num_reps):
    s1.simulate(525600)
    s1.print_state()
    reps.append(s1.num_fires)
print()
print(reps)
print(sum(reps)/len(reps))
print(statistics.stdev(reps))




