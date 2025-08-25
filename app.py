import streamlit as st
import pandas as pd
import os, tempfile
from sqlalchemy import create_engine, text
from datetime import datetime, date

# --- DB en carpeta escribible (válido en Streamlit Cloud) ---
DB_PATH = os.path.join(tempfile.gettempdir(), "school.db")
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)

# --- Crear tablas ---
def ensure_tables():
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run TEXT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            created_at TEXT
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS subjects(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS enrollments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            UNIQUE(student_id,subject_id,year),
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS assessments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            date TEXT,
            max_score REAL DEFAULT 100.0,
            weight REAL DEFAULT 1.0,
            FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS grades(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enrollment_id INTEGER NOT NULL,
            assessment_id INTEGER NOT NULL,
            score REAL,
            UNIQUE(enrollment_id,assessment_id),
            FOREIGN KEY(enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE,
            FOREIGN KEY(assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
        );
        """))

def q(sql, params=None):
    with engine.begin() as conn:
        res = conn.execute(text(sql), params or {})
        try:
            return pd.DataFrame(res.fetchall(), columns=res.keys())
        except Exception:
            return pd.DataFrame()

def exec_sql(sql, params=None):
    with engine.begin() as conn:
        conn.execute(text(sql), params or {})

# --- PANTALLAS ---
def ui_students():
    st.header("Estudiantes")
    with st.expander("Agregar / Editar / Eliminar", expanded=True):
        c1,c2,c3 = st.columns(3)
        with c1:
            run = st.text_input("RUN/RUT (opcional)")
            fn = st.text_input("Nombre *")
            ln = st.text_input("Apellido *")
        with c2:
            email = st.text_input("Email")
            mode = st.radio("Acción", ["Crear","Actualizar","Eliminar"], horizontal=True)
        with c3:
            sid = st.number_input("ID estudiante (Actualizar/Eliminar)", min_value=0, step=1)

        if st.button("Guardar estudiante"):
            if mode=="Crear":
                exec_sql("""INSERT INTO students(run,first_name,last_name,email,created_at)
                            VALUES(:r,:f,:l,:e,:c)""",
                         {"r":run or None, "f":fn, "l":ln, "e":email or None, "c":datetime.utcnow().isoformat()})
                st.success("Creado.")
            elif mode=="Actualizar":
                exec_sql("""UPDATE students SET run=:r, first_name=:f, last_name=:l, email=:e WHERE id=:id""",
                         {"r":run or None, "f":fn, "l":ln, "e":email or None, "id":int(sid)})
                st.success("Actualizado.")
            else:
                exec_sql("DELETE FROM students WHERE id=:id", {"id":int(sid)})
                st.warning("Eliminado.")
    st.dataframe(q("SELECT * FROM students ORDER BY id DESC"), use_container_width=True)

def ui_subjects():
    st.header("Asignaturas")
    with st.expander("Agregar / Editar / Eliminar", expanded=True):
        c1,c2,c3 = st.columns(3)
        with c1:
            code = st.text_input("Código *", placeholder="MAT7B")
            name = st.text_input("Nombre *", placeholder="Matemática")
        with c2:
            mode = st.radio("Acción", ["Crear","Actualizar","Eliminar"], horizontal=True)
        with c3:
            subj_id = st.number_input("ID asignatura (Actualizar/Eliminar)", min_value=0, step=1)

        if st.button("Guardar asignatura"):
            if mode=="Crear":
                exec_sql("INSERT INTO subjects(code,name) VALUES(:c,:n)", {"c":code, "n":name})
                st.success("Creada.")
            elif mode=="Actualizar":
                exec_sql("UPDATE subjects SET code=:c, name=:n WHERE id=:id",
                         {"c":code, "n":name, "id":int(subj_id)})
                st.success("Actualizada.")
            else:
                exec_sql("DELETE FROM subjects WHERE id=:id", {"id":int(subj_id)})
                st.warning("Eliminada.")
    st.dataframe(q("SELECT * FROM subjects ORDER BY id DESC"), use_container_width=True)

def ui_enrollments():
    st.header("Matrículas (Alumno ↔ Asignatura ↔ Año)")
    students = q("SELECT id, first_name||' '||last_name AS name FROM students ORDER BY name ASC")
    subjects = q("SELECT id, name FROM subjects ORDER BY name ASC")
    if students.empty or subjects.empty:
        st.info("Crea al menos un estudiante y una asignatura.")
        return

    with st.expander("Matricular / Desmatricular", expanded=True):
        c1,c2,c3 = st.columns(3)
        with c1:
            s_name = st.selectbox("Estudiante", students["name"])
            s_id = int(students.loc[students["name"]==s_name, "id"].iloc[0])
        with c2:
            sub_name = st.selectbox("Asignatura", subjects["name"])
            sub_id = int(subjects.loc[subjects["name"]==sub_name, "id"].iloc[0])
        with c3:
            yr = st.number_input("Año", min_value=2000, max_value=2100, value=date.today().year, step=1)
        c1_,c2_ = st.columns(2)
        with c1_:
            if st.button("Matricular"):
                try:
                    exec_sql("""INSERT INTO enrollments(student_id,subject_id,year)
                                VALUES(:s,:u,:y)""", {"s":s_id, "u":sub_id, "y":int(yr)})
                    st.success("Matriculado.")
                except Exception as e:
                    st.error(f"No se pudo matricular: {e}")
        with c2_:
            if st.button("Desmatricular"):
                exec_sql("""DELETE FROM enrollments WHERE student_id=:s AND subject_id=:u AND year=:y""",
                         {"s":s_id, "u":sub_id, "y":int(yr)})
                st.warning("Desmatriculado.")

    st.subheader("Matrículas")
    st.dataframe(q("""
        SELECT e.id, (st.first_name||' '||st.last_name) AS estudiante,
               su.name AS asignatura, e.year
        FROM enrollments e
        JOIN students st ON st.id=e.student_id
        JOIN subjects su ON su.id=e.subject_id
        ORDER BY e.year DESC, estudiante ASC, asignatura ASC
    """), use_container_width=True)

def ui_assessments():
    st.header("Evaluaciones")
    subjects = q("SELECT id, name FROM subjects ORDER BY name ASC")
    if subjects.empty:
        st.info("Crea asignaturas primero.")
        return
    with st.expander("Crear / Editar / Eliminar", expanded=True):
        c1,c2,c3 = st.columns(3)
        with c1:
            sub_name = st.selectbox("Asignatura", subjects["name"])
            sub_id = int(subjects.loc[subjects["name"]==sub_name, "id"].iloc[0])
            title = st.text_input("Título *", placeholder="Prueba 1")
        with c2:
            dt = st.date_input("Fecha", value=date.today())
            max_score = st.number_input("Puntaje máximo", value=100.0)
        with c3:
            weight = st.number_input("Ponderación", value=1.0, step=0.1)
            mode = st.radio("Acción", ["Crear","Actualizar","Eliminar"], horizontal=True)
            aid = st.number_input("ID evaluación (Actualizar/Eliminar)", min_value=0, step=1)

        if st.button("Guardar evaluación"):
            if mode=="Crear":
                exec_sql("""INSERT INTO assessments(subject_id,title,date,max_score,weight)
                            VALUES(:s,:t,:d,:m,:w)""",
                         {"s":sub_id, "t":title, "d":str(dt), "m":float(max_score), "w":float(weight)})
                st.success("Creada.")
            elif mode=="Actualizar":
                exec_sql("""UPDATE assessments SET subject_id=:s, title=:t, date=:d, max_score=:m, weight=:w
                            WHERE id=:id""",
                         {"s":sub_id, "t":title, "d":str(dt), "m":float(max_score), "w":float(weight), "id":int(aid)})
                st.success("Actualizada.")
            else:
                exec_sql("DELETE FROM assessments WHERE id=:id", {"id":int(aid)})
                st.warning("Eliminada.")

    st.dataframe(q("""
        SELECT a.id, su.name AS asignatura, a.title, a.date, a.max_score, a.weight
        FROM assessments a JOIN subjects su ON su.id=a.subject_id
        ORDER BY a.date DESC
    """), use_container_width=True)

def ui_grades():
    st.header("Notas")
    # Elegir año y asignatura para simplificar la carga
    years = q("SELECT DISTINCT year FROM enrollments ORDER BY year DESC")
    subjects = q("SELECT id, name FROM subjects ORDER BY name ASC")
    if years.empty or subjects.empty:
        st.info("Asegúrate de tener matrículas y asignaturas.")
        return
    yr = st.selectbox("Año", years["year"])
    sub_name = st.selectbox("Asignatura", subjects["name"])
    sub_id = int(subjects.loc[subjects["name"]==sub_name,"id"].iloc[0])

    # Evaluaciones de esa asignatura
    assessments = q("SELECT id, title, max_score FROM assessments WHERE subject_id=:s ORDER BY date ASC", {"s":sub_id})
    if assessments.empty:
        st.info("Crea evaluaciones para esta asignatura.")
        return
    assess_title = st.selectbox("Evaluación", assessments["title"])
    aid = int(assessments.loc[assessments["title"]==assess_title,"id"].iloc[0])
    max_sc = float(assessments.loc[assessments["title"]==assess_title,"max_score"].iloc[0])

    # Estudiantes matriculados en esa asignatura y año
    enrolls = q("""
        SELECT e.id AS enrollment_id, st.first_name||' '||st.last_name AS estudiante
        FROM enrollments e
        JOIN students st ON st.id=e.student_id
        WHERE e.subject_id=:s AND e.year=:y
        ORDER BY estudiante ASC
    """, {"s":sub_id, "y":int(yr)})
    if enrolls.empty:
        st.info("No hay estudiantes matriculados en esta asignatura/año.")
        return

    st.write(f"Ingrese notas (0–{max_sc}):")
    for _, row in enrolls.iterrows():
        col1, col2 = st.columns([3,1])
        with col1:
            st.text(row["estudiante"])
        with col2:
            current = q("""SELECT score FROM grades WHERE enrollment_id=:e AND assessment_id=:a""",
                        {"e":int(row["enrollment_id"]), "a":aid})
            val = float(current["score"].iloc[0]) if not current.empty else 0.0
            score = st.number_input(f"Nota - {row['estudiante']}", min_value=0.0, max_value=max_sc,
                                    value=val, step=0.1, key=f"score_{row['enrollment_id']}")
            if st.button(f"Guardar {row['estudiante']}", key=f"save_{row['enrollment_id']}"):
                if current.empty:
                    exec_sql("""INSERT INTO grades(enrollment_id,assessment_id,score)
                                VALUES(:e,:a,:s)""", {"e":int(row["enrollment_id"]), "a":aid, "s":float(score)})
                else:
                    exec_sql("""UPDATE grades SET score=:s WHERE enrollment_id=:e AND assessment_id=:a""",
                             {"s":float(score), "e":int(row["enrollment_id"]), "a":aid})
                st.success("Guardado.")

    st.subheader("Resumen de notas (todas las evaluaciones)")
    gradebook = q("""
        SELECT st.first_name||' '||st.last_name AS estudiante,
               su.name AS asignatura, a.title, a.max_score, a.weight, g.score
        FROM grades g
        JOIN enrollments e ON e.id=g.enrollment_id
        JOIN students st ON st.id=e.student_id
        JOIN assessments a ON a.id=g.assessment_id
        JOIN subjects su ON su.id=a.subject_id
        WHERE e.subject_id=:s AND e.year=:y
        ORDER BY estudiante ASC, a.date ASC
    """, {"s":sub_id, "y":int(yr)})
    st.dataframe(gradebook, use_container_width=True)

def ui_reports():
    st.header("Informe para apoderado")
    years = q("SELECT DISTINCT year FROM enrollments ORDER BY year DESC")
    if years.empty:
        st.info("Registra matrículas primero.")
        return
    yr = st.selectbox("Año", years["year"])

    students = q("""
        SELECT DISTINCT st.id, st.first_name||' '||st.last_name AS nombre
        FROM enrollments e JOIN students st ON st.id=e.student_id
        WHERE e.year=:y
        ORDER BY nombre ASC
    """, {"y":int(yr)})

    if students.empty:
        st.info("No hay estudiantes matriculados ese año.")
        return

    s_name = st.selectbox("Estudiante", students["nombre"])
    s_id = int(students.loc[students["nombre"]==s_name,"id"].iloc[0])

    # Notas del estudiante por asignatura
    df = q("""
        SELECT su.name AS asignatura, a.title, a.max_score, a.weight, g.score
        FROM grades g
        JOIN enrollments e ON e.id=g.enrollment_id
        JOIN assessments a ON a.id=g.assessment_id
        JOIN subjects su ON su.id=a.subject_id
        WHERE e.student_id=:s AND e.year=:y
        ORDER BY su.name ASC, a.date ASC
    """, {"s":s_id, "y":int(yr)})

    if df.empty:
        st.info("Este estudiante aún no registra notas.")
        return

    df["pct"] = df["score"] / df["max_score"]
    por_asignatura = (
        df.groupby("asignatura")
          .apply(lambda x: (x["pct"]*x["weight"]).sum()/x["weight"].sum())
          .reset_index(name="prom_ponderado")
    )
    por_asignatura["prom_ponderado_%"] = (por_asignatura["prom_ponderado"]*100).round(2)

    promedio_general = round((por_asignatura["prom_ponderado"].mean()*100), 2)

    st.subheader(f"Informe {s_name} - {yr}")
    st.write(f"**Promedio general:** {promedio_general}%")
    st.dataframe(por_asignatura[["asignatura","prom_ponderado_%"]]
                 .rename(columns={"asignatura":"Asignatura","prom_ponderado_%":"Promedio (%)"}),
                 use_container_width=True)

    csv = por_asignatura[["asignatura","prom_ponderado_%"]].to_csv(index=False).encode("utf-8")
    st.download_button("Descargar informe (CSV)", data=csv,
                       file_name=f"informe_{s_name.replace(' ','_')}_{yr}.csv", mime="text/csv")

def main():
    st.set_page_config(page_title="Plataforma Escolar - MVP", layout="wide")
    ensure_tables()
    st.sidebar.title("Plataforma Escolar - MVP")
    page = st.sidebar.radio("Ir a", ["Estudiantes","Asignaturas","Matrículas","Evaluaciones","Notas","Informes"], index=0)
    if page=="Estudiantes":
        ui_students()
    elif page=="Asignaturas":
        ui_subjects()
    elif page=="Matrículas":
        ui_enrollments()
    elif page=="Evaluaciones":
        ui_assessments()
    elif page=="Notas":
        ui_grades()
    else:
        ui_reports()

if __name__ == "__main__":
    main()
