import streamlit as st
import requests
import pandas as pd
import datetime
import os

st.set_page_config(page_title="SolarDelta | Free Solar Health Check", page_icon="☀️", layout="centered")

# --- FOUNDER CONTROLS (Sidebar) ---
# This will only show up if the leads.csv file has been created by someone submitting an email
if os.path.exists("leads.csv"):
    with open("leads.csv", "r") as f:
        st.sidebar.caption("⚙️ Admin Controls")
        st.sidebar.download_button(
            label="📥 Download Leads CSV", 
            data=f, 
            file_name="leads.csv", 
            mime="text/csv"
        )

st.title("☀️ SolarDelta: Financial Health Check")
st.markdown("Find out if silent hardware faults or micro-shading are costing you money.")

# The "Lead Magnet" UI
st.subheader("Step 1: The 30-Second Quick Check")
st.markdown("Enter your basic system details below. We will pull the 30-year local weather data from the National Renewable Energy Laboratory (NREL) and tell you exactly what your system *should* have produced last month.")

col1, col2, col3 = st.columns(3)
zip_code = col1.text_input("Zip Code", value="92130")
system_size = col2.number_input("System Size (kW)", value=8.5, step=0.5)
actual_kwh = col3.number_input("Last Month's Output (kWh)", value=550, step=50)

if st.button("Calculate Financial Loss", type="primary"):
    with st.spinner("Pulling NREL Irradiance Models..."):
        try:
            # We use a rough lat/lon mapping for the MVP demo
            lat, lon = 32.9489, -117.2107 
            
            url = "https://developer.nrel.gov/api/pvwatts/v8.json"
            params = {
                "api_key": "DEMO_KEY", "lat": lat, "lon": lon,
                "system_capacity": system_size, "azimuth": 180, "tilt": 20,
                "array_type": 1, "module_type": 0, "losses": 14
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            # Assuming "Last Month" is January (Index 0)
            expected_kwh = data['outputs']['ac_monthly'][0]
            
            health_score = (actual_kwh / expected_kwh) * 100
            lost_kwh = expected_kwh - actual_kwh
            financial_loss = lost_kwh * 0.45 # Assuming $0.45/kWh CA rates
            
            st.divider()
            st.subheader("📊 Your Results")
            
            if health_score >= 95:
                st.success(f"**System Healthy!** You
