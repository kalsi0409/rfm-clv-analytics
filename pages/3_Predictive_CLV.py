import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from lifetimes import BetaGeoFitter, GammaGammaFitter
from lifetimes.utils import summary_data_from_transaction_data

st.set_page_config(page_title="Predictive CLV", page_icon="🔮", layout="wide")
st.title("🔮 Predictive Customer Lifetime Value")

# Safety Check: Ensure data was uploaded on the landing page
if 'df' not in st.session_state:
    st.error("⚠️ No data found! Please go back to the 🏠 Overview page and upload your dataset first.")
else:
    df = st.session_state['df']
    cols = st.session_state['cols']
    
    id_col = cols['id']
    date_col = cols['date']
    sales_col = cols['sales']
    
    # --- MODEL CONFIGURATIONS ---
    st.sidebar.header("⚙️ Model Parameters")
    t_days = st.sidebar.slider("Prediction Window (Days)", min_value=30, max_value=730, value=365, step=30)
    profit_margin = st.sidebar.slider("Profit Margin (%)", min_value=1, max_value=100, value=10, step=5) / 100.0
    
    st.markdown("### 🧠 Model Training & Forecast")
    
    with st.spinner("Processing transaction matrix and training models..."):
        # 1. Transform raw transactions into an RFM matrix tailored for the lifetimes package
        # Note: 'frequency' here means repeat purchases (Total - 1)
        clv_summary = summary_data_from_transaction_data(
            df, 
            customer_id_col=id_col, 
            datetime_col=date_col, 
            monetary_value_col=sales_col
        )
        
        # 2. Train BG/NBD Model (Predicts transaction counts)
        bgf = BetaGeoFitter(penalizer_coef=0.01)
        bgf.fit(clv_summary['frequency'], clv_summary['recency'], clv_summary['T'])
        
        # 3. Filter for Gamma-Gamma constraints (Requires at least 1 repeat purchase with positive monetary value)
        returning_customers = clv_summary[(clv_summary['frequency'] > 0) & (clv_summary['monetary_value'] > 0)]
        
        if returning_customers.empty:
            st.warning("⚠️ Not enough repeat customer transaction depth to run the Gamma-Gamma spend model.")
        else:
            # Train Gamma-Gamma Model (Predicts spend value)
            ggf = GammaGammaFitter(penalizer_coef=0.01)
            ggf.fit(returning_customers['frequency'], returning_customers['monetary_value'])
            
            # 4. Score all customers
            clv_summary['Expected_Purchases'] = bgf.conditional_expected_number_of_purchases_up_to_time(
                t_days, clv_summary['frequency'], clv_summary['recency'], clv_summary['T']
            )
            
            clv_summary['Expected_Avg_Spend'] = ggf.conditional_expected_average_profit(
                clv_summary['frequency'], clv_summary['monetary_value']
            )
            
            # Final CLV formula evaluation
            clv_summary['Predicted_CLV'] = ggf.customer_lifetime_value(
                bgf,
                clv_summary['frequency'],
                clv_summary['recency'],
                clv_summary['T'],
                clv_summary['monetary_value'],
                time=t_days/30, # expressed in months
                discount_rate=0.01
            ) * profit_margin

            # Cache calculations in session state
            st.session_state['clv_summary'] = clv_summary

            # --- DISPLAY DASHBOARD VISUALS ---
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(f"Top Forecasted Value (Next {t_days} Days)", f"${clv_summary['Predicted_CLV'].max():,.2f}")
                st.subheader("📋 Top 5 High-Value Future Projections")
                st.dataframe(clv_summary.sort_values(by='Predicted_CLV', ascending=False).head(5), use_container_width=True)
                
            with col2:
                st.subheader("📈 Historical Spend vs. Predicted Future CLV")
                # Create a scatter plot to identify high-value targets
                fig = px.scatter(
                    clv_summary, 
                    x='monetary_value', 
                    y='Predicted_CLV',
                    labels={'monetary_value': 'Historical Avg Ticket Size ($)', 'Predicted_CLV': 'Predicted CLV ($)'},
                    hover_data=['frequency'],
                    color='Expected_Purchases',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
                
            # Allow data downloading for downstream campaigns
            st.markdown("---")
            csv_data = clv_summary.to_csv().encode('utf-8')
            st.download_button(
                label="📥 Export CLV Predictions CSV",
                data=csv_data,
                file_name='customer_clv_predictions.csv',
                mime='text/csv'
            )