# 📊 AI Data Analyst Pro

**Upload your data. Get instant insights, visualizations, predictions, and AI-powered reports.**

A production-ready, modular Streamlit application for automated data analysis — built for
students, freelancers, analysts, and startups who need fast, no-code insight from raw data.

---

## ✨ Features

- **Modern dashboard UI** — glassmorphism cards, dark theme, custom CSS (no default Streamlit look)
- **File upload** — CSV, Excel (.xlsx), JSON, with validation and size limits
- **Automatic data profiling** — shape, missing values, duplicates, dtypes, data quality score
- **Data cleaning** — one-click auto-clean, missing value imputation, dtype conversion, outlier removal
- **EDA & statistics** — mean/median/mode/std, correlation matrix, categorical summaries
- **AI chart generator** — auto-recommended interactive Plotly charts (bar, line, scatter, histogram, box, pie, heatmap)
- **AI insights engine** — LLM-generated business insights grounded strictly in your dataset's statistics (Claude / OpenAI / Gemini), with a fully functional **offline fallback** if no API key is set
- **AI chatbot** — ask natural-language questions about your uploaded data
- **ML prediction module** — automatic classification/regression detection, Random Forest / Logistic / Linear Regression, full metrics (accuracy, precision, recall, F1, RMSE, MAE, R²)
- **PDF report generator** — professional report with stats, insights, and ML results (ReportLab)
- **Session management** — dataset, cleaning state, chat history, and ML results persist across pages via `st.session_state`
- **Security** — API keys via `st.secrets` only, never hardcoded or exposed to the client

---

## 🗂️ Project Structure

```
ai-data-analyst-pro/
├── app.py                        # Main Streamlit app (page routing + UI)
├── requirements.txt
├── README.md
├── .streamlit/
│   ├── config.toml                # Theme config
│   └── secrets.toml.example       # Copy to secrets.toml and fill in your API key
├── src/
│   ├── data_loader.py             # Upload, validation, parsing (CSV/XLSX/JSON)
│   ├── cleaner.py                 # Cleaning, imputation, outlier detection
│   ├── analyzer.py                # Profiling, statistics, correlation
│   ├── visualizer.py              # Plotly chart generation + recommendations
│   ├── ai_engine.py                # LLM insights + chatbot (multi-provider, offline fallback)
│   ├── ml_model.py                # Classification/regression training & evaluation
│   ├── report_generator.py        # PDF report builder (ReportLab)
│   └── utils.py                   # Custom CSS + UI helper components
└── assets/
    └── sample_dataset.csv         # Example retail sales dataset for demo/testing
```

---

## 🚀 Run Locally

```bash
git clone <your-repo-url>
cd ai-data-analyst-pro
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Optional: enable full AI features
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml and add your API key

streamlit run app.py
```

The app is **fully usable without any API key** — AI Insights and the Chatbot automatically
fall back to a deterministic, statistics-based summary if no key is configured.

---

## ☁️ Deploy to Streamlit Community Cloud

1. Push this project to a **public or private GitHub repository**.
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **New app**.
3. Select your repo, branch, and set **Main file path** to `app.py`.
4. Under **Advanced settings → Secrets**, paste your key(s), e.g.:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
   (Do **not** commit a real `secrets.toml` file — use the Cloud secrets UI instead.)
5. Click **Deploy**. Your app will be live at `https://<your-app-name>.streamlit.app`.

**Notes for Streamlit Cloud compatibility:**
- No local file paths outside the repo are used.
- No GPU dependencies — all ML runs on scikit-learn (CPU only).
- `requirements.txt` pins only lightweight, well-supported packages.
- Python 3.10+ compatible.

---

## 🔑 Enabling AI Features

The AI Insights and Chatbot pages support three providers — configure **any one**:

| Provider | Secret key | Model used |
|---|---|---|
| Anthropic (Claude) | `ANTHROPIC_API_KEY` | `claude-sonnet-4-6` |
| OpenAI | `OPENAI_API_KEY` | `gpt-4o-mini` |
| Google Gemini | `GEMINI_API_KEY` | `gemini-1.5-flash` |

`google-generativeai` (Gemini) is already included in `requirements.txt`, so **Gemini works out of the box**
with just a `GEMINI_API_KEY` — no extra setup needed. If you choose OpenAI instead, add `openai` to
`requirements.txt` (left out by default since it's not one of the two defaults).

All AI responses are grounded in an aggregated statistical summary of your dataset — never raw
row-level data — and the system prompt explicitly forbids inventing numbers or trends not present
in that summary.

---

## 🧪 Testing Checklist

- [ ] Upload a valid CSV — preview, metadata, and dtypes render correctly
- [ ] Upload a valid XLSX — parses correctly
- [ ] Upload a valid JSON (list of records) — parses correctly
- [ ] Upload an unsupported file type (e.g. `.txt`) — shows a friendly error, doesn't crash
- [ ] Upload an empty file — shows a friendly error
- [ ] Load the bundled example dataset — works with zero setup
- [ ] Data Cleaning: Auto-Clean, missing value strategies, dtype conversion, outlier removal all run without error
- [ ] Download cleaned CSV — opens correctly in Excel/Sheets
- [ ] EDA page renders summary stats, categorical summary, and correlation heatmap
- [ ] Visualizations page shows recommended charts + custom chart builder works for all 7 chart types
- [ ] AI Insights page works **with no API key configured** (offline mode) and **with a key configured**
- [ ] Chatbot answers a question grounded in the dataset (test both modes)
- [ ] ML Predictions: train a classification model and a regression model; metrics display correctly
- [ ] PDF Report: generates and downloads successfully, includes all sections
- [ ] Reload/refresh the browser mid-session — session state behaves reasonably (dataset persists during the session)
- [ ] Test with a dataset that has all-numeric columns, all-categorical columns, and a mixed dataset

---

## 🔒 Security Notes

- API keys are read only via `st.secrets` — never hardcoded, logged, or sent to the browser.
- Uploaded files are processed **in-memory for the session only**; nothing is written to persistent storage.
- File size and type are validated before parsing.
- All I/O operations are wrapped in exception handling with user-friendly error messages.

---

## 📄 License

Free to use and modify for personal, educational, or commercial projects.
