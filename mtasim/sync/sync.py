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
        self.trash_arrival_rate_scalar = 1.0/190
        number_of_minutes_per_year = 525600
        self.riders_per_minute_per_track = ((annual_ridership/num_track_beds)/number_of_minutes_per_year)
        self.trash_arrival_rate = self.trash_arrival_rate_scalar * self.riders_per_minute_per_track
        # Choose fire_arrival_rate_scalar to yield approximately two fires per year at the busiest stations
        self.fire_arrival_rate_scalar = 1.0/1000000000

        # SHARED
        self.next_fire_arrival_uniform = 0.0
        self.next_trash_arrival = 0.0

        # SHARED
        # Units: minutes
        self.time = 0.0

        # Shared
        self.maintenance_delay = 0.0
        self.cost_of_track_cleaning_fireless = 10000.0
        self.cost_of_track_cleaning_fire = 30000.0

        # SPECIFIC: baseline sim
        self.aggregate_trash_baseline = 0
        self.num_cleanings_baseline = 0
        self.num_scheduled_cleanings = 0
        self.num_fires_baseline = 0
        self.next_fire_arrival_baseline = 0.0
        self.fire_arrival_rate_baseline = 0.0
        self.total_maintenance_cost_baseline = 0.0

        # SPECIFIC: demand sim
        self.aggregate_trash_alt = 0
        self.num_cleanings_alt = 0
        self.num_threshold_cleanings = 0
        self.num_fires_alt = 0
        self.next_fire_arrival_alt = 0.0
        self.fire_arrival_rate_alt = 0.0
        self.total_maintenance_cost_alt = 0.0

    def initialize_simulation(self):
        # initialize time
        self.time = 0.0

        # initialize values for baseline sim
        self.aggregate_trash_baseline = 0
        self.num_cleanings_baseline = 0
        self.num_scheduled_cleanings = 0
        self.num_fires_baseline = 0
        self.total_maintenance_cost_baseline = 0.0

        # initialize values for alt sim
        self.aggregate_trash_alt = 0
        self.num_cleanings_alt = 0
        self.num_threshold_cleanings = 0
        self.num_fires_alt = 0
        self.total_maintenance_cost_alt = 0.0

        # to be used for fire_arrivals
        self.next_fire_arrival_uniform = 0.0
        # initialize residual clocks
        self.next_trash_arrival = random.expovariate(self.trash_arrival_rate)
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

    def print_year_simulation_summary(self):
        print("--------------------------------")
        print("Current Time: " + str(self.time))
        print("Baseline: Number of cleanings to date:" + str(self.num_cleanings_baseline))
        print("Baseline: Number of scheduled cleanings to date:" + str(self.num_scheduled_cleanings))
        print("Baseline: Number of fires to date:" + str(self.num_fires_baseline))
        print("Baseline: Total Maintenance Cost:" + str(self.total_maintenance_cost_baseline))
        print("Alt: Number of cleanings to date:" + str(self.num_cleanings_alt))
        print("Alt: Number of threshold cleanings to date:" + str(self.num_threshold_cleanings))
        print("Alt: Number of fires to date:" + str(self.num_fires_alt))
        print("Alt: Total Maintenance Cost:" + str(self.total_maintenance_cost_alt))
        print("--------------------------------")

    def recalculate_next_fire_arrival(self):
        # set fire arrival rate based on aggregate trash
        self.fire_arrival_rate_baseline = self.fire_arrival_rate_scalar * self.aggregate_trash_baseline
        self.fire_arrival_rate_alt = self.fire_arrival_rate_scalar * self.aggregate_trash_alt
        # generate one uniform random variable that will be used to calc the exponential for both sims
        self.next_fire_arrival_uniform = numpy.random.uniform(0.0,1.0)
        # set both sims next fire based on the uniform and their respective levels of aggregate trash
        # or set them to infinity if there is no trash in their station
        if self.aggregate_trash_baseline == 0:
            self.next_fire_arrival_baseline = math.inf
        else:
            self.next_fire_arrival_baseline = (-1.0 / self.fire_arrival_rate_baseline) * math.log(1 - self.next_fire_arrival_uniform)
        if self.aggregate_trash_alt == 0:
            self.next_fire_arrival_alt = math.inf
        else:
            self.next_fire_arrival_alt = (-1.0 / self.fire_arrival_rate_alt) * math.log(1 - self.next_fire_arrival_uniform)

    def clean_baseline(self, fire):
        self.num_cleanings_baseline = self.num_cleanings_baseline + 1
        self.aggregate_trash_baseline = 0
        # Include some time delay for the cleaning and add to productivity loss
        # Should depend on if fire == True
        # set new residual clock for baseline_station_reopens
        if fire:
            self.total_maintenance_cost_baseline = self.total_maintenance_cost_baseline + self.cost_of_track_cleaning_fire
        else:
            self.total_maintenance_cost_baseline = self.total_maintenance_cost_baseline + self.cost_of_track_cleaning_fireless
            self.num_scheduled_cleanings = self.num_scheduled_cleanings + 1
        self.next_fire_arrival_baseline = math.inf

    def clean_alt(self, fire):
        self.num_cleanings_alt = self.num_cleanings_alt + 1
        self.aggregate_trash_alt = 0
        # Include some time delay for the cleaning and add to productivity loss
        # Should depend on if fire == True
        # set new residual clock for alt_station_reopense
        if fire:
            self.total_maintenance_cost_alt = self.total_maintenance_cost_alt + self.cost_of_track_cleaning_fire
        else:
            self.total_maintenance_cost_alt = self.total_maintenance_cost_alt + self.cost_of_track_cleaning_fireless
            self.num_threshold_cleanings = self.num_threshold_cleanings + 1
        self.next_fire_arrival_alt = math.inf

    def simulate(self, end_time):
        # initialize start of simulation
        self.initialize_simulation()
        while self.time < end_time:
            if self.next_trash_arrival == min(self.next_trash_arrival, self.next_scheduled_cleaning,
                                              self.next_fire_arrival_baseline, self.next_fire_arrival_alt):
                time_elapsed = self.next_trash_arrival
                self.next_scheduled_cleaning = self.next_scheduled_cleaning - time_elapsed
                self.next_trash_arrival = random.expovariate(self.trash_arrival_rate)
                self.time = self.time + time_elapsed
                # TODO: In future, add check for if station is being cleaned before incrementing aggregate trash
                self.aggregate_trash_baseline = self.aggregate_trash_baseline + 1
                self.aggregate_trash_alt = self.aggregate_trash_alt + 1
                if self.aggregate_trash_alt > self.trash_threshold:
                    print("tct: " + str(self.time))
                    self.clean_alt(False)
                # We ALWAYS need to recalculate next fire arrival upon trash arrival
                self.recalculate_next_fire_arrival()
            elif self.next_scheduled_cleaning == min(self.next_trash_arrival, self.next_scheduled_cleaning,
                                              self.next_fire_arrival_baseline, self.next_fire_arrival_alt):
                time_elapsed = self.next_scheduled_cleaning
                self.next_trash_arrival = self.next_trash_arrival - time_elapsed
                self.next_fire_arrival_alt = self.next_fire_arrival_alt - time_elapsed
                self.next_scheduled_cleaning = self.cleaning_rate
                self.time = self.time + time_elapsed
                print("scat: " + str(self.aggregate_trash_baseline))
                self.clean_baseline(False)
            elif self.next_fire_arrival_baseline == min(self.next_trash_arrival, self.next_scheduled_cleaning,
                                                self.next_fire_arrival_baseline, self.next_fire_arrival_alt):
                nfab = self.next_fire_arrival_baseline
                nfaa = self.next_fire_arrival_alt
                time_elapsed = self.next_fire_arrival_baseline
                self.next_scheduled_cleaning = self.next_scheduled_cleaning - time_elapsed
                self.next_trash_arrival = self.next_trash_arrival - time_elapsed
                self.time = self.time + time_elapsed
                print("FIRE BASELINE")
                self.num_fires_baseline = self.num_fires_baseline + 1
                self.clean_baseline(True)  # Note: that this changes self.next_fire_arrival_baseline to infinity
                if nfab == nfaa:
                    # syncd: fire arrives at both stations
                    print("FIRE ALT")
                    self.num_fires_alt = self.num_fires_alt + 1
                    self.clean_alt(True)
                else:
                    # not syncd: fire arrives only at baseline station
                    self.next_fire_arrival_alt = self.next_fire_arrival_alt - time_elapsed
            else: # self.next_fire_arrival_alt alone is the min
                time_elapsed = self.next_fire_arrival_alt
                self.next_scheduled_cleaning = self.next_scheduled_cleaning - time_elapsed
                self.next_trash_arrival = self.next_trash_arrival - time_elapsed
                self.next_fire_arrival_baseline = self.next_fire_arrival_baseline - time_elapsed
                self.time = self.time + time_elapsed
                self.num_fires_alt = self.num_fires_alt + 1
                print("FIRE ALT")
                self.clean_alt(True)

