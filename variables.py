from enum import Enum
from pydantic import BaseModel, conint, confloat
from typing import List, Union

MINIMUM_SPEED = 2.0  # km/h
MINIMUM_DISTANCE = 0.5  # km


class Age(str, Enum):
    UNDER_FORTY = "01"
    FORTY_TO_SIXTY_FIVE = "02"
    OVER_SIXTY_FIVE = "03"
    UNKNOWN = "00"


class DayType(str, Enum):
    MONDAY = "01"
    TUESDAY = "02"
    WEDNESDAY = "03"
    THURSDAY = "04"
    FRIDAY = "05"
    SATURDAY = "06"
    SUNDAY = "07"
    HOLIDAY = "08"
    UNKNOWN = "00"


def get_distance_category(distance: confloat(ge=0.0)):
    if distance <= 5.0:
        return Distance.SHORT
    elif distance <= 15.0:
        return Distance.MEDIUM
    else:
        return Distance.LONG


class Distance(str, Enum):
    SHORT = "01"  # less than 5 km
    MEDIUM = "02"  # 5 km to 15 km
    LONG = "03"  # 15 km and more
    UNKNOWN = "00"


class HomogeneousGroup(str, Enum):
    WORKING_PERSON = "01"  # less than 5 km
    NON_WORKING_PERSON = "02"  # 5 km to 15 km
    STUDENT = "03"  # includes students, apprentices and pupils
    UNKNOWN = "00"


class MobilityGroup(str, Enum):
    CAR_USER = "01"  # uses mostly cars
    MULTI_MODAL = "02"  # uses multi modal means of transport
    NON_CAR_USER = "03"  # mostly doesnt use cars
    UNKNOWN = "00"


class Purpose(int, Enum):
    WORK = 1
    BUSINESS = 2
    EDUCATION = 3
    SHOPPING = 4
    PRIVATE_EXECUTIONS = 5
    COMPANIONSHIP = 6
    LEISURE = 7
    HOME = 8
    BACK = 9
    UNKNOWN = 0


class RegionType(str, Enum):
    URBAN_METROPOLIS = "71"
    URBAN_MAJOR_CITY = "72"
    URBAN_CITY_AREA = "73"
    URBAN_VILLAGE = "74"
    RURAL_CENTRAL_CITY = "75"
    RURAL_CITY_AREA = "76"
    RURAL_VILLAGE = "77"
    UNKNOWN = "00"


class Resolution(float, Enum):
    TIME = 0.5
    DISTANCE = 5.0
    SPEED = 5.0


def get_start_category(time: confloat(ge=0.0)):
    if time <= 10.0:
        return Start.MORNING
    elif time <= 14.0:
        return Start.MIDDAY
    elif time <= 17.0:
        return Start.AFTERNOON
    elif time <= 24.0:
        return Start.EVENING
    else:
        return Start.UNKNOWN


class Start(str, Enum):
    MORNING = "01"  # before 10am
    MIDDAY = "02"  # 10am to 2pm
    AFTERNOON = "03"  # 2pm to 5pm
    EVENING = "04"  # 5pm to midnight
    UNKNOWN = "00"


class StartLocation(str, Enum):
    AT_HOME = "01"
    NOT_AT_HOME = "02"
    UNKNOWN = "00"


class FederalState(str, Enum):
    SCHLESWIG_HOLSTEIN = "01"
    HAMBURG = "02"
    LOWER_SAXONY = "03"
    BREMEN = "04"
    NORTH_RHINE_WESTPHALIA = "05"
    HESSE = "06"
    RHINELAND_PALATINATE = "07"
    BADEN_WUERTTEMBERG = "08"
    BAVARIA = "09"
    SAARLAND = "10"
    BERLIN = "11"
    BRANDENBURG = "12"
    MECKLENBURG_WESTERN_POMERANIA = "13"
    SAXONY = "14"
    SAXONY_ANHALT = "15"
    THURINGIA = "16"
    UNKNOWN = "00"


def get_staytime_category(time: confloat(ge=0.0)):
    if time is None:
        return StayTime.UNKNOWN
    if time <= 1.0:
        return StayTime.SHORT
    elif time <= 4.0:
        return StayTime.MEDUIM
    elif time <= 24.0:
        return StayTime.LONG
    else:
        return StayTime.UNKNOWN


class StayTime(str, Enum):
    SHORT = "01"  # up to one hour
    MEDUIM = "02"  # one to four hours
    LONG = "03"  # four to 24 hours
    UNKNOWN = "00"


class TripChainInput(BaseModel):
    region_type: RegionType = RegionType.UNKNOWN
    federal_state: FederalState = FederalState.UNKNOWN
    homogeneous_group: HomogeneousGroup = HomogeneousGroup.UNKNOWN
    mobility_group: MobilityGroup = MobilityGroup.UNKNOWN
    age: Age = Age.UNKNOWN
    start_location_of_first_trip: StartLocation = StartLocation.UNKNOWN
    day_type: DayType = DayType.UNKNOWN


class Trip(BaseModel):
    departure: confloat(ge=0.0)  # todo change that to datetime object
    distance: confloat(ge=0.0)
    duration: confloat(ge=0.0)  # todo change that to time object
    mean_speed = confloat(ge=0.0)
    arrival: confloat(ge=0.0)  # todo change that to datetime object
    purpose: Purpose
    staytime: Union[confloat(ge=0.0), None]  # todo change that to time object


class TripChain(BaseModel):
    length: conint(ge=0)
    purpose_chain: List[Purpose]
    trips: List[Trip]


class VariableNames(str, Enum):
    TRIP_CHAIN_LENGTH = "TripChainLength"
    PURPOSES_VALUES = "PurposesValues"
    PURPOSES = "Purposes"
    FIRST_START = "FirstStart"
    STAYTIME = "StayTime"
    DISTANCE = "Distance"
    SPEED = "Speed"
