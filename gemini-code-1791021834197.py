import streamlit as st
import pandas as pd
import random

# Page Configuration
st.set_page_config(page_title="Hisar Division Revenue Training", page_icon="🏛️", layout="wide")

# Load and clean the dictionary data
@st.cache_data
def load_data():
    df = pd.read_excel("Revenue terms dictionary final August.xlsx", sheet_name='Sheet1', skiprows=2)
    df.dropna(subset=[' WORD', 'MEANING(In Hindi)', 'MEANING(In English)'], inplace=True)
    df[' WORD'] = df[' WORD'].astype(str).str.strip()
    df['MEANING(In Hindi)'] = df['MEANING(In Hindi)'].astype(str).str.strip()
    df['MEANING(In English)'] = df['MEANING(In English)'].astype(str).str.strip()
    return df

df = load_data()

# Initialize Session State
if 'score' not in st.session_state:
    st.session_state.score = 0
    st.session_state.attempts = 0
    st.session_state.current_question = None
    st.session_state.options = []

def generate_question():
    row = df.sample(1).iloc[0]
    word = row[' WORD']
    correct = row['MEANING(In Hindi)']
    english_meaning = row['MEANING(In English)']
    
    wrong_options = df[df[' WORD'] != word].sample(3)['MEANING(In Hindi)'].tolist()
    options = wrong_options + [correct]
    random.shuffle(options)
    
    st.session_state.current_question = {
        'word': word, 
        'correct': correct, 
        'english': english_meaning
    }
    st.session_state.options = options

if st.session_state.current_question is None:
    generate_question()

# Sidebar Navigation
st.sidebar.title("🏛️ Portal Navigation")
page = st.sidebar.radio("Go to", ["🎮 Vocabulary Game", "📊 Admin Dashboard"])

if page == "🎮 Vocabulary Game":
    st.title("The Tehsildar Quiz: Revenue Terms")
    st.write("Test your knowledge of traditional land and revenue vocabulary.")
    
    st.markdown("---")
    
    word = st.session_state.current_question['word']
    st.subheader(f"राजस्व रिकॉर्ड में **'{word}'** का क्या अर्थ है?")
    
    choice = st.radio("Select the correct meaning:", st.session_state.options, index=None, key="radio_choice")
    
    if st.button("Submit Answer", type="primary"):
        if choice == st.session_state.current_question['correct']:
            st.success(f"**Correct!** It means: {st.session_state.current_question['english']}")
            st.session_state.score += 1
            st.balloons()
        elif choice is None:
            st.warning("Please select an option before submitting.")
        else:
            st.error(f"**Incorrect.** The correct answer was: {st.session_state.current_question['correct']} ({st.session_state.current_question['english']})")
        
        if choice is not None:
            st.session_state.attempts += 1
            generate_question()
            
    st.markdown("---")
    st.metric("Your Training Score", f"{st.session_state.score} / {st.session_state.attempts}")
    
    if st.button("Reset Game"):
        st.session_state.score = 0
        st.session_state.attempts = 0
        generate_question()

elif page == "📊 Admin Dashboard":
    st.title("Divisional Training Dashboard")
    st.write("Monitor capacity-building and vocabulary mastery across the administrative blocks in Hisar.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Terms in Database", f"{len(df)}")
    col2.metric("Total Practice Attempts", f"{st.session_state.attempts}")
    
    accuracy = 0
    if st.session_state.attempts > 0:
        accuracy = round((st.session_state.score / st.session_state.attempts) * 100, 1)
    col3.metric("Average Accuracy", f"{accuracy}%")
    
    st.markdown("---")
    st.subheader("Revenue Term Master List")
    st.write("Use this table to quickly search for terms and verify translations.")
    
    search_term = st.text_input("Search for a word (Hindi or English):")
    if search_term:
        filtered_df = df[
            df[' WORD'].str.contains(search_term, case=False, na=False) | 
            df['MEANING(In Hindi)'].str.contains(search_term, case=False, na=False) |
            df['MEANING(In English)'].str.contains(search_term, case=False, na=False)
        ]
        st.dataframe(filtered_df[[' WORD', 'MEANING(In Hindi)', 'MEANING(In English)']], use_container_width=True)
    else:
        st.dataframe(df[[' WORD', 'MEANING(In Hindi)', 'MEANING(In English)']], use_container_width=True)