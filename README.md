# 📊 Predictive Customer Lifetime Value & RFM Analytics Suite

An enterprise-grade customer analytics platform combining traditional historical segmentation with probabilistic machine learning models to forecast customer worth and optimize marketing unit economics.

## 🚀 App Architecture & Layout
* **1. Overview & Data Health:** Main landing dashboard assessing dataset integrity and core operational KPIs.
* **2. Historical RFM Analysis:** Behavioral customer profiling using quintile-based Recency, Frequency, and Monetary scoring.
* **3. Predictive CLV:** Machine learning pipeline implementing **BG/NBD** (transaction counts) and **Gamma-Gamma** (spend valuation) probabilistic submodels via the `lifetimes` library.
* **4. Customer Lookup Deep-Dive:** Granite-level lookup engine for tracking individual customer interaction histories and lifetime value forecasts.
* **5. Marketing Strategy & Unit Economics:** Premium layer tracking $LTV:CAC$ ratios, attribution channel efficiency, retention cohorts, and automated tactical recommendation playbooks.

## 🛠️ Local Installation & Execution
1. Clone the repository:
   ```bash
   git clone [https://github.com/kalsi0409/rfm-clv-analytics.git](https://github.com/kalsi0409/rfm-clv-analytics.git)
   cd rfm-clv-analytics
