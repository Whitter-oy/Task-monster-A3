"""English-only deadline controls independent of the browser's locale."""
import calendar
from datetime import date, time

import streamlit as st

MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


def choose_date(year, month, day):
    st.session_state.new_due_date = date(year, month, day)


def clear_date():
    st.session_state.new_due_date = None


def keyboard_time(hour, minute):
    """Accept keyboard digits only; invalid input never silently changes a deadline."""
    hour, minute = hour.strip(), minute.strip()
    if not all(value.isascii() and value.isdigit() for value in (hour, minute)):
        return None
    try:
        return time(int(hour), int(minute))
    except ValueError:
        return None


def deadline_picker():
    selected = st.session_state.get("new_due_date")
    today = date.today()
    initial = selected or today
    with st.container(key="deadline_picker"):
        st.caption("Deadline · optional")
        date_column, hour_column, minute_column = st.columns([2, 1, 1])
        with date_column:
            label = f"{selected.day:02d} {MONTHS[selected.month-1][:3]} {selected.year}" if selected else "Choose date"
            with st.popover(label, use_container_width=True):
                st.markdown("**Choose a deadline date**")
                month_column, year_column = st.columns([3, 2])
                with month_column:
                    month_name = st.selectbox("Month", MONTHS, index=initial.month-1, key="deadline_month")
                with year_column:
                    year = st.number_input("Year", min_value=1900, max_value=9999, value=initial.year, step=1, key="deadline_year")
                month = MONTHS.index(month_name) + 1
                for column, weekday in zip(st.columns(7), WEEKDAYS):
                    column.markdown(f'<div class="calendar-weekday">{weekday}</div>', unsafe_allow_html=True)
                for week in calendar.Calendar().monthdayscalendar(year, month):
                    for column, day in zip(st.columns(7), week):
                        if day:
                            column.button(str(day), key=f"deadline_day_{year}_{month}_{day}", type="primary" if selected == date(year, month, day) else "secondary", use_container_width=True, on_click=choose_date, args=(year, month, day))
                st.button("Clear date", key="clear_deadline", on_click=clear_date, use_container_width=True)
        with hour_column:
            with st.container(key="deadline_hour_field"):
                hour = st.text_input("Hour", value="23", max_chars=2, placeholder="00–23", label_visibility="collapsed", key="deadline_hour_text", autocomplete="off")
        with minute_column:
            with st.container(key="deadline_minute_field"):
                minute = st.text_input("Minute", value="59", max_chars=2, placeholder="00–59", label_visibility="collapsed", key="deadline_minute_text", autocomplete="off")
    return st.session_state.get("new_due_date"), keyboard_time(hour, minute)
