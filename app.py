import streamlit as st
from langchain_openai import OpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationSummaryMemory
import pandas as pd
import os
import uuid

# Set the page configuration before any other Streamlit command
st.set_page_config(page_title="GP Appointment Booking", page_icon=":robot_face:")

# Load external CSS
def load_css(file_name):
    """Load external CSS file for styling."""
    with open(file_name, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the CSS file
load_css("style.css")

# Initialize session state variables
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = None
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
        "Suggested Department": None
    }
if 'question_index' not in st.session_state:
    st.session_state['question_index'] = 0

# Directly set your API key here
API_KEY = "sk-proj-1LMvc7i58NZMDfUJ3vxAT3BlbkFJqtqiHxvBqjYmwakjqNpE"

# Setting the header
st.markdown(
    "<h1 style='text-align: center; color: #333;'>Book Your GP Appointment</h1>", 
    unsafe_allow_html=True
)

# Sidebar for conversation summarization
# Add an image to the sidebar
st.sidebar.image("Default_As_she_gazes_intently_at_her_patients_chart_the_sunlig_3.jpg", caption="PPAS", use_column_width=True)  # Ensure the image path is correct

# Scrolling content in the sidebar
st.sidebar.markdown(
    """
    <div class="marquee-container">
        <span class="marquee-text">
            Welcome to our Clinic! Our General Practitioners are available for consultations to address a wide range of health concerns. Whether it's a cough, fever, headache, or any other medical issue, we are here to provide the best care possible. Book an appointment today and let our team assist you with personalized medical advice.
        </span>
    </div>
    """, 
    unsafe_allow_html=True
)

# Function to determine department based on main reason
def suggest_department(reason):
    """Suggests the best department based on the user's main reason for booking."""
    department_map = {
        "cough": "Respiratory Medicine",
        "fever": "General Medicine",
        "headache": "Neurology",
        "stomach pain": "Gastroenterology",
        "skin rash": "Dermatology",
        "back pain": "Orthopedics",
        "eye pain": "Ophthalmology",
        "ear pain": "ENT",
        "mental health": "Psychiatry",
        "chest pain": "Cardiology",
        "diabetes": "Endocrinology",
        "tooth pain": "Dentistry"
    }
    for keyword, department in department_map.items():
        if keyword in reason.lower():
            return department
    return "General Practitioner"

def ask_additional_questions(reason):
    """Ask general or personal questions based on the main reason."""
    questions = {
        "cough": [
            "How long have you had the cough?",
            "Is the cough accompanied by any other symptoms?"
        ],
        "fever": [
            "What is your current temperature?",
            "Have you taken any medication for the fever?"
        ],
        "headache": [
            "Where is the pain located?",
            "How severe is the headache on a scale from 1 to 10?"
        ],
        "stomach pain": [
            "When did the stomach pain start?",
            "Is the pain constant or does it come and go?"
        ],
        "skin rash": [
            "What does the rash look like?",
            "Does the rash itch or hurt?"
        ],
        "back pain": [
            "Did the back pain start after an injury?",
            "Have you experienced similar pain before?"
        ],
        "eye pain": [
            "When did the eye pain start?",
            "Are there any changes in your vision?"
        ],
        "ear pain": [
            "Is the ear pain in one or both ears?",
            "Have you experienced any hearing loss?"
        ],
        "mental health": [
            "Have you been experiencing any anxiety or depression?",
            "Do you have a history of mental health issues?"
        ],
        "chest pain": [
            "When did the chest pain start?",
            "Does the pain spread to other parts of your body?"
        ],
        "diabetes": [
            "Are you currently taking medication for diabetes?",
            "What was your last blood sugar reading?"
        ],
        "tooth pain": [
            "How severe is the tooth pain on a scale from 1 to 10?",
            "Have you visited a dentist for this issue before?"
        ]
    }
    for keyword, question_list in questions.items():
        if keyword in reason.lower():
            return question_list
    return ["Please describe your symptoms in more detail."]

def get_response(user_input):
    """Generate a response from the AI model based on user input."""
    if st.session_state['conversation'] is None:
        llm = OpenAI(
            temperature=0,
            openai_api_key=API_KEY,
            model_name='gpt-3.5-turbo-instruct'
        )

        st.session_state['conversation'] = ConversationChain(
            llm=llm,
            verbose=True,
            memory=ConversationSummaryMemory(llm=llm)
        )

    response = st.session_state['conversation'].predict(input=user_input)
    return response

