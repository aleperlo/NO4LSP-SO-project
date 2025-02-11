import json
from collections import defaultdict
from typing import List, Literal, Union, Tuple, Dict
import numpy as np
from numpy.typing import NDArray
import copy
import pandas as pd


class Room:
    def __init__(self, id: str, capacity: int):
        """Initialize the Room object

        Args:
            id (str): Room identifier
            capacity (int): Room capacity, it is time independent
        """
        self.id = id
        self.capacity = capacity

    def __str__(self):
        return f"Room {self.id}"


class OperatingTheater:
    def __init__(self, id: str, availability: List[int]):
        """Initialize the Operating Theater object

        Args:
            id (str): Operating Theater identifier
            availability (List[int]): Availability of the Operating Theater for each day, in minutes
        """
        self.id = id
        self.availability = availability

    def __str__(self):
        return f"OperatingTheater {self.id}"


class Surgeon:
    def __init__(self, id: str, max_surgery_time: List[int]):
        """Initialize the Surgeon object

        Args:
            id (str): Surgeon identifier
            max_surgery_time (List[int]): Maximum surgery time for each day, in minutes
        """
        self.id = id
        self.max_surgery_time = max_surgery_time

    def __str__(self):
        return f"Surgeon {self.id}"


class Occupant:
    def __init__(
        self,
        id: str,
        gender: str,
        age_group: str,
        length_of_stay: int,
        workload_produced: List[int],
        skill_level_required: List[int],
        room: Room,
        age_groups: List[str],
    ):
        """Initialize the Occupant object

        Args:
            id (str): Occupant identifier
            gender (str): gender of the occupant
            age_group (str): age group of the occupant
            length_of_stay (int): length of stay of the occupant
            workload_produced (List[int]): workload produced by the occupant for each shift
            skill_level_required (List[int]): skill level required by the occupant for each shift
            room (Room): room where the occupant is assigned
            age_groups (List[str]): list of all age groups
        """
        self.id = id
        self.gender = gender
        self.age_group = age_groups.index(age_group)
        self.length_of_stay = length_of_stay
        self.workload_produced = workload_produced
        self.skill_level_required = skill_level_required
        self.room = room

    def __str__(self):
        return f"Occupant {self.id}"


class Patient(Occupant):
    def __init__(
        self,
        id: str,
        mandatory: bool,
        gender: str,
        age_group: str,
        length_of_stay: int,
        surgery_release_day: int,
        surgery_duration: int,
        surgeon: Surgeon,
        incompatible_rooms: List[Room],
        workload_produced: List[int],
        skill_level_required: List[int],
        surgery_due_day: Union[int, None] = None,
        age_groups: List[str] = None,
    ):
        """Initialize the Patient object

        Args:
            id (str): Patient identifier
            mandatory (bool): establish if the patient is mandatory
            gender (str): gender of the occupant
            age_group (str): age group of the occupant
            length_of_stay (int): length of stay of the occupant
            surgery_release_day (int): earliest possible admission date for the patient
            surgery_duration (int): surgery duration in minutes
            surgeon (Surgeon): surgeon assigned to the patient
            incompatible_rooms (List[Room]): list of rooms where the patient cannot be assigned
            workload_produced (List[int]): workload produced by the patient for each shift
            skill_level_required (List[int]): skill level required by the patient for each shift
            surgery_due_day (Union[int, None], optional): latest possible admission date, provided only for mandatory patients. Defaults to None.
            age_groups (List[str], optional): list of all age groups. Defaults to None.
        """
        super().__init__(
            id=id,
            gender=gender,
            age_group=age_group,
            length_of_stay=length_of_stay,
            workload_produced=workload_produced,
            skill_level_required=skill_level_required,
            room=None,
            age_groups=age_groups,
        )
        self.mandatory = mandatory
        self.surgery_release_day = surgery_release_day
        self.surgery_duration = surgery_duration
        self.surgeon = surgeon
        self.incompatible_rooms = incompatible_rooms
        self.surgery_due_day = surgery_due_day
        self.assignment = dict()
        self.assignment["id"] = self.id
        self.assignment["admission_day"] = "none"

    def __str__(self):
        return f"Patient {self.id}"

    def set_assignment(self, admission_day: int, room: str, ot: str):
        """Save assignment information

        Args:
            admission_day (int): index of the day when the patient is admitted
            room (str): id of the room where the patient is assigned
            ot (str): id of the operating theater where the patient is assigned
        """

        self.assignment["admission_day"] = admission_day
        self.assignment["room"] = room
        self.assignment["operating_theater"] = ot

    def unset_assignment(self):
        """Remove assignment information"""
        self.assignment["admission_day"] = "none"
        self.assignment.pop("room", None)
        self.assignment.pop("operating_theater", None)


class WorkingShift:
    def __init__(self, day: int, shift: str, max_load: int, shift_types: List[str]):
        """Initialize the WorkingShift object

        Args:
            day (int): index of the day
            shift (str): shift type
            max_load (int): maximum workload for the shift
            shift_types (List[str]): list of all shift types
        """
        self.day = day
        self.shift = shift
        self.max_load = max_load
        self.index = day * len(shift_types) + shift_types.index(shift)

    def __str__(self):
        return f"Shift {self.day} {self.shift} {self.max_load}"


class Nurse:
    def __init__(
        self,
        id: str,
        skill_level: int,
        working_shifts: List[dict],
        shift_types: List[str],
        days: int,
    ):
        """Initialize the Nurse object

        Args:
            id (str): Nurse identifier
            skill_level (int): skill level of the nurse
            working_shifts (List[dict]): list of working shifts
            shift_types (List[str]): list of all shift types
            days (int): number of days
        """
        self.id = id
        self.skill_level = skill_level
        self.working_shifts: defaultdict[int, WorkingShift] = defaultdict(lambda: None)
        self.available = np.zeros(days * len(shift_types), dtype=bool)
        self.assignment: defaultdict[str, Union[str, List[dict]]] = defaultdict(
            lambda: {}
        )
        self.assignment["id"] = self.id
        self.assignment["assignments"] = []
        for w in working_shifts:
            w["shift_types"] = shift_types
            w_obj = WorkingShift(**w)
            self.working_shifts[w_obj.index] = w_obj
            self.available[w_obj.index] = True
            self.assignment["assignments"].append(
                {"day": w_obj.day, "shift": w_obj.shift, "rooms": []}
            )

    def is_available(self, shift_index: int) -> bool:
        """Check if the nurse is available at the given shift

        Args:
            shift_index (int): index of the shift

        Returns:
            bool: True if the nurse is available, False otherwise
        """
        return self.available[shift_index]

    def maximum_workload(self, shift_index: int) -> int:
        """Return the maximum workload for the given shift

        Args:
            shift_index (int): index of the shift

        Returns:
            int: maximum workload for the shift
        """
        return self.working_shifts[shift_index].max_load

    def __str__(self):
        return f"Nurse {self.id}"

    def set_assignment(self, day: int, shift: str, room: str):
        """Save assignment information

        Args:
            day (int): index of the day
            shift (int): shift type
            room (int): id of the room
        """
        for assignment in self.assignment["assignments"]:
            if (
                assignment["day"] == day
                and assignment["shift"] == shift
                and room not in assignment["rooms"]
            ):
                assignment["rooms"].append(room)
                break

    def unset_assignment(self, day: int, shift: str, room: str):
        """Remove assignment information

        Args:
            day (int): index of the day
            shift (str): shift type
            room (str): id of the room
        """
        for assignment in self.assignment["assignments"]:
            if (
                assignment["day"] == day
                and assignment["shift"] == shift
                and room in assignment["rooms"]
            ):
                assignment["rooms"].remove(room)
                break


