import streamlit as st
import pandas as pd
import os
import uuid
from llama_integration import load_gpt2_model, predict_specialty_gpt2
from doctor_assignment import load_doctor_data, train_doctor_model, assign_doctor
from gp_finder import find_gp_by_postcode
from schedule_appointment import schedule_appointment

# Set page configuration (This must be the first Streamlit command)
st.set_page_config(page_title="GP Appointment Booking", page_icon=":robot_face:")

# CSS to style the chat interface
st.markdown("""
    <style>
    .user-message {
        background-color: #ffdddd;
        border-radius: 10px;
        padding: 10px;
        color: black;
        font-weight: bold;
        text-align: left;
        margin-bottom: 10px;
        margin-left: auto;
        margin-right: 0px;
        width: fit-content;
    }
    .ai-message {
        background-color: #ddffdd;
        border-radius: 10px;
        padding: 10px;
        color: black;
        font-weight: bold;
        text-align: left;
        margin-bottom: 10px;
        margin-left: 0px;
        margin-right: auto;
        width: fit-content;
    }
    .container-with-gif {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {
        "Appointment ID": None,
        "Name": None,
        "Email": None,
        "Address": None,
        "Postcode": None,
        "Phone": None,
        "Main Reason": None,
        "Questions": [],
        "Suggested Department": None,
        "Nearest GP": None,
        "Assigned Doctor": None
    }
if 'question_index' not in st.session_state:
    st.session_state['question_index'] = 0
if 'appointment_confirmed' not in st.session_state:
    st.session_state['appointment_confirmed'] = False

# Load the GPT-2 model and tokenizer for predicting the specialty
tokenizer, model = load_gpt2_model()


if tokenizer is None or model is None:
    st.error("Failed to load the language model. Please try again later.")
else:
   
    doctor_data = load_doctor_data("extended_doctors_second.csv")   # Load the doctor data and train the model 
    

    if doctor_data is not None:     # Check if doctor data is loaded correctly
        try:
            # Expecting five returned values now
            doctor_model, label_encoders, y_encoder, feature_names, scaler = train_doctor_model(doctor_data)
        except Exception as e:
            st.error(f"Failed to train the doctor model: {e}")
            st.stop()  # Stop execution if the model cannot be trained
    else:
        st.error("Failed to load doctor data.")
        st.stop()  # Stop execution if the doctor data cannot be loaded

    st.markdown("<h1 style='text-align: center; color: #333;'>Book Your GP Appointment</h1>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align: center; color: #333;'>Hello, I’m Cypheria, your personal health assistant. I’m here to help you book an appointment with us.</h6>", unsafe_allow_html=True)

    st.sidebar.image("Default_As_she_gazes_intently_at_her_patients_chart_the_sunlig_3.jpg", caption="PPAS", use_column_width=True)
    st.sidebar.markdown(
        """
        <div class="marquee-container">
            <span class="marquee-text">
                Welcome to our Clinic! Our General Practitioners are available for consultations to address a wide range of health concerns. Book an appointment today and let our team assist you with personalized medical advice.
            </span>
        </div>
        <h3> Precision Physician Allocation System</h3>
        """, 
        unsafe_allow_html=True
    )

    def ask_general_questions(reason):
        reason = reason.lower()
        if "cough" in reason:
            return ["How long have you had the cough?", "Is it a dry or wet cough?", "Do you have any difficulty breathing?"]
        elif "fever" in reason:
            return ["How high is your fever?", "Do you have any other symptoms like chills or body aches?"]
        elif "headache" in reason:
            return ["Where is the headache located?", "How severe is the headache on a scale of 1 to 10?", "Have you experienced nausea or dizziness?"]
        elif "stomach pain" in reason or "abdominal pain" in reason:
            return ["When did the stomach pain start?", "Is the pain constant or does it come and go?", "Have you had any changes in your bowel movements?"]
        elif "rash" in reason or "skin" in reason:
            return ["When did you first notice the rash?", "Is it itchy or painful?", "Have you tried any treatments?"]
        elif "back pain" in reason:
            return ["When did the back pain start?", "Is the pain related to any specific activity or injury?"]
        elif "eye pain" in reason or "vision" in reason:
            return ["How long have you had the eye pain?", "Have you noticed any changes in your vision?"]
        elif "ear pain" in reason or "hearing" in reason:
            return ["Which ear is affected?", "Have you experienced any hearing loss?"]
        elif "anxiety" in reason or "depression" in reason:
            return ["How long have you been feeling this way?", "Do you have any history of mental health issues?"]
        elif "chest pain" in reason:
            return ["When did the chest pain start?", "Does the pain spread to other parts of your body?", "Is the pain related to physical activity?"]
        elif "tooth pain" in reason or "dental pain" in reason:
            return ["How severe is the tooth pain?", "Have you seen a dentist recently?"]
        else:
            return ["Can you please describe your symptoms in more detail?"]

    def store_user_data():
        user_data = pd.DataFrame([st.session_state['user_data']])
        if not os.path.isfile('user_data.csv'):
            user_data.to_csv('user_data.csv', index=False)
        else:
            user_data.to_csv('user_data.csv', mode='a', header=False, index=False)

    def display_final_details():
        closest_gp_info = st.session_state['user_data']['Nearest GP']
        assigned_doctor = st.session_state['user_data'].get('Assigned Doctor', "N/A")

        if closest_gp_info:
            final_details = (
                f"**Appointment ID:** {st.session_state['user_data']['Appointment ID']}\n"
                f"**Name:** {st.session_state['user_data']['Name']}\n"
                f"**Email:** {st.session_state['user_data']['Email']}\n"
                f"**Address:** {st.session_state['user_data']['Address']}\n"
                f"**Postcode:** {st.session_state['user_data']['Postcode']}\n"
                f"**Phone:** {st.session_state['user_data']['Phone']}\n"
                f"**Suggested Department:** {st.session_state['user_data']['Suggested Department']}\n"
                f"**Nearest GP:** {closest_gp_info['Name']} at {closest_gp_info['Address']}\n"
            )
        else:
            final_details = (
                f"**Appointment ID:** {st.session_state['user_data']['Appointment ID']}\n"
                f"**Name:** {st.session_state['user_data']['Name']}\n"
                f"**Email:** {st.session_state['user_data']['Email']}\n"
                f"**Address:** {st.session_state['user_data']['Address']}\n"
                f"**Postcode:** {st.session_state['user_data']['Postcode']}\n"
                f"**Phone:** {st.session_state['user_data']['Phone']}\n"
                f"**Suggested Department:** {st.session_state['user_data']['Suggested Department']}\n"
                f"**Nearest GP:** Not available\n"
            )

        final_details += f"**Assigned Doctor:** {assigned_doctor}\n"

        st.markdown(final_details)

    response_container = st.container()
    container = st.container()

    if not st.session_state['appointment_confirmed']:
        with st.container():
            st.markdown("<div class='container-with-gif'>", unsafe_allow_html=True)
            with st.form(key='my_form', clear_on_submit=True):
                user_input = st.text_area(
                    "Please tell us about your reason for booking an appointment:",
                    key='input',
                    height=100,
                    placeholder="e.g., I have a cough."
                )
                submit_button = st.form_submit_button(label='Send')

                if submit_button and user_input:
                    st.session_state['messages'].append(user_input)

                    if st.session_state['user_data']['Main Reason'] is None:
                        st.session_state['user_data']['Main Reason'] = user_input
                        st.session_state['user_data']['Questions'] = ask_general_questions(user_input)
                        
                        if st.session_state['user_data']['Questions']:
                            st.session_state['messages'].append(
                                f"Thanks for sharing! Here are some additional questions:\n{st.session_state['user_data']['Questions'][0]}"
                            )
                        else:
                            st.session_state['messages'].append("Please provide more details about your condition.")

                    elif st.session_state['question_index'] < len(st.session_state['user_data']['Questions']):
                        st.session_state['question_index'] += 1
                        if st.session_state['question_index'] < len(st.session_state['user_data']['Questions']):
                            question = st.session_state['user_data']['Questions'][st.session_state['question_index']]
                            st.session_state['messages'].append(question)
                        
                        else:
                            st.session_state['messages'].append("Could you please provide your full name?")

                    elif st.session_state['user_data']['Name'] is None:
                        st.session_state['user_data']['Name'] = user_input
                        st.session_state['messages'].append("Could you please provide your email address?")

                    elif st.session_state['user_data']['Email'] is None:
                        st.session_state['user_data']['Email'] = user_input
                        st.session_state['messages'].append("Could you please provide your address?")

                    elif st.session_state['user_data']['Address'] is None:
                        st.session_state['user_data']['Address'] = user_input
                        st.session_state['messages'].append("Could you please provide your postcode?")

                    elif st.session_state['user_data']['Postcode'] is None:
                        st.session_state['user_data']['Postcode'] = user_input

                        # Find closest GP using Google Maps API
                        closest_gp = find_gp_by_postcode(user_input)
                        if closest_gp:
                            # Store only the first GP
                            st.session_state['user_data']['Nearest GP'] = closest_gp[0]  # Take only the first GP
                        else:
                            st.session_state['user_data']['Nearest GP'] = None
                            st.session_state['messages'].append("No GP found nearby.")
                        st.session_state['messages'].append("Could you please provide your phone number?")

                    elif st.session_state['user_data']['Phone'] is None:
                        st.session_state['user_data']['Phone'] = user_input
                        st.session_state['user_data']['Appointment ID'] = str(uuid.uuid4())
                        
                        # Predict specialty using GPT-2 model
                        st.session_state['user_data']['Suggested Department'] = predict_specialty_gpt2(model, tokenizer, st.session_state['user_data']['Main Reason'])
                        
                        # Assign doctor using the trained model
                        st.session_state['user_data']['Assigned Doctor'] = assign_doctor(
                            st.session_state['user_data']['Suggested Department'],
                            doctor_model,
                            label_encoders,
                            y_encoder,
                            doctor_data,
                            feature_names,
                            scaler
                        )
                        
                        store_user_data()
                        st.session_state['appointment_confirmed'] = True

                        st.session_state['messages'].append(
                            f"Thank you! Your appointment has been booked with {st.session_state['user_data']['Assigned Doctor']['Name']}."
                        )

                        # Schedule the appointment and send confirmation email
                        schedule_appointment(
                            st.session_state['user_data'],
                            st.session_state['user_data']['Assigned Doctor']
                        )

                        display_final_details()

                        st.markdown(
                            """
                            <script>
                            window.scrollTo(0, 0);
                            </script>
                            """,
                            unsafe_allow_html=True
                        )

                with response_container:
                    for i in range(len(st.session_state['messages'])):
                        if (i % 2) == 0:
                            with st.container():
                                st.markdown(f"<div class='user-message'><span class='message-text user'>{st.session_state['messages'][i]}<span class='emoji-heart'>❤️</span></span></div>", unsafe_allow_html=True)
                        else:
                            with st.container():
                                st.markdown(f"<div class='ai-message'><span class='message-text ai'>{st.session_state['messages'][i]}</span></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("Thank you for booking your appointment. If you need further assistance, feel free to contact us!")