def store_user_data():
    """Store the user data in a CSV file."""
    user_data = pd.DataFrame([st.session_state['user_data']])
    if not os.path.isfile('user_data.csv'):
        user_data.to_csv('user_data.csv', index=False)
    else:
        user_data.to_csv('user_data.csv', mode='a', header=False, index=False)

def display_final_details():
    """Display final user details."""
    final_details = (
        f"**Appointment ID:** {st.session_state['user_data']['Appointment ID']}\n"
        f"**Name:** {st.session_state['user_data']['Name']}\n"
        f"**Email:** {st.session_state['user_data']['Email']}\n"
        f"**Address:** {st.session_state['user_data']['Address']}\n"
        f"**Postcode:** {st.session_state['user_data']['Postcode']}\n"
        f"**Phone:** {st.session_state['user_data']['Phone']}\n"
        f"**Suggested Department:** {st.session_state['user_data']['Suggested Department']}\n"
    )
    st.markdown(final_details)

response_container = st.container()

# Container for user input text box
container = st.container()

# Wrap your form in a container with a GIF background
with st.container():
    st.markdown("<div class='container-with-gif'>", unsafe_allow_html=True)
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area(
            "Please tell us about your reason for booking an appointment:",
            key='input',
            height=100,
            placeholder="e.g., I have a fever and cough."
        )
        submit_button = st.form_submit_button(label='Send')

        if submit_button and user_input:
            st.session_state['messages'].append(user_input)

            # Main logic to process the conversation
            if st.session_state['user_data']['Main Reason'] is None:
                # Ask the main reason for booking
                st.session_state['user_data']['Main Reason'] = user_input
                st.session_state['user_data']['Suggested Department'] = suggest_department(user_input)
                st.session_state['user_data']['Questions'] = ask_additional_questions(user_input)
                
                # Append the first question after main reason
                st.session_state['messages'].append(
                    f"Thanks for sharing! Here are some additional questions:\n{st.session_state['user_data']['Questions'][0]}"
                )

            elif st.session_state['question_index'] < len(st.session_state['user_data']['Questions']):
                # Process additional questions
                st.session_state['question_index'] += 1
                if st.session_state['question_index'] < len(st.session_state['user_data']['Questions']):
                    question = st.session_state['user_data']['Questions'][st.session_state['question_index']]
                    st.session_state['messages'].append(question)
                else:
                    st.session_state['messages'].append("Could you please provide your full name?")

            elif st.session_state['user_data']['Name'] is None:
                # Ask for name
                st.session_state['user_data']['Name'] = user_input
                st.session_state['messages'].append("Could you please provide your email address?")

            elif st.session_state['user_data']['Email'] is None:
                # Ask for email
                st.session_state['user_data']['Email'] = user_input
                st.session_state['messages'].append("Could you please provide your address?")

            elif st.session_state['user_data']['Address'] is None:
                # Ask for address
                st.session_state['user_data']['Address'] = user_input
                st.session_state['messages'].append("Could you please provide your postcode?")

            elif st.session_state['user_data']['Postcode'] is None:
                # Ask for postcode
                st.session_state['user_data']['Postcode'] = user_input
                st.session_state['messages'].append("Could you please provide your phone number?")

            elif st.session_state['user_data']['Phone'] is None:
                # Ask for phone number
                st.session_state['user_data']['Phone'] = user_input
                st.session_state['user_data']['Appointment ID'] = str(uuid.uuid4())  # Generate unique appointment ID
                st.session_state['messages'].append(
                    f"Thanks, {st.session_state['user_data']['Name']}! We've stored your information and suggested the best department for you. Your unique appointment ID is {st.session_state['user_data']['Appointment ID']}."
                )
                store_user_data()
                display_final_details()

            # Display conversation history
            with response_container:
                for i in range(len(st.session_state['messages'])):
                    if (i % 2) == 0:
                        # User message with user image on the right
                        with st.container():
                            col1, col2 = st.columns([9, 1])
                            with col1:
                                st.markdown(f"<div class='user-message'>{st.session_state['messages'][i]}</div>", unsafe_allow_html=True)
                            with col2:
                                st.markdown("<div style='font-size: 24px;'>❤️</div>", unsafe_allow_html=True)
                    else:
                        # AI response with background GIF on the left
                        with st.container():
                            col1, col2 = st.columns([1, 9])
                            with col1:
                                st.image("download.jpeg", width=50)
                            with col2:
                                st.markdown(f"<div class='ai-message ai-message-bg'>{st.session_state['messages'][i]}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