class Indexer:
    def __init__(self):
        """Initialize the Indexer object"""
        self.types: defaultdict[str, int] = defaultdict(lambda: 0)
        self.indexer: defaultdict[
            str,
            dict[int, Union[Patient, Occupant, Surgeon, Nurse, OperatingTheater, Room]],
        ] = defaultdict(lambda: {})
        self.reverse_indexer: defaultdict[str, dict[str, int]] = defaultdict(lambda: {})

    def get_index(
        self,
        type: Literal[
            "patients",
            "occupants",
            "surgeons",
            "nurses",
            "operating_theaters",
            "rooms",
        ],
        obj: Union[Patient, Occupant, Surgeon, Nurse, OperatingTheater, Room],
    ) -> int:
        """Insert the object in the indexer and return the corresponding index

        Args:
            type (Literal["patients", "occupants", "surgeons", "nurses", "operating_theaters", "rooms"]): category of the object
            obj (Union[Patient, Occupant, Surgeon, Nurse, OperatingTheater, Room]): object to insert

        Returns:
            int: index of the object
        """
        if type == "occupants":
            type = "patients"
        index = self.types[type]
        self.types[type] += 1
        self.indexer[type][index] = obj
        self.reverse_indexer[type][obj.id] = index
        return index

    def lookup(
        self,
        type: Literal[
            "patients",
            "occupants",
            "surgeons",
            "nurses",
            "operating_theaters",
            "rooms",
        ],
        index: int,
    ) -> Union[Patient, Occupant, Surgeon, Nurse, OperatingTheater, Room]:
        """Return the object given the type and the index

        Args:
            type (Literal["patients", "occupants", "surgeons", "nurses", "operating_theaters", "rooms"]): category of the object
            index (int): index of the object

        Returns:
            Union[Patient, Occupant, Surgeon, Nurse, OperatingTheater, Room]: object
        """
        if type == "occupants":
            type = "patients"
        return self.indexer[type][index]

    def reverse_lookup(
        self,
        type: Literal[
            "patients",
            "occupants",
            "surgeons",
            "nurses",
            "operating_theaters",
            "rooms",
        ],
        id: str,
    ) -> int:
        """Return the index given the type and the id

        Args:
            type (Literal["patients", "occupants", "surgeons", "nurses", "operating_theaters", "rooms"]): category of the object
            id (str): identifier of the object

        Returns:
            int: index of the object
        """
        if type == "occupants":
            type = "patients"
        return self.reverse_indexer[type][id]

    def id_lookup(
        self,
        type: Literal[
            "patients",
            "occupants",
            "surgeons",
            "nurses",
            "operating_theaters",
            "rooms",
        ],
        id: str,
    ) -> Union[Patient, Occupant, Surgeon, Nurse, OperatingTheater, Room]:
        """Return the object given the type and the id

        Args:
            type (Literal["patients", "occupants", "surgeons", "nurses", "operating_theaters", "rooms"]): category of the object
            id (str): identifier of the object

        Returns:
            Union[Patient, Occupant, Surgeon, Nurse, OperatingTheater, Room]: object
        """
        return self.lookup(type, self.reverse_lookup(type, id))


class NeighboringAction:
    def __init__(self):
        pass


class PASActionSchedule(NeighboringAction):
    def __init__(self, day: int, room: int, patient: int, ot: int):
        """Patient scheduling action

        Args:
            day (int): index of the day
            room (int): index of the room
            patient (int): index of the patient
            ot (int): index of the operating theater
        """
        self.day = day
        self.room = room
        self.patient = patient
        self.ot = ot

    def __str__(self):
        return f"Admitted patient {self.patient}, day {self.day}, room {self.room}, OT {self.ot}"

    def __eq__(self, value):
        if not isinstance(value, PASActionSchedule):
            return False
        return (
            self.day == value.day
            and self.room == value.room
            and self.patient == value.patient
            and self.ot == value.ot
        )


class PASActionUnschedule(NeighboringAction):
    def __init__(self, day: int, room: int, patient: int, ot: int):
        """Patient unscheduling action

        Args:
            patient (int): index of the patient
        """
        self.day = day
        self.room = room
        self.patient = patient
        self.ot = ot

    def __str__(self):
        return f"Unscheduled patient {self.patient}"

    def __eq__(self, value):
        if not isinstance(value, PASActionUnschedule):
            return False
        return (
            self.patient == value.patient
            and self.day == value.day
            and self.room == value.room
            and self.ot == value.ot
        )


class NRAActionSchedule(NeighboringAction):
    def __init__(self, shift: int, room: int, nurse: int):
        """Nurse scheduling action

        Args:
            shift (int): index of the shift
            room (int): index of the room
            nurse (int): index of the nurse
        """
        self.shift = shift
        self.room = room
        self.nurse = nurse

    def __str__(self):
        return f"Scheduled nurse {self.nurse}, shift {self.shift}, room {self.room}"

    def __eq__(self, value):
        if not isinstance(value, NRAActionSchedule) and not isinstance(
            value, NRAActionUnschedule
        ):
            return False
        return (
            self.shift == value.shift
            and self.room == value.room
            and self.nurse == value.nurse
        )


class NRAActionUnschedule(NeighboringAction):
    def __init__(self, shift: int, room: int, nurse: int):
        """Nurse unscheduling action

        Args:
            shift (int): index of the shift
            room (int): index of the room
            nurse (int): index of the nurse
        """
        self.shift = shift
        self.room = room
        self.nurse = nurse

    def __str__(self):
        return f"Unscheduled nurse {self.nurse}, shift {self.shift}, room {self.room}"

    def __eq__(self, value):
        if not isinstance(value, NRAActionUnschedule) and not isinstance(
            value, NRAActionSchedule
        ):
            return False
        return (
            # self.shift == value.shift and
            self.room == value.room
            and self.nurse == value.nurse
        )


class ActionError(Exception):
    def __init__(self, message: str = "Action error"):
        """Initialize the ActionError object

        Args:
            message (str, optional): message to display. Defaults to "Action error".
        """
        self.message = message
        super().__init__(self.message)


