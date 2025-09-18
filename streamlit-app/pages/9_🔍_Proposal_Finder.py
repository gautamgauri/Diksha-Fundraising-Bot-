import streamlit as st
import sys
import os

# Add crawler module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'fundingbot_asha_crawler'))

try:
    from fundingbot_asha_crawler import crawler, usaid_crawler
    from fundingbot_asha_crawler import settings, usaid_settings
    CRAWLER_AVAILABLE = True
except ImportError as e:
    CRAWLER_AVAILABLE = False
    st.error(f"Crawler modules not available: {e}")

st.set_page_config(page_title="Proposal Finder", page_icon="🔍", layout="wide")

st.title("🔍 Funding Proposal Finder")
st.markdown("**Discover relevant funding proposals from multiple sources**")

if not CRAWLER_AVAILABLE:
    st.error("⚠️ Crawler modules are not available. Please check installation.")
    st.stop()

# Source selection
st.subheader("📋 Select Funding Sources")

col1, col2 = st.columns(2)

with col1:
    use_asha = st.checkbox("🇮🇳 Asha for Education", True,
                          help="Indian education NGO proposals (₹25-42L)")

with col2:
    use_usaid = st.checkbox("🇺🇸 USAID Archives", True,
                           help="US development proposals (<$100K, education/youth)")

if not use_asha and not use_usaid:
    st.warning("Please select at least one funding source.")
    st.stop()

