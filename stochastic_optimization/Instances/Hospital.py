import json
from collections import defaultdict
import numpy as np


class Indexer:
    def __init__(self):
        self.types = defaultdict(lambda: 0)
        self.indexer = defaultdict(lambda: {})
        self.reverse_indexer = defaultdict(lambda: {})

    def get_index(self, type, obj):
        if type == "occupant":
            type = "patient"
        index = self.types[type]
        self.types[type] += 1
        self.indexer[type][index] = obj
        self.reverse_indexer[type][obj.id] = index
        return index

    def lookup(self, type, index):
        return self.indexer[type][index]

    def reverse_lookup(self, type, id):
        return self.reverse_indexer[type][id]

    def id_lookup(self, type, id):
        return self.lookup(type, self.reverse_lookup(type, id))


class Room:
    def __init__(self, id, capacity):
        self.id = id
        self.capacity = capacity

    def __str__(self):
        return f"Room {self.id}"


class OperatingTheater:
    def __init__(self, id, availability):
        self.id = id
        self.availability = availability

    def __str__(self):
        return f"OperatingTheater {self.id}"


class Occupant:
    def __init__(self, id, gender, age_group, length_of_stay, workload_produced, skill_level_required, room):
        self.id = id
        self.gender = gender
        self.age_group = age_group
        self.length_of_stay = length_of_stay
        self.workload_produced = workload_produced
        self.skill_level_required = skill_level_required
        self.room = room

    def __str__(self):
        return f"Occupant {self.id}"


class Surgeon:
    def __init__(self, id, max_surgery_time):
        self.id = id
        self.max_surgery_time = max_surgery_time

    def __str__(self):
        return f"Surgeon {self.id}"


class Patient(Occupant):
    def __init__(self, id, mandatory, gender, age_group, length_of_stay, surgery_release_day, surgery_duration, surgeon, incompatible_rooms, workload_produced, skill_level_required, surgery_due_day=None):
        super().__init__(id, gender, age_group, length_of_stay,
                         workload_produced, skill_level_required, None)
        self.mandatory = mandatory
        self.surgery_release_day = surgery_release_day
        self.surgery_duration = surgery_duration
        self.surgeon = surgeon
        self.incompatible_rooms = incompatible_rooms
        self.surgery_due_day = surgery_due_day

    def __str__(self):
        return f"Patient {self.id}"


class WorkingShift:
    def __init__(self, day, shift, max_load, shift_types):
        self.day = day
        self.shift = shift
        self.max_load = max_load
        for i, s in enumerate(shift_types):
            if shift == s:
                break
        self.index = day * len(shift_types) + i

    def __str__(self):
        return f"Shift {self.day} {self.shift} {self.max_load}"


class Nurse:
    def __init__(self, id, skill_level, working_shifts, shift_types, days):
        self.id = id
        self.skill_level = skill_level
        self.working_shifts = []
        self.available = np.zeros(days * len(shift_types), dtype=bool)
        for w in working_shifts:
            w["shift_types"] = shift_types
            w_obj = WorkingShift(**w)
            self.working_shifts.append(w_obj)
            self.available[w_obj.index] = True

    def is_available(self, shift_index):
        return self.available[shift_index]

    def __str__(self):
        return f"Nurse {self.id}"


