import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase
from src.database.db import create_attendance


import time



def  show_attendance_result(df,logs):
    st.header("Please review attendance before confirming")
    st.dataframe(df,hide_index=True,width='stretch')
    

    col1,col2 = st.columns(2)
    with col1:
        if st.button("Discard",width='stretch'):
            st.session_state.attendance_images = []
            st.session_state.voive_attendance_results = None
            st.rerun()

    with col2:
        if st.button("Confirm & Save",type='primary',width='stretch'):
            try:
                create_attendance(logs)
                st.toast("Attendance Taken")
                time.sleep(1)
                st.session_state.attendance_images = []
                st.session_state.voive_attendance_results = None
                st.rerun()

            except Exception as e:
                st.error(f"Sync failed! {str(e)}")

@st.dialog('Attendance Report')
def attendance_result_dialog(df,logs):
    show_attendance_result(df,logs)

   