print("Starting")
# s1 = Station(40000000, 2, 6000, 30240)
# s1 = Station(200000, 1, 6000, 30240)
# s1 = Station(20000000, 1, 10000, 60000)
s1 = Station(20000000, 1, 5700, 30240)
# s1 = Station(40000000, 1, 6000, 60000)
num_reps = 50

fires_baseline = []
fires_alt = []
cleanings_baseline = []
cleanings_alt = []
maintenance_cost_baseline = []
maintenance_cost_alt = []

Z = 1.96  # z-value for interval formula

reps = 0
for i in range(num_reps):
    reps = reps + 1
    s1.simulate(525600)
    s1.print_year_simulation_summary()
    fires_baseline.append(s1.num_fires_baseline)
    fires_alt.append(s1.num_fires_alt)
    cleanings_baseline.append(s1.num_cleanings_baseline)
    cleanings_alt.append(s1.num_cleanings_alt)
    maintenance_cost_baseline.append(s1.total_maintenance_cost_baseline)
    maintenance_cost_alt.append(s1.total_maintenance_cost_alt)
    # CI stuff
    if (reps > 10):
        fires_sample_mean_baseline = sum(fires_baseline)/float(len(fires_baseline))
        fires_sample_mean_alt = sum(fires_alt)/float(len(fires_alt))
        fires_stddev_baseline = statistics.stdev(fires_baseline)
        fires_stddev_alt = statistics.stdev(fires_alt)
        ci_baseline = (Z * fires_stddev_baseline) / math.sqrt(reps)
        ci_alt = (Z * fires_stddev_alt) / math.sqrt(reps)
        print("number of yearlong simulations run: " + str(reps))
        print("baseline stddev: " + str(fires_stddev_baseline))
        print("baseline fires: " + str(fires_sample_mean_baseline) + " +/- " + str(ci_baseline))
        print("alt stddev: " + str(fires_stddev_alt))
        print("alt fires: " + str(fires_sample_mean_alt) + " +/- " + str(ci_alt))
        print("\n\n\n")
        if fires_sample_mean_baseline > fires_sample_mean_alt:
            if fires_sample_mean_baseline - ci_baseline > fires_sample_mean_alt + ci_alt:
                print("WINDOWS NO LONGER OVERLAP")
        else:
            if fires_sample_mean_alt - ci_alt > fires_sample_mean_baseline + ci_baseline:
                print("WINDOWS NO LONGER OVERLAP")


