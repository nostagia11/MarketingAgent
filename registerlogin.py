import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt



# ------------------ DB CONNECTION cont ------------------
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




# 🔐 Password Hashing Functions
def hash_password(password: str) -> str:
    """Hash a password for storing."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)


def check_password(password: str, hashed: bytes) -> bool:
    """Verify a stored password against one provided by user.
    return bcrypt.checkpw(password.encode('utf-8'), hashed)"""
    # Convert memoryview to bytes if needed
    if isinstance(hashed, memoryview):
        hashed = hashed.tobytes()
    return bcrypt.checkpw(password.encode('utf-8'), hashed)




# ------------------ SESSION STATE HELPERS ------------------
def set_user_session(username, user_id):
    """Store the current user's session info."""
    st.session_state.username = username
    st.session_state.user_id = user_id
    st.session_state.logged_in = True



# ------------------ AUTH FORMS ------------------
def signup_form():
    st.title("Create Account")
    with st.form("signup_form", clear_on_submit=True):
        new_username = st.text_input("Enter Username*")
        new_user_email = st.text_input("Enter Email Address*")
        new_user_pas = st.text_input("Enter Password*", type="password")
        user_pas_conf = st.text_input("Confirm Password*", type="password")
        submitted = st.form_submit_button("Sign Up")

        """if submitted:
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
                        st.session_state.form = "signin_form"  """# switch to login form
        if submitted:
            if "" in [new_username, new_user_email, new_user_pas]:
                st.error("⚠️ Some fields are missing")
                return

            # Check if username or email already exists
            cur.execute("SELECT 1 FROM _users WHERE log = %s OR email = %s;", (new_username, new_user_email))
            if cur.fetchone():
                st.error("⚠️ Username or email already exists")
                return

            if new_user_pas != user_pas_conf:
                st.error("⚠️ Passwords do not match")
                return

            hashed_pw = hash_password(new_user_pas)

            # Insert and get the generated user ID
            cur.execute(
                "INSERT INTO _users (log, email, pass) VALUES (%s, %s, %s) RETURNING id;",
                (new_username, new_user_email, hashed_pw)
            )
            new_user_id = cur.fetchone()["id"]
            conn.commit()

            # Set session with new user
            set_user_session(new_username, new_user_id)
            st.success(f"✅ Account created successfully! Welcome {new_username} 🎉")
            st.session_state.form = "app_interface"
            st.rerun()


def signin_form():
    st.title("Sign In")
    with st.form("signin_form", clear_on_submit=True):
        username = st.text_input("Enter Username")
        user_pas = st.text_input("Enter Password", type="password")
        submitted = st.form_submit_button("Sign In")

        if submitted:
            cur.execute("SELECT * FROM _users WHERE log = %s;", (username,))
            user = cur.fetchone()

            if not user:
                st.error("❌ Invalid username or password")
                return

            stored_hash = user["pass"].encode("utf-8") if isinstance(user["pass"], str) else user["pass"]

            if check_password(user_pas, stored_hash):
                set_user_session(user["log"], user["id"])
                st.success(f"🎉 Welcome {user['log'].upper()}!")
                st.session_state.form = "app_interface"
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

# Add Sign Up button below login form
    st.write("---")
    if st.button("Create an Account"):
        st.session_state.form = "signup_form"
        st.rerun()

# ------------------ APP INTERFACE ------------------
def app_interface():
    # Logout button at the top right
    """col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("Log Out"):
            user_update("")
            st.session_state.form = "signin_form"
            st.rerun()"""
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("Log Out",key="logoutg"):
            st.session_state.clear()
            st.rerun()
        st.write(f"👋 Logged in as **{st.session_state.username.upper()}** (User ID: {st.session_state.user_id})")






