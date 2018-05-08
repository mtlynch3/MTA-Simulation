import math
import random
import statistics
from collections import deque


class Station:

    def __init__(self, annual_ridership, num_track_beds, trash_threshold, cleaning_rate):
        self.annual_ridership = annual_ridership
        self.num_track_beds = num_track_beds

        #remove this; only needed for demand based cleaning simulation
        self.trash_threshold = trash_threshold

        self.cleaning_rate = cleaning_rate
        self.next_scheduled_cleaning = 0.0

        self.maintenance_delay = 0.0

        # (1.0/100000000) chosen to yield rate of approximately 1/5
        # i.e. 1 unit of trash arriving every five minutes at the BUSIEST stations
        self.trash_arrival_rate = (1.0/100000000) * annual_ridership

        self.fire_arrival_rate = 0.0

        #START OF NEW STUFF
        self.expenditure = 0.0
        self.productivity_cost = 0.0
        self.nyc_hourly_wage = 34.0

        #figure out better way to get these values
        self.base_cleaning_cost = 2000
        self.fire_cleaning_cost = 3500

        self. length = 0.0
        #END OF NEW STUFF

        # Units: minutes
        self.time = 0.0

        self.aggregate_trash = 0

        self.num_cleanings = 0

        self.num_scheduled_cleanings = 0

        self.num_fires = 0

        self.next_trash_arrival = 0.0
        self.next_fire_arrival = 0.0

    def initialize_simulation(self):
        self.time = 0.0

        self.aggregate_trash = 0
        self.num_cleanings = 0
        self.num_scheduled_cleanings = 0
        self.num_fires = 0

        #NEW THING
        self.expenditure = 0.0
        self.productivity_cost = 0.0
        #self.maintenance_delay = 0.0
        #END OF NEW THING

        self.next_trash_arrival = random.expovariate(self.trash_arrival_rate)
        self.next_fire_arrival = math.inf
        self.next_scheduled_cleaning = self.cleaning_rate

    def print_state(self):
        print("--------------------------------")
        print("Current Time: " + str(self.time))
        print("Aggregate Trash: " + str(self.aggregate_trash))
        print("Time until next trash: " + str(self.next_trash_arrival))
        print("Time until next cleaning: " + str(self.next_scheduled_cleaning))
        print("Time until next fire: " + str(self.next_fire_arrival))
        print("\nFire arrival rate: " + str(self.fire_arrival_rate))
        print("\nNumber of cleanings to date:" + str(self.num_cleanings))
        print("Number of scheduled cleanings to date:" + str(self.num_scheduled_cleanings))
        print("Number of fires to date:" + str(self.num_fires))
        #NEW THING
        print("Total maintenance expenditure to date: " + str(self.expenditure))
       # print("Total delay due to maintenance: " + str(self.maintenance_delay))
        print("Total productivity loss on NYC: " + str(self.productivity_cost))
        #END OF NEW THING
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
            self.num_scheduled_cleanings = self.num_scheduled_cleanings + 1
            self.expenditure += self.base_cleaning_cost
            self.next_scheduled_cleaning = self.cleaning_rate
        self.next_trash_arrival = random.expovariate(self.trash_arrival_rate)
        self.next_fire_arrival = math.inf

    def calculate_productivity_cost(self):
        #self.productivity_cost += self.length/60 * self.nyc_hourly_wage *
        self.productivity_cost += self.length/60 * self.nyc_hourly_wage * self.annual_ridership/525600 * self.length

    def simulate(self, end_time):
        # initialize start of simulation
        self.initialize_simulation()

        while (self.time < end_time):
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
                self.length = 90
                self.calculate_productivity_cost()
                self.time = self.time + time_elapsed
                self.clean(False)
            else:  # next_fire_arrival is the min
                # self.print_state()
                # print("********* FIRE!!!")
                time_elapsed = self.next_fire_arrival
                self.time = self.time + time_elapsed
                self.num_fires = self.num_fires + 1
                #self.length_of_fire = random.uniform(60,120)
                #self.maintenance_delay +=self.length_of_fire
                #print("The length of this fire is: " + str(self.length_of_fire))
                self.expenditure += self.fire_cleaning_cost
                self.clean(True)


print("Starting")
#s1 = Station(40000000, 2, 6000, 30240)
s1 = Station(200000, 1, 6000, 30240)
# s1 = Station(20000000, 1, 6000, 60000)
# s1 = Station(40000000, 1, 6000, 60000)
num_reps = 5
reps = []
for i in range(num_reps):
    s1.simulate(525600)
    s1.print_state()
    reps.append((s1.num_fires, s1.num_cleanings, s1.expenditure))
print()
print("Number of fires over simulation")
print([x[0] for x in reps])
print(sum([x[0] for x in reps])/len([x[0] for x in reps]))
print(statistics.stdev([x[0] for x in reps]))

print("number of cleanings over simulation")
print([x[1] for x in reps])
print(sum([x[1] for x in reps])/len([x[1] for x in reps]))
print(statistics.stdev([x[1] for x in reps]))


# NEW THING
print("Expenditure over simulation")
print([x[2] for x in reps])
print(sum([x[2] for x in reps])/len([x[2] for x in reps]))
print(statistics.stdev([x[2] for x in reps]))
# END OF NEW THING