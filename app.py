"""
AI Data Analyst Pro
--------------------
A production-ready AI-powered data analysis assistant built with Streamlit.

Run locally:   streamlit run app.py
Deploy:        Streamlit Community Cloud (see README.md)
"""

import streamlit as st
import pandas as pd
import traceback

from src import data_loader, cleaner, analyzer, visualizer, ai_engine, ml_model, report_generator, utils

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Data Analyst Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

utils.inject_custom_css()

# ----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# ----------------------------------------------------------------------------
defaults = {
    "df": None,
    "df_cleaned": None,
    "filename": None,
    "chat_history": [],
    "ml_result": None,
    "ai_insights_cache": None,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


def get_active_df():
    """Return the cleaned dataset if available, otherwise the raw uploaded dataset."""
    if st.session_state.df_cleaned is not None:
        return st.session_state.df_cleaned
    return st.session_state.df


# ----------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## AI_DATA_ANALYST // PRO")
    st.caption("upload → clean → analyze → predict → report")
    st.divider()

    page = st.radio(
        "Navigate",
        [
            "🏠 Home",
            "📁 Upload Data",
            "🧹 Data Cleaning",
            "📈 EDA & Statistics",
            "📊 Visualizations",
            "🤖 AI Insights",
            "💬 AI Chatbot",
            "🎯 ML Predictions",
            "📄 PDF Report",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    if st.session_state.df is not None:
        st.success(f"loaded: {st.session_state.filename}")
        st.caption(f"{st.session_state.df.shape[0]} rows × {st.session_state.df.shape[1]} cols")
    else:
        st.info("no dataset loaded")

    provider, _ = ai_engine.get_available_provider(st.secrets if hasattr(st, "secrets") else {})
    st.caption(f"ai_provider: {provider or 'offline'}")

# ============================================================================
# PAGE: HOME
# ============================================================================
if page == "🏠 Home":
    utils.hero_section()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(utils.feature_card("A1", "🧹", "Automatic Cleaning",
                     "Detect and fix missing values, duplicates, and outliers in one click."),
                     unsafe_allow_html=True)
    with c2:
        st.markdown(utils.feature_card("B1", "📊", "Interactive Visuals",
                     "AI-recommended, fully interactive Plotly charts tailored to your data."),
                     unsafe_allow_html=True)
    with c3:
        st.markdown(utils.feature_card("C1", "🤖", "AI-Powered Insights",
                     "Ask questions and get business insights grounded strictly in your data."),
                     unsafe_allow_html=True)

    st.write("")
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown(utils.feature_card("A2", "🎯", "ML Predictions",
                     "Train classification or regression models automatically — no code needed."),
                     unsafe_allow_html=True)
    with c5:
        st.markdown(utils.feature_card("B2", "📄", "PDF Reports",
                     "Export a polished, professional report with charts, stats, and insights."),
                     unsafe_allow_html=True)
    with c6:
        st.markdown(utils.feature_card("C2", "🔒", "Private & Secure",
                     "Your data is processed only in your session — never stored permanently."),
                     unsafe_allow_html=True)

    st.write("")
    utils.section_header("Pipeline")
    steps = st.columns(5)
    labels = ["Upload", "Clean", "Explore", "Predict", "Report"]
    icons = ["📁", "🧹", "📈", "🎯", "📄"]
    for i, (col, label, icon) in enumerate(zip(steps, labels, icons), start=1):
        with col:
            st.markdown(utils.pipeline_step(f"0{i}", icon, label), unsafe_allow_html=True)

    st.write("")
    utils.section_header("Supported Formats")
    st.markdown(f"{utils.ext_tag('csv')} {utils.ext_tag('xlsx')} {utils.ext_tag('json')}",
                unsafe_allow_html=True)

    st.write("")
    st.info("🔐 **Security:** Files are processed in-memory during your session only. "
            "API keys are stored securely via Streamlit secrets and are never exposed to the client.")

    if st.button("Run First Analysis →"):
        st.info("Go to **📁 Upload Data** in the sidebar to begin.")

    utils.app_footer()

# ============================================================================
# PAGE: UPLOAD DATA
# ============================================================================
elif page == "📁 Upload Data":
    utils.section_header("📁 Upload Your Dataset")

    col_a, col_b = st.columns([2, 1])
    with col_a:
        uploaded_file = st.file_uploader(
            "Drag and drop your file here, or click to browse",
            type=["csv", "xlsx", "xls", "json"],
            help="Maximum file size: 200 MB. Supported formats: CSV, Excel, JSON.",
        )
    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📎 Load Example Dataset"):
            try:
                df = data_loader.load_sample_dataset()
                st.session_state.df = df
                st.session_state.df_cleaned = None
                st.session_state.filename = "sample_dataset.csv"
                st.session_state.ml_result = None
                st.session_state.ai_insights_cache = None
                st.success("Sample dataset loaded!")
            except Exception as e:
                st.error(f"Could not load sample dataset: {e}")

    if uploaded_file is not None:
        try:
            with st.spinner("Reading and validating file..."):
                df = data_loader.load_dataset(uploaded_file)
                meta = data_loader.get_file_metadata(uploaded_file, df)
            st.session_state.df = df
            st.session_state.df_cleaned = None
            st.session_state.filename = uploaded_file.name
            st.session_state.ml_result = None
            st.session_state.ai_insights_cache = None
            st.success(f"✅ Successfully loaded **{meta['filename']}**")
        except data_loader.DataLoadError as e:
            st.error(f"❌ {e}")
        except Exception as e:
            st.error(f"❌ Unexpected error while loading file: {e}")

    if st.session_state.df is not None:
        df = st.session_state.df
        meta = {
            "filename": st.session_state.filename,
            "rows": df.shape[0],
            "columns": df.shape[1],
            "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB",
        }

        st.write("")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Filename", meta["filename"])
        m2.metric("Rows", f"{meta['rows']:,}")
        m3.metric("Columns", meta["columns"])
        m4.metric("Memory Usage", meta["memory_usage"])

        st.write("")
        utils.section_header("Dataset Preview")
        st.dataframe(df.head(50), use_container_width=True)

        with st.expander("📋 Column Data Types"):
            dtype_df = pd.DataFrame({"Column": df.columns, "Data Type": df.dtypes.astype(str).values})
            st.dataframe(dtype_df, use_container_width=True, hide_index=True)
    else:
        st.info("👆 Upload a CSV, Excel, or JSON file to get started — or load the example dataset.")

# ============================================================================
# PAGE: DATA CLEANING
# ============================================================================
elif page == "🧹 Data Cleaning":
    utils.section_header("🧹 Data Cleaning")

    if st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first (see **📁 Upload Data**).")
    else:
        df = get_active_df()
        quality = cleaner.get_quality_report(df)

        q1, q2, q3, q4 = st.columns(4)
        q1.metric("Quality Score", f"{quality['score']}/100", quality["label"])
        q2.metric("Missing Cells", quality["missing_cells"], f"{quality['missing_pct']}%")
        q3.metric("Duplicate Rows", quality["duplicate_rows"], f"{quality['duplicate_pct']}%")
        q4.metric("Total Rows", df.shape[0])

        st.write("")
        tab1, tab2, tab3, tab4 = st.tabs(["⚡ Quick Clean", "🕳️ Missing Values", "🔧 Convert Types", "🎯 Outliers"])

        with tab1:
            st.write("One-click automatic cleaning: removes exact duplicates, fills numeric gaps with median, "
                      "and categorical gaps with the most frequent value.")
            if st.button("✨ Auto-Clean Dataset"):
                st.session_state.df_cleaned = cleaner.auto_clean(df)
                st.success("Dataset auto-cleaned!")
                st.rerun()

            if st.button("↩️ Reset to Original"):
                st.session_state.df_cleaned = None
                st.success("Reverted to original uploaded dataset.")
                st.rerun()

            st.divider()
            colr1, colr2 = st.columns(2)
            with colr1:
                if st.button("🗑️ Remove Duplicate Rows Only"):
                    st.session_state.df_cleaned = cleaner.remove_duplicates(df)
                    st.success("Duplicates removed.")
                    st.rerun()
            with colr2:
                cols_to_drop = st.multiselect("Remove specific columns", df.columns.tolist())
                if st.button("🗑️ Remove Selected Columns") and cols_to_drop:
                    st.session_state.df_cleaned = cleaner.remove_columns(df, cols_to_drop)
                    st.success(f"Removed columns: {', '.join(cols_to_drop)}")
                    st.rerun()

        with tab2:
            missing_cols = df.columns[df.isna().any()].tolist()
            if not missing_cols:
                st.success("✅ No missing values detected.")
            else:
                st.write(f"Columns with missing values: {', '.join(missing_cols)}")
                strategy = st.selectbox(
                    "Choose imputation strategy",
                    ["mean", "median", "mode", "zero", "ffill", "bfill", "drop_rows", "drop_columns"],
                    help="mean/median apply to numeric columns only. Mode/zero apply to all.",
                )
                target_cols = st.multiselect("Apply to columns", missing_cols, default=missing_cols)
                if st.button("Apply Missing Value Strategy"):
                    st.session_state.df_cleaned = cleaner.handle_missing_values(df, strategy, target_cols)
                    st.success(f"Applied '{strategy}' strategy.")
                    st.rerun()

        with tab3:
            col_to_convert = st.selectbox("Select column", df.columns.tolist())
            target_type = st.selectbox("Convert to", ["int", "float", "string", "datetime", "category"])
            if st.button("Convert Type"):
                try:
                    st.session_state.df_cleaned = cleaner.convert_dtype(df, col_to_convert, target_type)
                    st.success(f"Converted '{col_to_convert}' to {target_type}.")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

        with tab4:
            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            if not numeric_cols:
                st.info("No numeric columns available for outlier detection.")
            else:
                out_col = st.selectbox("Select numeric column", numeric_cols)
                mask = cleaner.detect_outliers_iqr(df, out_col)
                st.write(f"Detected **{mask.sum()}** outliers in '{out_col}' using the IQR method.")
                if mask.sum() > 0 and st.button("Remove Outliers"):
                    st.session_state.df_cleaned = cleaner.remove_outliers(df, out_col)
                    st.success("Outliers removed.")
                    st.rerun()

        st.write("")
        utils.section_header("Cleaned Dataset Preview")
        active_df = get_active_df()
        st.dataframe(active_df.head(50), use_container_width=True)

        csv_bytes = data_loader.df_to_csv_bytes(active_df)
        st.download_button("⬇️ Download Cleaned Dataset (CSV)", csv_bytes,
                            file_name="cleaned_dataset.csv", mime="text/csv")

# ============================================================================
# PAGE: EDA & STATISTICS
# ============================================================================
elif page == "📈 EDA & Statistics":
    utils.section_header("📈 Exploratory Data Analysis")

    if st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first.")
    else:
        df = get_active_df()
        profile = analyzer.profile_dataset(df)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows", profile["n_rows"])
        c2.metric("Columns", profile["n_columns"])
        c3.metric("Numeric Cols", len(profile["numeric_columns"]))
        c4.metric("Categorical Cols", len(profile["categorical_columns"]))

        st.write("")
        utils.section_header("Summary Statistics (Numeric)")
        stats_df = analyzer.summary_statistics(df)
        if stats_df.empty:
            st.info("No numeric columns found.")
        else:
            st.dataframe(stats_df, use_container_width=True)

        utils.section_header("Categorical Summary")
        cat_df = analyzer.categorical_summary(df)
        if cat_df.empty:
            st.info("No categorical columns found.")
        else:
            st.dataframe(cat_df, use_container_width=True)

        utils.section_header("Correlation Matrix")
        corr = analyzer.correlation_matrix(df)
        if corr.empty:
            st.info("Not enough numeric columns for correlation analysis.")
        else:
            fig = visualizer.make_chart(df, "heatmap", title="Correlation Heatmap")
            st.plotly_chart(fig, use_container_width=True)

            top_corr = analyzer.top_correlations(df, 5)
            if top_corr:
                st.write("**Top correlated pairs:**")
                for a, b, v in top_corr:
                    st.write(f"- `{a}` vs `{b}`: **{v}**")

# ============================================================================
# PAGE: VISUALIZATIONS
# ============================================================================
elif page == "📊 Visualizations":
    utils.section_header("📊 AI Chart Generator")

    if st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first.")
    else:
        df = get_active_df()
        recs = visualizer.recommend_charts(df)

        st.write("**🤖 Recommended charts based on your data:**")
        tabs = st.tabs([f"{r['title'][:28]}" for r in recs] if recs else ["No recommendations"])

        for tab, rec in zip(tabs, recs):
            with tab:
                try:
                    fig = visualizer.make_chart(
                        df, rec["type"],
                        x=rec.get("x"), y=rec.get("y"), title=rec["title"]
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Could not render chart: {e}")

        st.divider()
        utils.section_header("🎨 Build a Custom Chart")
        col1, col2, col3 = st.columns(3)
        with col1:
            chart_type = st.selectbox("Chart type", ["bar", "line", "scatter", "histogram", "box", "pie", "heatmap"])
        with col2:
            x_col = st.selectbox("X-axis / column", ["(none)"] + df.columns.tolist())
        with col3:
            y_col = st.selectbox("Y-axis (if applicable)", ["(none)"] + df.select_dtypes(include="number").columns.tolist())

        if st.button("Generate Chart"):
            try:
                fig = visualizer.make_chart(
                    df, chart_type,
                    x=None if x_col == "(none)" else x_col,
                    y=None if y_col == "(none)" else y_col,
                    title=f"Custom {chart_type} chart",
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Could not render chart: {e}")

# ============================================================================
# PAGE: AI INSIGHTS
# ============================================================================
elif page == "🤖 AI Insights":
    utils.section_header("🤖 AI-Powered Data Insights")

    if st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first.")
    else:
        df = get_active_df()
        profile = analyzer.profile_dataset(df)
        top_corr = analyzer.top_correlations(df, 5)

        st.write("**⚡ Quick statistical insights (always available, no API key needed):**")
        rule_insights = ai_engine.generate_rule_based_insights(df, profile, top_corr)
        for insight in rule_insights:
            st.markdown(f"- {insight}")

        st.divider()
        st.write("**🧠 Deep AI-generated business insights:**")
        secrets = dict(st.secrets) if hasattr(st, "secrets") else {}
        provider, _ = ai_engine.get_available_provider(secrets)
        if provider is None:
            st.info("No AI API key configured — add one to `.streamlit/secrets.toml` for narrative "
                    "business insights. Showing statistical insights above in the meantime.")

        if st.button("✨ Generate AI Insights"):
            with st.spinner("Analyzing your dataset..."):
                context = analyzer.build_ai_context_summary(df)
                insights = ai_engine.generate_ai_insights(secrets, context)
                st.session_state.ai_insights_cache = insights

        if st.session_state.ai_insights_cache:
            st.markdown(st.session_state.ai_insights_cache)

# ============================================================================
# PAGE: AI CHATBOT
# ============================================================================
elif page == "💬 AI Chatbot":
    utils.section_header("💬 Ask Your Data")

    if st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first.")
    else:
        df = get_active_df()
        secrets = dict(st.secrets) if hasattr(st, "secrets") else {}

        st.caption("Ask questions like: \"What are the important trends?\", \"Explain this dataset\", "
                    "\"Which features affect sales?\", \"Give business recommendations.\"")

        for msg in st.session_state.chat_history:
            role_class = "chat-user" if msg["role"] == "user" else "chat-ai"
            label = "🧑 You" if msg["role"] == "user" else "🤖 AI"
            st.markdown(f'<div class="{role_class}"><b>{label}:</b><br>{msg["content"]}</div>',
                        unsafe_allow_html=True)

        question = st.chat_input("Ask a question about your data...")
        if question:
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.spinner("Thinking..."):
                context = analyzer.build_ai_context_summary(df)
                answer = ai_engine.ask_ai(secrets, context, question)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()

        if st.session_state.chat_history and st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

# ============================================================================
# PAGE: ML PREDICTIONS
# ============================================================================
elif page == "🎯 ML Predictions":
    utils.section_header("🎯 Machine Learning Predictions")

    if st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first.")
    else:
        df = get_active_df()

        target_column = st.selectbox("🎯 Select target column (what you want to predict)", df.columns.tolist())

        if target_column:
            task_type = ml_model.detect_task_type(df, target_column)
            st.info(f"Detected task type: **{task_type.upper()}**")

            available_features = ml_model.get_usable_features(df, target_column)
            feature_columns = st.multiselect(
                "Select feature columns", available_features, default=available_features[:10]
            )

            algo_options = (
                ["random_forest", "logistic_regression"] if task_type == "classification"
                else ["linear_regression", "random_forest"]
            )
            algorithm = st.selectbox("Select algorithm", algo_options)
            test_size = st.slider("Test set size", 0.1, 0.4, 0.2, 0.05)

            if st.button("🚀 Train Model"):
                if not feature_columns:
                    st.error("Please select at least one feature column.")
                elif df[target_column].dropna().nunique() < 2:
                    st.error("Target column needs at least 2 distinct values to train a model.")
                else:
                    try:
                        with st.spinner("Training model..."):
                            X, y, task_type, target_encoder = ml_model.prepare_data(df, target_column, feature_columns)
                            result = ml_model.train_model(X, y, task_type, algorithm, test_size)
                            result["target"] = target_column
                            result["algorithm"] = algorithm
                            result["target_encoder"] = target_encoder
                            st.session_state.ml_result = result
                        st.success("✅ Model trained successfully!")
                    except Exception as e:
                        st.error(f"Training failed: {e}")
                        st.code(traceback.format_exc())

        if st.session_state.ml_result:
            result = st.session_state.ml_result
            st.write("")
            utils.section_header("📊 Model Performance")

            metrics = result["metrics"]
            if result["task_type"] == "classification":
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Accuracy", metrics["accuracy"])
                m2.metric("Precision", metrics["precision"])
                m3.metric("Recall", metrics["recall"])
                m4.metric("F1 Score", metrics["f1_score"])
            else:
                m1, m2, m3 = st.columns(3)
                m1.metric("RMSE", metrics["rmse"])
                m2.metric("MAE", metrics["mae"])
                m3.metric("R² Score", metrics["r2_score"])

            if result["feature_importance"] is not None:
                st.write("")
                st.write("**🔑 Feature Importance**")
                fi = result["feature_importance"].reset_index()
                fi.columns = ["feature", "importance"]
                import plotly.express as px
                fig = px.bar(fi.head(15), x="importance", y="feature", orientation="h",
                             template="plotly_dark", color="importance",
                             color_continuous_scale=["#3a2f1c", "#8a6414", "#ffb000"])
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                   font=dict(color="#ede6d6", family="IBM Plex Mono, monospace"))
                st.plotly_chart(fig, use_container_width=True)

            st.write("")
            st.write("**🔮 Sample Predictions vs Actual**")
            comparison = pd.DataFrame({
                "Actual": result["y_test"].values[:15],
                "Predicted": result["y_pred"][:15],
            })
            st.dataframe(comparison, use_container_width=True)

# ============================================================================
# PAGE: PDF REPORT
# ============================================================================
elif page == "📄 PDF Report":
    utils.section_header("📄 Generate PDF Report")

    if st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first.")
    else:
        df = get_active_df()
        st.write("This report includes dataset overview, data quality, summary statistics, "
                  "AI insights, and ML results (if a model has been trained).")

        include_ai = st.checkbox("Include AI insights (requires generating them first, or uses offline summary)", value=True)

        if st.button("📄 Generate PDF Report"):
            with st.spinner("Building your report..."):
                profile = analyzer.profile_dataset(df)
                quality = cleaner.get_quality_report(df)
                stats_df = analyzer.summary_statistics(df)

                if include_ai:
                    ai_text = st.session_state.ai_insights_cache
                    if not ai_text:
                        secrets = dict(st.secrets) if hasattr(st, "secrets") else {}
                        context = analyzer.build_ai_context_summary(df)
                        ai_text = ai_engine.generate_ai_insights(secrets, context)
                else:
                    ai_text = "AI insights were not included in this report."

                ml_summary = None
                if st.session_state.ml_result:
                    r = st.session_state.ml_result
                    ml_summary = {
                        "task_type": r["task_type"],
                        "target": r["target"],
                        "algorithm": r["algorithm"],
                        "metrics": r["metrics"],
                    }

                try:
                    pdf_bytes = report_generator.generate_pdf_report(
                        filename=st.session_state.filename or "dataset",
                        profile=profile,
                        quality=quality,
                        stats_df=stats_df,
                        ai_insights=ai_text,
                        ml_summary=ml_summary,
                    )
                    st.success("✅ Report generated!")
                    st.download_button(
                        "⬇️ Download PDF Report", pdf_bytes,
                        file_name="ai_data_analyst_report.pdf", mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Report generation failed: {e}")
                    st.code(traceback.format_exc())
