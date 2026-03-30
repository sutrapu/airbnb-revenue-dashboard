import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Airbnb Business Pro", layout="wide", initial_sidebar_state="expanded")

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Airbnb Business Intelligence Dashboard")
st.markdown("Upload your Airbnb **Host Earnings CSV** or **Market Listings CSV** to generate insights.")

# 2. File Uploader
uploaded_file = st.file_uploader("Upload CSV file", type="csv")

if uploaded_file is not None:
    # Load data
    df = pd.read_csv(uploaded_file)
    cols = df.columns.tolist()

    # --- OPTION A: HOST EARNINGS MODE ---
    if 'Date' in cols and 'Amount' in cols:
        st.success("📂 Successfully detected: Host Earnings Report")
        
        # Data Cleaning
        df['Date'] = pd.to_datetime(df['Date'])
        for col in ['Amount', 'Gross Earnings', 'Host Fee', 'Cleaning Fee']:
            if col in df.columns:
                df[col] = df[col].replace('[\$,]', '', regex=True).astype(float)
        
        # Filter for payouts
        payouts = df[df['Type'] == 'Payout'] if 'Type' in df.columns else df

        # Top Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Net Payouts", f"${payouts['Amount'].sum():,.2f}")
        m2.metric("Gross Revenue", f"${payouts['Gross Earnings'].sum():,.2f}" if 'Gross Earnings' in payouts.columns else "N/A")
        m3.metric("Total Cleaning Fees", f"${payouts['Cleaning Fee'].sum():,.2f}" if 'Cleaning Fee' in payouts.columns else "N/A")
        m4.metric("Avg Payout", f"${payouts['Amount'].mean():,.2f}")

        # Monthly Chart
        st.subheader("📈 Revenue Trend")
        monthly_df = payouts.resample('M', on='Date').sum(numeric_only=True).reset_index()
        monthly_df['Month'] = monthly_df['Date'].dt.strftime('%b %Y')
        fig_trend = px.line(monthly_df, x='Month', y='Amount', markers=True, title="Monthly Net Revenue")
        st.plotly_chart(fig_trend, use_container_width=True)

    # --- OPTION B: MARKET INTELLIGENCE MODE (listings.csv) ---
    elif 'price' in cols and 'estimated_revenue_l365d' in cols:
        st.success("📂 Successfully detected: Market Intelligence Report")

        # Clean Price (Remove $ and commas)
        if df['price'].dtype == 'object':
            df['price'] = df['price'].replace('[\$,]', '', regex=True).astype(float)

        # --- Sidebar Filters ---
        st.sidebar.header("🔍 Market Filters")
        
        all_neighborhoods = sorted(df['neighbourhood_cleansed'].dropna().unique())
        selected_nb = st.sidebar.multiselect("Select Neighborhoods", all_neighborhoods, default=all_neighborhoods)
        
        all_rooms = df['room_type'].unique()
        selected_room = st.sidebar.multiselect("Select Room Type", all_rooms, default=all_rooms)

        # Apply Filters
        mask = (df['neighbourhood_cleansed'].isin(selected_nb)) & (df['room_type'].isin(selected_room))
        filtered_df = df[mask]

        # Market Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Listings", len(filtered_df))
        c2.metric("Avg Nightly Rate", f"${filtered_df['price'].mean():,.2f}")
        c3.metric("Avg Review Score", f"{filtered_df['review_scores_rating'].mean():,.2f}⭐")
        c4.metric("Est. Annual Market Revenue", f"${filtered_df['estimated_revenue_l365d'].sum():,.0f}")

        # Map View
        st.subheader("📍 Geospatial Revenue Map")
        st.markdown("Circle size represents the **Nightly Price**.")
        map_df = filtered_df.copy().dropna(subset=['latitude', 'longitude'])
        # Scale size for visibility
        map_df['map_size'] = map_df['price'] / 5 
        st.map(map_df, latitude='latitude', longitude='longitude', size='map_size', color='#FF5A5F')

        # Charts
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("💰 Revenue by Neighborhood")
            geo_rev = filtered_df.groupby('neighbourhood_cleansed')['estimated_revenue_l365d'].sum().sort_values().reset_index()
            fig_bar = px.bar(geo_rev, y='neighbourhood_cleansed', x='estimated_revenue_l365d', orientation='h', color='estimated_revenue_l365d')
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_right:
            st.subheader("⭐ Rating vs Revenue")
            fig_scatter = px.scatter(filtered_df, x='review_scores_rating', y='estimated_revenue_l365d', 
                                     size='accommodates', color='room_type', hover_name='name')
            st.plotly_chart(fig_scatter, use_container_width=True)

        # Data Table
        with st.expander("👀 View Raw Market Data"):
            st.dataframe(filtered_df[['name', 'neighbourhood_cleansed', 'price', 'estimated_revenue_l365d', 'review_scores_rating', 'room_type']])

    else:
        st.warning("⚠️ CSV format not recognized. Please upload a standard Airbnb Earnings or Listings file.")

else:
    # Landing Page
    st.info("👋 Welcome! Please upload your CSV file in the sidebar or main window to start your analysis.")
    st.image("https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&q=80&w=1000", caption="Optimize your business with data.")

# Footer
st.markdown("---")
st.caption("Airbnb Business Intelligence Tool | Built with Python & Streamlit")
