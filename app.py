# app.py
import streamlit as st
import pandas as pd
import openpyxl
from datetime import datetime, date, time as dt_time
from pathlib import Path

# =========================
# إعداد ملف Excel إذا لم يوجد
# =========================
file_name = "missions.xlsx"
file_path = Path(file_name)

if not file_path.exists():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Missions"
    ws.append(["Mission", "Date", "Time", "Finished"])
    wb.save(file_name)

# =========================
# دوال مساعدة
# =========================
def load_data():
    df = pd.read_excel(file_name)
    return df

def save_mission(mission, date_str, time_str):
    wb = openpyxl.load_workbook(file_name)
    ws = wb["Missions"]
    ws.append([mission, date_str, time_str, "No"])
    wb.save(file_name)

def mark_finished(index):
    df = pd.read_excel(file_name)
    df.at[index, "Finished"] = "Yes"
    df.to_excel(file_name, index=False)

# =========================
# واجهة التطبيق
# =========================
st.set_page_config(page_title="Mission Reminder Web App", layout="wide")
st.title("📌 Mission Reminder Web App")

# -------------------------
# إضافة مهمة جديدة
# -------------------------
st.subheader("➕ Add New Mission")
with st.form("add_mission_form"):
    mission = st.text_input("Mission")
    date_input = st.date_input("Date", date.today())
    time_input = st.time_input("Time", dt_time(hour=9, minute=0))
    submitted = st.form_submit_button("Add Mission")
    if submitted:
        if mission and date_input and time_input:
            save_mission(mission, date_input.strftime("%Y-%m-%d"), time_input.strftime("%H:%M"))
            st.success(f"Mission '{mission}' added successfully!")
        else:
            st.warning("Please fill all fields!")

# -------------------------
# عرض المهام + بحث + فلترة
# -------------------------
st.subheader("📊 All Missions")
df = load_data()

# شريط البحث
search_text = st.text_input("🔍 Search Mission")
if search_text:
    df = df[df["Mission"].str.contains(search_text, case=False)]

# فلترة بالتاريخ
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("From", value=date(2000,1,1))
with col2:
    end_date = st.date_input("To", value=date(2100,1,1))

df["Date"] = pd.to_datetime(df["Date"])
df_filtered = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]

st.dataframe(df_filtered)

# -------------------------
# تصدير
# -------------------------
st.subheader("📤 Export Missions")
col3, col4 = st.columns(2)
with col3:
    if st.button("📥 Export Excel"):
        export_name = f"missions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df_filtered.to_excel(export_name, index=False)
        st.success(f"Exported to {export_name}")

with col4:
    if st.button("📄 Export CSV"):
        export_name = f"missions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df_filtered.to_csv(export_name, index=False)
        st.success(f"Exported to {export_name}")

# -------------------------
# إشعارات بسيطة (Toast)
# -------------------------
st.subheader("⏰ Notifications")
now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
for idx, row in df_filtered.iterrows():
    if row["Finished"] == "No" and f"{row['Date'].strftime('%Y-%m-%d')} {row['Time']}" == now_str:
        st.toast(f"Mission Reminder: {row['Mission']} at {row['Time']}")
        mark_finished(idx)