class Loader:
    def __init__(self, file_path: str, indexer: Indexer):
        """Initialize the Loader object

        Args:
            file_path (str): path to the JSON file containing the hospital data
            indexer (Indexer): indexer object
        """
        with open(file_path, "r") as fp:
            self.data: dict[str, Union[int, str, dict]] = json.load(fp)
        self.indexer = indexer
        self.days: int = self.data["days"]
        self.skill_levels: int = self.data["skill_levels"]
        self.shift_types: List[str] = self.data["shift_types"]
        self.age_groups: List[str] = self.data["age_groups"]
        self.weights: dict[str, int] = self.data["weights"]

    def get_days(self) -> int:
        """Return the number of days

        Returns:
            int: number of days
        """
        return self.days

    def get_skill_levels(self) -> int:
        """Return the number of skill levels

        Returns:
            int: number of skill levels
        """
        return self.skill_levels

    def get_shift_types(self) -> List[str]:
        """Return the list of shift types

        Returns:
            List[str]: list of shift types
        """
        return self.shift_types

    def get_age_groups(self) -> List[str]:
        """Return the list of age groups

        Returns:
            List[str]: list of age groups
        """
        return self.age_groups

    def get_weights(self) -> Dict[str, int]:
        """Return the weights

        Returns:
            Dict[str, int]: dictionary of weights
        """
        return self.weights

    def load_rooms(self) -> NDArray:
        """Load the rooms

        Returns:
            NDArray: array of rooms
        """
        rooms = np.array([], dtype=Room)
        for room_dict in self.data["rooms"]:
            room = Room(**room_dict)
            rooms = np.append(rooms, room)
            self.indexer.get_index("rooms", room)
        return rooms

    def load_operating_theaters(self) -> NDArray:
        """Load the operating theaters

        Returns:
            NDArray: array of operating theaters
        """
        operating_theaters = np.array([], dtype=OperatingTheater)
        operating_theaters = np.append(
            operating_theaters,
            OperatingTheater(id="dummy", availability=[0] * self.days),
        )
        self.indexer.get_index("operating_theaters", operating_theaters[-1])
        for operating_theater_dict in self.data["operating_theaters"]:
            operating_theater = OperatingTheater(**operating_theater_dict)
            operating_theaters = np.append(operating_theaters, operating_theater)
            self.indexer.get_index("operating_theaters", operating_theater)
        return operating_theaters

    def load_surgeons(self) -> NDArray:
        """Load the surgeons

        Returns:
            NDArray: array of surgeons
        """
        surgeons = np.array([], dtype=Surgeon)
        for surgeon_dict in self.data["surgeons"]:
            surgeon = Surgeon(**surgeon_dict)
            surgeons = np.append(surgeons, surgeon)
            self.indexer.get_index("surgeons", surgeon)
        return surgeons

    def load_occupants(self) -> NDArray:
        """Load the occupants

        Returns:
            NDArray: array of occupants
        """
        occupants = np.array([], dtype=Occupant)
        for occupant_dict in self.data["occupants"]:
            room_id: str = occupant_dict.pop("room_id")
            room = self.indexer.id_lookup("rooms", room_id)
            occupant = Occupant(room=room, age_groups=self.age_groups, **occupant_dict)
            occupants = np.append(occupants, occupant)
            self.indexer.get_index("occupants", occupant)
        return occupants

    def load_patients(self, occupants: NDArray) -> NDArray:
        """Load the patients

        Args:
            occupants (NDArray): array of occupants

        Returns:
            NDArray: array of patients (including occupants)
        """
        patients = np.array([], dtype=Patient)
        patients = np.append(patients, occupants)
        for patient_dict in self.data["patients"]:
            surgeon_id = patient_dict.pop("surgeon_id")
            surgeon = self.indexer.id_lookup("surgeons", surgeon_id)
            incompatible_room_ids = patient_dict.pop("incompatible_room_ids")
            incompatible_rooms = [
                self.indexer.id_lookup("rooms", i) for i in incompatible_room_ids
            ]
            patient = Patient(
                surgeon=surgeon,
                incompatible_rooms=incompatible_rooms,
                age_groups=self.age_groups,
                **patient_dict,
            )
            patients = np.append(patients, patient)
            self.indexer.get_index("patients", patient)
        return patients

    def load_nurses(self) -> NDArray:
        """Load the nurses

        Returns:
            NDArray: array of nurses
        """
        nurses = np.array([], dtype=Nurse)
        for nurse_dict in self.data["nurses"]:
            nurse_dict["shift_types"] = self.shift_types
            nurse = Nurse(days=self.days, **nurse_dict)
            nurses = np.append(nurses, nurse)
            self.indexer.get_index("nurses", nurse)
        return nurses


class Logger:
    def __init__(self):
        """Initialize the Logger object"""
        self.penalties: List[str] = []
        self.actions: List[str] = []

    def log_action(self, penalty: int, action: str):
        """Log the action

        Args:
            penalty (int): penalty value
            action (str): action description
        """
        self.penalties.append(penalty)
        self.actions.append(action)

    def get_log(self, file_path: str):
        """Print the log to csv file

        Args:
            file_path (str): path to the file
        """
        pd.DataFrame({"penalties": self.penalties, "actions": self.actions}).to_csv(
            file_path, index=True
        )


