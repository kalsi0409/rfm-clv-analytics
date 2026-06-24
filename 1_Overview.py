import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="CLV & RFM Dashboard", page_icon="🏠", layout="wide")

st.title("🏠 Customer Analytics: CLV & RFM Overview")
st.markdown("""
Welcome to the Predictive CLV & RFM App. Upload your transactional data below to evaluate 
historical performance and project future customer value.
""")

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader("Upload your transaction history (CSV)", type=["csv"])

if uploaded_file is not None:
    # Load data
    df = pd.read_csv(uploaded_file)
    
    st.subheader("📋 Raw Data Preview")
    st.dataframe(df.head(), use_container_width=True)
    
    # --- DYNAMIC COLUMN MAPPING ---
    st.sidebar.header("🛠️ Column Mapping")
    st.sidebar.markdown("Match your dataset's columns to the required features:")
    
    cust_id_col = st.sidebar.selectbox("Customer ID", options=df.columns)
    date_col = st.sidebar.selectbox("Invoice Date", options=df.columns)
    sales_col = st.sidebar.selectbox("Transaction Value / Revenue", options=df.columns)
    
    # Clean Data Type Constraints
    df[date_col] = pd.to_datetime(df[date_col])
    df[sales_col] = pd.to_numeric(df[sales_col], errors='coerce')
    
    # Drop rows missing crucial info
    df = df.dropna(subset=[cust_id_col, date_col, sales_col])
    
    # --- SUMMARY STATISTICS / DATA HEALTH ---
    st.subheader("📊 Dataset Health & KPIs")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", f"${df[sales_col].sum():,.2f}")
    with col2:
        st.metric("Unique Customers", f"{df[cust_id_col].nunique():,}")
    with col3:
        st.metric("Total Transactions", f"{df.shape[0]:,}")
    with col4:
        st.metric("Avg Order Value", f"${df[sales_col].mean():,.2f}")
        
    # Store dataframe in streamlit session state for use across multi-page sheets
    st.session_state['df'] = df
    st.session_state['cols'] = {'id': cust_id_col, 'date': date_col, 'sales': sales_col}
    
    st.success("🎉 Data successfully mapped and loaded! Proceed to the 'RFM Analysis' page in the sidebar.")
else:
    st.info("💡 Please upload a CSV file containing at least a Customer Identifier, Date column, and Purchase values to begin.")