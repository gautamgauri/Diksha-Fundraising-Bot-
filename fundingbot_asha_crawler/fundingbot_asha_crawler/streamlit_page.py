
import os, streamlit as st, pandas as pd
import crawler, settings

st.set_page_config(page_title="Asha Proposal Crawler", layout="wide")
st.title("Asha Proposal Crawler ($30K–$50K filter)")

st.markdown("""
**🇮🇳 Asha for Education Proposals**
Budget range now shown in USD for consistency with USAID crawler.
*Original range: ₹25L–₹42L (~$30K–$50K)*
""")

# Main configuration
col1, col2 = st.columns(2)

with col1:
    st.subheader("Crawling Parameters")
    max_pages = st.number_input("Max pages", 50, 2000, settings.DEFAULT_MAX_PAGES, 50)
    delay_sec = st.number_input("Delay (sec)", 0.2, 5.0, settings.DEFAULT_DELAY_SEC, 0.1)
    usd_rate = st.number_input("₹ per $", 60.0, 120.0, settings.DEFAULT_USD_RATE, 0.5)

with col2:
    st.subheader("Budget Filters (USD)")
    min_usd = st.number_input("Min USD ($)", 10000, 100000, int(settings.DEFAULT_MIN_USD), 5000)
    max_usd = st.number_input("Max USD ($)", 10000, 100000, int(settings.DEFAULT_MAX_USD), 5000)

    st.info(f"INR equivalent: ₹{min_usd*usd_rate:,.0f} – ₹{max_usd*usd_rate:,.0f}")

# Advanced options
with st.expander("Advanced Options"):
    seeds_text = st.text_area("Seed URLs", "\\n".join(settings.SEEDS))
    out_dir = st.text_input("Output folder", "./out")

    st.subheader("Legacy INR Mode")
    use_legacy_inr = st.checkbox("Use legacy INR parameters instead")
    if use_legacy_inr:
        min_inr = st.number_input("Min INR (₹)", 0, value=settings.DEFAULT_MIN_INR, step=500000)
        max_inr = st.number_input("Max INR (₹)", 0, value=settings.DEFAULT_MAX_INR, step=500000)

if st.button("🚀 Run Asha Crawler", type="primary"):
    seeds = [s.strip() for s in seeds_text.splitlines() if s.strip()]

    with st.spinner("Crawling Asha for Education proposals..."):
        try:
            if use_legacy_inr:
                # Use legacy INR mode
                csv_path = crawler.run(
                    out_dir=out_dir, min_inr=min_inr, max_inr=max_inr,
                    usd_rate=usd_rate, max_pages=max_pages, delay_sec=delay_sec, seeds=seeds
                )
            else:
                # Use new USD mode
                csv_path = crawler.run(
                    out_dir=out_dir, min_usd=min_usd, max_usd=max_usd,
                    usd_rate=usd_rate, max_pages=max_pages, delay_sec=delay_sec, seeds=seeds
                )

            st.success(f"✅ Crawler completed! CSV saved to: {csv_path}")

            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)

                # Display summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Proposals", len(df))
                with col2:
                    avg_usd = df['amount_requested_usd'].mean() if 'amount_requested_usd' in df.columns and df['amount_requested_usd'].notna().any() else 0
                    st.metric("Avg Budget", f"${avg_usd:,.0f}" if avg_usd > 0 else "N/A")
                with col3:
                    with_budget = df['amount_requested_usd'].notna().sum() if 'amount_requested_usd' in df.columns else 0
                    st.metric("With Budget Info", with_budget)

                # Display data
                st.subheader("📋 Results")
                st.dataframe(df, use_container_width=True)

                # Download button
                csv_data = df.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv_data,
                    "asha_proposals.csv",
                    "text/csv"
                )
            else:
                st.warning("No results file found.")

        except Exception as e:
            st.error(f"❌ Error running crawler: {str(e)}")

# Information section
st.subheader("ℹ️ About Asha Crawler")
st.markdown("""
**Data Source:** Asha for Education (ashanet.org)
**Focus:** Education projects in India
**Budget Range:** $30K–$50K (₹25L–₹42L)
**Document Types:** PDF proposals and project documents

**Output:** CSV file with proposal details, budget in USD, and metadata.
""")