class PAS:
    def __init__(
        self,
        indexer: Indexer,
        days: int,
        rooms: int,
        patients: int,
    ):
        """Initialize the Patient Admission Scheduling (PAS) object

        Args:
            indexer (Indexer): indexer object
            days (int): number of days
            rooms (int): number of rooms
            patients (int): number of patients
        """
        # For every day, keep track of the patients assigned to each room
        self.pas_matrix = np.zeros((days, rooms, patients), dtype=bool)
        self.indexer = indexer

    def print(self):
        """Print the current status of the PAS matrix"""
        for p in np.argwhere(self.pas_matrix):
            for key, value in dict(zip(["day", "rooms", "patients"], p)).items():
                if key == "day":
                    print(f"PAS: {key}: {value}", end=" ")
                else:
                    print(
                        f"PAS: {key}: {self.indexer.lookup(type=key, index=value).id}",
                        end=" ",
                    )
            print()

    def save(self) -> NDArray:
        """Save the current status of the PAS problem

        Returns:
            NDArray: PAS matrix
        """
        self.pas_matrix_copy = copy.deepcopy(self.pas_matrix)
        return self.pas_matrix_copy

    def restore(self, pas_matrix: NDArray = None):
        """Restore the PAS problem to the previous status

        Args:
            pas_matrix (NDArray): PAS matrix
        """
        if pas_matrix is not None:
            self.pas_matrix = copy.deepcopy(pas_matrix)
        else:
            self.pas_matrix = copy.deepcopy(self.pas_matrix_copy)

    def add_occupants(self, occupants: NDArray):
        """Add occupants to the PAS matrix

        Args:
            occupants (NDArray): array of occupants

        Raises:
            ValueError: if the array contains elements that are not instances of Occupant
        """
        for occupant in occupants:
            if not isinstance(occupant, Occupant):
                raise ValueError("Occupant is not an instance of Occupant")

            occupant_index = self.indexer.reverse_lookup("occupants", occupant.id)
            room_index = self.indexer.reverse_lookup("rooms", occupant.room.id)
            coordinates = (
                np.arange(0, occupant.length_of_stay),
                room_index,
                occupant_index,
            )
            self.pas_matrix[coordinates] = True

    def schedule_patient(
        self, day: int, end_day: int, room_index: int, patient_index: int
    ):
        """Schedule the patient

        Args:
            day (int): start day
            end_day (int): end day
            room_index (int): index of the room
            patient_index (int): index of the patient
        """
        self.pas_matrix[day:end_day, room_index, patient_index] = True

    def unschedule_patient(self, patient_index: int):
        """Unschedule the patient

        Args:
            patient_index (int): index of the patient
        """
        self.pas_matrix[:, :, patient_index] = False

    def get_patient_schedule(self, patient_index: int) -> Tuple[int, int]:
        """Return the schedule of the patient

        Args:
            patient_index (int): index of the patient

        Returns:
            Tuple[int, int]: index of the day and room
        """
        days, rooms = np.nonzero(self.pas_matrix[:, :, patient_index])
        return days[0], rooms[0]

    def check_already_scheduled(self, patient_index: int) -> bool:
        """Check if the patient is already scheduled

        Args:
            patient (int): index of the patient

        Returns:
            bool: True if the patient is already scheduled, False otherwise
        """
        return self.pas_matrix[:, :, patient_index].any(axis=(0, 1))

    def check_admission_day(self, day: int, patient: Patient) -> bool:
        """Check if the patient can be scheduled on the given day

        Args:
            day (int): start day
            patient (Patient): patient object

        Returns:
            bool: True if the patient can be scheduled, False otherwise
        """
        check = day >= patient.surgery_release_day
        if patient.mandatory:
            check &= day <= patient.surgery_due_day
        return check

    def check_gender(
        self, day: int, end_day, patients: NDArray, patient: Patient, room_index: int
    ) -> bool:
        """Check if all patients in the room have the same gender

        Args:
            day (int): start day
            end_day (_type_): end day
            patients (NDArray): array of patients
            patient (Patient): patient object
            room_index (int): index of the room

        Returns:
            bool: True if all patients in the room have the same gender, False otherwise
        """
        # Mask of patients in the same room
        patients_same_room_mask = np.any(
            self.pas_matrix[day:end_day, room_index, :], axis=0
        )
        gender_fun = np.vectorize(lambda p: p.gender == patient.gender, otypes=[bool])
        return gender_fun(patients[patients_same_room_mask]).all()

    def check_room_compatible(self, patient: Patient, room: Room) -> bool:
        """Check if the patient is compatible with the room

        Args:
            patient (Patient): patient object
            room (Room): room object

        Returns:
            bool: True if the patient is compatible with the room, False otherwise
        """
        return room.id not in patient.incompatible_rooms

    def check_room_capacity(
        self, day: int, end_day: int, room_index: int, room: Room
    ) -> bool:
        """Check if the room capacity is not exceeded

        Args:
            day (int): start day
            end_day (int): end day
            room_index (int): index of the room
            room (Room): room object

        Returns:
            bool: True if the room capacity is not exceeded, False otherwise
        """
        n_patients_same_room: int = self.pas_matrix[day:end_day, room_index, :].sum(
            axis=1
        )
        return np.all(n_patients_same_room + 1 <= room.capacity)

    def check_room_empty(self, day: int, room_index: int) -> bool:
        """Check if the room is empty

        Args:
            day (int): start day

        Returns:
            bool: True if the room is empty, False otherwise
        """
        return not self.pas_matrix[day, room_index, :].any()

    def get_scheduled_patients_mask(self) -> NDArray:
        """Return the mask of scheduled patients

        Returns:
            NDArray: mask of scheduled patients
        """
        return self.pas_matrix.any(axis=(0, 1))

    def penalty_age_mix(self, weight: int, age_groups: int) -> int:
        """Compute the penalty for age mix

        Args:
            weight (int): weight of the penalty
            age_groups (int): number of distinct age groups

        Returns:
            int: penalty for age mix
        """
        days, rooms, patients = np.nonzero(self.pas_matrix)
        min_ages = np.zeros(self.pas_matrix.shape, dtype=int) + age_groups
        max_ages = np.zeros(self.pas_matrix.shape, dtype=int)
        for day, room, patient in zip(days, rooms, patients):
            age = self.indexer.lookup("patients", patient).age_group
            min_ages[day, room, patient] = age
            max_ages[day, room, patient] = age
        return (max_ages.max(axis=-1) - min_ages.min(axis=-1))[
            min_ages.min(axis=-1) < age_groups
        ].sum() * weight

    def penalty_unscheduled(self, weight: int) -> int:
        """Compute the penalty for unscheduled patients

        Args:
            weight (int): weight of the penalty

        Returns:
            int: penalty for unscheduled patients
        """
        return np.sum(~self.get_scheduled_patients_mask()) * weight


class SCP:
    def __init__(
        self,
        indexer: Indexer,
        days: int,
        patients: int,
        surgeons: int,
        operating_theaters: int,
        dummy_ot=0,
    ):
        """Initialize the Surgery Capacity Planning (SCP) object

        Args:
            indexer (Indexer): indexer object
            days (int): number of days
            patients (int): number of patients
            surgeons (int): number of surgeons
            operating_theaters (int): number of operating theaters
            dummy_ot (int, optional): index of the dummy operating theater. Defaults to 0.
        """
        # For each day, keep track of the scheduled surgeries time for each patient, surgeon, and operating theater
        self.scp_matrix = np.zeros(
            (days, patients, surgeons, operating_theaters), dtype=int
        )
        self.indexer = indexer
        self.dummy_ot = dummy_ot

    def print(self):
        """Print the current status of the PAS matrix"""
        # for p in np.argwhere(self.scp_matrix):
        #     for key, value in dict(
        #         zip(["day", "patients", "surgeons", "operating_theaters"], p)
        #     ).items():
        #         if key == "day":
        #             print(f"PAS: {key}: {value}", end=" ")
        #         else:
        #             print(
        #                 f"PAS: {key}: {self.indexer.lookup(type=key, index=value).id}",
        #                 end=" ",
        #             )
        print()

    def save(self) -> NDArray:
        """Save the current status of the SCP problem

        Returns:
            NDArray: SCP matrix
        """
        self.scp_matrix_copy = copy.deepcopy(self.scp_matrix)
        return self.scp_matrix_copy

    def restore(self, scp_matrix: NDArray = None):
        """Restore the SCP problem to the previous status

        Args:
            scp_matrix (NDArray): SCP matrix
        """
        if scp_matrix is not None:
            self.scp_matrix = copy.deepcopy(scp_matrix)
        else:
            self.scp_matrix = copy.deepcopy(self.scp_matrix_copy)

    def schedule_patient(
        self,
        day: int,
        patient: Patient,
        patient_index: int,
        surgeon_index: int,
        ot_index: int,
    ):
        """Schedule the patient

        Args:
            day (int): day of the surgery
            patient_index (int): index of the patient
            surgeon_index (int): index of the surgeon
            ot_index (int): index of the operating theater
        """
        self.scp_matrix[day, patient_index, surgeon_index, ot_index] = (
            patient.surgery_duration
        )

    def unschedule_patient(self, patient_index: int):
        """Unschedule the patient

        Args:
            patient_index (int): index of the patient
        """
        self.scp_matrix[:, patient_index, :, :] = 0

    def get_patient_schedule(self, patient_index: int) -> Tuple[int, int, int]:
        """Return the schedule of the patient

        Args:
            patient_index (int): index of the patient

        Returns:
            Tuple[int, int, int]: index of the day, surgeon, and operating theater
        """
        days, surgeons, ots = np.nonzero(self.scp_matrix[:, patient_index, :, :])
        return days[0], surgeons[0], ots[0]

    def check_surgeon_overtime(
        self, day: int, surgeon: Surgeon, surgeon_index: int, patient: Patient
    ) -> bool:
        """Check if the surgeon is available for the surgery

        Args:
            day (int): day of the surgery
            surgeon (Surgeon): surgeon object
            surgeon_index (int): index of the surgeon
            patient (Patient): patient object

        Returns:
            bool: True if the surgeon is available, False otherwise
        """
        surgeries_duration = self.scp_matrix[day, :, surgeon_index, :].sum(axis=(0, 1))
        return (
            surgeries_duration + patient.surgery_duration
            <= surgeon.max_surgery_time[day]
        )

    def check_operating_theater_overtime(
        self,
        day: int,
        operating_theater: OperatingTheater,
        operating_theater_index: int,
        patient: Patient,
    ) -> bool:
        """Check if the operating theater is available for the surgery

        Args:
            day (int): day of the surgery
            operating_theater (OperatingTheater): operating theater object
            operating_theater_index (int): index of the operating theater
            patient (Patient): patient object

        Returns:
            bool: True if the operating theater is available, False otherwise
        """
        surgeries_duration = self.scp_matrix[day, :, :, operating_theater_index].sum(
            axis=(0, 1)
        )
        return (
            surgeries_duration + patient.surgery_duration
            <= operating_theater.availability[day]
        )

    def penalty_open_ot(self, weight: int) -> int:
        """Compute the penalty for open operating theaters

        Args:
            weight (int): weight of the penalty

        Returns:
            int: penalty for open operating theaters
        """
        return (
            self.scp_matrix[:, :, :, self.dummy_ot :].any(axis=(1, 2)).sum(axis=(0, 1))
            * weight
        )

    def penalty_transfer(self, weight: int) -> int:
        """Compute the penalty for surgeon transfers

        Args:
            weight (int): weight of the penalty

        Returns:
            int: penalty for surgeon transfers
        """
        different_ots = self.scp_matrix[:, :, :, self.dummy_ot :].any(axis=1).sum(axis=-1)
        return (
            (different_ots[different_ots > 0] - 1).sum()
            * weight
        )

    def penalty_delay(self, weight: int) -> int:
        """Compute the penalty for patient delays

        Args:
            weight (int): weight of the penalty

        Returns:
            int: penalty for patient delays
        """
        penalty = 0
        days, patients, _, _ = np.nonzero(self.scp_matrix[:, :, :, self.dummy_ot :])
        for day, patient in zip(days, patients):
            release_day = self.indexer.lookup("patients", patient).surgery_release_day
            if (diff := day - release_day) > 0:
                penalty += diff

        return penalty * weight


