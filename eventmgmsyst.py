# Import necessary libraries
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# SQLite database setup
DB_NAME = "events.db"

def create_table():
    """Create the events table if it doesn't already exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Description TEXT NOT NULL,
        Date TEXT NOT NULL,
        Time TEXT NOT NULL,
        Location TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def add_event_to_db(name, description, date, time, location):
    """Add a new event to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (Name, Description, Date, Time, Location) VALUES (?, ?, ?, ?, ?)",
                   (name, description, date, time, location))
    conn.commit()
    conn.close()

def get_events_from_db():
    """Retrieve all events from the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events")
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

# Streamlit UI
st.title("Event Management System")
create_table()  # Ensure the database table exists

# Tabs for different functionalities
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
            add_event_to_db(name, description, str(date), str(time), location)
            st.success("Event added successfully!")
        else:
            st.error("Please fill in all the required fields.")

# Tab 2: View Events
with tab2:
    st.header("View All Events")
    events = get_events_from_db()
    if events:
        df = pd.DataFrame(events, columns=["ID", "Name", "Description", "Date", "Time", "Location"])
        st.dataframe(df)
    else:
        st.info("No events found. Add some events first.")

# Tab 3: Manage Events
with tab3:
    st.header("Manage Events")
    events = get_events_from_db()
    if events:
        df = pd.DataFrame(events, columns=["ID", "Name", "Description", "Date", "Time", "Location"])
        st.dataframe(df)

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
    events = get_events_from_db()
    if events:
        sorted_events = sort_events_by_date(events)
        sorted_df = pd.DataFrame(sorted_events, columns=["ID", "Name", "Description", "Date", "Time", "Location"])
        st.dataframe(sorted_df)
    else:
        st.info("No events to sort. Add some events first.")
# streamlit run C:\Users\Ganesh\PycharmProjects\pythonProject\eventmgmsyst.py
