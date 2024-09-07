import pandas as pd
from send_email import send_appointment_email  # Import the email function from send_email.py


timetable_df = pd.read_csv('doctor_timetable.csv')

def check_doctor_availability(doctor_id, doctor_name, specialization):
   
    available_slots = timetable_df[(timetable_df['Name'] == doctor_name) &
                                   (timetable_df['Specialization'] == specialization) &
                                   (timetable_df['DoctorID'] == doctor_id)]

    if not available_slots.empty:
        # If available, return the first available day and time slot
        return available_slots.iloc[0]['Day'], available_slots.iloc[0]['Time Slot']
    else:
        return None, None

def schedule_appointment(user_data, doctor_info):
    # Check the doctor's availability
    day, time_slot = check_doctor_availability(doctor_info['DoctorID'], doctor_info['Name'], doctor_info['Specialization'])
    
    if day and time_slot:
        # Doctor is available, schedule the appointment
        send_appointment_email(user_data, doctor_info['Name'], day, time_slot)
        print(f"Appointment scheduled with {doctor_info['Name']} on {day} at {time_slot}.")
    else:
        print(f"Doctor {doctor_info['Name']} is not available at the requested time.")
