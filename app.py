import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, date
<<<<<<< HEAD

DB_PATH = "school.db"
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)

# -------------------- SIMPLE AUTH (MVP) --------------------
def ensure_auth_table():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'admin'
            );
        """))
        user = conn.execute(text("SELECT * FROM users WHERE username='admin'")).fetchone()
        if not user:
            conn.execute(text("INSERT INTO users (username, password, role) VALUES ('admin','admin','admin')"))

def login_form():
    st.sidebar.subheader("Login")
    u = st.sidebar.text_input("Username", value="")
    p = st.sidebar.text_input("Password", value="", type="password")
    if st.sidebar.button("Sign in"):
        with engine.begin() as conn:
            row = conn.execute(text("SELECT * FROM users WHERE username=:u AND password=:p"), {"u": u, "p": p}).fetchone()
        if row:
            st.session_state["auth"] = {"username": u, "role": row.role}
            st.experimental_rerun()
        else:
            st.sidebar.error("Invalid credentials")

def logout_button():
    if st.sidebar.button("Logout"):
        st.session_state.pop("auth", None)
        st.experimental_rerun()

# -------------------- DB SCHEMA --------------------
def ensure_tables():
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run TEXT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            grade_level TEXT,
            email TEXT,
            phone TEXT,
            created_at TEXT
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            grade_band TEXT,
            year INTEGER
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            year INTEGER,
            UNIQUE(student_id, course_id, year),
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            date TEXT,
            max_score REAL DEFAULT 100.0,
            weight REAL DEFAULT 1.0,
            FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enrollment_id INTEGER NOT NULL,
            assessment_id INTEGER NOT NULL,
            score REAL,
            UNIQUE(enrollment_id, assessment_id),
            FOREIGN KEY(enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE,
            FOREIGN KEY(assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enrollment_id INTEGER NOT NULL,
            session_date TEXT NOT NULL,
            status TEXT NOT NULL,
            remarks TEXT,
            UNIQUE(enrollment_id, session_date),
            FOREIGN KEY(enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE
        );
        """))

# -------------------- HELPERS --------------------
def run_query(sql, params=None):
    with engine.begin() as conn:
        res = conn.execute(text(sql), params or {})
        try:
            df = pd.DataFrame(res.fetchall(), columns=res.keys())
        except Exception:
            df = pd.DataFrame()
    return df

def exec_sql(sql, params=None):
    with engine.begin() as conn:
        conn.execute(text(sql), params or {})

# -------------------- SCREENS --------------------
def screen_students():
    st.header("Students")
    with st.expander("Add / Edit student", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            run = st.text_input("RUN/RUT (optional)")
            first_name = st.text_input("First name *")
            last_name = st.text_input("Last name *")
        with col2:
            grade_level = st.text_input("Grade level (e.g., 7°B, 3° Medio A)")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
        with col3:
            mode = st.radio("Mode", ["Create", "Update", "Delete"], horizontal=True)
            student_id = st.number_input("Student ID (for Update/Delete)", min_value=0, step=1)

        if st.button("Submit"):
            if mode == "Create":
                exec_sql("""
                    INSERT INTO students (run, first_name, last_name, grade_level, email, phone, created_at)
                    VALUES (:run, :fn, :ln, :gl, :em, :ph, :ca)
                """, {"run": run or None, "fn": first_name, "ln": last_name, "gl": grade_level or None,
                      "em": email or None, "ph": phone or None, "ca": datetime.utcnow().isoformat()})
                st.success("Student created.")
            elif mode == "Update":
                exec_sql("""
                    UPDATE students SET run=:run, first_name=:fn, last_name=:ln, grade_level=:gl, email=:em, phone=:ph
                    WHERE id=:id
                """, {"run": run or None, "fn": first_name, "ln": last_name, "gl": grade_level or None,
                      "em": email or None, "ph": phone or None, "id": int(student_id)})
                st.success("Student updated.")
            else:
                exec_sql("DELETE FROM students WHERE id=:id", {"id": int(student_id)})
                st.warning("Student deleted.")

    df = run_query("SELECT * FROM students ORDER BY id DESC")
    st.dataframe(df, use_container_width=True)

# -------------------- MAIN --------------------
def main():
    st.set_page_config(page_title="School Platform MVP", layout="wide")
    ensure_auth_table()
    ensure_tables()

    st.sidebar.title("MVP: School Platform")
    if "auth" not in st.session_state:
        st.session_state["auth"] = None

    if st.session_state["auth"] is None:
        login_form()
        st.stop()

    logout_button()
    page = st.sidebar.radio("Go to", ["Students"], index=0)
    if page == "Students":
        screen_students()

if __name__ == "__main__":
    main()
=======

DB_PATH = "school.db"
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)