print("\nFires baseline")
print(fires_baseline)
print(sum(fires_baseline)/len(fires_baseline))
print(statistics.stdev(fires_baseline))

print("\nFires alt")
print(fires_alt)
print(sum(fires_alt)/len(fires_alt))
print(statistics.stdev(fires_alt))

print("\nCleanings baseline")
print(cleanings_baseline)
print(sum(cleanings_baseline)/len(cleanings_baseline))
print(statistics.stdev(cleanings_baseline))

print("\nCleanings alt")
print(cleanings_alt)
print(sum(cleanings_alt)/len(cleanings_alt))
print(statistics.stdev(cleanings_alt))

print("\nMaintenance baseline")
print(maintenance_cost_baseline)
print(sum(maintenance_cost_baseline)/len(maintenance_cost_baseline))
print(statistics.stdev(maintenance_cost_baseline))

print("\nMaintenance alt")
print(maintenance_cost_alt)
print(sum(maintenance_cost_alt)/len(maintenance_cost_alt))
print(statistics.stdev(maintenance_cost_alt))



# reps = []
# for i in range(num_reps):
#     s1.simulate(525600)
#     s1.print_state()
#     reps.append((s1.num_fires_baseline, s1.num_cleanings_baseline))
# print()
# print([x[0] for x in reps])
# print(sum([x[0] for x in reps])/len([x[0] for x in reps]))
# print(statistics.stdev([x[0] for x in reps]))
#
# print([x[1] for x in reps])
# print(sum([x[1] for x in reps])/len([x[1] for x in reps]))
# print(statistics.stdev([x[1] for x in reps]))




