import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt

# ------------------ DB CONNECTION ------------------
@st.cache_resource
def connect_db():
    conn = psycopg2.connect(
        host=st.secrets["postgres"]["host"],
        dbname=st.secrets["postgres"]["dbname"],
        user=st.secrets["postgres"]["user"],
        password=st.secrets["postgres"]["password"],
        port=st.secrets["postgres"]["port"]
    )
    conn.set_client_encoding('UTF8')
    return conn

conn = connect_db()
cur = conn.cursor(cursor_factory=RealDictCursor)

# ------------------ SESSION STATE ------------------
if "username" not in st.session_state:
    st.session_state.username = ""
if "form" not in st.session_state:
    st.session_state.form = "signin_form"  # default form is login

# 🔐 Password Hashing Functions
def hash_password(password: str) -> str:
    """Hash a password for storing."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def check_password(password: str, hashed: bytes) -> bool:
    """Verify a stored password against one provided by user."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def user_update(name):
    st.session_state.username = name

# ------------------ AUTH FORMS ------------------
def signup_form():
    st.title("Create Account")
    with st.form("signup_form", clear_on_submit=True):
        new_username = st.text_input("Enter Username*")
        new_user_email = st.text_input("Enter Email Address*")
        new_user_pas = st.text_input("Enter Password*", type="password")
        user_pas_conf = st.text_input("Confirm Password*", type="password")
        submitted = st.form_submit_button("Sign Up")

        if submitted:
            if "" in [new_username, new_user_email, new_user_pas]:
                st.error("Some fields are missing")
            else:
                cur.execute("SELECT * FROM users WHERE log = %s;", (new_username,))
                if cur.fetchone():
                    st.error("Username already exists")
                else:
                    cur.execute("SELECT * FROM users WHERE email = %s;", (new_user_email,))
                    if cur.fetchone():
                        st.error("Email is already registered")
                    elif new_user_pas != user_pas_conf:
                        st.error("Passwords do not match")
                    else:
                        cur.execute(
                            "INSERT INTO users (log, email, pass) VALUES (%s, %s, %s);",
                            (new_username, new_user_email, new_user_pas)
                        )
                        conn.commit()
                        st.success("Account created successfully! Please log in.")
                        st.session_state.form = "signin_form"  # switch to login form


def signin_form():
    st.title("Sign In")
    with st.form("signin_form", clear_on_submit=True):
        username = st.text_input("Enter Username")
        user_pas = st.text_input("Enter Password", type="password")
        submitted = st.form_submit_button("Sign In")

        if submitted:
            cur.execute(
                "SELECT * FROM users WHERE log = %s AND pass = %s;",
                (username, user_pas)
            )
            if cur.fetchone():
                user_update(username)
                #st.success(f"Welcome {username.upper()} 🎉")


            else:
                st.error("Username or Password is incorrect. Please try again or create an account.")


# ------------------ APP INTERFACE ------------------
def app_interface():
    # Logout button at the top right
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("Log Out"):
            user_update("")
            st.session_state.form = "signin_form"
            st.rerun()

    st.write(f"👋 You are logged in as **{st.session_state.username.upper()}**")




# ------------------ MAIN FLOW ------------------
if st.session_state.username == "":
    if st.session_state.form == "signup_form":
        signup_form()
        if st.button("Already have an account? Sign In"):
            st.session_state.form = "signin_form"
            st.rerun()
    else:
        signin_form()

        if st.button("Create Account"):
            st.session_state.form = "signup_form"
            st.rerun()


else:
    app_interface()