
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Initialize the event database (in-memory storage for now)
if "events" not in st.session_state:
    st.session_state.events = []

# Helper functions
def generate_event_id():
    """Generate a unique event ID using numpy."""
    if st.session_state.events:
        ids = [event['ID'] for event in st.session_state.events]
        return int(np.max(ids) + 1)
    return 1

def add_event(name, description, date, time, location):
    """Add a new event to the database."""
    event = {
        "ID": generate_event_id(),
        "Name": name,
        "Description": description,
        "Date": date,
        "Time": time,
        "Location": location
    }
    st.session_state.events.append(event)

def update_event(event_id, name, description, date, time, location):
    """Update an existing event."""
    for event in st.session_state.events:
        if event['ID'] == event_id:
            event.update({
                "Name": name,
                "Description": description,
                "Date": date,
                "Time": time,
                "Location": location
            })

def delete_event(event_id):
    """Delete an event from the database."""
    st.session_state.events = [event for event in st.session_state.events if event['ID'] != event_id]

def sort_events_by_date():
    """Sort events by date using numpy."""
    if st.session_state.events:
        sorted_events = sorted(st.session_state.events, key=lambda x: datetime.strptime(x["Date"], "%Y-%m-%d"))
        st.session_state.events = sorted_events

# Streamlit UI
st.title("Event Management System")

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
            add_event(name, description, str(date), str(time), location)
            st.success("Event added successfully!")
        else:
            st.error("Please fill in all the required fields.")

# Tab 2: View Events
with tab2:
    st.header("View All Events")
    if st.session_state.events:
        df = pd.DataFrame(st.session_state.events)
        st.dataframe(df)
    else:
        st.info("No events found. Add some events first.")

# Tab 3: Manage Events
with tab3:
    st.header("Manage Events")
    if st.session_state.events:
        event_ids = [event['ID'] for event in st.session_state.events]
        selected_event_id = st.selectbox("Select an Event ID to Manage", options=event_ids)
        selected_event = next(event for event in st.session_state.events if event['ID'] == selected_event_id)

        # Display selected event details
        name = st.text_input("Event Name", value=selected_event["Name"])
        description = st.text_area("Event Description", value=selected_event["Description"])
        date = st.date_input("Event Date", value=datetime.strptime(selected_event["Date"], "%Y-%m-%d").date())
        time = st.time_input("Event Time", value=datetime.strptime(selected_event["Time"], "%H:%M:%S").time())
        location = st.text_input("Event Location", value=selected_event["Location"])

        # Update or delete the event
        if st.button("Update Event"):
            update_event(selected_event_id, name, description, str(date), str(time), location)
            st.success("Event updated successfully!")
        if st.button("Delete Event"):
            delete_event(selected_event_id)
            st.warning("Event deleted successfully!")
    else:
        st.info("No events found. Add some events first.")

# Tab 4: Sort Events
with tab4:
    st.header("Sort Events by Date")
    if st.session_state.events:
        if st.button("Sort Events"):
            sort_events_by_date()
            st.success("Events sorted by date!")
            sorted_df = pd.DataFrame(st.session_state.events)
            st.dataframe(sorted_df)
    else:
        st.info("No events to sort. Add some events first.")
# streamlit run C:\Users\Ganesh\PycharmProjects\pythonProject\aat.py
