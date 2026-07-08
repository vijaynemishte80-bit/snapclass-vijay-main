import streamlit as st
from src.ui.base_layout import style_background_dashboard,style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predicted_attendance,get_face_embeddings,train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import get_all_students,create_student,get_students_subjects,get_student_attendance,unenroll_student_to_subject
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card
import time

def student_dashboard():
    student_data=st.session_state.student_data
    student_id = student_data['student_id']
    
    C1,C2=st.columns(2,vertical_alignment='center',gap='xxlarge')
    with C1:
        header_dashboard()
    with C2:
        st.subheader(f"""Welcome, {student_data['name']}""")
        if st.button("Logout",type='secondary',key='loginbackbtn',shortcut='control+backspace'):
            st.session_state['is_logged_in']=False
            del st.session_state.student_data
            st.rerun()

    st.space()

    c1,c2=st.columns(2)
    with c1:
        st.header("Your Enrolled Subjects")
    with c2:
        if st.button("Enroll Subject",type='primary',width='stretch'):
            enroll_dialog()

    st.divider()

    with st.spinner("Loading your enrolled subjects......"):
        subjects = get_students_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map={}

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total":0,"attended":0}

        stats_map[sid]['total'] += 1

        if log.get("is_present"):
            stats_map[sid]['attended'] += 1
     
    cols = st.columns(2)
   
    for i,sub_node in enumerate(subjects):
        sub =sub_node['subjects']
        sid = sub_node['subject_id']
        
     

        stats = stats_map.get(sid,{"total":0,"attended":0})

        def unenroll_btn():
            if st.button("UnEnroll From cource",type='tertiary',width='stretch',key=f"Unenroll_{sid}",icon=":material/delete_forever:"):
               result=unenroll_student_to_subject(student_id,sid)
               if result:
                   st.toast(f"Unenroll from {sub['name']} Successfully!")
               else:
                   st.error(f"Unenroll failed-nothing from {sub['name']} successfully")
               time.sleep(1)
               st.rerun()

        with cols[i%2]:
            subject_card(
                name = sub['name'],
                code = sub['subject_code'],
                section = sub['section'],
                stats = [
                    ("📅","Total",stats['total']),
                    ("✅","Attended",stats['attended'])

                ],
                footer_callback = unenroll_btn
            )


           

    footer_dashboard() 

def student_screen():
    style_background_dashboard()
    style_base_layout()
    
    if 'student_data' in st.session_state:
        student_dashboard()
        return
    C1,C2=st.columns(2,vertical_alignment='center',gap='xxlarge')
    with C1:
        header_dashboard()
    with C2:
        if st.button("Go Back to Home",type='secondary',key='studentloginbackbtn',shortcut='control+backspace'):
            st.session_state['login_type']=None
            st.rerun()    

    st.header("Login using FaceID",text_alignment='center')
    st.space()
    st.space()


    show_registartion = False
    photo_source=st.camera_input("Position your face in the center")
    if photo_source:
        img = np.array(Image.open(photo_source))
        with st.spinner('AI is scanning.....'):
            detected,all_ids,num_face = predicted_attendance(img)

            if num_face == 0:
                st.warning('No face Found')
            elif num_face >1:
                st.warning('Multiple faces detected')
            else:
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next((s for s in all_students if s['student_id'] == student_id),None)

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role ='student'
                        st.session_state.student_data = student
                        st.toast(f"Welcome back! {student['name']}")
                        time.sleep(1)
                        st.rerun()

                else:
                    st.info('Face not Recognized! You might be a new student!')
                    show_registartion = True
    if show_registartion:
        with st.container(border=True):
            st.header("Register new profile")
            new_name = st.text_input("Enter your name", placeholder = 'e.g. Vijay Nemishte')

            st.subheader('Optional: Voice Enrollment')
            st.info('enroll your for voice only attendance')

            audio_data = None

            try:
                audio_data = st.audio_input('Record a short phrase like I am present,My name is Vijay')
            except Exception:
                st.error('audio data failed!')
            
            if st.button('Create Account', type='primary'):
                if new_name:
                    st.spinner('Creating profile')
                    img = np.array(Image.open(photo_source))
                    encodings = get_face_embeddings(img)
                    if encodings:
                        face_emb = encodings[0].tolist()

                        voice_emb = None
                        if audio_data:
                            voice_emb = get_voice_embedding(audio_data.read())

                        response_data = create_student(new_name,face_embedding=face_emb,voice_embedding=voice_emb)

                        if response_data:
                            train_classifier()
                            st.session_state.is_logged_in = True
                            st.session_state.user_role ='student'
                            st.session_state.student_data = response_data[0]
                            st.toast(f"Profile Created! Hi {new_name}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Couldn't create profile,try again")
                    else:
                        st.error("Couldn't capture your facial feature for Registration")

            else:
                st.warning('Please enter your name')

                


    footer_dashboard()
    