class NRA:
    def __init__(
        self,
        indexer: Indexer,
        days: int,
        shifts: int,
        rooms: int,
        nurses: int,
        patients: int,
    ):
        """Initialize the Nurse Rostering Assignment (NRA) object

        Args:
            indexer (Indexer): indexer object
            days (int): number of days
            shifts (int): number of shifts
            rooms (int): number of rooms
            nurses (int): number of nurses
            patients (int): number of patients
        """
        self.days = days
        self.shifts = shifts
        # For each shift, keep track of the nurses assigned to each room
        self.nra_matrix = np.zeros((days * shifts, rooms, nurses), dtype=bool)
        # For each shift, keep track of the patient assigned to each room
        self.patient_matrix = np.zeros((days * shifts, rooms, patients), dtype=bool)
        # For each shift, keep track of the workload produced by each patient in each room
        self.workload_matrix = np.zeros((days * shifts, rooms, patients), dtype=int)
        # For each shift, keep track of the skill level required by each patient in each room
        self.skill_matrix = np.zeros((days * shifts, rooms, patients), dtype=int)
        self.indexer = indexer

    def print(self):
        """Print the current status of the NRA matrix"""
        for n in np.argwhere(self.nra_matrix):
            for key, value in dict(zip(["shifts", "rooms", "nurses"], n)).items():
                if key == "shifts":
                    print(f"NRA: {key}: {value}", end=" ")
                else:
                    print(
                        f"NRA: {key}: {self.indexer.lookup(type=key, index=value).id}",
                        end=" ",
                    )
            print()

    def save(self) -> Tuple[NDArray, NDArray, NDArray, NDArray]:
        """Save the current status of the NRA problem

        Returns:
            Tuple[NDArray, NDArray, NDArray, NDArray]: NRA matrix, workload matrix, skill matrix, patient matrix
        """
        self.nra_matrix_copy = copy.deepcopy(self.nra_matrix)
        self.workload_matrix_copy = copy.deepcopy(self.workload_matrix)
        self.skill_matrix_copy = copy.deepcopy(self.skill_matrix)
        self.patient_matrix_copy = copy.deepcopy(self.patient_matrix)
        return (
            self.nra_matrix_copy,
            self.workload_matrix_copy,
            self.skill_matrix_copy,
            self.patient_matrix_copy,
        )

    def restore(
        self,
        nra_matrix: NDArray = None,
        workload_matrix: NDArray = None,
        skill_matrix: NDArray = None,
        patient_matrix: NDArray = None,
    ):
        """Restore the NRA problem to the previous status

        Args:
            nra_matrix (NDArray, optional): NRA matrix. Defaults to None.
            workload_matrix (NDArray, optional): workload matrix. Defaults to None.
            skill_matrix (NDArray, optional): skill matrix. Defaults to None.
            patient_matrix (NDArray, optional): patient matrix. Defaults to None.
        """
        if (
            nra_matrix is not None
            and workload_matrix is not None
            and skill_matrix is not None
            and patient_matrix is not None
        ):
            self.nra_matrix = copy.deepcopy(nra_matrix)
            self.workload_matrix = copy.deepcopy(workload_matrix)
            self.skill_matrix = copy.deepcopy(skill_matrix)
            self.patient_matrix = copy.deepcopy(patient_matrix)
        else:
            self.nra_matrix = copy.deepcopy(self.nra_matrix_copy)
            self.workload_matrix = copy.deepcopy(self.workload_matrix_copy)
            self.skill_matrix = copy.deepcopy(self.skill_matrix_copy)
            self.patient_matrix = copy.deepcopy(self.patient_matrix_copy)

    def add_occupants(self, occupants: NDArray):
        """Add occupants to the NRA matrix

        Args:
            occupants (NDArray): array of occupants

        Raises:
            ValueError: if the array contains elements that are not instances of Occupant
        """
        for occupant in occupants:
            if not isinstance(occupant, Occupant):
                raise ValueError("Occupant is not an instance of Occupant")

            occupant_index = self.indexer.reverse_lookup("occupants", occupant.id)
            room_index = self.indexer.reverse_lookup("rooms", occupant.room.id)
            coordinates = (
                np.arange(0, occupant.length_of_stay * self.shifts),
                room_index,
                occupant_index,
            )
            self.workload_matrix[coordinates] = np.array(occupant.workload_produced)
            self.skill_matrix[coordinates] = np.array(occupant.skill_level_required)

    def schedule_patient(
        self,
        day: int,
        end_day: int,
        room_index: int,
        patient: Patient,
        patient_index: int,
    ):
        """Schedule the patient

        Args:
            day (int): start day
            end_day (int): end day
            room_index (int): index of the room
            patient (Patient): patient object
            patient_index (int): index of the patient
        """
        coordinates = (
            np.arange(day * self.shifts, end_day * self.shifts),
            room_index,
            patient_index,
        )
        self.workload_matrix[coordinates] = np.array(
            patient.workload_produced[: (end_day - day) * self.shifts]
        )
        self.skill_matrix[coordinates] = np.array(
            patient.skill_level_required[: (end_day - day) * self.shifts]
        )
        self.patient_matrix[coordinates] = True

    def unschedule_patient(self, patient_index: int):
        """Unschedule the patient

        Args:
            patient_index (int): index of the patient
        """
        self.workload_matrix[:, :, patient_index] = 0
        self.skill_matrix[:, :, patient_index] = 0
        self.patient_matrix[:, :, patient_index] = False

    def assign_nurse(self, shift: int, room_index: int, nurse_index: int):
        """Assign the nurse to the room

        Args:
            shift (int): index of the shift
            room_index (int): index of the room
            nurse_index (int): index of the nurse
        """
        self.nra_matrix[shift, room_index, nurse_index] = True

    def unassign_nurse(self, shift: int, room_index: int, nurse_index: int):
        """Unassign the nurse from the room

        Args:
            shift (int): index of the shift
            room_index (int): index of the room
            nurse_index (int): index of the nurse
        """
        self.nra_matrix[shift, room_index, nurse_index] = False

    def get_nurse_schedule(self, nurse_index: int) -> Tuple[List[int], List[int]]:
        """Return the schedule of the nurse

        Args:
            nurse_index (int): index of the nurse

        Returns:
            Tuple[List[int], List[int]]: list of corresponding shifts and rooms
        """
        shifts, rooms = np.nonzero(self.nra_matrix[:, :, nurse_index])
        return shifts, rooms
    
    def check_room_covered_shift(self, shift: int, room_index: int) -> bool:
        """Check if the room is covered by any nurse for the given shift

        Args:
            shift (int): index of the shift
            room_index (int): index of the room

        Returns:
            bool: True if the room is covered by any nurse, False otherwise
        """
        return self.nra_matrix[shift, room_index, :].any()

    def check_room_covered_day(self, day: int, end_day: int, room_index: int) -> bool:
        """Check if the room is covered for all shifts by any nurse

        Args:
            day (int): start day
            end_day (int): end day
            room_index (int): index of the room

        Returns:
            bool: True if the room is covered for all shifts by any nurse, False otherwise
        """
        return (
            self.nra_matrix[
                day * self.shifts : end_day * self.shifts,
                room_index,
                :,
            ]
            .any(axis=1)
            .all()
        )

    def check_already_assigned(
        self, nurse_index: int, shift: int, room_index: int
    ) -> bool:
        """Check if the nurse is already assigned

        Args:
            nurse_index (int): index of the nurse
            shift (int): index of the shift
            room_index (int): index of the room


        Returns:
            bool: True if the nurse is already assigned, False otherwise
        """
        return self.nra_matrix[shift, room_index, nurse_index]

    def penalty_skill(self, weight: int) -> int:
        """Compute the penalty for skill level

        Args:
            weight (int): weight of the penalty

        Returns:
            int: penalty for skill level
        """
        penalty = 0
        max_skill_level_per_room = self.skill_matrix.max(axis=-1)
        shifts, rooms, nurses = np.nonzero(self.nra_matrix)
        for shift, room, nurse in zip(shifts, rooms, nurses):
            nurse_skill = self.indexer.lookup("nurses", nurse).skill_level
            if (diff := max_skill_level_per_room[shift, room] - nurse_skill) > 0:
                penalty += diff
        return penalty * weight

    def penalty_continuity(self, weight: int) -> int:
        """Compute the penalty for continuity of care

        Args:
            weight (int): weight of the penalty

        Returns:
            int: penalty for continuity of care
        """
        
        penalty = 0
        for patient in range(self.patient_matrix.shape[-1]):
            if not self.patient_matrix[:, :, patient].any(axis=(0, 1)):
                continue
            shifts, rooms = np.nonzero(self.patient_matrix[:, :, patient])
            penalty += self.nra_matrix[shifts, rooms[0], :].any(axis=0).sum()
        return penalty * weight

    def penalty_workload(self, weight: int) -> int:
        """Compute the penalty for workload

        Args:
            weight (int): weight of the penalty

        Returns:
            int: penalty for workload
        """
        penalty = 0
        total_workload_per_room = self.workload_matrix.sum(axis=-1)
        shifts, rooms, nurses = np.nonzero(self.nra_matrix)
        for shift, room, nurse in zip(shifts, rooms, nurses):
            nurse_workload = self.indexer.lookup("nurses", nurse).maximum_workload(
                shift
            )
            if (diff := total_workload_per_room[shift, room] - nurse_workload) > 0:
                penalty += diff

        return penalty * weight


