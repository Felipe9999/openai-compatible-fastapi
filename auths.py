import os
import sys
import time
import sqlite3
import hashlib
import binascii

import streamlit as st
from dotenv import load_dotenv

import configs as cfg

load_dotenv()
    
def create_users_table_if_not_exists():
    conn = sqlite3.connect(cfg.DB_NAME, check_same_thread=False)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    password_hash TEXT
                )''')
    conn.commit()
    conn.close()
    
def hash_password(password: str) -> str:
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64].encode('ascii')
    stored_hash = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                  provided_password.encode('utf-8'), 
                                  salt, 
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_hash
    
# Function to check if the email domain is supported
def is_supported_domain(email):
    domain = email.split('@')[-1]
    return domain in cfg.SUPPORTED_DOMAINS

def register_user(email, password):
    conn = sqlite3.connect(cfg.DB_NAME, check_same_thread=False)
    c = conn.cursor()
    try:
        hashed_pw = hash_password(password)
        c.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', (email, hashed_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = sqlite3.connect(cfg.DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT password_hash FROM users WHERE email = ?', (email,))
    result = c.fetchone()
    conn.close()
    
    if result:
        stored_hash = result[0]
        return verify_password(stored_hash, password)
    return False

def log_in_mechanism():
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            email_strip = login_email.strip(" \n")
            if not email_strip or not login_password:
                st.warning("Please enter both email and password.")
            else:
                if authenticate_user(email_strip, login_password):
                    st.success(f"Login successful! Welcome, {email_strip}.")
                    st.session_state.logged_in = True
                    st.session_state.email = email_strip
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
                    
    with tab2:
        st.subheader("Register")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
        
        if st.button("Register"):
            email_strip = reg_email.strip(" \n")
            if not email_strip or not reg_password:
                st.warning("Please enter all fields.")
            elif reg_password != reg_password_confirm:
                st.error("Passwords do not match.")
            elif not is_supported_domain(email_strip):
                st.warning(f"This email domain is not supported. Please use an email from {','.join(cfg.SUPPORTED_DOMAINS)}")
            else:
                if register_user(email_strip, reg_password):
                    st.success("Registration successful! You can now log in from the Login tab.")
                else:
                    st.error("Email is already registered.")

def log_out_mechanism():
    if st.sidebar.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.email = ''
        st.rerun()
