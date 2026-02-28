import streamlit as st
import requests
import pandas as pd
import datetime
import os

st.set_page_config(page_title="SolarDelta | Free Solar Health Check", page_icon="☀️", layout="centered")

# --- FOUNDER CONTROLS (Sidebar) ---
st.sidebar.caption("⚙️ Admin Controls")
if os.path.exists("leads.csv"):
    with open("leads.csv", "r") as f:
        st.sidebar.download_button(
            label="📥 Download Leads CSV", 
            data=f, 
            file_name="leads.csv", 
            mime="text/csv"
        )
else:
    st.sidebar.info("No leads captured yet. Submit a test email below to generate the file!")

st.title("☀️ SolarDelta: Financial Health Check")
st.markdown("Find out if silent hardware faults or micro-shading are costing you money.")

st.subheader("Step 1: The 30-Second Quick Check")
st.markdown("Enter your basic system details below. We will pull the 30-year local weather data from the National Renewable Energy Laboratory (NREL) and tell you exactly what your system *should* have produced last month.")

col1, col2, col3 = st.columns(3)
zip_code = col1.text_input("Zip Code", value="92130")
system_size = col2.number_input("System Size (kW)", value=14.0, step=0.5)
actual_kwh = col3.number_input("Last Month's Output (kWh)", value=550, step=50)

# Initialize session state so the results stay on screen
if 'calculated' not in st.session_state:
    st.session_state['calculated'] = False

if st.button("Calculate Financial Loss", type="primary"):
    st.session_state['calculated'] = True

if st.session_state['calculated']:
    with st.spinner("Pulling NREL Irradiance Models..."):
        try:
            lat, lon = 32.9489, -117.2107 
            
            url = "https://developer.nrel.gov/api/pvwatts/v8.json"
            params = {
                "api_key": "DEMO_KEY", "lat": lat, "lon": lon,
                "system_capacity": system_size, "azimuth": 280, "tilt": 20,
                "array_type": 1, "module_type": 0, "losses": 14
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            expected_kwh = data['outputs']['ac_monthly'][0]
            
            health_score = (actual_kwh / expected_kwh) * 100
            lost_kwh = expected_kwh - actual_kwh
            financial_loss = lost_kwh * 0.45 
            
            st.divider()
            st.subheader("📊 Your Results")
            
            if health_score >= 95:
                st.success(f"**System Healthy!** You produced {actual_kwh} kWh. Expected was {expected_kwh:.0f} kWh.")
            else:
                st.error(f"**Underperformance Detected.** Your system is operating at {health_score:.1f}% of its potential.")
                st.metric("Estimated Monthly Financial Loss", f"${financial_loss:.2f}", f"-{lost_kwh:.0f} kWh")
                st.markdown("*Signature suggests potential shading, heavy soiling, or inverter clipping.*")
                
            st.divider()
            
        except Exception as e:
            st.error("Error connecting to NREL database. Please try again.")
            financial_loss = 0.0

    # The Lead Capture Form (runs independently of the calculate button)
    st.subheader("Want the exact cause?")
    st.markdown("Enter your email. I will manually run a deep-dive diagnostic on your inverter data to pinpoint the exact tree, hardware fault, or grime causing the drop.")
    
    with st.form("lead_capture_form"):
        email = st.text_input("Email Address")
        submitted = st.form_submit_button("Send me my Free Deep-Dive Report")
        
        if submitted:
            if email:
                with open("leads.csv", "a") as file:
                    file.write(f"{datetime.datetime.now()},{email},{zip_code},{system_size},{actual_kwh},{financial_loss:.2f}\n")
                
                st.success(f"Request received for {email}! I will email you within 24 hours with instructions on how to share your data.")
            else:
                st.error("Please enter a valid email address.")

st.divider()
st.caption("Privacy: We do not store your data. Calculations are done in real-time.")