# Configuration tabs
tab1, tab2, tab3 = st.tabs(["⚙️ Crawler Settings", "🎯 Filtering", "☁️ Export Options"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        max_pages = st.number_input("Max pages per source", 10, 500, 100, 10)
        delay_sec = st.number_input("Delay between requests (sec)", 0.5, 5.0, 1.0, 0.1)

    with col2:
        output_dir = st.text_input("Output directory", "./multi_source_out")

with tab2:
    if use_asha:
        st.markdown("**🇮🇳 Asha for Education Filters**")
        col1, col2 = st.columns(2)
        with col1:
            asha_min_usd = st.number_input("Min USD ($)", 10000, 100000, int(settings.DEFAULT_MIN_USD), 5000, key="asha_min")
        with col2:
            asha_max_usd = st.number_input("Max USD ($)", 10000, 100000, int(settings.DEFAULT_MAX_USD), 5000, key="asha_max")

        # Show INR equivalent
        usd_rate = 83.0  # Default rate
        st.info(f"INR equivalent: ₹{asha_min_usd*usd_rate:,.0f} – ₹{asha_max_usd*usd_rate:,.0f}")

    if use_usaid:
        st.markdown("**🇺🇸 USAID Filters**")
        col1, col2 = st.columns(2)
        with col1:
            usaid_max_usd = st.number_input("Max USD ($)", 10000, 500000, usaid_settings.MAX_USD_BUDGET, 10000)
        with col2:
            focus_options = st.multiselect("Focus Areas", ["Education", "Youth"], ["Education", "Youth"])

with tab3:
    upload_to_drive = st.checkbox("📁 Upload results to Google Drive")
    drive_folder_id = st.text_input("Google Drive Folder ID (optional)")

    combine_results = st.checkbox("📊 Combine results into single file", True)

# Run crawlers
if st.button("🚀 Start Multi-Source Crawl", type="primary"):
    results = {}
    total_proposals = 0

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        sources_to_run = []
        if use_asha: sources_to_run.append("asha")
        if use_usaid: sources_to_run.append("usaid")

        for i, source in enumerate(sources_to_run):
            progress = i / len(sources_to_run)
            progress_bar.progress(progress)

            if source == "asha":
                status_text.text("🇮🇳 Crawling Asha for Education...")

                asha_result = crawler.run(
                    out_dir=os.path.join(output_dir, "asha"),
                    min_usd=asha_min_usd,
                    max_usd=asha_max_usd,
                    max_pages=max_pages,
                    delay_sec=delay_sec,
                    upload_to_drive=upload_to_drive,
                    drive_folder_id=drive_folder_id if drive_folder_id.strip() else None,
                    return_details=True
                )

                results["asha"] = asha_result
                if hasattr(asha_result, 'rows'):
                    total_proposals += len(asha_result.rows)

            elif source == "usaid":
                status_text.text("🇺🇸 Crawling USAID archives...")

                # Update USAID settings based on user input
                usaid_settings.MAX_USD_BUDGET = usaid_max_usd

                usaid_result = usaid_crawler.run_usaid_crawler(
                    out_dir=os.path.join(output_dir, "usaid"),
                    max_pages=max_pages,
                    delay_sec=delay_sec,
                    upload_to_drive=upload_to_drive,
                    drive_folder_id=drive_folder_id if drive_folder_id.strip() else None,
                    return_details=True
                )

                results["usaid"] = usaid_result
                if hasattr(usaid_result, 'rows'):
                    total_proposals += len(usaid_result.rows)

        progress_bar.progress(1.0)
        status_text.text("✅ Crawling completed!")

        # Display results
        st.success(f"🎉 Multi-source crawl completed! Found {total_proposals} total proposals.")

        # Results summary
        col1, col2, col3 = st.columns(3)

        if "asha" in results:
            with col1:
                asha_count = len(results["asha"].rows) if hasattr(results["asha"], 'rows') else 0
                st.metric("🇮🇳 Asha Proposals", asha_count)

        if "usaid" in results:
            with col2:
                usaid_count = len(results["usaid"].rows) if hasattr(results["usaid"], 'rows') else 0
                st.metric("🇺🇸 USAID Proposals", usaid_count)

        with col3:
            st.metric("📊 Total Found", total_proposals)

        # Detailed results
        st.subheader("📋 Detailed Results")

        for source, result in results.items():
            if hasattr(result, 'rows') and result.rows:
                with st.expander(f"📄 {source.upper()} Results ({len(result.rows)} proposals)"):
                    import pandas as pd
                    df = pd.DataFrame(result.rows)
                    st.dataframe(df, use_container_width=True)

                    # Download button for individual source
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        f"📥 Download {source.upper()} CSV",
                        csv_data,
                        f"{source}_proposals.csv",
                        "text/csv",
                        key=f"download_{source}"
                    )

        # Combined results if requested
        if combine_results and len(results) > 1:
            st.subheader("📊 Combined Results")

            combined_rows = []
            for source, result in results.items():
                if hasattr(result, 'rows'):
                    for row in result.rows:
                        row_copy = row.copy()
                        row_copy['source'] = source
                        combined_rows.append(row_copy)

            if combined_rows:
                import pandas as pd
                combined_df = pd.DataFrame(combined_rows)
                st.dataframe(combined_df, use_container_width=True)

                # Download combined results
                combined_csv = combined_df.to_csv(index=False)
                st.download_button(
                    "📥 Download Combined CSV",
                    combined_csv,
                    "multi_source_proposals.csv",
                    "text/csv"
                )

        # Drive upload summary
        uploaded_files = []
        for source, result in results.items():
            if hasattr(result, 'uploaded_to_drive') and result.uploaded_to_drive:
                uploaded_files.append(f"{source.upper()}: [View]({result.drive_web_link})")

        if uploaded_files:
            st.info("☁️ Files uploaded to Google Drive:\n" + "\n".join(uploaded_files))

    except Exception as e:
        st.error(f"❌ Error during multi-source crawl: {str(e)}")
        import traceback
        with st.expander("🔍 Error Details"):
            st.code(traceback.format_exc())

# Information section
with st.expander("ℹ️ About Multi-Source Proposal Finder"):
    st.markdown("""
    This tool searches multiple funding databases to find relevant proposals:

    **🇮🇳 Asha for Education:**
    - Focus: Education projects in India
    - Budget: $30K-$50K (~₹25-42 Lakhs)
    - Documents: PDF proposals from ashanet.org

    **🇺🇸 USAID Archives:**
    - Focus: Education/youth projects worldwide
    - Budget: Under $100K (configurable)
    - Documents: DEC repository, Development Data Library, ForeignAssistance.gov

    **Output:** CSV files with proposal details, budget in USD, and metadata for analysis.
    """)