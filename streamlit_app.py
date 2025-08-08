# modern_grades_dashboard.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statistics import mode, StatisticsError
import re
import tempfile
import os
from PIL import Image as PILImage
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

st.set_page_config(page_title="Mokinių pasiekimų analizė", layout="wide")

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3, h4 {
        font-family: 'Segoe UI', sans-serif;
        color: #2F4F4F;
    }
</style>
""", unsafe_allow_html=True)

st.title("📘 Mokinių pasiekimų analizė")

uploaded_file = st.file_uploader("📂 Įkelkite Excel (.xlsx) failą su suvestine", type=["xlsx"])

if uploaded_file:
    df_raw = pd.read_excel(uploaded_file, sheet_name="Pasiekimų ir lankomumo", skiprows=3)
    df_raw = df_raw.rename(columns={df_raw.columns[0]: "Eil_Nr", df_raw.columns[1]: "Vardas_Pavarde"})
    df_raw = df_raw[df_raw["Vardas_Pavarde"].notna() & df_raw["Eil_Nr"].notna()]

    attendance_cols = [
        "Praleistos pamokos",
        "Pateisintos dėl ligos",
        "Pateisintos dėl kitų priežasčių",
        "Nepateisinta"
    ]
    attendance_df = df_raw[["Vardas_Pavarde"] + [col for col in attendance_cols if col in df_raw.columns]].copy()

    subject_columns = [col for col in df_raw.columns[2:25] if all(x not in str(col).lower() for x in ["vidurkis", "metinis", "pusm", "socialinė"])]

    def extract_numeric(x):
        match = re.search(r"(\d+)", str(x))
        return int(match.group(1)) if match else None

    df_raw[subject_columns] = df_raw[subject_columns].applymap(extract_numeric)

    df_long = df_raw.melt(id_vars=["Vardas_Pavarde"], value_vars=subject_columns, var_name="Dalykas", value_name="Ivertinimas")
    df_long = df_long[df_long["Ivertinimas"].notna()]

    st.sidebar.header("🎛️ Filtravimas")
    mokinys = st.sidebar.selectbox("Pasirinkite mokinį", ["Visi"] + sorted(df_long["Vardas_Pavarde"].unique()))
    dalykas = st.sidebar.selectbox("Pasirinkite dalyką", ["Visi"] + sorted(df_long["Dalykas"].unique()))

    filtered_df = df_long.copy()
    if mokinys != "Visi":
        filtered_df = filtered_df[filtered_df["Vardas_Pavarde"] == mokinys]
    if dalykas != "Visi":
        filtered_df = filtered_df[filtered_df["Dalykas"] == dalykas]

    mean_score = filtered_df["Ivertinimas"].mean()
    std_score = filtered_df["Ivertinimas"].std()
    try:
        moda_score = mode(filtered_df["Ivertinimas"])
    except StatisticsError:
        moda_score = "—"

    record_count = len(filtered_df)
    student_count = filtered_df["Vardas_Pavarde"].nunique()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📊 Vidurkis", f"{mean_score:.2f}")
    col2.metric("📌 Moda", moda_score)
    col3.metric("📉 Standartinis nuokrypis", f"{std_score:.2f}")
    col4.metric("🧾 Įrašų skaičius", record_count)
    col5.metric("👥 Mokinių skaičius", student_count)

    st.markdown("### 📚 Vidutiniai įvertinimai pagal dalyką")
    pastel_color = "#A3C4F3"
    subject_avg = df_long.groupby("Dalykas")["Ivertinimas"].mean().sort_values()
    fig1, ax1 = plt.subplots()
    bars1 = ax1.barh(subject_avg.index, subject_avg.values, color=pastel_color)
    ax1.set_xlabel("Vidurkis")
    ax1.set_xlim(0, 10)
    for bar in bars1:
        width = bar.get_width()
        ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2, f"{width:.1f}", va='center', fontsize=9)
    st.pyplot(fig1)

    st.markdown("### 🏆 Mokiniai pagal bendrą vidurkį")
    student_avg = df_long.groupby("Vardas_Pavarde")["Ivertinimas"].mean().sort_values(ascending=False)
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    bars2 = ax2.barh(student_avg.index[::-1], student_avg.values[::-1], color="#D3D3D3")
    if mokinys != "Visi":
        for i, label in enumerate(student_avg.index[::-1]):
            if label == mokinys:
                bars2[i].set_color(pastel_color)
    for bar in bars2:
        width = bar.get_width()
        ax2.text(width + 0.1, bar.get_y() + bar.get_height()/2, f"{width:.1f}", va='center', fontsize=9)
    ax2.set_xlabel("Vidurkis")
    ax2.set_xlim(0, 10)
    st.pyplot(fig2)

    def get_level(score):
        if score >= 9: return "Aukštesnysis (9–10)"
        elif score >= 7: return "Pagrindinis (7–8)"
        elif score >= 5: return "Patenkinamas (5–6)"
        elif score == 4: return "Slenkstinis (4)"
        else: return "Nepatenkinamas (<4)"

    st.markdown("### 📊 Pasiekimų lygių pasiskirstymas")
    level_counts = filtered_df["Ivertinimas"].apply(get_level).value_counts().sort_index()
    fig3, ax3 = plt.subplots()
    bars3 = ax3.bar(level_counts.index, level_counts.values, color="#C7D9B7")
    for bar in bars3:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2, height + 0.5, str(height), ha='center', fontsize=9)
    ax3.set_ylabel("Mokinių skaičius")
    st.pyplot(fig3)

    st.markdown("### 📋 Mokinių įvertinimų lentelė su pasiekimų lygiais")
    table_df = filtered_df.copy()
    table_df["Pasiekimų lygis"] = table_df["Ivertinimas"].apply(get_level)
    st.dataframe(table_df[["Vardas_Pavarde", "Dalykas", "Ivertinimas", "Pasiekimų lygis"]], use_container_width=True)

    def generate_recommendations(student_df):
        avg = student_df["Ivertinimas"].mean()
        if avg >= 9:
            return "Puikūs rezultatai. Rekomenduojame tęsti tokiu pačiu tempu."
        elif avg >= 7:
            return "Geri pasiekimai. Galima skirti daugiau dėmesio sunkesniems dalykams."
        elif avg >= 5:
            return "Vidutiniai rezultatai. Rekomenduojame papildomas konsultacijas."
        else:
            return "Silpni rezultatai. Būtina stipri pagalba ir dažnesnės konsultacijos."

    FONT_PATH = "DejaVuSans.ttf"
    pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))

    if st.button("📄 Generuoti PDF ataskaitą"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
            styles = getSampleStyleSheet()

            header_style = ParagraphStyle(name='Header', fontSize=18, leading=22, spaceAfter=12, fontName='DejaVu')
            normal_style = ParagraphStyle(name='NormalLT', fontName='DejaVu', fontSize=10, leading=12)
            bold_style = ParagraphStyle(name='BoldLT', fontName='DejaVu', fontSize=10, leading=12, spaceAfter=6, textColor=colors.black, bulletFontName='DejaVu')

            story = []
            story.append(Paragraph("📘 Mokinių pasiekimų ataskaita", header_style))

            if mokinys != "Visi":
                student_df = df_long[df_long["Vardas_Pavarde"] == mokinys]
                story.append(Paragraph(f"<b>Mokinys:</b> {mokinys}", normal_style))
                data = [["Dalykas", "Įvertinimas"]] + [[row["Dalykas"], str(row["Ivertinimas"])] for _, row in student_df.iterrows()]
                table = Table(data, hAlign='LEFT')
                table.setStyle(TableStyle([
                    ('FONTNAME', (0,0), (-1,-1), 'DejaVu'),
                    ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                    ('FONTNAME', (0,0), (-1,0), 'DejaVu')
                ]))
                story.append(table)
                story.append(Spacer(1, 0.5*cm))
            else:
                story.append(Paragraph("<b>Kiekvieno dalyko klasės vidurkiai:</b>", bold_style))
                subject_avg_df = subject_avg.reset_index()
                subject_avg_table = [["Dalykas", "Vidurkis"]] + [[row["Dalykas"], f"{row['Ivertinimas']:.2f}"] for _, row in subject_avg_df.iterrows()]
                table = Table(subject_avg_table, hAlign='LEFT')
                table.setStyle(TableStyle([
                    ('FONTNAME', (0,0), (-1,-1), 'DejaVu'),
                    ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                    ('FONTNAME', (0,0), (-1,0), 'DejaVu')
                ]))
                story.append(table)
                story.append(Spacer(1, 0.5*cm))

            fig_paths = []
            for i, fig in enumerate([fig1, fig2, fig3]):
                fig_path = os.path.join(tempfile.gettempdir(), f"fig_{i}.png")
                fig.savefig(fig_path, bbox_inches="tight", dpi=300)
                fig_paths.append(fig_path)

            for path in fig_paths:
                img = PILImage.open(path)
                iw, ih = img.size
                aspect = ih / iw
                target_width = 16 * cm
                target_height = target_width * aspect
                story.append(Image(path, width=target_width, height=target_height))
                story.append(Spacer(1, 0.5*cm))

            doc.build(story)

            st.success("✅ PDF ataskaita sugeneruota")
            st.download_button("📥 Atsisiųsti PDF", data=open(tmp.name, "rb"), file_name="ataskaita.pdf")
