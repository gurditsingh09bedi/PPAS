import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

def send_appointment_email(user_data, doctor_name, appointment_day, appointment_time):
    sender_email = "gurditsingh2030@gmail.com"
    sender_password = "************"  
    receiver_email = user_data['Email']

    # Construct Google Maps URL for directions
    nearest_gp = user_data.get('Nearest GP')
    maps_url = "#"

    if nearest_gp:
        # Check if latitude and longitude are available
        if 'Latitude' in nearest_gp and 'Longitude' in nearest_gp:
            # Constructing the Google Maps URL with the latitude and longitude of the GP
            maps_url = f"https://www.google.com/maps/search/?api=1&query={nearest_gp['Latitude']},{nearest_gp['Longitude']}"

    subject = "Your GP Appointment Confirmation"
    body = f"""
    <html>
    <body>
        <h2>Your GP Appointment Details</h2>
        <p><strong>Appointment ID:</strong> {user_data['Appointment ID']}</p>
        <p><strong>Name:</strong> {user_data['Name']}</p>
        <p><strong>Email:</strong> {user_data['Email']}</p>
        <p><strong>Address:</strong> {user_data['Address']}</p>
        <p><strong>Postcode:</strong> {user_data['Postcode']}</p>
        <p><strong>Phone:</strong> {user_data['Phone']}</p>
        <p><strong>Suggested Department:</strong> {user_data['Suggested Department']}</p>
    """

    if nearest_gp:
        body += f"""
        <p><strong>Nearest GP:</strong> {nearest_gp['Name']} at {nearest_gp['Address']}</p>
        <p><a href="{maps_url}" target="_blank">Click here to get directions on Google Maps</a></p>
        """

    body += f"""
        <h3>Assigned Doctor Details</h3>
        <p><strong>Name:</strong> {doctor_name}</p>
        <p><strong>Appointment Day:</strong> {appointment_day}</p>
        <p><strong>Appointment Time:</strong> {appointment_time}</p>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error(f"An error occurred while sending the email: {e}")
