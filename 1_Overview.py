import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="CLV & RFM Dashboard", page_icon="🏠", layout="wide")

st.title("🏠 Customer Analytics: CLV & RFM Overview")
st.markdown("""
Welcome to the Predictive CLV & RFM App. Select a pre-loaded dataset or upload your own transactional data below to evaluate 
historical performance and project future customer value.
""")

# --- DATA SOURCE SELECTION ---
DATA_DIR = "data"
DEFAULT_FILE_NAME = "mock_data.csv"
default_file_path = os.path.join(DATA_DIR, DEFAULT_FILE_NAME)

# Layout for data input options
col_select, col_upload = st.columns(2)

with col_select:
    # Check if our target file exists in the data directory
    if os.path.exists(default_file_path):
        options_list = [f"Default Dataset ({DEFAULT_FILE_NAME})", "Upload my own instead"]
        selected_source = st.selectbox("📁 Data Source Selection:", options=options_list)
    else:
        st.warning(f"⚠️ '{DEFAULT_FILE_NAME}' not found in the 'data/' folder.")
        selected_source = "Upload my own instead"

with col_upload:
    uploaded_file = st.file_uploader("📤 Or upload a custom transaction history (CSV)", type=["csv"])

# --- LOAD DATA LOGIC ---
df = None

# Prioritize direct user upload first; otherwise fall back to default mock data selection
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("Using your uploaded dataset!")
elif selected_source == f"Default Dataset ({DEFAULT_FILE_NAME})":
    df = pd.read_csv(default_file_path)
    st.info(f"Loaded pre-saved project dataset: **{DEFAULT_FILE_NAME}**")

# --- PROCESS DATA IF LOADED ---
if df is not None:
    st.subheader("📋 Raw Data Preview")
    st.dataframe(df.head(), use_container_width=True)
    
    # --- DYNAMIC COLUMN MAPPING ---
    st.sidebar.header("🛠️ Column Mapping")
    st.sidebar.markdown("Match your dataset's columns to the required features:")
    
    # Smart helper logic to automatically select the matching column index
    cols_list = list(df.columns)
    
    def get_default_index(keywords, options):
        for kw in keywords:
            for i, opt in enumerate(options):
                if kw.lower() in opt.lower():
                    return i
        return 0

    cust_id_col = st.sidebar.selectbox("Customer ID", options=cols_list, index=get_default_index(["id", "customer", "cust"], cols_list))
    date_col = st.sidebar.selectbox("Invoice Date", options=cols_list, index=get_default_index(["date", "invoice", "time"], cols_list))
    sales_col = st.sidebar.selectbox("Transaction Value / Revenue", options=cols_list, index=get_default_index(["sales", "revenue", "amount", "value"], cols_list))
    
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
    st.info("💡 Please select the Default Dataset or upload a custom CSV file to begin.")