import streamlit as st
import pandas as pd
import datetime as dt
import plotly.express as px

st.set_page_config(page_title="RFM Analysis", page_icon="📊", layout="wide")
st.title("📊 Historical RFM Segmentation")

# Check if data was loaded on the overview page
if 'df' not in st.session_state:
    st.error("⚠️ No data found! Please go back to the 🏠 Overview page and upload your dataset first.")
else:
    df = st.session_state['df']
    cols = st.session_state['cols']
    
    id_col = cols['id']
    date_col = cols['date']
    sales_col = cols['sales']
    
    st.markdown("### ⚙️ RFM Score Generation")
    
    # 1. Define snapshot date
    snapshot_date = df[date_col].max() + dt.timedelta(days=1)
    
    # 2. Compute Recency, Frequency, Monetary values
    rfm = df.groupby(id_col).agg({
        date_col: lambda x: (snapshot_date - x.max()).days,
        id_col: 'count',
        sales_col: 'sum'
    })
    
    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    rfm = rfm.reset_index()
    
    # 3. Handle scoring boundaries via quintiles (1 to 5)
    rfm['R_Score'] = pd.qcut(rfm['Recency'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], q=5, labels=[1, 2, 3, 4, 5])
    
    # Combine scores into a string segment
    rfm['RFM_Segment'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
    
    # 4. Human-readable Segment Mapping
    def assign_segment(row):
        r, f = int(row['R_Score']), int(row['F_Score'])
        if r >= 4 and f >= 4: return 'Champions'
        elif r >= 3 and f >= 3: return 'Loyal Customers'
        elif r >= 4 and f <= 2: return 'Recent / New'
        elif r <= 2 and f >= 4: return 'At Risk'
        elif r <= 2 and f <= 2: return 'Hibernating / Lost'
        else: return 'Needs Attention'
            
    rfm['Segment_Name'] = rfm.apply(assign_segment, axis=1)
    st.session_state['rfm'] = rfm
    
    # --- METRICS & VISUALIZATIONS ---
    segment_counts = rfm['Segment_Name'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Count']
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("📋 Segment Breakdown")
        st.dataframe(segment_counts, use_container_width=True, hide_index=True)
        
    with col2:
        st.subheader("🗺️ Customer Segmentation Treemap")
        fig = px.treemap(segment_counts, path=['Segment'], values='Count',
                         color='Count', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
        
    st.subheader("🔍 Scored Customer Registry Preview")
    st.dataframe(rfm.head(10), use_container_width=True)