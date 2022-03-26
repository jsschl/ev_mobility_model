from variables import *
from helpers import *
import os
import csv
from typing import Dict


class TripChainGenerator(BaseModel):
    trip_input: TripInput = TripInput()
    conditional_distributions: Dict = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conditional_distributions = dict()

        # read in the conditional distributions
        files = os.listdir("data")
        for filename in files:
            if filename[-3:] == "csv":
                key = filename[:-4]
                distribution = dict()
                with open(os.path.join("data", filename)) as file:
                    print("reading " + filename + "...")
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

    def get_distribution(self, variable, key):
        return self.conditional_distributions[variable][key]


if __name__ == "__main__":
    generator = TripChainGenerator()

    # manipulate trip input data
    generator.trip_input.day_type = DAYTYPE.MONDAY

    print(generator.get_distribution('TripChainLength', '01010101'))
    print(generator.get_distribution('PurposesValues', 1)[3])
    print(Age('01'))  # todo rethink definition to be backwards callable