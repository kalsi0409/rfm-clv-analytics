import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Marketing Strategy", page_icon="🎯", layout="wide")
st.title("🎯 Marketing Optimization & Unit Economics")

if 'df' not in st.session_state or 'clv_summary' not in st.session_state:
    st.error("⚠️ Data cache missing. Please complete data loading and CLV prediction runs first.")
else:
    df = st.session_state['df']
    clv_summary = st.session_state['clv_summary']
    rfm = st.session_state.get('rfm', None)
    
    # Ensure our marketing metadata columns exist
    if 'AcquisitionChannel' not in df.columns or 'CAC' not in df.columns:
        st.warning("⚠️ High-tier marketing columns not detected. Injecting synthetic placeholders for rendering...")
        channels = ['Meta Ads', 'Paid Search', 'Organic', 'Email Marketing']
        df['AcquisitionChannel'] = np.random.choice(channels, size=len(df))
        df['CAC'] = df['AcquisitionChannel'].map({'Meta Ads': 65.0, 'Paid Search': 45.0, 'Organic': 0.0, 'Email Marketing': 15.0})

    # --- DATA QUALITY & OUTLIER REGULATION ---
    st.sidebar.header("🛡️ Data Quality Controls")
    outlier_threshold = st.sidebar.slider("Filter Invoices Above ($)", min_value=100, max_value=1000, value=500)
    clean_df = df[df[st.session_state['cols']['sales']] <= outlier_threshold]
    
    # --- SECTION 1: UNIT ECONOMICS (CLV vs CAC) ---
    st.subheader("📊 Unit Economics by Acquisition Channel")
    
    # Calculate unique baseline figures per customer to map CAC metrics safely
    customer_marketing = df.groupby(st.session_state['cols']['id']).agg({
        'AcquisitionChannel': 'first',
        'CAC': 'first'
    })
    
    analytics_master = clv_summary.join(customer_marketing, how='inner')
    
    channel_summary = analytics_master.groupby('AcquisitionChannel').agg(
        Total_Customers=('Predicted_CLV', 'count'),
        Avg_CAC=('CAC', 'mean'),
        Avg_Predicted_CLV=('Predicted_CLV', 'mean')
    ).reset_index()
    
    channel_summary['CLV_to_CAC_Ratio'] = channel_summary['Avg_Predicted_CLV'] / channel_summary['Avg_CAC'].replace(0, 0.01)
    
    col1, col2 = st.columns([2, 3])
    with col1:
        st.dataframe(
            channel_summary.style.format({
                'Avg_CAC': '${:,.2f}',
                'Avg_Predicted_CLV': '${:,.2f}',
                'CLV_to_CAC_Ratio': '{:.2f}x'
            }), 
            use_container_width=True, hide_index=True
        )
    with col2:
        fig_ratio = px.bar(
            channel_summary, x='AcquisitionChannel', y='CLV_to_CAC_Ratio',
            title="LTV : CAC Efficiency Multiple (Target > 3.0x)",
            labels={'CLV_to_CAC_Ratio': 'Ratio Multiple', 'AcquisitionChannel': 'Channel'},
            color='CLV_to_CAC_Ratio', color_continuous_scale='Greens'
        )
        st.plotly_chart(fig_ratio, use_container_width=True)

    # --- SECTION 2: COHORT RETENTION ESTIMATION ---
    st.subheader("📉 Cohort Analysis & Retention Framework")
    
    # 1. Create the transaction month flag
    clean_df['InvoiceMonth'] = clean_df[st.session_state['cols']['date']].dt.to_period('M')
    
    # 2. Identify the first purchase cohort month per customer
    first_purchase = clean_df.groupby(st.session_state['cols']['id'])['InvoiceMonth'].min().reset_index()
    first_purchase.columns = [st.session_state['cols']['id'], 'CohortMonth']
    
    # 3. Merge safely without overlapping column conflicts
    cohort_merge = pd.merge(clean_df, first_purchase, on=st.session_state['cols']['id'])
    
    # 4. Compute the relative month step indexes
    cohort_merge['PeriodIndex'] = (cohort_merge['InvoiceMonth'].dt.year - cohort_merge['CohortMonth'].dt.year) * 12 + (cohort_merge['InvoiceMonth'].dt.month - cohort_merge['CohortMonth'].dt.month)
    
    # 5. Build the user activity grid
    cohort_matrix = cohort_merge.groupby(['CohortMonth', 'PeriodIndex'])[st.session_state['cols']['id']].nunique().reset_index()
    cohort_pivot = cohort_matrix.pivot(index='CohortMonth', columns='PeriodIndex', values=st.session_state['cols']['id'])
    cohort_size = cohort_pivot.iloc[:, 0]
    retention_matrix = cohort_pivot.divide(cohort_size, axis=0)
    
    st.dataframe(retention_matrix.style.format("{:.1%}", na_rep=""), use_container_width=True)

    # --- SECTION 3: STRATEGIC RECOMMENDATION ENGINE ---
    st.subheader("💡 Algorithmic Playbook & Strategic Decisions")
    
    recommendation_table = [
        {"Segment": "Champions", "Tactic": "VIP Reward Programs & Early Access", "Expected Lift": "+15% AOV", "Investment Priority": "High"},
        {"Segment": "Loyal Customers", "Tactic": "Cross-sell adjacent categories via Email", "Expected Lift": "+22% Frequency", "Investment Priority": "Medium"},
        {"Segment": "Recent / New", "Tactic": "Triggered Welcome email sequences", "Expected Lift": "+10% Activation", "Investment Priority": "Medium"},
        {"Segment": "At Risk", "Tactic": "Win-back discounts & survey feedback loops", "Expected Lift": "+5% Retention", "Investment Priority": "High"},
        {"Segment": "Hibernating / Lost", "Tactic": "Low-cost programmatic display remarketing", "Expected Lift": "+1% Reactivation", "Investment Priority": "Low"}
    ]
    st.table(pd.DataFrame(recommendation_table))