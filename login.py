import yagmail
import random
from st_pages import hide_pages
# Configure your email client
def send_otp(email_address):
    # Set up the email client with your email and app password
    yag = yagmail.SMTP('mahimnasd17@gmail.com', 'dvht ncia theh kjut')

    # Generate a random 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # Send OTP email
    yag.send(
        to=email_address,
        subject='Your 2FA OTP Code',
        contents=f'Your One-Time Password (OTP) is: {otp}'
    )
    return otp

import streamlit as st

# Placeholder to store user session information
if 'otp_sent' not in st.session_state:
    st.session_state['otp_sent'] = False

if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None

if 'generated_otp' not in st.session_state:
    st.session_state['generated_otp'] = None

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Step 1: User enters their email
if not st.session_state['otp_sent']:
    st.header("Login with 2FA")
    email_input = st.text_input("Enter your email", value="", type="default")

    if st.button("Send OTP"):
        if email_input:
            otp = send_otp(email_input)
            st.session_state['generated_otp'] = otp
            st.session_state['otp_sent'] = True
            st.session_state['user_email'] = email_input
            st.success(f"OTP has been sent to {email_input}.")
        else:
            st.error("Please enter a valid email address.")

# Step 2: User enters the OTP
if st.session_state['otp_sent'] and not st.session_state['authenticated']:
    st.header("Enter OTP")
    otp_input = st.text_input("Enter the OTP sent to your email", value="", type="password")

    if st.button("Verify OTP"):
        if otp_input == st.session_state['generated_otp']:
            st.success("You have been authenticated successfully!")
            st.session_state['authenticated'] = True
        else:
            st.error("Invalid OTP. Please try again.")

# Step 3: Display content for authenticated users
if st.session_state['authenticated']:
    hide_pages(hidden_pages="travel_guru")
    st.switch_page("pages/workassist.py")
    st.header("Welcome to the Secure Section")
    st.write("You have successfully logged in with 2FA.")