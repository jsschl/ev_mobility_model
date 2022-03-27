from variables import *
from helpers import *
import os
import csv
from typing import Dict


class TripChainGenerator(BaseModel):
    trip_input: TripInput = TripInput()
    conditional_distributions: Dict = None

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.conditional_distributions = dict()

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

        key = self.trip_input.mobility_group + self.trip_input.start_location_of_first_trip + self.trip_input.day_type \
              + self.trip_input.homogeneous_group
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
            key = self.trip_input.start_location_of_first_trip + self.trip_input.homogeneous_group + \
                self.trip_input.day_type + self.trip_input.age
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

    def sample_first_start(
            self,
            trip_chain_length: conint(ge=0, le=12),
            purpose: Purpose,
            next_purpose: Purpose
    ) -> confloat(ge=0.0):
        # todo
        return None

    def sample_trip_chain(self):
        length = self.sample_trip_chain_length()
        purpose_chain = self.sample_purpose_chain(length)
        return self.sample_trip_chain_from_purpose_chain(purpose_chain=purpose_chain)

    def sample_trip_chain_from_purpose_chain(self,
                                             purpose_chain: List[Purpose]
                                             ) -> List[Trip]:
        if purpose_chain is []:
            return []
        else:
            if len(purpose_chain) == 1:
                next_purpose = Purpose.UNKNOWN
            else:
                next_purpose = purpose_chain[1]
            first_start = self.sample_first_start(len(purpose_chain),
                                                  purpose=purpose_chain[0],
                                                  next_purpose=next_purpose)
            # todo continue



if __name__ == "__main__":
    generator = TripChainGenerator()

    # manipulate trip input data
    generator.trip_input.day_type = DayType.MONDAY

    # call Enum backwards
    print(Age('01'))  # todo rethink definition to be backwards callable

    # exemplary samples
    sampled_length = generator.sample_trip_chain_length()
    print('Length: ' + str(sampled_length))

    sampled_purpose_chain = generator.sample_purpose_chain(sampled_length)
    print('Purpose Chain: ' + str(sampled_purpose_chain))
