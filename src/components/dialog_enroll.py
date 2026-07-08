import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase
import time


@st.dialog('Enroll in subject')
def enroll_dialog():
    st.write("Enter subject code provided by your teacher to enroll")
    join_code = st.text_input("Subject Code",placeholder="Eg.CS101")
    
    if st.button("Register Now",type='primary',width='stretch'):
       
        if join_code:
            res = supabase.table('subjects').select('subject_id,name,subject_code').eq('subject_code',join_code).execute()
            
            if res.data:
                subject = res.data[0]
                student_id = st.session_state.student_data['student_id']

                
                check = supabase.table("subjects_students").select('*').eq('subject_id',subject['subject_id']).eq('student_id',student_id).execute()
                
                if check.data:
                    st.warning("You already enrolled in this program")
                else:
                    result=enroll_student_to_subject(student_id,subject['subject_id'])
                   
                    st.success("Succeccfully Enrolled")
                    time.sleep(1)
                    st.rerun()

            else:
                st.error(f"No subject found with code '{join_code}'.Please check subject code and try again")

        else:
            st.warning("Please Enter Subject Code!")


