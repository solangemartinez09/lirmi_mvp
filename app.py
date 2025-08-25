import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

engine = create_engine("sqlite:///school.db", future=True)

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            created_at TEXT
        );
    """))

st.title("Lirmi MVP - Sanity Check")
name = st.text_input("Nombre del estudiante")

if st.button("Agregar") and name.strip():
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO students (name, created_at) VALUES (:n, :c)"),
            {"n": name.strip(), "c": datetime.utcnow().isoformat()}
        )
    st.success("Guardado")

df = pd.read_sql_query("SELECT * FROM students ORDER BY id DESC", engine)
st.dataframe(df, use_container_width=True)
