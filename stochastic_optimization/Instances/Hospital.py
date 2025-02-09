from io import TextIOWrapper
import json
from collections import defaultdict
from typing import List, Literal, Union, Tuple, Dict
import numpy as np
import copy


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
    def __init__(self, patient: int):
        """Patient unscheduling action

        Args:
            patient (int): index of the patient
        """
        self.patient = patient

    def __str__(self):
        return f"Unscheduled patient {self.patient}"

    def __eq__(self, value):
        if not isinstance(value, PASActionUnschedule):
            return False
        return self.patient == value.patient


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
            # self.shift == value.shift
            # and
            self.room == value.room
            and self.nurse == value.nurse
        )


class Hospital:
    def __init__(self, fp: TextIOWrapper):
        """Initialize the Hospital object

        Args:
            fp (TextIOWrapper): file pointer to the JSON file containing the hospital data
        """
        self.indexer = Indexer()
        json_data: dict[str, Union[int, str, dict]] = json.load(fp)

        self.days: int = json_data["days"]
        self.skill_levels: int = json_data["skill_levels"]
        self.shift_types: List[str] = json_data["shift_types"]
        self.age_groups: List[str] = json_data["age_groups"]
        self.weights: dict[str, int] = json_data["weights"]

        # Rooms
        self.rooms = np.array([], dtype=Room)
        for room_dict in json_data["rooms"]:
            room = Room(**room_dict)
            self.rooms = np.append(self.rooms, room)
            self.indexer.get_index("rooms", room)

        # Operating theaters (including dummy for occupants)
        self.operating_theaters = np.array([], dtype=OperatingTheater)
        self.operating_theaters = np.append(
            self.operating_theaters,
            OperatingTheater(id="dummy", availability=[0] * self.days),
        )
        self.indexer.get_index("operating_theaters", self.operating_theaters[-1])
        for operating_theater_dict in json_data["operating_theaters"]:
            operating_theater = OperatingTheater(**operating_theater_dict)
            self.operating_theaters = np.append(
                self.operating_theaters, operating_theater
            )
            self.indexer.get_index("operating_theaters", operating_theater)

        # Surgeons
        self.surgeons = np.array([], dtype=Surgeon)
        for surgeon_dict in json_data["surgeons"]:
            surgeon = Surgeon(**surgeon_dict)
            self.surgeons = np.append(self.surgeons, surgeon)
            self.indexer.get_index("surgeons", surgeon)

        # Occupants
        self.occupants = np.array([], dtype=Occupant)
        for occupant_dict in json_data["occupants"]:
            room_id: str = occupant_dict.pop("room_id")
            room = self.indexer.id_lookup("rooms", room_id)
            occupant = Occupant(room=room, age_groups=self.age_groups, **occupant_dict)
            self.occupants = np.append(self.occupants, occupant)
            self.indexer.get_index("occupants", occupant)

        # Patients
        self.patients = np.array([], dtype=Patient)
        self.patients = np.append(self.patients, self.occupants)
        for patient_dict in json_data["patients"]:
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
            self.patients = np.append(self.patients, patient)
            self.indexer.get_index("patients", patient)

        # Nurses
        self.nurses = np.array([], dtype=Nurse)
        for nurse_dict in json_data["nurses"]:
            nurse_dict["shift_types"] = self.shift_types
            nurse = Nurse(days=self.days, **nurse_dict)
            self.nurses = np.append(self.nurses, nurse)
            self.indexer.get_index("nurses", nurse)

        # Create matrix for Patient Admission Scheduling (PAS) problem
        # Actually it also includes the Surgical Case Planning (SCP) problem
        self.pas_size = (
            self.days,
            len(self.rooms),
            len(self.patients),
            len(self.operating_theaters),
        )
        self.pas_matrix = np.zeros(self.pas_size, dtype=bool)
        # Create matrix for Nurse to Room Assignment (NRA) problem
        self.nra_size = (
            self.days * len(self.shift_types),
            len(self.rooms),
            len(self.nurses),
        )
        self.nra_matrix = np.zeros(self.nra_size, dtype=bool)

        # Add occupants to PAS matrix
        for occupant in self.occupants:
            occupant_index = self.indexer.reverse_lookup("occupants", occupant.id)
            room_index = self.indexer.reverse_lookup("rooms", occupant.room.id)
            coordinates = (
                np.arange(0, occupant.length_of_stay),
                room_index,
                occupant_index,
                0,
            )
            self.pas_matrix[coordinates] = True

    def print(self):
        """Print the current status of the hospital"""
        # Patient Admission Scheduling and Surgical Case Planning
        for p in np.argwhere(self.pas_matrix):
            for key, value in dict(
                zip(["day", "rooms", "patients", "operating_theaters"], p)
            ).items():
                if key == "day":
                    print(f"PAS: {key}: {value}", end=" ")
                else:
                    print(
                        f"PAS: {key}: {self.indexer.lookup(type=key, index=value).id}",
                        end=" ",
                    )
            print()

        # Nurse to Room Assignment
        for n in np.argwhere(self.nra_matrix):
            for key, value in dict(zip(["shift", "rooms", "nurses"], n)).items():
                if key == "shift":
                    print(f"NRA: {key}: {value}", end=" ")
                else:
                    print(
                        f"NRA: {key}: {self.indexer.lookup(type=key, index=value).id}",
                        end=" ",
                    )
            print()

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
        operating_theater: OperatingTheater = self.indexer.lookup(
            "operating_theaters", operating_theater_index
        )
        end_day = min(self.days, day + patient.length_of_stay)

        # Check if patient is already scheduled
        if self.pas_matrix[:, :, patient_index, :].any(axis=(0, 1, 2)):
            raise ValueError("Patient is already scheduled")

        # Global constraints
        # Constraint H6: Admission day
        admission_day_ok = day >= patient.surgery_release_day
        if patient.mandatory:
            admission_day_ok &= day <= patient.surgery_due_day
        if not admission_day_ok:
            raise ValueError("Patient cannot be scheduled on this day")

        # PAS constraints
        # Constraint H1: No gender mix
        # Mask of patients in the same room
        patients_same_room_mask = np.any(
            self.pas_matrix[day:end_day, room_index, :, :], axis=(0, 2)
        )
        # Check if all patients in the room have the same gender
        gender_fun = np.vectorize(lambda p: p.gender == patient.gender, otypes=[bool])
        gender_ok = gender_fun(self.patients[patients_same_room_mask]).all()
        # Constraint H2: Compatible rooms
        compatible_ok = room.id not in patient.incompatible_rooms
        # Constraint H7: Room capacity
        # Count distinct patients in the room for each day and check if the capacity is ever exceeded
        n_patients_same_room: int = (
            self.pas_matrix[day:end_day, room_index, :, :].any(axis=2).sum(axis=1)
        )
        capacity_ok = np.all(n_patients_same_room + 1 <= room.capacity)
        # Constraint H8: Room coverage
        # Check if the room is covered for all shifts by any nurse
        room_covered_ok = (
            self.nra_matrix[
                day * len(self.shift_types) : end_day * len(self.shift_types),
                room_index,
                :,
            ]
            .any(axis=1)
            .all()
        )

        if not gender_ok or not compatible_ok or not capacity_ok or not room_covered_ok:
            raise ValueError("Patient cannot be scheduled in this room")

        # SCP constraints (only patients need to be checked, not occupants)
        # Mask of patients admitted in the same day (same surgery day)
        patients_same_day_mask = self.pas_matrix[day, :, len(self.occupants) :, :].any(
            axis=(0, 2)
        )
        # Constraint H3: Surgeon overtime
        # Check if patients are operated by the same surgeon as the patient to be scheduled
        scp_fun = np.vectorize(
            lambda p: p.surgeon.id == surgeon.id if type(p) == Patient else False,
            otypes=[bool],
        )
        # For the patients admitted in the same day, check if the surgeon is the same as the patient to be scheduled
        patients_same_surgeon_mask = scp_fun(
            self.patients[len(self.occupants) :][patients_same_day_mask]
        )
        # Get duration of surgery for each patient
        duration_fun = np.vectorize(lambda p: p.surgery_duration, otypes=[int])
        # For the patients admitted in the same day and operated by the same surgeon, compute the total duration of surgery
        surgeries_duration: int = duration_fun(
            self.patients[len(self.occupants) :][patients_same_day_mask][
                patients_same_surgeon_mask
            ]
        ).sum()
        surgeon_overtime_ok = (
            surgeries_duration + patient.surgery_duration
            <= surgeon.max_surgery_time[day]
        )
        # Constraint H4: OT overtime
        # Mask of patients operated in the same operating theater
        patients_same_ot_mask = self.pas_matrix[
            day, :, len(self.occupants) :, operating_theater_index
        ].any(axis=0)
        # For the patients operated in the same operating theater, compute the total duration of surgery
        surgeries_duration = duration_fun(
            self.patients[len(self.occupants) :][patients_same_ot_mask]
        ).sum()
        ot_duration_ok = (
            surgeries_duration + patient.surgery_duration
            <= operating_theater.availability[day]
        )

        if not surgeon_overtime_ok or not ot_duration_ok:
            raise ValueError("Patient cannot be scheduled in this operating theater")

        self.pas_matrix[
            day:end_day, room_index, patient_index, operating_theater_index
        ] = True
        penalty, penalty_dict = self.compute_penalty()
        if not assign:
            self.pas_matrix[
                day:end_day, room_index, patient_index, operating_theater_index
            ] = False
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
        if not self.pas_matrix[:, :, patient_index, :].any(axis=(0, 1, 2)):
            raise ValueError("Patient is not scheduled")

        old_schedule = np.copy(self.pas_matrix[:, :, patient_index, :])
        self.pas_matrix[:, :, patient_index, :] = False
        penalty, penalty_dict = self.compute_penalty()
        if not assign:
            self.pas_matrix[:, :, patient_index, :] = old_schedule
        return penalty, penalty_dict

    def schedule_nurse(
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
        nurse = self.indexer.lookup("nurses", nurse_index)
        # Check if nurse is available
        if not nurse.is_available(shift):
            raise ValueError("Nurse is not available at this shift")

        # Check if a nurse is already assigned to the room
        if self.nra_matrix[shift, room_index, :].any():
            raise ValueError("Nurse is already assigned to the room")

        self.nra_matrix[shift, room_index, nurse_index] = True
        penalty, penalty_dict = self.compute_penalty()
        if not assign:
            self.nra_matrix[shift, room_index, nurse_index] = False
        return penalty, penalty_dict

    def unschedule_nurse(
        self, shift: int, room_index: int, nurse_index: int, assign: bool = False
    ) -> Tuple[int, Dict[str, int]]:
        """Unschedule a nurse

        Args:
            shift (int): index of the shift
            room_index (int): index of the room
            nurse_index (int): index of the nurse
            assign (bool, optional): if True, save the change. Defaults to False.

        Returns:
            Tuple[int, Dict[str, int]]: overall penalty and individual penalties
        """
        if not self.nra_matrix[shift, room_index, nurse_index]:
            raise ValueError("Nurse is not assigned to the room on this shift")

        if self.pas_matrix[shift // len(self.shift_types), room_index, :, :].any(
            axis=(0, 1)
        ):
            raise ValueError("Nurse is assigned to a patient")

        self.nra_matrix[shift, room_index, nurse_index] = False
        penalty, penalty_dict = self.compute_penalty()
        if not assign:
            self.nra_matrix[shift, room_index, nurse_index] = True
        return penalty, penalty_dict

    def compute_penalty(self) -> Tuple[int, Dict[str, int]]:
        """Compute the penalty of the current solution

        Returns:
            Tuple[int, Dict[str, int]]: overall penalty and individual penalties
        """
        # TODO: Check everything, compare to validation results
        penalty = 0
        penalty_dict = {}

        # Remove the operating theaters
        patients_scheduled_infos = np.any(self.pas_matrix, axis=-1)
        # Compute indexes of assigned patients, with respective rooms and days
        rooms, days, patients = np.nonzero(patients_scheduled_infos)

        # Constraint S1: Age group TODO
        # Get age of assigned patients given their indexes
        age_fun = np.vectorize(lambda p: p.age_group, otypes=[int])
        age = age_fun(self.patients[patients])
        # Compute minimum age of patients in each room and day
        age_distribution = np.zeros(patients_scheduled_infos.shape, dtype=int) + 3
        age_distribution[rooms, days, patients] = age
        min_age = age_distribution.min(axis=-1)
        # Compute maximum age of patients in each room and day
        age_distribution = np.zeros(patients_scheduled_infos.shape, dtype=int)
        age_distribution[rooms, days, patients] = age
        max_age = age_distribution.max(axis=-1)
        # Compute penalty for age group mix
        age_diff = max_age - min_age
        penalty_dict["S1"] = (
            age_diff[age_diff > 0].sum() * self.weights["room_mixed_age"]
        )
        penalty += age_diff[age_diff > 0].sum() * self.weights["room_mixed_age"]

        # Constraint S2: Minimum skill level
        skill_level_shape = (
            self.days * len(self.shift_types),
            len(self.rooms),
            len(self.patients),
        )
        # Compute required skill level for each day, room and patient
        required_skill_level = np.zeros(skill_level_shape, dtype=int)
        patient_day = patients_scheduled_infos.sum(axis=1) > 0
        patient_day_repeated = np.repeat(patient_day, len(self.shift_types), axis=0)
        patient_mask = patient_day.sum(axis=0) > 0
        for patient in self.patients[patient_mask]:
            patient_index = self.indexer.reverse_lookup("patients", patient.id)
            shift_mask = patient_day_repeated[:, patient_index]
            room_index = np.argmax(
                patients_scheduled_infos[:, :, patient_index].sum(axis=0) > 0
            )
            l = len(required_skill_level[shift_mask, room_index, patient_index])
            required_skill_level[shift_mask, room_index, patient_index] = (
                patient.skill_level_required[:l]
            )
        # Compute provided skill level for each day, room and patient
        provided_skill_level = np.zeros(skill_level_shape, dtype=int)
        shifts, rooms, nurses = np.nonzero(self.nra_matrix)
        skill_level_fun = np.vectorize(lambda n: n.skill_level, otypes=[int])
        nurses_skill_levels = skill_level_fun(self.nurses[nurses])
        nurses_skill_levels = nurses_skill_levels[:, np.newaxis].repeat(
            len(self.patients), axis=1
        )
        provided_skill_level[shifts, rooms, :] = nurses_skill_levels
        skill_level_difference = required_skill_level - provided_skill_level
        penalty_dict["S2"] = (
            skill_level_difference[skill_level_difference > 0].sum()
            * self.weights["room_nurse_skill"]
        )
        penalty += (
            skill_level_difference[skill_level_difference > 0].sum()
            * self.weights["room_nurse_skill"]
        )

        # Constraint S3: Continuity of care
        repeated_assigned_patients = np.repeat(
            patients_scheduled_infos, len(self.shift_types), axis=0
        )
        shifts, rooms, patients = np.nonzero(repeated_assigned_patients)
        idx, nurse = np.nonzero(self.nra_matrix[shifts, rooms])
        nurse_value = np.zeros(shifts.shape, dtype=int) - 1
        nurse_value[idx] = nurse
        na_size = (self.days * len(self.shift_types), len(self.patients))
        nurse_assignments = np.zeros(na_size, dtype=int) - 1
        nurse_assignments[shifts, patients] = nurse_value
        distinct_nurses = (
            np.apply_along_axis(lambda x: len(np.unique(x)), 1, nurse_assignments) - 1
        )
        penalty += distinct_nurses.sum() * self.weights["continuity_of_care"]
        penalty_dict["S3"] = distinct_nurses.sum() * self.weights["continuity_of_care"]

        # Constraint S4: Maximum workload
        workload_shape = (
            self.days * len(self.shift_types),
            len(self.rooms),
            len(self.patients),
        )
        # Compute workload for each day, room and patient
        required_workload_patient = np.zeros(workload_shape, dtype=int)
        for patient in self.patients[patient_mask]:
            patient_index = self.indexer.reverse_lookup("patients", patient.id)
            shift_mask = patient_day_repeated[:, patient_index]
            room_index = np.argmax(
                patients_scheduled_infos[:, :, patient_index].sum(axis=0) > 0
            )
            l = len(required_workload_patient[shift_mask, room_index, patient_index])
            required_workload_patient[shift_mask, room_index, patient_index] = (
                patient.workload_produced[:l]
            )
        required_workload_room = required_workload_patient.sum(axis=-1)
        # Compute provided workload for each day, room and patient
        provided_workload = np.zeros(required_workload_room.shape, dtype=int)
        shifts, rooms, nurses = np.nonzero(self.nra_matrix)
        workload_fun = np.vectorize(lambda n, s: n.maximum_workload(s), otypes=[int])
        provided_workload[shifts, rooms] = workload_fun(self.nurses[nurses], shifts)
        workload_difference = required_workload_room - provided_workload
        penalty += (
            workload_difference[workload_difference > 0].sum()
            * self.weights["nurse_eccessive_workload"]
        )
        penalty_dict["S4"] = (
            workload_difference[workload_difference > 0].sum()
            * self.weights["nurse_eccessive_workload"]
        )

        # Constraint S5: Open OT
        patients_on_day = patients_scheduled_infos.sum(axis=1) > 0
        # Get the admission day of the patients
        admission_day = np.argmax(patients_on_day, axis=0)
        admission_day[np.all(patients_on_day == False, axis=0)] = -1
        # Get the index of the operating theater of the patients
        patient_ot = (
            self.pas_matrix[admission_day, :, np.arange(len(self.patients)), :]
            .sum(axis=1)
            .argmax(axis=1)
        )
        patient_ot[np.all(patients_on_day == False, axis=0)] = -1
        # Compute the number of patients per operating theater per day
        ot_patients = np.zeros((self.days, len(self.operating_theaters)), dtype=int)
        for day, ot in zip(admission_day, patient_ot):
            if day != -1 and ot != -1:
                ot_patients[day, ot] += 1
        ot_open = ot_patients[:, 1:]
        penalty += ot_open.sum() * self.weights["open_operating_theater"]
        penalty_dict["S5"] = ot_open.sum() * self.weights["open_operating_theater"]

        # Constraint S6: Surgeon transfer
        surgeon_fun = np.vectorize(
            lambda p: self.indexer.reverse_lookup("surgeons", p.surgeon.id),
            otypes=[int],
        )
        surgeon_id = surgeon_fun(self.patients[len(self.occupants) :])
        true_patient_ot = patient_ot[len(self.occupants) :]
        true_admission_day = admission_day[len(self.occupants) :]
        surgeon_ots_day = defaultdict(set)
        tmp = 0
        for surgeon, ot, day in zip(surgeon_id, true_patient_ot, true_admission_day):
            if ot != -1 and day != -1:
                if (ot, day) not in surgeon_ots_day[surgeon]:
                    tmp += self.weights["surgeon_transfer"]
                    surgeon_ots_day[surgeon].add((ot, day))
                    penalty += self.weights["surgeon_transfer"]
                    surgeon_ots_day[surgeon].add((ot, day))
        penalty_dict["S6"] = tmp

        # Constraint S7: Admission delay
        release_fun = np.vectorize(lambda p: p.surgery_release_day, otypes=[int])
        release_day = release_fun(self.patients[len(self.occupants) :])
        delay = (
            true_admission_day[true_admission_day >= 0]
            - release_day[true_admission_day >= 0]
        )
        penalty += delay.sum() * self.weights["patient_delay"]
        penalty_dict["S7"] = delay.sum() * self.weights["patient_delay"]

        # Constraint S8: Unscheduled patients
        penalty += (
            np.sum(~np.any(self.pas_matrix, axis=(0, 1, 3)))
            * self.weights["unscheduled_optional"]
        )
        penalty_dict["S8"] = (
            np.sum(~np.any(self.pas_matrix, axis=(0, 1, 3)))
            * self.weights["unscheduled_optional"]
        )

        return penalty, penalty_dict

    def save_status(self):
        """Save the current status as the best status found so far"""
        self.best_patients = copy.deepcopy(self.patients)
        self.best_nurses = copy.deepcopy(self.nurses)
        self.best_nra_matrix = np.copy(self.nra_matrix)
        self.best_pas_matrix = np.copy(self.pas_matrix)

    def load_status(self):
        """Load the best status found so far"""
        self.patients = np.copy(self.best_patients)
        self.nurses = np.copy(self.best_nurses)
        self.nra_matrix = np.copy(self.best_nra_matrix)
        self.pas_matrix = np.copy(self.best_pas_matrix)

    def apply_action(
        self, action: NeighboringAction, n, assign: bool = False
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

                print(
                    f"Patient {patient.id} scheduled on day {action.day} in room {room_id} and OT {ot_id}"
                )

        if isinstance(action, PASActionUnschedule):
            penalty, penalty_dict = self.unschedule_patient(action.patient, assign)
            if assign:
                patient: Patient = self.patients[action.patient]
                patient.unset_assignment()

                print(f"Patient {patient.id} unscheduled")

        if isinstance(action, NRAActionSchedule):
            penalty, penalty_dict = self.schedule_nurse(
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

                print(
                    f"Nurse {nurse.id} scheduled on shift {action.shift} in room {room_id}"
                )

        if isinstance(action, NRAActionUnschedule):
            penalty, penalty_dict = self.unschedule_nurse(
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

                print(
                    f"Nurse {nurse.id} unscheduled on shift {action.shift} in room {room_id}"
                )

        if assign:
            print(f"\tPenalty: {penalty}, penalties: {penalty_dict}", end="\n\n")

        return penalty, penalty_dict

    def generate_patients_moves(self) -> List[NeighboringAction]:
        """Generate all possible neighboring moves for the patients

        Returns:
            List[NeighboringAction]: list of possible moves
        """
        moves = []
        # Mask of unscheduled patients
        patients_unscheduled_mask = ~self.pas_matrix[
            :, :, len(self.occupants) :, :
        ].any(axis=(0, 1, 3))
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
            if np.any(self.pas_matrix[:, :, patient_index, :]):
                moves.append(PASActionUnschedule(patient_index))
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
            shifts, rooms = np.nonzero(self.nra_matrix[:, :, nurse_index])
            forbidden_actions = {(s, r) for s, r in zip(shifts, rooms)}
            # Unschedule actions based on the current state
            for shift_index, room_index in zip(shifts, rooms):
                unschedule_move = NRAActionUnschedule(
                    shift_index, room_index, nurse_index
                )
                moves.append(unschedule_move)
            # Schedule actions based on the forbidden actions
            for shift in nurse.working_shifts.values():
                for room_index, _ in enumerate(self.rooms):
                    if (shift.index, room_index) in forbidden_actions:
                        continue
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

    def json_dump(self, filename: str):
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
