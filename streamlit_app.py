import os
import streamlit as st
import snowflake.connector  #upm package(snowflake-connector-python==2.7.0)
 
 
# Initialize connection, using st.experimental_singleton to only run once.
@st.experimental_singleton
def connectToSnowflake(c):
    con = snowflake.connector.connect(
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        account=os.getenv("ACCOUNT"),
        role=os.getenv("ROLE"),
        warehouse=os.getenv("WAREHOUSE"),
    )
    return con

st.title("📃 Dunder Mifflin")
st.header("Employee Satisfaction Survey")

with st.form("step-1-form"):
    first_name = st.text_input("Your first name", placeholder="Dwight")
    last_name = st.text_input("Your last name", placeholder="Schrute")
    department = st.selectbox('Which department do you work in?',('Sales','Accounting','HR'))
    job_title = st.text_input("Your job title", placeholder="Assistant to the regional manager")
    step_1_submit = st.form_submit_button("Next")

if step_1_submit and not last_name and first_name:
    st.warning('Please enter your last name.')
elif step_1_submit and last_name and not first_name:
    st.warning('Please enter your first name.')

if step_1_submit and first_name and last_name:
    st.session_state['first_name'] = first_name
    st.session_state['last_name'] = last_name
    st.session_state['job_title'] = job_title
    st.session_state['department'] = department

if 'first_name' not in st.session_state and 'last_name' not in st.session_state:
    st.write(" ")

elif 'first_name' in st.session_state and 'last_name'  in st.session_state:
    st.subheader('Please rate the following statements on a scale from 1 to 5, with 1 being "strongly disagree" and 5 being "strongly agree."')

    with st.form("step-2-form"):
        # st.image("WLB.jpg",width=500)   
        satisfaction_wlb = st.slider('I have great work-life balance at Dunder Mifflin.', 1, 10, key="satisfaction-wlb")
        # st.write("\n")
        # st.image("Birthday.jpg",width=500)
        satisfaction_culture = st.slider("I enjoy Dunder Mifflin's company culture.", 1, 10, key="satisfaction-culture")
        
        if department=="Sales":
            satisfaction_mgr = st.slider('My manager, Michael Scott, is effective.', 1, 10, key="satisfaction-mgr")
        elif department=="Accounting":
            satisfaction_mgr = st.slider('My manager, Oscar Nunez, is effective.', 1, 10, key="satisfaction-mgr")
        elif department=="HR":
            satisfaction_mgr = st.slider('My manager, Toby Flenderson, is effective.', 1, 10, key="satisfaction-mgr")
        satisfaction_events = st.slider('I enjoy company events, such as the Dundies and Crime Aid.', 1, 10, key="satisfaction-events")
        satisfaction_office = st.slider('The facilities are clean and functional.', 1, 10, key="satisfaction-office")
        step_2_submit = st.form_submit_button("Submit")

    if step_2_submit:
        conn = connectToSnowflake({
            "USER": USER, 
            "PASSWORD": PASSWORD, 
            "ACCOUNT": ACCOUNT,
            "ROLE": ROLE,
            "WAREHOUSE": WAREHOUSE,
        })

        first_name = st.session_state['first_name']
        last_name = st.session_state['last_name']
        cur = conn.cursor()
        cur.execute('use EMPLOYEE_SURVEY.PUBLIC')
        cur.execute("INSERT INTO RESPONSES (FIRST_NAME, LAST_NAME, JOB_TITLE, DEPARTMENT, SATISFACTION_WLB, SATISFACTION_CULTURE, SATISFACTION_MGR, SATISFACTION_EVENTS, SATISFACTION_OFFICE) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (first_name, last_name, st.session_state['job_title'], st.session_state['department'], satisfaction_wlb, satisfaction_culture, satisfaction_mgr, satisfaction_events, satisfaction_office))
        cur.execute("SELECT * FROM RESPONSES")
        results = cur.fetchall()

        st.balloons()
        st.success("Thanks for submitting your response!")

        cur.execute('select avg(SATISFACTION_WLB) from RESPONSES')
        avg_satisfaction_wlb = cur.fetchone()
        avg_satisfaction_wlb = str(round(avg_satisfaction_wlb[0],3)) + " out of 10"

        cur.execute('select avg(SATISFACTION_CULTURE) from RESPONSES')
        avg_satisfaction_culture = cur.fetchone()
        avg_satisfaction_culture = str(round(avg_satisfaction_culture[0],3)) + " out of 10"

        cur.execute('select avg(SATISFACTION_MGR) from RESPONSES')
        avg_satisfaction_mgr = cur.fetchone()
        avg_satisfaction_mgr = str(round(avg_satisfaction_mgr[0],3)) + " out of 10"

        cur.execute('select avg(SATISFACTION_EVENTS) from RESPONSES')
        avg_satisfaction_events = cur.fetchone()
        avg_satisfaction_events = str(round(avg_satisfaction_events[0],3)) + " out of 10"

        cur.execute('select avg(SATISFACTION_OFFICE) from RESPONSES')
        avg_satisfaction_office = cur.fetchone()
        avg_satisfaction_office = str(round(avg_satisfaction_office[0],3)) + " out of 10"

        st.metric("Average satisfaction with work-life balance", avg_satisfaction_wlb)
        st.metric("Average satisfaction with company culture", avg_satisfaction_culture)
        st.metric("Average satisfaction with manager", avg_satisfaction_mgr)
        st.metric("Average satisfaction with events", avg_satisfaction_events)
        st.metric("Average satisfaction with office", avg_satisfaction_office)

        for key in st.session_state.keys():
            del st.session_state[key]
