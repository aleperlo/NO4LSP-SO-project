import json


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


class Patient:
    def __init__(self, id, mandatory, gender, age_group, length_of_stay, surgery_release_day, surgery_duration, surgeon, incompatible_rooms, workload_produced, skill_level_required, surgery_due_day=None):
        self.id = id
        self.mandatory = mandatory
        self.gender = gender
        self.age_group = age_group
        self.length_of_stay = length_of_stay
        self.surgery_release_day = surgery_release_day
        self.surgery_duration = surgery_duration
        self.surgeon = surgeon
        self.incompatible_rooms = incompatible_rooms
        self.workload_produced = workload_produced
        self.skill_level_required = skill_level_required
        self.surgery_due_day = surgery_due_day
    
    def __str__(self):
        return f"Patient {self.id}"


class WorkingShift:
    def __init__(self, day, shift, max_load):
        self.day = day
        self.shift = shift
        self.max_load = max_load

    def __str__(self):
        return f"Shift {self.day} {self.shift} {self.max_load}"


class Nurse:
    def __init__(self, id, skill_level, working_shifts):
        self.id = id
        self.skill_level = skill_level
        self.working_shifts = [WorkingShift(**w) for w in working_shifts]
    
    def __str__(self):
        return f"Nurse {self.id}"


class Hospital:
    def __init__(self, fp):
        json_data = json.load(fp)

        self.days = json_data["days"]
        self.skill_levels = json_data["skill_levels"]
        self.shift_types = json_data["shift_types"]
        self.age_groups = json_data["age_groups"]
        self.weights = json_data['weights']

        self.occupants = {}
        self.patients = {}
        self.surgeons = {}
        self.operating_theaters = {}
        self.rooms = {}
        self.nurses = {}

        for room_dict in json_data["rooms"]:
            room = Room(**room_dict)
            self.rooms[room.id] = room
        for operating_theater_dict in json_data["operating_theaters"]:
            operating_theater = OperatingTheater(**operating_theater_dict)
            self.operating_theaters[operating_theater.id] = operating_theater
        for occupant_dict in json_data["occupants"]:
            room_id = occupant_dict.pop("room_id")
            room = self.rooms[room_id]
            occupant = Occupant(room=room, **occupant_dict)
            self.occupants[occupant.id] = occupant
        for surgeon_dict in json_data["surgeons"]:
            surgeon = Surgeon(**surgeon_dict)
            self.surgeons[surgeon.id] = surgeon
        for patient_dict in json_data["patients"]:
            surgeon_id = patient_dict.pop('surgeon_id')
            surgeon = self.surgeons[surgeon_id]
            incompatible_room_ids = patient_dict.pop('incompatible_room_ids')
            incompatible_rooms = [self.rooms[i] for i in incompatible_room_ids]
            patient = Patient(
                surgeon=surgeon, incompatible_rooms=incompatible_rooms, **patient_dict)
            self.patients[patient.id] = patient
        for nurse_dict in json_data["nurses"]:
            nurse = Nurse(**nurse_dict)
            self.nurses[nurse.id] = nurse
