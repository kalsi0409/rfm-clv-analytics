import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Customer Lookup", page_icon="👤", layout="wide")
st.title("👤 Individual Customer Insights & Profiling")

# Verification: Ensure previous dependencies and states are cached
if 'df' not in st.session_state or 'clv_summary' not in st.session_state:
    st.error("⚠️ State cache empty. Please make sure data is uploaded on the Overview page and trained on the Predictive CLV page.")
else:
    df = st.session_state['df']
    cols = st.session_state['cols']
    rfm = st.session_state.get('rfm', None)
    clv_summary = st.session_state['clv_summary']
    
    id_col = cols['id']
    date_col = cols['date']
    sales_col = cols['sales']
    
    # --- SEARCH BAR ---
    st.markdown("### 🔍 Search Customer Registry")
    customer_list = clv_summary.index.unique().tolist()
    selected_cust = st.selectbox("Select or Type a Customer ID:", options=customer_list)
    
    if selected_cust:
        st.markdown(f"## Profile File: **{selected_cust}**")
        st.markdown("---")
        
        # --- ROW 1: METRICS ---
        col1, col2, col3, col4 = st.columns(4)
        
        # Pull profile historical metadata
        cust_history = df[df[id_col] == selected_cust]
        cust_clv = clv_summary.loc[selected_cust]
        
        with col1:
            if rfm is not None:
                seg_name = rfm[rfm[id_col] == selected_cust]['Segment_Name'].values[0]
                st.metric("Assigned RFM Segment", str(seg_name))
            else:
                st.metric("Assigned RFM Segment", "N/A")
                
        with col2:
            st.metric("Total Purchases To-Date", f"{cust_history.shape[0]} orders")
            
        with col3:
            st.metric("Predicted Purchases", f"{cust_clv['Expected_Purchases']:.2f}")
            
        with col4:
            st.metric("Forecasted Net Value (CLV)", f"${cust_clv['Predicted_CLV']:,.2f}")
            
        # --- ROW 2: TABLES & CHARTS ---
        st.markdown("### 🕒 Purchase Timeline History")
        
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.subheader("📦 Historical Ledger")
            display_ledger = cust_history[[date_col, sales_col]].sort_values(by=date_col, ascending=False)
            st.dataframe(display_ledger.rename(columns={date_col: 'Date', sales_col: 'Amount ($)'}), use_container_width=True, hide_index=True)
            
        with col_right:
            st.subheader("📊 Purchase Patterns Over Time")
            fig = px.bar(
                cust_history, 
                x=date_col, 
                y=sales_col,
                labels={date_col: 'Timeline', sales_col: 'Ticket Size ($)'},
                title="Historical Invoice Value Distribution",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)