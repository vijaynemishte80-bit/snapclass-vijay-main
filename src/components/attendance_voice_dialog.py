import streamlit as st
from src.database.config import supabase
from src.pipelines.voice_pipeline import process_bulk_audio
from datetime import datetime
from src.components.attendance_result_dialog import show_attendance_result
import pandas as pd


@st.dialog("Voice Attendance")
def voice_attendance_dialog(selected_subject_id):
    st.header("Record audio of the students then Ai will recognize these audio")

    audio_data = None

    audio_data = st.audio_input("Record classroom audio")

    if st.button("Record Audio",width='stretch',type='primary'):
        with st.spinner("Processing audio data....."):
            enroll_res = supabase.table('subjects_students').select("*,students(*)").eq('subject_id',selected_subject_id).execute()
            enrolled_students = enroll_res.data

            if not enrolled_students:
                st.warning("No students enrolled in these cource")
                return
            candidate_dict={
                s['students']['student_id']:s['students']['voice_embedding']

                for s in enrolled_students if s['students'].get('voice_embedding')
            }

            if not candidate_dict:
                st.error("No enrolled voice students have voice profile register")
                return
            
            audio_bytes = audio_data.read()

            detected_scores = process_bulk_audio(audio_bytes,candidate_dict)

            results,attendance_to_log = [],[]
            current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            for node in enrolled_students:
                student = node['students']
                score = detected_scores.get(student['student_id'],0.0)
                is_present = bool(score > 0.0) 

                results.append({
                    "Name":student['name'],
                    "ID":student['student_id'],
                    "source":score if is_present else "-",
                    "Status":"✅Present" if is_present else "❌Absent"

                                    
                })
                attendance_to_log.append({
                    'student_id':student['student_id'],
                    'subject_id': selected_subject_id,
                    'timestamp': current_timestamp,
                    'is_present': bool(is_present)
                        
                })
            st.session_state.voice_attendance_results = (pd.DataFrame(results),attendance_to_log)
    if st.session_state.get('voice_attendance_results'):
        st.divider()
        df_results,log = st.session_state.voice_attendance_results
        show_attendance_result(df_results,log)

    

