import json
from collections import defaultdict
from typing import List, Literal, Union
import numpy as np
import pprint


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
        age_groups = ["child", "adult", "elderly"]
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
        self.working_shifts = {}
        self.available = np.zeros(days * len(shift_types), dtype=bool)
        for w in working_shifts:
            w["shift_types"] = shift_types
            w_obj = WorkingShift(**w)
            self.working_shifts[w_obj.index] = w_obj
            self.available[w_obj.index] = True

    def is_available(self, shift_index: int):
        return self.available[shift_index]

    def maximum_workload(self, shift_index: int):
        return self.working_shifts[shift_index].max_load

    def __str__(self):
        return f"Nurse {self.id}"


class Indexer:
    def __init__(self):
        self.types: defaultdict[str, int] = defaultdict(lambda: 0)
        self.indexer: defaultdict[
            str,
            dict[int, Union[Patient, Occupant, Surgeon,
                            Nurse, OperatingTheater, Room]],
        ] = defaultdict(lambda: {})
        self.reverse_indexer: defaultdict[str,
                                          dict[str, int]] = defaultdict(lambda: {})

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
    ):
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
    ):
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
    ):
        return self.lookup(type, self.reverse_lookup(type, id))


class NeighboringAction:
    def __init__(self):
        pass


class PASAction(NeighboringAction):
    def __init__(self, day, room, patient, ot):
        self.day = day
        self.room = room
        self.patient = patient
        self.ot = ot

    def __eq__(self, value):
        if not isinstance(value, PASAction):
            return False
        return self.day == value.day and self.room == value.room and self.patient == value.patient and self.ot == value.ot


class NRAActionSchedule(NeighboringAction):
    def __init__(self, shift, room, nurse):
        self.shift = shift
        self.room = room
        self.nurse = nurse

    def __eq__(self, value):
        if not isinstance(value, NRAActionSchedule):
            return False
        return self.shift == value.shift and self.room == value.room and self.nurse == value.nurse

