"""
data_loader.py
Handles file upload, validation, and loading for CSV / Excel / JSON files.
"""

import pandas as pd
import json
from io import BytesIO

MAX_FILE_SIZE_MB = 200
ALLOWED_EXTENSIONS = ["csv", "xlsx", "xls", "json"]


class DataLoadError(Exception):
    """Raised when a file cannot be loaded or validated."""
    pass


def _read_csv_with_delimiter_detection(uploaded_file) -> pd.DataFrame:
    """
    Read a CSV robustly: try to sniff the delimiter (comma, semicolon, tab, pipe)
    instead of blindly assuming comma. Falls back through encodings too.
    This prevents the common 'entire file loaded into 1 column' bug when a CSV
    uses ';' (common in European exports) or tab/pipe separators.
    """
    import csv

    candidate_encodings = ["utf-8", "latin1"]
    candidate_delimiters = [",", ";", "\t", "|"]

    last_error = None

    for encoding in candidate_encodings:
        uploaded_file.seek(0)
        try:
            raw_bytes = uploaded_file.read()
            text_sample = raw_bytes[:8192].decode(encoding, errors="strict")
        except (UnicodeDecodeError, Exception) as e:
            last_error = e
            continue

        # Try to sniff the delimiter from a sample of the file
        detected_delimiter = None
        try:
            dialect = csv.Sniffer().sniff(text_sample, delimiters=",;\t|")
            detected_delimiter = dialect.delimiter
        except csv.Error:
            detected_delimiter = None

        delimiters_to_try = [detected_delimiter] if detected_delimiter else []
        delimiters_to_try += [d for d in candidate_delimiters if d != detected_delimiter]

        best_df = None
        best_col_count = 1

        for delim in delimiters_to_try:
            try:
                from io import BytesIO
                trial_df = pd.read_csv(BytesIO(raw_bytes), sep=delim, encoding=encoding, engine="python")
                if trial_df.shape[1] > best_col_count:
                    best_col_count = trial_df.shape[1]
                    best_df = trial_df
                    # Good enough — a real multi-column parse found
                    if best_col_count > 1:
                        break
            except Exception as e:
                last_error = e
                continue

        if best_df is not None:
            return best_df

        # As a last resort for this encoding, do a plain default read
        try:
            from io import BytesIO
            return pd.read_csv(BytesIO(raw_bytes), encoding=encoding)
        except Exception as e:
            last_error = e
            continue

    raise DataLoadError(f"Could not parse CSV file with any known delimiter/encoding: {last_error}")


def validate_file(uploaded_file) -> None:
    """Validate file extension and size before attempting to parse it."""
    if uploaded_file is None:
        raise DataLoadError("No file was uploaded.")

    ext = uploaded_file.name.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise DataLoadError(
            f"Unsupported file type '.{ext}'. Please upload CSV, XLSX, or JSON."
        )

    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise DataLoadError(
            f"File is too large ({size_mb:.1f} MB). Maximum allowed is {MAX_FILE_SIZE_MB} MB."
        )

    if uploaded_file.size == 0:
        raise DataLoadError("The uploaded file is empty.")


def load_dataset(uploaded_file) -> pd.DataFrame:
    """
    Load a validated uploaded file into a pandas DataFrame.
    Supports CSV, Excel (xlsx/xls), and JSON (list-of-records or nested).
    """
    validate_file(uploaded_file)
    ext = uploaded_file.name.split(".")[-1].lower()

    try:
        if ext == "csv":
            df = _read_csv_with_delimiter_detection(uploaded_file)

        elif ext in ("xlsx", "xls"):
            df = pd.read_excel(uploaded_file)

        elif ext == "json":
            raw = json.load(uploaded_file)
            if isinstance(raw, list):
                df = pd.json_normalize(raw)
            elif isinstance(raw, dict):
                # try common shapes: {"data": [...]}, or a single record
                if "data" in raw and isinstance(raw["data"], list):
                    df = pd.json_normalize(raw["data"])
                else:
                    df = pd.json_normalize(raw)
            else:
                raise DataLoadError("JSON structure not recognized as tabular data.")
        else:
            raise DataLoadError("Unsupported file format.")

    except DataLoadError:
        raise
    except Exception as e:
        raise DataLoadError(f"Failed to parse file: {e}")

    if df is None or df.empty:
        raise DataLoadError("The uploaded dataset contains no rows.")

    if df.shape[1] == 0:
        raise DataLoadError("The uploaded dataset contains no columns.")

    # Clean column names lightly (strip whitespace)
    df.columns = [str(c).strip() for c in df.columns]

    return df


def get_file_metadata(uploaded_file, df: pd.DataFrame) -> dict:
    """Return basic metadata about the uploaded file/dataset."""
    memory_bytes = df.memory_usage(deep=True).sum()
    return {
        "filename": uploaded_file.name,
        "size_kb": round(uploaded_file.size / 1024, 2),
        "rows": df.shape[0],
        "columns": df.shape[1],
        "memory_usage": f"{memory_bytes / (1024 ** 2):.2f} MB"
        if memory_bytes > 1024 ** 2
        else f"{memory_bytes / 1024:.2f} KB",
    }


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert a DataFrame to downloadable CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")


def load_sample_dataset() -> pd.DataFrame:
    """Load the bundled example dataset (assets/sample_dataset.csv)."""
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "assets", "sample_dataset.csv")
    return pd.read_csv(path)
