import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Airbnb Revenue Tracker", layout="wide")

st.title("📊 Airbnb Business Revenue Report")
st.markdown("Upload your Airbnb 'Paid' Earnings CSV to generate your report.")

# --- File Uploader ---
uploaded_file = st.file_uploader("Choose your Airbnb CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Data Cleaning
    df['Date'] = pd.to_datetime(df['Date'])
    money_cols = ['Amount', 'Gross Earnings', 'Host Fee', 'Cleaning Fee']
    for col in money_cols:
        if col in df.columns:
            df[col] = df[col].replace('[\$,]', '', regex=True).astype(float)
    
    # Filtering
    payouts = df[df['Type'] == 'Payout']

    # --- Metrics Row ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Gross", f"${payouts['Gross Earnings'].sum():,.2f}")
    col2.metric("Net Payout", f"${payouts['Amount'].sum():,.2f}")
    col3.metric("Airbnb Fees", f"${payouts['Host Fee'].sum():,.2f}")

    # --- Charts ---
    monthly_df = payouts.resample('M', on='Date').sum(numeric_only=True).reset_index()
    monthly_df['Month'] = monthly_df['Date'].dt.strftime('%b %Y')
    
    fig = px.bar(monthly_df, x='Month', y='Amount', title="Revenue by Month")
    st.plotly_chart(fig, use_container_width=True)
    
    st.success("Report Generated Successfully!")
else:
    st.info("Please upload a CSV file to begin.")
