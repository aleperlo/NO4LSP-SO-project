import json
from collections import defaultdict
from typing import List, Literal, Union
import numpy as np


class Room:
    def __init__(self, id: str, capacity: int):
        self.id = id
        self.capacity = capacity

    def __str__(self):
        return f"Room {self.id}"


class OperatingTheater:
    def __init__(self, id: str, availability: List[int]):
        self.id = id
        self.availability = availability

    def __str__(self):
        return f"OperatingTheater {self.id}"


class Surgeon:
    def __init__(self, id: str, max_surgery_time: List[int]):
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
    ):
        self.id = id
        self.gender = gender
        self.age_group = age_group
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
    ):
        super().__init__(
            id,
            gender,
            age_group,
            length_of_stay,
            workload_produced,
            skill_level_required,
            None,
        )
        self.mandatory = mandatory
        self.surgery_release_day = surgery_release_day
        self.surgery_duration = surgery_duration
        self.surgeon = surgeon
        self.incompatible_rooms = incompatible_rooms
        self.surgery_due_day = surgery_due_day

    def __str__(self):
        return f"Patient {self.id}"


class WorkingShift:
    def __init__(self, day: int, shift: str, max_load: int, shift_types: List[str]):
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
        self.id = id
        self.skill_level = skill_level
        self.working_shifts: List[WorkingShift] = []
        self.available = np.zeros(days * len(shift_types), dtype=bool)
        for w in working_shifts:
            w["shift_types"] = shift_types
            w_obj = WorkingShift(**w)
            self.working_shifts.append(w_obj)
            self.available[w_obj.index] = True

    def is_available(self, shift_index: int):
        return self.available[shift_index]

    def __str__(self):
        return f"Nurse {self.id}"


class Indexer:
    def __init__(self):
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
    ):
        if type == "occupant":
            type = "patient"
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
    ):
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
    ):
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
    ):
        return self.lookup(type, self.reverse_lookup(type, id))