# -------------------- SIMPLE AUTH (MVP) --------------------
def ensure_auth_table():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'admin'
            );
        """))
        user = conn.execute(text("SELECT * FROM users WHERE username='admin'")).fetchone()
        if not user:
            conn.execute(text("INSERT INTO users (username, password, role) VALUES ('admin','admin','admin')"))

def login_form():
    st.sidebar.subheader("Login")
    u = st.sidebar.text_input("Username", value="")
    p = st.sidebar.text_input("Password", value="", type="password")
    if st.sidebar.button("Sign in"):
        with engine.begin() as conn:
            row = conn.execute(text("SELECT * FROM users WHERE username=:u AND password=:p"), {"u": u, "p": p}).fetchone()
        if row:
            st.session_state["auth"] = {"username": u, "role": row.role}
            st.experimental_rerun()
        else:
            st.sidebar.error("Invalid credentials")

def logout_button():
    if st.sidebar.button("Logout"):
        st.session_state.pop("auth", None)
        st.experimental_rerun()

# -------------------- DB SCHEMA --------------------
def ensure_tables():
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run TEXT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            grade_level TEXT,
            email TEXT,
            phone TEXT,
            created_at TEXT
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            grade_band TEXT,
            year INTEGER
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            year INTEGER,
            UNIQUE(student_id, course_id, year),
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            date TEXT,
            max_score REAL DEFAULT 100.0,
            weight REAL DEFAULT 1.0,
            FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enrollment_id INTEGER NOT NULL,
            assessment_id INTEGER NOT NULL,
            score REAL,
            UNIQUE(enrollment_id, assessment_id),
            FOREIGN KEY(enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE,
            FOREIGN KEY(assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enrollment_id INTEGER NOT NULL,
            session_date TEXT NOT NULL,
            status TEXT NOT NULL,
            remarks TEXT,
            UNIQUE(enrollment_id, session_date),
            FOREIGN KEY(enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE
        );
        """))

# -------------------- HELPERS --------------------
def run_query(sql, params=None):
    with engine.begin() as conn:
        res = conn.execute(text(sql), params or {})
        try:
            df = pd.DataFrame(res.fetchall(), columns=res.keys())
        except Exception:
            df = pd.DataFrame()
    return df

def exec_sql(sql, params=None):
    with engine.begin() as conn:
        conn.execute(text(sql), params or {})

# -------------------- SCREENS --------------------
def screen_students():
    st.header("Students")
    with st.expander("Add / Edit student", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            run = st.text_input("RUN/RUT (optional)")
            first_name = st.text_input("First name *")
            last_name = st.text_input("Last name *")
        with col2:
            grade_level = st.text_input("Grade level (e.g., 7°B, 3° Medio A)")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
        with col3:
            mode = st.radio("Mode", ["Create", "Update", "Delete"], horizontal=True)
            student_id = st.number_input("Student ID (for Update/Delete)", min_value=0, step=1)

        if st.button("Submit"):
            if mode == "Create":
                exec_sql("""
                    INSERT INTO students (run, first_name, last_name, grade_level, email, phone, created_at)
                    VALUES (:run, :fn, :ln, :gl, :em, :ph, :ca)
                """, {"run": run or None, "fn": first_name, "ln": last_name, "gl": grade_level or None,
                      "em": email or None, "ph": phone or None, "ca": datetime.utcnow().isoformat()})
                st.success("Student created.")
            elif mode == "Update":
                exec_sql("""
                    UPDATE students SET run=:run, first_name=:fn, last_name=:ln, grade_level=:gl, email=:em, phone=:ph
                    WHERE id=:id
                """, {"run": run or None, "fn": first_name, "ln": last_name, "gl": grade_level or None,
                      "em": email or None, "ph": phone or None, "id": int(student_id)})
                st.success("Student updated.")
            else:
                exec_sql("DELETE FROM students WHERE id=:id", {"id": int(student_id)})
                st.warning("Student deleted.")

    df = run_query("SELECT * FROM students ORDER BY id DESC")
    st.dataframe(df, use_container_width=True)

# -------------------- MAIN --------------------
def main():
    st.set_page_config(page_title="School Platform MVP", layout="wide")
    ensure_auth_table()
    ensure_tables()

    st.sidebar.title("MVP: School Platform")
    if "auth" not in st.session_state:
        st.session_state["auth"] = None

    if st.session_state["auth"] is None:
        login_form()
        st.stop()

    logout_button()
    page = st.sidebar.radio("Go to", ["Students"], index=0)
    if page == "Students":
        screen_students()

if __name__ == "__main__":
    main()


>>>>>>> 1550442 (Agregar código real del proyecto y dependencias)
