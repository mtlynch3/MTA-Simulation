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
        # self.trash_arrival_rate_scalar = 1.0/190
        self.trash_arrival_rate_scalar = 1.0/380
        number_of_minutes_per_year = 525600
        self.riders_per_minute_per_track = ((annual_ridership/num_track_beds)/number_of_minutes_per_year)
        self.trash_arrival_rate = self.trash_arrival_rate_scalar * self.riders_per_minute_per_track
        # Choose fire_arrival_rate_scalar to yield approximately two fires per year at the busiest stations
        self.fire_arrival_rate_scalar = 1.0/100000000

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

        ######## Productivity Loss
        self.wage_per_minute = 0.56667  # dollars - equivalent to $34/hr
        self.minutes_per_cleaning = 90
        self.minutes_per_fire_repair = 270
        self.pl_nofire_baseline = []
        self.pl_nofire_alt = []
        self.pl_fire_baseline = []
        self.pl_fire_alt = []
        ######## /Productivity Loss

        # SPECIFIC: baseline sim
        self.aggregate_trash_baseline = 0
        self.num_cleanings_baseline = 0
        self.num_scheduled_cleanings = 0
        self.num_fires_baseline = 0
        self.next_fire_arrival_baseline = 0.0
        self.fire_arrival_rate_baseline = 0.0
        self.total_maintenance_cost_baseline = 0.0
        self.total_productivity_loss_baseline = 0.0

        # SPECIFIC: demand sim
        self.aggregate_trash_alt = 0
        self.num_cleanings_alt = 0
        self.num_threshold_cleanings = 0
        self.num_fires_alt = 0
        self.next_fire_arrival_alt = 0.0
        self.fire_arrival_rate_alt = 0.0
        self.total_maintenance_cost_alt = 0.0
        self.total_productivity_loss_alt = 0.0

    def initialize_simulation(self):
        # initialize time
        self.time = 0.0

        # initialize values for baseline sim
        self.aggregate_trash_baseline = 0
        self.num_cleanings_baseline = 0
        self.num_scheduled_cleanings = 0
        self.num_fires_baseline = 0
        self.total_maintenance_cost_baseline = 0.0
        self.total_productivity_loss_baseline = 0.0

        # initialize values for alt sim
        self.aggregate_trash_alt = 0
        self.num_cleanings_alt = 0
        self.num_threshold_cleanings = 0
        self.num_fires_alt = 0
        self.total_maintenance_cost_alt = 0.0
        self.total_productivity_loss_alt = 0.0

        ######## Productivity Loss
        self.pl_nofire_baseline = []
        self.pl_nofire_alt = []
        self.pl_fire_baseline = []
        self.pl_fire_alt = []
        ######## /Productivity Loss

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

    def generate_random_prod_loss(self, rate, duration):
        num_riders = numpy.random.poisson(rate * duration, 1)[0]
        loss = 0.0
        for i in range(num_riders):
            additional = self.wage_per_minute * duration * random.random()
            loss = loss + additional
        return loss

    def increase_productivity_loss(self, baseline, fire):
        if baseline:
            prod_loss = 0.0
            if fire:
                if len(self.pl_fire_alt) > 0:
                    prod_loss = self.pl_fire_alt.pop(0)
                else:
                    prod_loss = self.generate_random_prod_loss(self.riders_per_minute_per_track, self.minutes_per_fire_repair)
                    self.pl_fire_baseline.append(prod_loss)
            else:
                if len(self.pl_nofire_alt) > 0:
                    prod_loss = self.pl_nofire_alt.pop(0)
                else:
                    prod_loss = self.generate_random_prod_loss(self.riders_per_minute_per_track, self.minutes_per_cleaning)
                    self.pl_nofire_baseline.append(prod_loss)
            self.total_productivity_loss_baseline = self.total_productivity_loss_baseline + prod_loss
            print("******** Increasing Baseline Prod Loss by: " + str(prod_loss))
        else:
            prod_loss = 0.0
            if fire:
                if len(self.pl_fire_baseline) > 0:
                    prod_loss = self.pl_fire_baseline.pop(0)
                else:
                    prod_loss = self.generate_random_prod_loss(self.riders_per_minute_per_track, self.minutes_per_fire_repair)
                    self.pl_fire_alt.append(prod_loss)
            else:
                if len(self.pl_nofire_baseline) > 0:
                    prod_loss = self.pl_nofire_baseline.pop(0)
                else:
                    prod_loss = self.generate_random_prod_loss(self.riders_per_minute_per_track, self.minutes_per_cleaning)
                    self.pl_nofire_alt.append(prod_loss)
            self.total_productivity_loss_alt = self.total_productivity_loss_alt + prod_loss
            print("******** Increasing Alt Prod Loss by: " + str(prod_loss))


    def clean_baseline(self, fire):
        self.num_cleanings_baseline = self.num_cleanings_baseline + 1
        self.aggregate_trash_baseline = 0
        # Include some time delay for the cleaning and add to productivity loss
        # Should depend on if fire == True
        # set new residual clock for baseline_station_reopens
        if fire:
            self.total_maintenance_cost_baseline = self.total_maintenance_cost_baseline + self.cost_of_track_cleaning_fire
            # increment productivity loss
            self.increase_productivity_loss(True, True)
        else:
            self.total_maintenance_cost_baseline = self.total_maintenance_cost_baseline + self.cost_of_track_cleaning_fireless
            self.num_scheduled_cleanings = self.num_scheduled_cleanings + 1
            # increment productivity loss
            self.increase_productivity_loss(True, False)
        self.next_fire_arrival_baseline = math.inf

    def clean_alt(self, fire):
        self.num_cleanings_alt = self.num_cleanings_alt + 1
        self.aggregate_trash_alt = 0
        # Include some time delay for the cleaning and add to productivity loss
        # Should depend on if fire == True
        # set new residual clock for alt_station_reopens
        if fire:
            self.total_maintenance_cost_alt = self.total_maintenance_cost_alt + self.cost_of_track_cleaning_fire
            # increment productivity loss
            self.increase_productivity_loss(False, True)
        else:
            self.total_maintenance_cost_alt = self.total_maintenance_cost_alt + self.cost_of_track_cleaning_fireless
            self.num_threshold_cleanings = self.num_threshold_cleanings + 1
            # increment productivity loss
        self.increase_productivity_loss(False, False)
        self.next_fire_arrival_alt = math.inf

    def simulate(self, end_time):
        # initialize start of simulation
        self.initialize_simulation()
        while self.time < end_time:
            smallest_residual = min(self.next_trash_arrival, self.next_scheduled_cleaning,
                                    self.next_fire_arrival_baseline, self.next_fire_arrival_alt)
            if self.next_trash_arrival == smallest_residual:
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
            elif self.next_scheduled_cleaning == smallest_residual:
                time_elapsed = self.next_scheduled_cleaning
                self.next_trash_arrival = self.next_trash_arrival - time_elapsed
                self.next_fire_arrival_alt = self.next_fire_arrival_alt - time_elapsed
                self.next_scheduled_cleaning = self.cleaning_rate
                self.time = self.time + time_elapsed
                print("scat: " + str(self.aggregate_trash_baseline))
                self.clean_baseline(False)
            elif self.next_fire_arrival_baseline == smallest_residual:
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


