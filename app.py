import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Airbnb Data Pro", layout="wide")

st.title("📊 Airbnb Business Intelligence")
st.markdown("Upload either your **Host Earnings CSV** or a **Market Listings CSV**.")

uploaded_file = st.file_uploader("Choose your CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    cols = df.columns.tolist()

    # --- MODE 1: HOST EARNINGS (If 'Date' column exists) ---
    if 'Date' in cols:
        st.info("📂 Detected: Host Earnings Report")
        
        # Data Cleaning
        df['Date'] = pd.to_datetime(df['Date'])
        money_cols = ['Amount', 'Gross Earnings', 'Host Fee', 'Cleaning Fee']
        for col in money_cols:
            if col in df.columns:
                df[col] = df[col].replace('[\$,]', '', regex=True).astype(float)
        
        payouts = df[df['Type'] == 'Payout'] if 'Type' in df.columns else df

        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Net Payout", f"${payouts['Amount'].sum():,.2f}")
        if 'Gross Earnings' in payouts.columns:
            col2.metric("Gross Revenue", f"${payouts['Gross Earnings'].sum():,.2f}")
        
        # Chart
        monthly_df = payouts.resample('M', on='Date').sum(numeric_only=True).reset_index()
        monthly_df['Month'] = monthly_df['Date'].dt.strftime('%b %Y')
        fig = px.bar(monthly_df, x='Month', y='Amount', title="Monthly Revenue Trend")
        st.plotly_chart(fig, use_container_width=True)

    # --- MODE 2: MARKET DATA (If it's the listings.csv you just uploaded) ---
    elif 'price' in cols and 'estimated_revenue_l365d' in cols:
        st.info("📂 Detected: Market Listings Report")

        # Clean Price column (it usually looks like "$100.00")
        if df['price'].dtype == 'object':
            df['price'] = df['price'].replace('[\$,]', '', regex=True).astype(float)

        # Global Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Listings", len(df))
        c2.metric("Avg Nightly Price", f"${df['price'].mean():,.2f}")
        c3.metric("Est. Total Market Rev (1yr)", f"${df['estimated_revenue_l365d'].sum():,.0f}")

        # Visualization: Revenue by Neighborhood
        geo_rev = df.groupby('neighbourhood_cleansed')['estimated_revenue_l365d'].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(geo_rev, x='neighbourhood_cleansed', y='estimated_revenue_l365d', 
                     title="Total Estimated Revenue by Neighborhood",
                     labels={'neighbourhood_cleansed': 'Neighborhood', 'estimated_revenue_l365d': 'Revenue ($)'})
        st.plotly_chart(fig, use_container_width=True)

        # Show the raw data table
        st.subheader("Raw Market Data")
        st.dataframe(df[['name', 'neighbourhood_cleansed', 'price', 'estimated_revenue_l365d', 'review_scores_rating']])

    else:
        st.error("Unknown CSV format. Please ensure your file has a 'Date' column or standard Airbnb listing columns.")

else:
    st.info("Please upload a CSV file to begin.")