class Hospital:
    def __init__(self, fp: str):
        """Initialize the Hospital object

        Args:
            fp (str): file path to the JSON file containing the hospital data
        """
        self.indexer = Indexer()
        self.logger = Logger()
        self.loader = Loader(fp, self.indexer)

        self.days = self.loader.get_days()
        self.skill_levels = self.loader.get_skill_levels()
        self.shift_types = self.loader.get_shift_types()
        self.age_groups = self.loader.get_age_groups()
        self.weights = self.loader.get_weights()

        self.rooms = self.loader.load_rooms()
        self.operating_theaters = self.loader.load_operating_theaters()
        self.surgeons = self.loader.load_surgeons()
        self.occupants = self.loader.load_occupants()
        self.patients = self.loader.load_patients(self.occupants)
        self.nurses = self.loader.load_nurses()

        # Patient Admission Scheduling (PAS) problem
        self.pas = PAS(
            self.indexer,
            self.days,
            len(self.rooms),
            len(self.patients),
        )
        # Surgical Case Planning (SCP) problem
        self.scp = SCP(
            self.indexer,
            self.days,
            len(self.patients),
            len(self.surgeons),
            len(self.operating_theaters),
        )
        # Nurse to Room Assignment (NRA) problem
        self.nra = NRA(
            self.indexer,
            self.days,
            len(self.shift_types),
            len(self.rooms),
            len(self.nurses),
            len(self.patients),
        )

        # Add occupants to PAS:
        self.pas.add_occupants(self.occupants)
        self.nra.add_occupants(self.occupants)

    def print(self):
        """Print the current status of the hospital"""
        self.pas.print()
        self.scp.print()
        self.nra.print()

    def schedule_patient(
        self,
        day: int,
        room_index: int,
        patient_index: int,
        operating_theater_index: int,
        assign: bool = False,
    ) -> Tuple[int, Dict[str, int]]:
        """Schedule a patient in a room and operating theater for a given day

        Args:
            day (int): index of the day
            room_index (int): index of the room
            patient_index (int): index of the patient
            operating_theater_index (int): index of the operating theater
            assign (bool, optional): if True, the change is saved. Defaults to False.

        Returns:
            Tuple[int, Dict[str, int]]: overall penalty and individual penalties
        """
        # Information retrieval
        room: Room = self.indexer.lookup("rooms", room_index)
        patient: Patient = self.indexer.lookup("patients", patient_index)
        surgeon = patient.surgeon
        surgeon_index = self.indexer.reverse_lookup("surgeons", surgeon.id)
        operating_theater: OperatingTheater = self.indexer.lookup(
            "operating_theaters", operating_theater_index
        )
        end_day = min(self.days, day + patient.length_of_stay)

        # Check if patient is already scheduled
        if self.pas.check_already_scheduled(patient_index):
            raise ActionError(f"Patient is already scheduled")

        # Global constraints
        # Constraint H6: Admission day
        if not self.pas.check_admission_day(day, patient):
            raise ActionError("Patient cannot be scheduled on this day")

        # PAS constraints
        # Constraint H1: No gender mix
        gender_ok = self.pas.check_gender(
            day, end_day, self.patients, patient, room_index
        )
        # Constraint H2: Compatible rooms
        compatible_ok = self.pas.check_room_compatible(patient, room)
        # Constraint H7: Room capacity
        capacity_ok = self.pas.check_room_capacity(day, end_day, room_index, room)
        # Constraint H8: Room coverage
        room_covered_ok = self.nra.check_room_covered_day(day, end_day, room_index)

        if not gender_ok or not compatible_ok or not capacity_ok or not room_covered_ok:
            raise ActionError("Patient cannot be scheduled in this room")

        # SCP constraints (only patients need to be checked, not occupants)
        # Constraint H3: Surgeon overtime
        surgeon_overtime_ok = self.scp.check_surgeon_overtime(
            day, surgeon, surgeon_index, patient
        )
        # Constraint H4: OT overtime
        ot_duration_ok = self.scp.check_operating_theater_overtime(
            day, operating_theater, operating_theater_index, patient
        )

        if not surgeon_overtime_ok or not ot_duration_ok:
            raise ActionError("Patient cannot be scheduled in this operating theater")

        self.pas.schedule_patient(day, end_day, room_index, patient_index)
        self.scp.schedule_patient(
            day, patient, patient_index, surgeon_index, operating_theater_index
        )
        self.nra.schedule_patient(day, end_day, room_index, patient, patient_index)
        penalty, penalty_dict = self.compute_penalty()

        if not assign:
            self.pas.unschedule_patient(patient_index)
            self.scp.unschedule_patient(patient_index)
            self.nra.unschedule_patient(patient_index)

        return penalty, penalty_dict

    def unschedule_patient(
        self, patient_index: int, assign: bool = False
    ) -> Tuple[int, Dict[str, int]]:
        """Unschedule a patient

        Args:
            patient_index (int): index of the patient
            assign (bool, optional): if True, the change is saved. Defaults to False.

        Returns:
            Tuple[int, Dict[str, int]]: overall penalty and individual penalties
        """
        if not self.pas.check_already_scheduled(patient_index):
            raise ValueError("Patient is not scheduled")

        self.pas.save()
        self.scp.save()
        self.nra.save()

        self.pas.unschedule_patient(patient_index)
        self.scp.unschedule_patient(patient_index)
        self.nra.unschedule_patient(patient_index)
        penalty, penalty_dict = self.compute_penalty()

        if not assign:
            self.pas.restore()
            self.scp.restore()
            self.nra.restore()

        return penalty, penalty_dict

    def assign_nurse(
        self, shift: int, room_index: int, nurse_index: int, assign: bool = False
    ) -> Tuple[int, Dict[str, int]]:
        """Schedule a nurse in a room for a given shift

        Args:
            shift (int): index of the shift
            room_index (int): index of the room
            nurse_index (int): index of the nurse
            assign (bool, optional): if True, save the change. Defaults to False.

        Returns:
            Tuple[int, Dict[str, int]]: overall penalty and individual penalties
        """
        nurse: Nurse = self.indexer.lookup("nurses", nurse_index)
        # Check if nurse is available
        if not nurse.is_available(shift):
            raise ActionError("Nurse is not available at this shift")
        
        # Check if room is already covered
        if self.nra.check_room_covered_shift(shift, room_index):
            raise ActionError("Room is already covered by a nurse")
        
        self.nra.assign_nurse(shift, room_index, nurse_index)
        penalty, penalty_dict = self.compute_penalty()
        if not assign:
            self.nra.unassign_nurse(shift, room_index, nurse_index)
        return penalty, penalty_dict

    def unassign_nurse(
        self, shift: int, room_index: int, nurse_index: int, assign: bool = False
    ) -> Tuple[int, Dict[str, int]]:
        """Unassign a nurse

        Args:
            shift (int): index of the shift
            room_index (int): index of the room
            nurse_index (int): index of the nurse
            assign (bool, optional): if True, save the change. Defaults to False.

        Returns:
            Tuple[int, Dict[str, int]]: overall penalty and individual penalties
        """
        if not self.nra.check_already_assigned(nurse_index, shift, room_index):
            raise ActionError("Nurse is not assigned to the room on this shift")

        if not self.pas.check_room_empty(shift // len(self.shift_types), room_index):
            raise ActionError("Nurse is assigned to a patient")

        self.nra.unassign_nurse(shift, room_index, nurse_index)
        penalty, penalty_dict = self.compute_penalty()
        if not assign:
            self.nra.assign_nurse(shift, room_index, nurse_index)
        return penalty, penalty_dict

    def compute_penalty(self) -> Tuple[int, Dict[str, int]]:
        """Compute the penalty of the current solution

        Returns:
            Tuple[int, Dict[str, int]]: overall penalty and individual penalties
        """
        penalty = 0
        penalty_dict = {}

        # Constraint S1: Age group
        penalty_dict["S1"] = self.pas.penalty_age_mix(
            self.weights["room_mixed_age"], len(self.age_groups)
        )
        penalty += penalty_dict["S1"]

        # Constraint S2: Minimum skill level
        penalty_dict["S2"] = self.nra.penalty_skill(self.weights["room_nurse_skill"])
        penalty += penalty_dict["S2"]

        # Constraint S3: Continuity of care
        penalty_dict["S3"] = self.nra.penalty_continuity(
            self.weights["continuity_of_care"]
        )
        penalty += penalty_dict["S3"]

        # Constraint S4: Maximum workload
        penalty_dict["S4"] = self.nra.penalty_workload(
            self.weights["nurse_eccessive_workload"]
        )
        penalty += penalty_dict["S4"]

        # Constraint S5: Open OT
        penalty_dict["S5"] = self.scp.penalty_open_ot(
            self.weights["open_operating_theater"]
        )
        penalty += penalty_dict["S5"]

        # Constraint S6: Surgeon transfer
        penalty_dict["S6"] = self.scp.penalty_transfer(self.weights["surgeon_transfer"])
        penalty += penalty_dict["S6"]

        # Constraint S7: Admission delay
        penalty_dict["S7"] = self.scp.penalty_delay(self.weights["patient_delay"])
        penalty += penalty_dict["S7"]

        # Constraint S8: Unscheduled patients
        penalty_dict["S8"] = self.pas.penalty_unscheduled(
            self.weights["unscheduled_optional"]
        )
        penalty += penalty_dict["S8"]

        return penalty, penalty_dict

    def save_status(self):
        """Save the current status as the best status found so far"""
        self.best_patients = copy.deepcopy(self.patients)
        self.best_nurses = copy.deepcopy(self.nurses)
        self.pas_status = self.pas.save()
        self.scp_status = self.scp.save()
        self.nra_status = self.nra.save()

    def load_status(self):
        """Load the best status found so far"""
        self.patients = np.copy(self.best_patients)
        self.nurses = np.copy(self.best_nurses)
        self.pas.restore(self.pas_status)
        self.scp.restore(self.scp_status)
        self.nra.restore(self.nra_status)

    def apply_action(
        self, action: NeighboringAction, assign: bool = False
    ) -> Tuple[int, Dict[str, int]]:
        """Apply a neighboring action to the current state

        Args:
            action (NeighboringAction): action to apply
            assign (bool, optional): if True, the change is saved. Defaults to False.

        Returns:
            Tuple[int, Dict[str, int]]: overall penalty and individual penalties
        """

        if isinstance(action, PASActionSchedule):
            penalty, penalty_dict = self.schedule_patient(
                action.day, action.room, action.patient, action.ot, assign
            )
            if assign:
                room_id = self.indexer.lookup("rooms", action.room).id
                ot_id = self.indexer.lookup("operating_theaters", action.ot).id
                patient: Patient = self.patients[action.patient]
                patient.set_assignment(action.day, room_id, ot_id)

                # print(
                #     f"Patient {patient.id} scheduled on day {action.day} in room {room_id} and OT {ot_id}"
                # )

        if isinstance(action, PASActionUnschedule):
            penalty, penalty_dict = self.unschedule_patient(action.patient, assign)
            if assign:
                patient: Patient = self.patients[action.patient]
                patient.unset_assignment()

                # print(f"Patient {patient.id} unscheduled")

        if isinstance(action, NRAActionSchedule):
            penalty, penalty_dict = self.assign_nurse(
                action.shift, action.room, action.nurse, assign
            )
            if assign:
                room_id = self.indexer.lookup("rooms", action.room).id
                nurse: Nurse = self.nurses[action.nurse]
                nurse.set_assignment(
                    action.shift // len(self.shift_types),
                    self.shift_types[action.shift % len(self.shift_types)],
                    room_id,
                )

                # print(
                #     f"Nurse {nurse.id} assigned on shift {action.shift} in room {room_id}"
                # )

        if isinstance(action, NRAActionUnschedule):
            penalty, penalty_dict = self.unassign_nurse(
                action.shift, action.room, action.nurse, assign
            )
            if assign:
                room_id = self.indexer.lookup("rooms", action.room).id
                nurse: Nurse = self.nurses[action.nurse]
                nurse.unset_assignment(
                    action.shift // len(self.shift_types),
                    self.shift_types[action.shift % len(self.shift_types)],
                    room_id,
                )

                # print(
                #     f"Nurse {nurse.id} unassigned on shift {action.shift} in room {room_id}"
                # )

        if assign:
            self.logger.log_action(penalty, str(action))
            print(f"\tPenalty: {penalty}, penalties: {penalty_dict}", end="\n\n")

        return penalty, penalty_dict

    def generate_patients_moves(self) -> List[NeighboringAction]:
        """Generate all possible neighboring moves for the patients

        Returns:
            List[NeighboringAction]: list of possible moves
        """
        moves = []
        # Mask of unscheduled patients
        patients_unscheduled_mask = ~self.pas.get_scheduled_patients_mask()[
            len(self.occupants) :
        ]
        # Get unscheduled patients
        patients_unscheduled = self.patients[len(self.occupants) :][
            patients_unscheduled_mask
        ]
        # Check if there are mandatory patients among the unscheduled ones
        mandatory_fun = np.vectorize(lambda p: p.mandatory, otypes=[bool])
        # Mask of unscheduled mandatory patients
        patients_unscheduled_mandatory_mask = mandatory_fun(patients_unscheduled)
        for patient in self.patients[len(self.occupants) :]:
            patient: Patient
            patient_index = self.indexer.reverse_lookup("patients", patient.id)
            # Unschedule action if the patient is already scheduled
            if self.pas.check_already_scheduled(patient_index):
                day, room = self.pas.get_patient_schedule(patient_index)
                _, _, ot = self.scp.get_patient_schedule(patient_index)
                moves.append(PASActionUnschedule(day, room, patient_index, ot))
                continue
            # If there are unscheduled mandatory patients, they have priority
            if patients_unscheduled_mandatory_mask.any() and not patient.mandatory:
                continue
            # Compute incompatible rooms for the patient
            incompatible_rooms = {
                self.indexer.reverse_lookup("rooms", i.id)
                for i in patient.incompatible_rooms
            }
            # Compute start and end date that are feasible for the patient
            start_date = patient.surgery_release_day
            end_date = self.days - 1
            if patient.mandatory:
                end_date = patient.surgery_due_day
            for day in range(start_date, end_date + 1):
                for room_index, _ in enumerate(self.rooms):
                    if room_index in incompatible_rooms:
                        continue
                    for ot_index, _ in enumerate(self.operating_theaters):
                        if ot_index == 0:  # not consider dummy
                            continue
                        schedule_move = PASActionSchedule(
                            day, room_index, patient_index, ot_index
                        )
                        moves.append(schedule_move)
        return moves

    def generate_nurses_moves(self) -> List[NeighboringAction]:
        """Generate all possible neighboring moves for the nurses

        Returns:
            List[NeighboringAction]: list of possible moves
        """
        moves = []
        for nurse in self.nurses:
            nurse: Nurse
            nurse_index = self.indexer.reverse_lookup("nurses", nurse.id)
            # Shifts where the nurse is already scheduled, with the corresponding rooms
            # Each of these pairs (shift, room) characterizes a forbidden action
            shifts, rooms = self.nra.get_nurse_schedule(nurse_index)
            forbidden_actions = {(s, r) for s, r in zip(shifts, rooms)}
            # Schedule actions based on the forbidden actions
            for shift in nurse.working_shifts.values():
                for room_index, _ in enumerate(self.rooms):
                    if (shift.index, room_index) in forbidden_actions:
                        unschedule_move = NRAActionUnschedule(
                            shift.index, room_index, nurse_index
                        )
                        moves.append(unschedule_move)
                    else:
                        schedule_move = NRAActionSchedule(
                            shift.index, room_index, nurse_index
                        )
                        moves.append(schedule_move)
        return moves

    def get_neighboring_moves(self) -> List[NeighboringAction]:
        """Generate all possible neighboring moves

        Returns:
            List[NeighboringAction]: list of all possible neighboring moves
        """
        moves = self.generate_patients_moves()
        nurses_moves = self.generate_nurses_moves()
        moves.extend(nurses_moves)
        return moves

    def json_dump(self, filename: str, log_filename: str = ""):
        """Dump the current status of the hospital in a JSON file

        Args:
            filename (str): name of the file where to save the data
        """
        data = {"patients": [], "nurses": []}
        for patient in self.patients:
            if isinstance(patient, Patient):
                data["patients"].append(patient.assignment)
        for nurse in self.nurses:
            data["nurses"].append(nurse.assignment)
        with open(filename, "w") as outfile:
            json.dump(data, outfile, indent=4)

        if log_filename != "":
            self.logger.get_log(log_filename)