def calculate_confidence_intervals(data, num_reps, Z):
    sample_mean = sum(data)/float(len(data))
    stddev = statistics.stdev(data)
    ci_plus_minus = (Z * stddev) / math.sqrt(num_reps)
    return sample_mean, stddev, ci_plus_minus


def run_simulations(annual_ridership, num_track_beds, trash_threshold, cleaning_rate, comparison_var, limit = None):
    print("Starting")
    s1 = Station(annual_ridership, num_track_beds, trash_threshold, cleaning_rate)
    print()
    print("Annual ridership: " + str(s1.annual_ridership))
    print("Number of Track Beds: " + str(s1.num_track_beds))
    print("Trash Threshold: " + str(s1.trash_threshold))
    print("Cleaning Period: " + str(s1.cleaning_rate))
    print("Trash arrival rate (number of units of trash per minute): " + str(s1.trash_arrival_rate))
    print("Expected aggregation of trash in 1 cleaning period: " + str(s1.trash_arrival_rate * s1.cleaning_rate))
    print()
    fires_baseline = []
    fires_alt = []
    cleanings_baseline = []
    scheduled_cleanings = []
    cleanings_alt = []
    threshold_cleanings = []
    maintenance_cost_baseline = []
    maintenance_cost_alt = []
    productivity_loss_baseline = []
    productivity_loss_alt = []
    Z = 1.96  # z-value for interval formula
    reps = 0
    while True:
        reps = reps + 1
        s1.simulate(525600)
        s1.print_year_simulation_summary()
        fires_baseline.append(s1.num_fires_baseline)
        fires_alt.append(s1.num_fires_alt)
        cleanings_baseline.append(s1.num_cleanings_baseline)
        scheduled_cleanings.append(s1.num_scheduled_cleanings)
        cleanings_alt.append(s1.num_cleanings_alt)
        threshold_cleanings.append(s1.num_threshold_cleanings)
        maintenance_cost_baseline.append(s1.total_maintenance_cost_baseline)
        maintenance_cost_alt.append(s1.total_maintenance_cost_alt)
        productivity_loss_baseline.append(s1.total_productivity_loss_baseline)
        productivity_loss_alt.append(s1.total_productivity_loss_alt)
        # CI stuff
        if reps > 10:
            fires_sample_mean_baseline, fires_stddev_baseline, fires_ci_baseline = calculate_confidence_intervals(fires_baseline, reps, Z)
            fires_sample_mean_alt, fires_stddev_alt, fires_ci_alt = calculate_confidence_intervals(fires_alt, reps, Z)
            maintenance_sample_mean_baseline, maintenance_stddev_baseline, maintenance_ci_baseline = calculate_confidence_intervals(maintenance_cost_baseline, reps, Z)
            maintenance_sample_mean_alt, maintenance_stddev_alt, maintenance_ci_alt = calculate_confidence_intervals(maintenance_cost_alt, reps, Z)
            productivity_sample_mean_baseline, productivity_stddev_baseline, productivity_ci_baseline = calculate_confidence_intervals(productivity_loss_baseline, reps, Z)
            productivity_sample_mean_alt, productivity_stddev_alt, productivity_ci_alt = calculate_confidence_intervals(productivity_loss_alt, reps, Z)
            print("number of yearlong simulations run: " + str(reps))
            print("baseline fires: " + str(fires_sample_mean_baseline) + " +/- " + str(fires_ci_baseline))
            print("alt fires: " + str(fires_sample_mean_alt) + " +/- " + str(fires_ci_alt))
            print("baseline maintenance: " + str(maintenance_sample_mean_baseline) + " +/- " + str(maintenance_ci_baseline))
            print("alt maintenance: " + str(maintenance_sample_mean_alt) + " +/- " + str(maintenance_ci_alt))
            print("baseline productivity loss: " + str(productivity_sample_mean_baseline) + " +/- " + str(productivity_ci_baseline))
            print("alt productivity loss: " + str(productivity_sample_mean_alt) + " +/- " + str(productivity_ci_alt))
            print("\n\n\n")
            if comparison_var == "fires":
                if fires_sample_mean_baseline > fires_sample_mean_alt:
                    if fires_sample_mean_baseline - fires_ci_baseline > fires_sample_mean_alt + fires_ci_alt:
                        print("FIRES WINDOWS NO LONGER OVERLAP")
                        break
                else:
                    if fires_sample_mean_alt - fires_ci_alt > fires_sample_mean_baseline + fires_ci_baseline:
                        print("FIRES WINDOWS NO LONGER OVERLAP")
                        break
            elif comparison_var == "maintenance":
                if maintenance_sample_mean_baseline > maintenance_sample_mean_alt:
                    if maintenance_sample_mean_baseline - maintenance_ci_baseline > maintenance_sample_mean_alt + maintenance_ci_alt:
                        print("MAINTENANCE WINDOWS NO LONGER OVERLAP")
                        break
                else:
                    if maintenance_sample_mean_alt - maintenance_ci_alt > maintenance_sample_mean_baseline + maintenance_ci_baseline:
                        print("MAINTENANCE WINDOWS NO LONGER OVERLAP")
                        break
            elif comparison_var == "productivity":
                if productivity_sample_mean_baseline > productivity_sample_mean_alt:
                    if productivity_sample_mean_baseline - productivity_ci_baseline > productivity_sample_mean_alt + productivity_ci_alt:
                        print("PRODUCTIVITY WINDOWS NO LONGER OVERLAP")
                        break
                else:
                    if productivity_sample_mean_alt - productivity_ci_alt > productivity_sample_mean_baseline + productivity_ci_baseline:
                        print("PRODUCTIVITY LOSS WINDOWS NO LONGER OVERLAP")
                        break
            else:
                print("MUST PROVIDE COMPARISON VAR")
                break
        if limit is not None:
            if reps >= limit:
                break

    print("\nFires baseline")
    # print(fires_baseline)
    print(sum(fires_baseline)/len(fires_baseline))
    print(statistics.stdev(fires_baseline))

    print("\nFires alt")
    # print(fires_alt)
    print(sum(fires_alt)/len(fires_alt))
    print(statistics.stdev(fires_alt))

    print("\nCleanings baseline")
    # print(cleanings_baseline)
    print(sum(cleanings_baseline)/len(cleanings_baseline))
    print(statistics.stdev(cleanings_baseline))

    print("\nScheduled Cleanings baseline")
    # print(cleanings_baseline)
    print(sum(scheduled_cleanings)/len(scheduled_cleanings))
    print(statistics.stdev(scheduled_cleanings))

    print("\nCleanings alt")
    # print(cleanings_alt)
    print(sum(cleanings_alt)/len(cleanings_alt))
    print(statistics.stdev(cleanings_alt))

    print("\nThreshold Cleanings alt")
    # print(cleanings_alt)
    print(sum(threshold_cleanings)/len(threshold_cleanings))
    print(statistics.stdev(threshold_cleanings))

    print("\nMaintenance baseline")
    # print(maintenance_cost_baseline)
    print(sum(maintenance_cost_baseline)/len(maintenance_cost_baseline))
    print(statistics.stdev(maintenance_cost_baseline))

    print("\nMaintenance alt")
    # print(maintenance_cost_alt)
    print(sum(maintenance_cost_alt)/len(maintenance_cost_alt))
    print(statistics.stdev(maintenance_cost_alt))

    print("\nProductivity baseline")
    # print(maintenance_cost_baseline)
    print(sum(productivity_loss_baseline)/len(productivity_loss_baseline))
    print(statistics.stdev(productivity_loss_baseline))

    print("\nProductivity alt")
    # print(maintenance_cost_alt)
    print(sum(productivity_loss_alt)/len(productivity_loss_alt))
    print(statistics.stdev(productivity_loss_alt))


# run_simulations(20000000, 1, 2500, 30240, "fires", 50)
# run_simulations(20000000, 1, 2500, 30240, "maintenance", 50)
# run_simulations(3752400, 1, 1000, 65700, "fires")
# run_simulations(3752400, 1, 1000, 65700, "fires")
# run_simulations(3752400, 1, 1000, 65700, "fires")
# run_simulations(3752400, 1, 1000, 65700, "fires")
# run_simulations(3752400, 1, 1000, 65700, "fires")


# run_simulations(13300000, 1, 1725, 36250, "maintenance", 1500)

run_simulations(25000000, 1, 2150, 26280, "maintenance", 1500)



