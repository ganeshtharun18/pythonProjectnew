import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import hashlib

# Database setup
DB_NAME = "event_management.db"

def create_tables():
    """Create necessary tables for users and events."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
    """)
    # Create events table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Description TEXT NOT NULL,
        Date TEXT NOT NULL,
        Time TEXT NOT NULL,
        Location TEXT NOT NULL,
        username TEXT NOT NULL,
        FOREIGN KEY (username) REFERENCES users (username)
    )
    """)
    conn.commit()
    conn.close()

# User Authentication
def hash_password(password):
    """Hash a password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    """Register a new user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()
    return True

def login_user(username, password):
    """Check user credentials."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user

# Event Management
def add_event_to_db(name, description, date, time, location, username):
    """Add a new event to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (Name, Description, Date, Time, Location, username) VALUES (?, ?, ?, ?, ?, ?)",
                   (name, description, date, time, location, username))
    conn.commit()
    conn.close()

def get_events_from_db(username):
    """Retrieve all events for a specific user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE username = ?", (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_event_in_db(event_id, name, description, date, time, location):
    """Update an event in the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE events
    SET Name = ?, Description = ?, Date = ?, Time = ?, Location = ?
    WHERE ID = ?
    """, (name, description, date, time, location, event_id))
    conn.commit()
    conn.close()

def delete_event_from_db(event_id):
    """Delete an event from the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE ID = ?", (event_id,))
    conn.commit()
    conn.close()

def sort_events_by_date(events):
    """Sort events by date."""
    return sorted(events, key=lambda x: datetime.strptime(x[3], "%Y-%m-%d"))

# Custom CSS for styling
CSS = """
<style>
body {
    background-color: #f0f2f6;
    font-family: Arial, sans-serif;
}
h1, h2, h3 {
    color: #3a5a9e;
    text-align: center;
}
.stButton>button {
    background-color: #3a5a9e;
    color: white;
    border-radius: 5px;
    border: none;
    padding: 8px 16px;
}
.stButton>button:hover {
    background-color: #29487d;
    color: white;
}
.stDataFrame {
    border: 1px solid #3a5a9e;
    border-radius: 5px;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# Streamlit UI
st.title("Event Management System")
create_tables()  # Ensure the database tables exist

# Login/Registration
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

if not st.session_state.logged_in:
    st.sidebar.header("User Login/Registration")
    choice = st.sidebar.radio("Choose an option", ["Login", "Register"])

    if choice == "Register":
        st.sidebar.subheader("Create a New Account")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Register"):
            if username and password:
                if register_user(username, password):
                    st.sidebar.success("Registration successful! Please log in.")
                else:
                    st.sidebar.error("Username already exists. Try a different one.")
            else:
                st.sidebar.error("Please fill in all fields.")

    elif choice == "Login":
        st.sidebar.subheader("Log In")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Log In"):
            if username and password:
                if login_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.sidebar.success(f"Welcome, {username}!")
                else:
                    st.sidebar.error("Invalid username or password.")
            else:
                st.sidebar.error("Please fill in all fields.")

if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as: {st.session_state.username}")
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = None

    # Tabs for event management
    tab1, tab2, tab3, tab4 = st.tabs(["Add Event", "View Events", "Manage Events", "Sort Events"])

    # Tab 1: Add Event
    with tab1:
        st.header("Add a New Event")
        name = st.text_input("Event Name")
        description = st.text_area("Event Description")
        date = st.date_input("Event Date")
        time = st.time_input("Event Time")
        location = st.text_input("Event Location")
        if st.button("Add Event"):
            if name and description and location:
                add_event_to_db(name, description, str(date), str(time), location, st.session_state.username)
                st.success("Event added successfully!")
            else:
                st.error("Please fill in all the required fields.")

    # Tab 2: View Events
    with tab2:
        st.header("View All Events")
        events = get_events_from_db(st.session_state.username)
        if events:
            df = pd.DataFrame(events, columns=["ID", "Name", "Description", "Date", "Time", "Location", "Username"])
            st.dataframe(df.drop("Username", axis=1))  # Exclude username column from display
        else:
            st.info("No events found. Add some events first.")

    # Tab 3: Manage Events
    with tab3:
        st.header("Manage Events")
        events = get_events_from_db(st.session_state.username)
        if events:
            df = pd.DataFrame(events, columns=["ID", "Name", "Description", "Date", "Time", "Location", "Username"])
            st.dataframe(df.drop("Username", axis=1))

            event_ids = [event[0] for event in events]
            selected_event_id = st.selectbox("Select an Event ID to Manage", options=event_ids)
            selected_event = next(event for event in events if event[0] == selected_event_id)

            # Display selected event details
            name = st.text_input("Event Name", value=selected_event[1])
            description = st.text_area("Event Description", value=selected_event[2])
            date = st.date_input("Event Date", value=datetime.strptime(selected_event[3], "%Y-%m-%d").date())
            time = st.time_input("Event Time", value=datetime.strptime(selected_event[4], "%H:%M:%S").time())
            location = st.text_input("Event Location", value=selected_event[5])

            # Update or delete the event
            if st.button("Update Event"):
                update_event_in_db(selected_event_id, name, description, str(date), str(time), location)
                st.success("Event updated successfully!")
            if st.button("Delete Event"):
                delete_event_from_db(selected_event_id)
                st.warning("Event deleted successfully!")
        else:
            st.info("No events found. Add some events first.")

    # Tab 4: Sort Events
    with tab4:
        st.header("Sort Events by Date")
        events = get_events_from_db(st.session_state.username)
        if events:
            sorted_events = sort_events_by_date(events)
            sorted_df = pd.DataFrame(sorted_events, columns=["ID", "Name", "Description", "Date", "Time", "Location", "Username"])
            st.dataframe(sorted_df.drop("Username", axis=1))
        else:
            st.info("No events to sort. Add some events first.")
# streamlit run C:\Users\Ganesh\PycharmProjects\pythonProject\eventmgmnew.py
