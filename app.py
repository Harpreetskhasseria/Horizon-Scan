<<<<<<< HEAD
# app.py

import streamlit as st
import pandas as pd
import json
import subprocess
from exclusion_agent import classify_entries

st.set_page_config(page_title="Regulatory News Classifier", layout="wide")
st.title("📢 Regulatory News Intelligence Platform")

# ✅ Regulators list (hardcoded to match new scraper)
regulators = [
    "White House",
    "CFPB",
    "Federal Reserve",
    "BIS",
    "OCC",
    "FDIC"
]

# ✅ Sidebar UI
st.sidebar.header("Select Inputs")
selected_regulators = st.sidebar.multiselect("Select Regulators:", regulators, default=regulators)
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

# ✅ Run scraper button
if st.sidebar.button("Run Analysis"):
    formatted_start = start_date.strftime("%Y-%m-%d")
    formatted_end = end_date.strftime("%Y-%m-%d")
    st.write(f"📅 Running for Date Range: {formatted_start} to {formatted_end}")
    st.write("🚀 Launching external scraper...")

    # ✅ Call scraper script via subprocess
    try:
        subprocess.run(
            ["python", "gov_updates_llm_scraper.py", formatted_start, formatted_end] + selected_regulators,
            check=True
        )
        st.success("✅ Scraping completed successfully.")
    except subprocess.CalledProcessError as e:
        st.error("❌ Error running the scraper.")
        st.stop()

    # ✅ Load results from scraper_output.json
    try:
        with open("scraper_output.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        st.error("❌ scraper_output.json not found.")
        st.stop()

    # ✅ Summary table
    st.subheader("📊 Collection Summary")
    summary_data = [
        {"Regulator": r["Regulator"], "Method": r["Method"], "Records": r["Count"], "Source URL": r["SourceURL"]}
        for r in data
    ]
    st.table(pd.DataFrame(summary_data))

    # ✅ Gather all entries
    all_entries = []
    for r in data:
        all_entries.extend(r["Entries"])

    if not all_entries:
        st.warning("⚠️ No records found for the selected range.")
    else:
        with st.spinner("🤖 Classifying entries with LLM..."):
            classified = classify_entries(all_entries)

        st.subheader("✅ Final Classified Updates")
        df = pd.DataFrame(classified)
        st.dataframe(df, use_container_width=True)

        # ✅ CSV download
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, file_name="classified_regulatory_updates.csv")
=======
# app.py

import streamlit as st
import pandas as pd
import json
import subprocess
from exclusion_agent import classify_entries

st.set_page_config(page_title="Regulatory News Classifier", layout="wide")
st.title("📢 Regulatory News Intelligence Platform")

# ✅ Regulators list (hardcoded to match new scraper)
regulators = [
    "White House",
    "CFPB",
    "Federal Reserve",
    "BIS",
    "OCC",
    "FDIC"
]

# ✅ Sidebar UI
st.sidebar.header("Select Inputs")
selected_regulators = st.sidebar.multiselect("Select Regulators:", regulators, default=regulators)
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

# ✅ Run scraper button
if st.sidebar.button("Run Analysis"):
    formatted_start = start_date.strftime("%Y-%m-%d")
    formatted_end = end_date.strftime("%Y-%m-%d")
    st.write(f"📅 Running for Date Range: {formatted_start} to {formatted_end}")
    st.write("🚀 Launching external scraper...")

    # ✅ Call scraper script via subprocess
    try:
        subprocess.run(
            ["python", "gov_updates_llm_scraper.py", formatted_start, formatted_end] + selected_regulators,
            check=True
        )
        st.success("✅ Scraping completed successfully.")
    except subprocess.CalledProcessError as e:
        st.error("❌ Error running the scraper.")
        st.stop()

    # ✅ Load results from scraper_output.json
    try:
        with open("scraper_output.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        st.error("❌ scraper_output.json not found.")
        st.stop()

    # ✅ Summary table
    st.subheader("📊 Collection Summary")
    summary_data = [
        {"Regulator": r["Regulator"], "Method": r["Method"], "Records": r["Count"], "Source URL": r["SourceURL"]}
        for r in data
    ]
    st.table(pd.DataFrame(summary_data))

    # ✅ Gather all entries
    all_entries = []
    for r in data:
        all_entries.extend(r["Entries"])

    if not all_entries:
        st.warning("⚠️ No records found for the selected range.")
    else:
        with st.spinner("🤖 Classifying entries with LLM..."):
            classified = classify_entries(all_entries)

        st.subheader("✅ Final Classified Updates")
        df = pd.DataFrame(classified)
        st.dataframe(df, use_container_width=True)

        # ✅ CSV download
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, file_name="classified_regulatory_updates.csv")
>>>>>>> 7c4bb7b725c9e17e233f7fa5e8b6fa52bc11bf06