class Hospital:
    def __init__(self, fp):
        self.indexer = Indexer()
        json_data = json.load(fp)

        self.days = json_data["days"]
        self.skill_levels = json_data["skill_levels"]
        self.shift_types = json_data["shift_types"]
        self.age_groups = json_data["age_groups"]
        self.weights = json_data['weights']

        self.occupants = []
        self.patients = []
        self.surgeons = []
        self.operating_theaters = []
        self.rooms = []
        self.nurses = []

        for room_dict in json_data["rooms"]:
            room = Room(**room_dict)
            self.rooms.append(room)
            self.indexer.get_index("rooms", room)
        self.rooms = np.array(self.rooms)
        for operating_theater_dict in json_data["operating_theaters"]:
            operating_theater = OperatingTheater(**operating_theater_dict)
            self.operating_theaters.append(operating_theater)
            self.indexer.get_index("operating_theaters", operating_theater)
        self.operating_theaters = np.array(self.operating_theaters)
        for occupant_dict in json_data["occupants"]:
            room_id = occupant_dict.pop("room_id")
            room = self.indexer.id_lookup("rooms", room_id)
            occupant = Occupant(room=room, **occupant_dict)
            self.occupants.append(occupant)
            self.indexer.get_index("occupants", occupant)
        for surgeon_dict in json_data["surgeons"]:
            surgeon = Surgeon(**surgeon_dict)
            self.surgeons.append(surgeon)
            self.indexer.get_index("surgeons", surgeon)
        self.surgeons = np.array(self.surgeons)
        for patient_dict in json_data["patients"]:
            surgeon_id = patient_dict.pop('surgeon_id')
            surgeon = self.indexer.id_lookup("surgeons", surgeon_id)
            incompatible_room_ids = patient_dict.pop('incompatible_room_ids')
            incompatible_rooms = [self.indexer.id_lookup(
                "rooms", i) for i in incompatible_room_ids]
            patient = Patient(
                surgeon=surgeon, incompatible_rooms=incompatible_rooms, **patient_dict)
            self.patients.append(patient)
            self.indexer.get_index("patients", patient)
        self.patients = np.array(self.occupants + self.patients)
        for nurse_dict in json_data["nurses"]:
            nurse_dict["shift_types"] = self.shift_types
            nurse = Nurse(**nurse_dict)
            self.nurses.append(nurse)
            self.indexer.get_index("nurses", nurse)
        self.nurses = np.array(self.nurses)

        # Create matrix for Patient Admission Scheduling (PAS) problem
        # Actually it also includes the Surgical Case Planning (SCP) problem
        self.pas_size = (self.days, len(self.rooms), len(
            self.patients) + len(self.occupants), len(self.operating_theaters))
        self.pas_matrix = np.zeros(self.pas_size, dtype=bool)
        # Create matrix for Nurse to Room Assignment (NRA) problem
        self.nra_size = (self.days * len(self.shift_types),
                         len(self.rooms), len(self.nurses))
        self.nra_matrix = np.zeros(self.nra_size, dtype=bool)

        # Add occupants to PAS matrix
        for patient in self.occupants:
            patient_index = self.indexer.reverse_lookup(
                "occupants", patient.id)
            room_index = self.indexer.reverse_lookup("rooms", patient.room.id)
            coordinates = (np.arange(0, patient.length_of_stay),
                           room_index, patient_index)
            self.pas_matrix[coordinates] = True

    def schedule_patient(self, day, room_index, patient_index, operating_theater_index, assign=False):
        room = self.indexer.lookup("rooms", room_index)
        patient = self.indexer.lookup("patients", patient_index)
        surgeon = patient.surgeon
        operating_theater = self.indexer.lookup(
            "operating_theaters", operating_theater_index)

        end_day = min(self.days, day + patient.length_of_stay)

        if not isinstance(patient, Patient):
            raise ValueError("Only patients can be scheduled")

        # Global constraints
        # Constraint H6: Admission day
        admission_day_ok = day >= patient.surgery_release_day
        if patient.mandatory:
            admission_day_ok &= (day <= patient.surgery_due_day)
        if not admission_day_ok:
            raise ValueError("Patient cannot be scheduled on this day")
        # If patient is already scheduled, remove from PAS matrix
        self.pas_matrix[:, :, patient_index, operating_theater_index] = False

        # PAS constraints
        # Constraint H1: No gender mix
        patients_same_room = np.any(
            self.pas_matrix[day:end_day, room_index, :, :], axis=0)
        gender_ok = np.apply_along_axis(lambda x: x.gender == patient.gender,
                                        0, self.patients[patients_same_room]).all()
        # Constraint H2: Compatible rooms
        compatible_ok = room.id not in patient.incompatible_rooms
        # Constraint H7: Room capacity
        n_patients_in_room = self.pas_matrix[day:end_day, room_index, :, :].sum(
            axis=1)
        capacity_ok = np.all(n_patients_in_room <= room.capacity)
        if not gender_ok or not compatible_ok or not capacity_ok:
            raise ValueError("Patient cannot be scheduled in this room")

        # SCP constraints
        patients_on_day = self.patients[self.pas_matrix[day, :, :, :].any(axis=1)]
        # Constraint H5: Surgeon overtime
        surgeon_patients = np.apply_along_axis(
            lambda x: x.surgeon.id == surgeon.id, 0, patients_on_day)
        scheduled_duration = np.apply_along_axis(
            lambda x: x.surgery_duration, 0, self.patients[surgeon_patients]).sum()
        surgeon_overtime_ok = scheduled_duration + patient.surgery_duration <= surgeon.max_surgery_time[day]
        # Constraint H4: OT overtime
        ot_patients = self.pas_matrix[day, :, patients_on_day, operating_theater_index]
        ot_duration = np.apply_along_axis(
            lambda x: x.surgery_duration, 0, self.patients[ot_patients]).sum()
        ot_duration_ok = ot_duration + patient.surgery_duration <= operating_theater.availability[day]

        if not surgeon_overtime_ok or not ot_duration_ok:
            raise ValueError("Patient cannot be scheduled in this operating theater")

        if assign:
            self.pas_matrix[day:end_day, room_index, patient_index, operating_theater_index] = True
        # TODO: Return the loss upon scheduling

    def schedule_nurse(self, shift, room_index, nurse_index, assign=False):
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

    def unschedule_nurse(self, shift, room_index, nurse_index):
        # TODO: Consider adding checks on the fact that nurse is assigned to the room in that shift
        self.nra_matrix[shift, room_index, nurse_index] = False
        # TODO: Return the loss upon scheduling
