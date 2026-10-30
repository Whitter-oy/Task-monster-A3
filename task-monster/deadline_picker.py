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
            hour = st.selectbox("Hour", range(24), index=23, format_func=lambda value: f"{value:02d}", key="deadline_hour")
        with minute_column:
            minute = st.selectbox("Minute", range(60), index=59, format_func=lambda value: f"{value:02d}", key="deadline_minute")
        st.caption("Hong Kong time · 24-hour clock")
    return st.session_state.get("new_due_date"), time(hour, minute)