class NRAActionUnschedule(NeighboringAction):
    def __init__(self, shift, room, nurse):
        self.shift = shift
        self.room = room
        self.nurse = nurse

    def __eq__(self, value):
        if not isinstance(value, NRAActionUnschedule):
            return False
        return self.shift == value.shift and self.room == value.room and self.nurse == value.nurse


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
            self.rooms = np.append(self.rooms, room)
            self.indexer.get_index("rooms", room)
        # inserting dummy ot
        self.operating_theaters = np.append(
            self.operating_theaters, OperatingTheater("dummy", [0] * self.days)
        )
        self.indexer.get_index("operating_theaters",
                               self.operating_theaters[-1])
        for operating_theater_dict in json_data["operating_theaters"]:
            operating_theater = OperatingTheater(**operating_theater_dict)
            self.operating_theaters = np.append(
                self.operating_theaters, operating_theater
            )
            self.indexer.get_index("operating_theaters", operating_theater)
        for occupant_dict in json_data["occupants"]:
            room_id: str = occupant_dict.pop("room_id")
            room = self.indexer.id_lookup("rooms", room_id)
            occupant = Occupant(room=room, **occupant_dict)
            self.occupants = np.append(self.occupants, occupant)
            self.indexer.get_index("occupants", occupant)
        for surgeon_dict in json_data["surgeons"]:
            surgeon = Surgeon(**surgeon_dict)
            self.surgeons = np.append(self.surgeons, surgeon)
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
            self.patients = np.append(self.patients, patient)
            self.indexer.get_index("patients", patient)
        self.patients = np.append(self.occupants, self.patients)
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
        for patient in self.occupants:
            patient_index = self.indexer.reverse_lookup(
                "occupants", patient.id)
            room_index = self.indexer.reverse_lookup("rooms", patient.room.id)
            coordinates = (
                np.arange(0, patient.length_of_stay),
                room_index,
                patient_index,
                0,
            )
            self.pas_matrix[coordinates] = True

    def print(self):
        pprint.pprint(
            sorted(
                [
                    dict(zip(["day", "room", "patient", "ot"], pt))
                    for pt in np.argwhere(self.pas_matrix)
                ],
                key=lambda pt: pt["day"],
            )
        )
        pprint.pprint(
            sorted(
                [
                    dict(zip(["shift", "room", "nurse"], ne))
                    for ne in np.argwhere(self.nra_matrix)
                ],
                key=lambda ne: ne["shift"],
            )
        )

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
            self.pas_matrix[day:end_day, room_index, :, :], axis=(0, 2)
        )
        gender_fun = np.vectorize(
            lambda p: p.gender == patient.gender, otypes=[bool])
        gender_ok = gender_fun(self.patients[patients_same_room]).all()
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
        patients_on_day = self.pas_matrix[day, :, len(
            self.occupants):, :].any(axis=(0, 2))  # mask
        # Constraint H3: Surgeon overtime
        scp_fun = np.vectorize(
            lambda p: p.surgeon.id == surgeon.id if type(
                p) == Patient else False,
            otypes=[bool],
        )  # -> bool
        surgeon_patients = scp_fun(
            self.patients[len(self.occupants):][patients_on_day])  # mask
        duration_fun = np.vectorize(
            lambda p: p.surgery_duration, otypes=[int]
        )  # -> number
        scheduled_duration = duration_fun(
            self.patients[len(self.occupants):][patients_on_day][surgeon_patients]
        ).sum()  # number
        surgeon_overtime_ok = (
            scheduled_duration + patient.surgery_duration
            <= surgeon.max_surgery_time[day]
        )
        # Constraint H4: OT overtime
        ot_patients = self.pas_matrix[day, :, len(
            self.occupants):, operating_theater_index].any(axis=0)
        ot_duration = duration_fun(
            self.patients[len(self.occupants):][ot_patients]).sum()
        ot_duration_ok = (
            ot_duration + patient.surgery_duration
            <= operating_theater.availability[day]
        )

        if not surgeon_overtime_ok or not ot_duration_ok:
            raise ValueError(
                "Patient cannot be scheduled in this operating theater")

        self.pas_matrix[
            day:end_day, room_index, patient_index, operating_theater_index
        ] = True
        penalty = self.compute_penalty()
        if not assign:
            self.pas_matrix[
                day:end_day, room_index, patient_index, operating_theater_index
            ] = False
        return penalty

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

        self.nra_matrix[shift, room_index, nurse_index] = True
        penalty = self.compute_penalty()
        if not assign:
            self.nra_matrix[shift, room_index, nurse_index] = False
        return penalty

    def unschedule_nurse(self, shift: int, room_index: int, nurse_index: int, assign: bool = False):
        # TODO: Consider adding checks on the fact that nurse is assigned to the room in that shift
        self.nra_matrix[shift, room_index, nurse_index] = False
        penalty = self.compute_penalty()
        if not assign:
            self.nra_matrix[shift, room_index, nurse_index] = True
        return penalty

    def generate_initial_solution(self):
        mandatory_patients = []
        for patient in self.patients[len(self.occupants):]:
            if patient.mandatory:
                mandatory_patients.append(patient)
        for patient in mandatory_patients:
            for day in range(patient.surgery_release_day, patient.surgery_due_day + 1):
                for room_index, room in enumerate(self.rooms):
                    for ot_index, ot in enumerate(self.operating_theaters[1:]):
                        try:
                            self.schedule_patient(day, room_index, self.indexer.reverse_lookup(
                                "patients", patient.id), ot_index+1, assign=True)
                            print(
                                f"Patient {patient.id} scheduled on day {day} in room {room.id} and OT {ot.id}")
                        except ValueError as e:
                            pass

    def compute_penalty(self):
        penalty = 0

        assigned_patients = np.sum(self.pas_matrix, axis=-1) > 0
        # Compute indexes of assigned patients
        rooms, days, patients = np.nonzero(assigned_patients)

        # Constraint S1: Age group
        # Get age of assigned patients given their indexes
        age_fun = np.vectorize(lambda p: p.age_group, otypes=[int])
        age = age_fun(self.patients[patients])
        # Compute minimum age of patients in each room and day
        age_distribution = np.zeros(assigned_patients.shape, dtype=int) + 3
        age_distribution[rooms, days, patients] = age
        min_age = age_distribution.min(axis=-1)
        # Compute maximum age of patients in each room and day
        age_distribution = np.zeros(assigned_patients.shape, dtype=int)
        age_distribution[rooms, days, patients] = age
        max_age = age_distribution.max(axis=-1)
        # Compute penalty for age group mix
        age_diff = max_age - min_age
        penalty += age_diff[age_diff > 0].sum() * \
            self.weights["room_mixed_age"]

        # Constraint S2: Minimum skill level
        skill_level_shape = (self.days * len(self.shift_types),
                             len(self.rooms), len(self.patients))
        # Compute required skill level for each day, room and patient
        required_skill_level = np.zeros(skill_level_shape, dtype=int)
        patient_day = assigned_patients.sum(axis=1) > 0
        patient_day_repeated = np.repeat(
            patient_day, len(self.shift_types), axis=0)
        patient_mask = patient_day.sum(axis=0) > 0
        for patient in self.patients[patient_mask]:
            patient_index = self.indexer.reverse_lookup("patients", patient.id)
            shift_mask = patient_day_repeated[:, patient_index]
            room_index = np.argmax(
                assigned_patients[:, :, patient_index].sum(axis=0) > 0)
            required_skill_level[shift_mask, room_index,
                                 patient_index] = patient.skill_level_required
        # Compute provided skill level for each day, room and patient
        provided_skill_level = np.zeros(skill_level_shape, dtype=int)
        shifts, rooms, nurses = np.nonzero(self.nra_matrix)
        skill_level_fun = np.vectorize(lambda n: n.skill_level, otypes=[int])
        if len(nurses) > 0:
            provided_skill_level[shifts, rooms,
                                 :] = skill_level_fun(self.nurses[nurses])
            skill_level_difference = required_skill_level - provided_skill_level
            penalty += skill_level_difference[skill_level_difference >
                                              0].sum() * self.weights["room_nurse_skill"]

        # Constraint S3: Continuity of care
        repeated_assigned_patients = np.repeat(
            assigned_patients, len(self.shift_types), axis=0)
        shifts, rooms, patients = np.nonzero(repeated_assigned_patients)
        idx, nurse = np.nonzero(self.nra_matrix[shifts, rooms])
        nurse_value = np.zeros(shifts.shape, dtype=int) - 1
        nurse_value[idx] = nurse
        na_size = (self.days * len(self.shift_types), len(self.patients))
        nurse_assignments = np.zeros(na_size, dtype=int) - 1
        nurse_assignments[shifts, patients] = nurse_value
        distinct_nurses = np.apply_along_axis(
            lambda x: len(np.unique(x)), 1, nurse_assignments) - 1
        penalty += distinct_nurses.sum() * self.weights["continuity_of_care"]

        # Constraint S4: Maximum workload
        workload_shape = (self.days * len(self.shift_types),
                          len(self.rooms), len(self.patients))
        # Compute workload for each day, room and patient
        required_workload_patient = np.zeros(workload_shape, dtype=int)
        for patient in self.patients[patient_mask]:
            patient_index = self.indexer.reverse_lookup("patients", patient.id)
            shift_mask = patient_day_repeated[:, patient_index]
            room_index = np.argmax(
                assigned_patients[:, :, patient_index].sum(axis=0) > 0)
            required_workload_patient[shift_mask, room_index,
                                      patient_index] = patient.workload_produced
        required_workload_room = required_workload_patient.sum(axis=-1)
        # Compute provided workload for each day, room and patient
        provided_workload = np.zeros(required_workload_room.shape, dtype=int)
        shifts, rooms, nurses = np.nonzero(self.nra_matrix)
        workload_fun = np.vectorize(
            lambda n, s: n.maximum_workload(s), otypes=[int])
        provided_workload[shifts, rooms] = workload_fun(
            self.nurses[nurses], shifts)
        workload_difference = required_workload_room - provided_workload
        penalty += workload_difference[workload_difference >
                                       0].sum() * self.weights["nurse_eccessive_workload"]

        # Constraint S5: Open OT
        patients_on_day = assigned_patients.sum(axis=1) > 0
        # Get the admission day of the patients
        admission_day = np.argmax(patients_on_day, axis=0)
        admission_day[np.all(patients_on_day == False, axis=0)] = -1
        # Get the index of the operating theater of the patients
        patient_ot = self.pas_matrix[admission_day, :, np.arange(
            len(self.patients)), :].sum(axis=1).argmax(axis=1)
        patient_ot[np.all(patients_on_day == False, axis=0)] = -1
        # Compute the number of patients per operating theater per day
        ot_patients = np.zeros(
            (self.days, len(self.operating_theaters)), dtype=int)
        for day, ot in zip(admission_day, patient_ot):
            if day != -1 and ot != -1:
                ot_patients[day, ot] += 1
        ot_open = ot_patients[:, 1:]
        penalty += ot_open.sum() * self.weights["open_operating_theater"]

        # Constraint S6: Surgeon transfer
        surgeon_fun = np.vectorize(lambda p: self.indexer.reverse_lookup(
            "surgeons", p.surgeon.id), otypes=[int])
        surgeon_id = surgeon_fun(self.patients[len(self.occupants):])
        true_patient_ot = patient_ot[len(self.occupants):]
        true_admission_day = admission_day[len(self.occupants):]
        surgeon_ots_day = defaultdict(set)
        for surgeon, ot, day in zip(surgeon_id, true_patient_ot, true_admission_day):
            if ot != -1 and day != -1:
                if (ot, day) not in surgeon_ots_day[surgeon]:
                    penalty += self.weights["surgeon_transfer"]
                    surgeon_ots_day[surgeon].add((ot, day))

        # Constraint S7: Admission delay
        release_fun = np.vectorize(
            lambda p: p.surgery_release_day, otypes=[int])
        release_day = release_fun(self.patients[len(self.occupants):])
        delay = true_admission_day[true_admission_day >=
                                   0] - release_day[true_admission_day >= 0]
        penalty += delay.sum() * self.weights["patient_delay"]

        # Constraint S8: Unscheduled patients
        penalty += np.sum(~np.any(self.pas_matrix, axis=(0, 1, 3))
                          ) * self.weights["unscheduled_optional"]

        return penalty

    def apply_action(self, action, assign=False):
        if isinstance(action, PASAction):
            penalty = self.schedule_patient(action.day, action.room, action.patient, action.ot, assign)
        if isinstance(action, NRAActionSchedule):
            self.unschedule_nurse(action.shift, action.room, action.nurse, assign)
            penalty = self.schedule_nurse(action.shift, action.room, action.nurse, assign)
        if isinstance(action, NRAActionUnschedule):
            penalty = self.unschedule_nurse(action.shift, action.room, action.nurse, assign)
        return penalty
