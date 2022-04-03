from variables import *
from helpers import *
import os
import csv
import random
from typing import Dict, Union


class TripChainGenerator(BaseModel):
    trip_chain_input: TripChainInput = TripChainInput()
    seed: Union[int, None] = None
    conditional_distributions: Dict = None
    fix_working_distance: confloat(ge=MINIMUM_DISTANCE) = None

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.conditional_distributions = dict()

        # set the random generator
        if self.seed is not None:
            random.seed(self.seed)

        # read in the conditional distributions
        files = os.listdir("data")
        for filename in files:
            if filename[-3:] == "csv":
                key = filename[:-4]
                distribution = dict()
                with open(os.path.join("data", filename)) as file:
                    csv_reader = csv.reader(file, delimiter=';')
                    if key == "PurposesValues":
                        for row in csv_reader:
                            array = row[1][1:-1].split(', ')
                            for i in range(len(array)):
                                array[i] = array[i][1:-1]
                            distribution[int(row[0])] = array
                    else:
                        for row in csv_reader:
                            array = row[1][1:-1].split(', ')
                            for i in range(len(array)):
                                array[i] = float(array[i])
                            distribution[row[0]] = array
                self.conditional_distributions[key] = distribution

    def get_distribution(
            self,
            variable: str,
            key: Union[str, conint(ge=0)]
    ) -> Union[List[confloat(ge=0.0, le=1.0)], str]:

        return self.conditional_distributions[variable][key]

    def sample_trip_chain_length(self) -> conint(ge=0, le=12):

        key = self.trip_chain_input.mobility_group + self.trip_chain_input.start_location_of_first_trip + self.trip_chain_input.day_type \
              + self.trip_chain_input.homogeneous_group
        return generate_int_from_cumulative_distribution(
            self.get_distribution(
                variable=VariableNames.TRIP_CHAIN_LENGTH,
                key=key
            )
        )

    def sample_purpose_chain(
            self,
            trip_chain_length: conint(ge=0, le=12)
    ) -> List[Purpose]:

        if trip_chain_length == 0:
            return []
        else:
            variable = VariableNames.PURPOSES + str(trip_chain_length)
            key = self.trip_chain_input.start_location_of_first_trip + self.trip_chain_input.homogeneous_group + \
                  self.trip_chain_input.day_type + self.trip_chain_input.age
            sampled_index = generate_int_from_cumulative_distribution(
                self.get_distribution(
                    variable=variable,
                    key=key
                )
            )
            sampled_purpose_chain = list(self.get_distribution(
                VariableNames.PURPOSES_VALUES,
                trip_chain_length
            )[sampled_index])

            return [Purpose(int(value)) for value in sampled_purpose_chain]

    def _sample_distance(self, purpose, staytime):
        if purpose == Purpose.WORK and self.fix_working_distance is not None:
            return self.fix_working_distance
        key = get_staytime_category(staytime) + stringify(purpose) + self.trip_chain_input.mobility_group + \
              self.trip_chain_input.region_type
        sampled_category = generate_int_from_cumulative_distribution(
            self.get_distribution(
                variable=VariableNames.DISTANCE,
                key=key
            )
        )
        return max((sampled_category + random.random()) * Resolution.DISTANCE, MINIMUM_DISTANCE)

    def _sample_first_start(
            self,
            trip_chain_length: conint(ge=0, le=12),
            purpose: Purpose,
            next_purpose: Purpose
    ) -> confloat(ge=0.0):
        key = stringify(trip_chain_length) + stringify(purpose) + stringify(next_purpose)
        sampled_category = generate_int_from_cumulative_distribution(
            self.get_distribution(
                variable=VariableNames.FIRST_START,
                key=key
            )
        )
        return (sampled_category + random.random()) * Resolution.TIME

    def _sample_staytime(self, start, purpose, next_purpose, trip_chain_length):
        key = stringify(purpose) + stringify(trip_chain_length) + get_start_category(start) + stringify(next_purpose)
        sampled_category = generate_int_from_cumulative_distribution(
            self.get_distribution(
                variable=VariableNames.STAYTIME,
                key=key
            )
        )
        return (sampled_category + random.random()) * Resolution.TIME

    def _sample_speed(self, start, distance):
        key = get_distance_category(distance) + self.trip_chain_input.federal_state + get_start_category(start) + \
              self.trip_chain_input.age
        sampled_category = generate_int_from_cumulative_distribution(
            self.get_distribution(
                variable=VariableNames.SPEED,
                key=key
            )
        )
        return max((sampled_category + random.random()) * Resolution.SPEED, MINIMUM_SPEED)

    def sample_trip(self, start, purpose, next_purpose, trip_chain_length, last=False) -> Trip:
        if last:
            staytime = None
        else:
            staytime = self._sample_staytime(start=start, purpose=purpose, next_purpose=next_purpose,
                                             trip_chain_length=trip_chain_length)
        distance = self._sample_distance(purpose=purpose, staytime=staytime)
        speed = self._sample_speed(start=start, distance=distance)
        duration = distance / speed
        end = start + duration
        return Trip(departure=start, distance=distance, duration=duration, mean_speed=speed, arrival=end,
                    purpose=purpose, staytime=staytime)

    def sample_trip_chain(self):
        length = self.sample_trip_chain_length()
        purpose_chain = self.sample_purpose_chain(length)
        return self.sample_trip_chain_from_purpose_chain(purpose_chain=purpose_chain)

    def sample_trip_chain_from_purpose_chain(self,
                                             purpose_chain: List[Purpose]
                                             ) -> TripChain:
        trip_chain = TripChain(length=len(purpose_chain), purpose_chain=purpose_chain, trips=[])
        if not purpose_chain:
            return trip_chain

        # first start
        index = 0
        last = (index + 1 == trip_chain.length)
        purpose, next_purpose = get_purposes(purpose_chain=purpose_chain, index=index, last=last)
        start = self._sample_first_start(trip_chain_length=trip_chain.length,
                                              purpose=purpose,
                                              next_purpose=next_purpose)

        # sample trips
        while index < trip_chain.length:
            trip_chain.trips.append(self.sample_trip(start=start, purpose=purpose, next_purpose=next_purpose,
                                                     trip_chain_length=trip_chain.length, last=last))
            if last:
                return trip_chain

            index += 1
            last = (index + 1 == trip_chain.length)
            purpose, next_purpose = get_purposes(purpose_chain=purpose_chain, index=index, last=last)
            start = trip_chain.trips[-1].arrival + trip_chain.trips[-1].staytime

    def set_seed(self, seed):
        self.seed = seed
        random.seed(self.seed)

    def set_working_distance(self, value: confloat(ge=MINIMUM_DISTANCE)):
        self.fix_working_distance = value


if __name__ == "__main__":
    # exemplary model creation
    generator = TripChainGenerator()

    # sampling with different seeds
    for seed in range(100):
        generator.set_seed(seed)

        # manipulate trip input data
        generator.trip_chain_input.day_type = DayType.MONDAY
        generator.set_working_distance(50.0)

        # exemplary samples
        sampled_length = generator.sample_trip_chain_length()
        print('Length: ' + str(sampled_length))

        sampled_purpose_chain = generator.sample_purpose_chain(sampled_length)
        print('Purpose Chain: ' + str(sampled_purpose_chain))

        sampled_trip_chain = generator.sample_trip_chain_from_purpose_chain(sampled_purpose_chain)
        print('Trip Chain: ' + str(sampled_trip_chain))