class Hospital:
    def __init__(self, fp):
        self.indexer = Indexer()
        json_data: dict[str, Union[int, str, dict]] = json.load(fp)

        self.days: int = json_data["days"]
        self.skill_levels: int = json_data["skill_levels"]
        self.shift_types: List[str] = json_data["shift_types"]
        self.age_groups: List[str] = json_data["age_groups"]
        self.weights: dict[str, int] = json_data["weights"]

        self.occupants = np.array([], dtype=Occupant)
        self.patients = np.array([], dtype=Patient)
        self.surgeons = np.array([], dtype=Surgeon)
        self.operating_theaters = np.array([], dtype=OperatingTheater)
        self.rooms = np.array([], dtype=Room)
        self.nurses = np.array([], dtype=Nurse)

        for room_dict in json_data["rooms"]:
            room = Room(**room_dict)
            np.append(self.rooms, room)
            self.indexer.get_index("rooms", room)
        for operating_theater_dict in json_data["operating_theaters"]:
            operating_theater = OperatingTheater(**operating_theater_dict)
            np.append(self.operating_theaters, operating_theater)
            self.indexer.get_index("operating_theaters", operating_theater)
        for occupant_dict in json_data["occupants"]:
            room_id: str = occupant_dict.pop("room_id")
            room = self.indexer.id_lookup("rooms", room_id)
            occupant = Occupant(room=room, **occupant_dict)
            np.append(self.occupants, occupant)
            self.indexer.get_index("occupants", occupant)
        for surgeon_dict in json_data["surgeons"]:
            surgeon = Surgeon(**surgeon_dict)
            np.append(self.surgeons, surgeon)
            self.indexer.get_index("surgeons", surgeon)
        for patient_dict in json_data["patients"]:
            surgeon_id = patient_dict.pop("surgeon_id")
            surgeon = self.indexer.id_lookup("surgeons", surgeon_id)
            incompatible_room_ids = patient_dict.pop("incompatible_room_ids")
            incompatible_rooms = [
                self.indexer.id_lookup("rooms", i) for i in incompatible_room_ids
            ]
            patient = Patient(
                surgeon=surgeon, incompatible_rooms=incompatible_rooms, **patient_dict
            )
            np.append(self.patients, patient)
            self.indexer.get_index("patients", patient)
        self.patients = np.append(self.patients, self.occupants)
        for nurse_dict in json_data["nurses"]:
            nurse_dict["shift_types"] = self.shift_types
            nurse = Nurse(days=self.days, **nurse_dict)
            np.append(self.nurses, nurse)
            self.indexer.get_index("nurses", nurse)

        # Create matrix for Patient Admission Scheduling (PAS) problem
        # Actually it also includes the Surgical Case Planning (SCP) problem
        self.pas_size = (
            self.days,
            len(self.rooms),
            len(self.patients) + len(self.occupants),
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
        for patient in self.occupants:
            patient_index = self.indexer.reverse_lookup("occupants", patient.id)
            room_index = self.indexer.reverse_lookup("rooms", patient.room.id)
            coordinates = (
                np.arange(0, patient.length_of_stay),
                room_index,
                patient_index,
            )
            self.pas_matrix[coordinates] = True

    def schedule_patient(
        self,
        day: int,
        room_index: int,
        patient_index: int,
        operating_theater_index: int,
        assign: bool = False,
    ):
        room = self.indexer.lookup("rooms", room_index)
        patient = self.indexer.lookup("patients", patient_index)
        surgeon = patient.surgeon
        operating_theater = self.indexer.lookup(
            "operating_theaters", operating_theater_index
        )

        end_day = min(self.days, day + patient.length_of_stay)

        if not isinstance(patient, Patient):
            raise ValueError("Only patients can be scheduled")

        # Global constraints
        # Constraint H6: Admission day
        admission_day_ok = day >= patient.surgery_release_day
        if patient.mandatory:
            admission_day_ok &= day <= patient.surgery_due_day
        if not admission_day_ok:
            raise ValueError("Patient cannot be scheduled on this day")
        # If patient is already scheduled, remove from PAS matrix
        self.pas_matrix[:, :, patient_index, operating_theater_index] = False

        # PAS constraints
        # Constraint H1: No gender mix
        patients_same_room = np.any(
            self.pas_matrix[day:end_day, room_index, :, :], axis=0
        )
        gender_ok = np.apply_along_axis(
            lambda x: x.gender == patient.gender, 0, self.patients[patients_same_room]
        ).all()
        # Constraint H2: Compatible rooms
        compatible_ok = room.id not in patient.incompatible_rooms
        # Constraint H7: Room capacity
        n_patients_in_room: int = self.pas_matrix[day:end_day, room_index, :, :].sum(
            axis=1
        )
        capacity_ok = np.all(n_patients_in_room <= room.capacity)
        if not gender_ok or not compatible_ok or not capacity_ok:
            raise ValueError("Patient cannot be scheduled in this room")

        # SCP constraints
        patients_on_day = self.patients[self.pas_matrix[day, :, :, :].any(axis=1)]
        # Constraint H5: Surgeon overtime
        surgeon_patients = np.apply_along_axis(
            lambda x: x.surgeon.id == surgeon.id, 0, patients_on_day
        )
        scheduled_duration = np.apply_along_axis(
            lambda x: x.surgery_duration, 0, self.patients[surgeon_patients]
        ).sum()
        surgeon_overtime_ok = (
            scheduled_duration + patient.surgery_duration
            <= surgeon.max_surgery_time[day]
        )
        # Constraint H4: OT overtime
        ot_patients = self.pas_matrix[day, :, patients_on_day, operating_theater_index]
        ot_duration = np.apply_along_axis(
            lambda x: x.surgery_duration, 0, self.patients[ot_patients]
        ).sum()
        ot_duration_ok = (
            ot_duration + patient.surgery_duration
            <= operating_theater.availability[day]
        )

        if not surgeon_overtime_ok or not ot_duration_ok:
            raise ValueError("Patient cannot be scheduled in this operating theater")

        if assign:
            self.pas_matrix[
                day:end_day, room_index, patient_index, operating_theater_index
            ] = True
        # TODO: Return the loss upon scheduling

    def schedule_nurse(
        self, shift: int, room_index: int, nurse_index: int, assign: bool = False
    ):
        nurse = self.indexer.lookup("nurses", nurse_index)

        # Check if no nurse is assigned to the room
        room_ok = not self.nra_matrix[shift, room_index, :].any()
        if not room_ok:
            raise ValueError("Room is already assigned to a nurse")
        # Check if nurse is available
        if not nurse.is_available(shift):
            raise ValueError("Nurse is not available at this shift")

        if assign:
            self.nra_matrix[shift, room_index, nurse_index] = True
        # TODO: Return the loss upon scheduling

    def unschedule_nurse(self, shift: int, room_index: int, nurse_index: int):
        # TODO: Consider adding checks on the fact that nurse is assigned to the room in that shift
        self.nra_matrix[shift, room_index, nurse_index] = False
        # TODO: Return the loss upon scheduling
