import os
import streamlit as st
import pandas as pd
import usaid_crawler
import usaid_settings

st.set_page_config(page_title="USAID Education/Youth Proposal Crawler", layout="wide")
st.title("USAID Education/Youth Proposal Crawler (<$100K)")

st.markdown("""
**Target Sources:**
- 🏛️ **DEC** (Development Experience Clearinghouse): Project reports, evaluations, technical docs
- 📊 **DDL** (Development Data Library): Machine-readable project datasets
- 💰 **ForeignAssistance.gov**: Spend/award summaries
""")

# Configuration section
col1, col2 = st.columns(2)

with col1:
    st.subheader("Crawling Parameters")
    max_pages = st.number_input("Max pages", 10, 500, usaid_settings.DEFAULT_USAID_MAX_PAGES, 10)
    delay_sec = st.number_input("Delay (sec)", 0.5, 5.0, usaid_settings.DEFAULT_USAID_DELAY_SEC, 0.1)
    max_budget = st.number_input("Max budget ($)", 10000, 500000, usaid_settings.MAX_USD_BUDGET, 10000)

with col2:
    st.subheader("Filtering Options")
    seeds_text = st.text_area("Seed URLs", "\n".join(usaid_settings.USAID_SEEDS))
    out_dir = st.text_input("Output folder", "./usaid_out")

    # Theme focus
    focus_education = st.checkbox("Focus on Education", True)
    focus_youth = st.checkbox("Focus on Youth", True)

# Advanced options
with st.expander("Advanced Options"):
    upload_to_drive = st.checkbox("Upload results to Google Drive")
    drive_folder_id = st.text_input("Google Drive Folder ID (optional)")

    st.subheader("Keywords Customization")
    custom_education_keywords = st.text_area("Education Keywords (comma-separated)",
                                           ", ".join(usaid_settings.EDUCATION_KEYWORDS))
    custom_youth_keywords = st.text_area("Youth Keywords (comma-separated)",
                                        ", ".join(usaid_settings.YOUTH_KEYWORDS))

# Display current keyword sets
st.subheader("Current Keywords")
col1, col2 = st.columns(2)
with col1:
    st.write("**Education Keywords:**")
    st.write(", ".join(sorted(usaid_settings.EDUCATION_KEYWORDS)[:10]) + "...")
with col2:
    st.write("**Youth Keywords:**")
    st.write(", ".join(sorted(usaid_settings.YOUTH_KEYWORDS)[:10]) + "...")

# Run crawler button
if st.button("🚀 Run USAID Crawler", type="primary"):
    if not focus_education and not focus_youth:
        st.error("Please select at least one theme focus (Education or Youth)")
    else:
        # Update settings if custom keywords provided
        if custom_education_keywords.strip():
            usaid_settings.EDUCATION_KEYWORDS = {kw.strip() for kw in custom_education_keywords.split(",")}
        if custom_youth_keywords.strip():
            usaid_settings.YOUTH_KEYWORDS = {kw.strip() for kw in custom_youth_keywords.split(",")}

        # Update max budget
        usaid_settings.MAX_USD_BUDGET = max_budget

        seeds = [s.strip() for s in seeds_text.splitlines() if s.strip()]

        with st.spinner("Crawling USAID repositories for education/youth proposals..."):
            try:
                result = usaid_crawler.run_usaid_crawler(
                    out_dir=out_dir,
                    max_pages=max_pages,
                    delay_sec=delay_sec,
                    seeds=seeds,
                    upload_to_drive=upload_to_drive,
                    drive_folder_id=drive_folder_id if drive_folder_id.strip() else None,
                    return_details=True
                )

                st.success(f"✅ USAID crawler completed successfully!")

                # Display statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Documents", result.total_documents_found)
                with col2:
                    st.metric("Education Focused", result.education_focused)
                with col3:
                    st.metric("Youth Focused", result.youth_focused)
                with col4:
                    st.metric("Under Budget", result.under_budget_threshold)

                # Display Google Drive info if uploaded
                if result.uploaded_to_drive:
                    st.info(f"📁 Results uploaded to Google Drive: [View File]({result.drive_web_link})")

                # Display results
                st.subheader("Results")
                st.write(f"CSV saved to: `{result.csv_path}`")

                if os.path.exists(result.csv_path) and result.rows:
                    df = pd.read_csv(result.csv_path)

                    # Filter display based on selections
                    if not focus_education:
                        df = df[~df['themes'].str.contains('education', case=False, na=False)]
                    if not focus_youth:
                        df = df[~df['themes'].str.contains('youth', case=False, na=False)]

                    st.dataframe(df, use_container_width=True)

                    # Download button
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name="usaid_education_youth_proposals.csv",
                        mime="text/csv"
                    )

                    # Summary insights
                    st.subheader("📊 Summary Insights")

                    if len(df) > 0:
                        avg_budget = df['amount_requested_usd'].mean() if df['amount_requested_usd'].notna().any() else 0
                        total_proposals = len(df)

                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Average Budget:** ${avg_budget:,.2f}" if avg_budget > 0 else "**Average Budget:** Not available")
                            st.write(f"**Total Matching Proposals:** {total_proposals}")

                        with col2:
                            # Document type distribution
                            if 'document_type' in df.columns:
                                doc_types = df['document_type'].value_counts()
                                st.write("**Document Types:**")
                                for doc_type, count in doc_types.head(5).items():
                                    st.write(f"- {doc_type}: {count}")
                    else:
                        st.warning("No proposals found matching the criteria. Try adjusting your filters or keywords.")

                else:
                    st.warning("No results file found or no matching proposals discovered.")

            except Exception as e:
                st.error(f"❌ Error running USAID crawler: {str(e)}")

# Information section
st.subheader("ℹ️ About the USAID Crawler")
st.markdown("""
This crawler searches USAID's primary repositories for education and youth-focused proposals under $100,000:

**Data Sources:**
- **Development Experience Clearinghouse (DEC)**: Technical and programmatic documents
- **Development Data Library (DDL)**: Machine-readable datasets
- **ForeignAssistance.gov**: Award and spending data

**Filtering Criteria:**
- Budget: Under $100,000 USD
- Themes: Education and/or Youth focused content
- Document Types: Proposals, evaluations, reports, grants, technical guidance

**Output:** CSV file with proposal details, budget information, theme analysis, and document metadata.
""")