"""
report_generator.py
Generates a professional PDF report summarizing the dataset, quality checks,
statistics, AI insights, and ML results using ReportLab.
"""

from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)

PRIMARY = colors.HexColor("#0f766e")
ACCENT = colors.HexColor("#134e4a")
LIGHT = colors.HexColor("#f0fdfa")


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleBig", fontSize=24, leading=28, textColor=PRIMARY,
                               spaceAfter=6, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="SubTitle", fontSize=12, textColor=colors.grey, spaceAfter=20))
    styles.add(ParagraphStyle(name="Section", fontSize=15, textColor=ACCENT, spaceBefore=18,
                               spaceAfter=8, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="Body", fontSize=10, leading=15))
    styles.add(ParagraphStyle(name="ReportBullet", fontSize=10, leading=15, leftIndent=12))
    return styles


def _table(data, col_widths=None):
    t = Table(data, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def generate_pdf_report(
    filename: str,
    profile: dict,
    quality: dict,
    stats_df,
    ai_insights: str,
    ml_summary: dict = None,
    chart_images: list = None,
) -> bytes:
    """
    Build the full PDF report and return it as bytes.
    chart_images: list of (title, PNG bytes) tuples to embed.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm,
                             leftMargin=1.8 * cm, rightMargin=1.8 * cm)
    styles = _styles()
    story = []

    # --- Cover ---
    story.append(Paragraph("AI Data Analyst Pro", styles["TitleBig"]))
    story.append(Paragraph("Automated Data Analysis Report", styles["SubTitle"]))
    story.append(Paragraph(f"<b>Source file:</b> {filename}", styles["Body"]))
    story.append(Paragraph(f"<b>Generated on:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Body"]))
    story.append(Spacer(1, 12))

    # --- Dataset Overview ---
    story.append(Paragraph("1. Dataset Overview", styles["Section"]))
    overview_data = [
        ["Metric", "Value"],
        ["Rows", str(profile["n_rows"])],
        ["Columns", str(profile["n_columns"])],
        ["Numeric Columns", str(len(profile["numeric_columns"]))],
        ["Categorical Columns", str(len(profile["categorical_columns"]))],
        ["Datetime Columns", str(len(profile["datetime_columns"]))],
        ["Duplicate Rows", str(profile["duplicate_rows"])],
    ]
    story.append(_table(overview_data, col_widths=[7 * cm, 7 * cm]))

    # --- Data Quality ---
    story.append(Paragraph("2. Data Quality", styles["Section"]))
    quality_data = [
        ["Metric", "Value"],
        ["Quality Score", f"{quality['score']} / 100 ({quality['label']})"],
        ["Missing Cells", f"{quality['missing_cells']} ({quality['missing_pct']}%)"],
        ["Duplicate Rows", f"{quality['duplicate_rows']} ({quality['duplicate_pct']}%)"],
    ]
    story.append(_table(quality_data, col_widths=[7 * cm, 7 * cm]))

    # --- Statistics ---
    if stats_df is not None and not stats_df.empty:
        story.append(Paragraph("3. Summary Statistics", styles["Section"]))
        table_data = [["Column"] + list(stats_df.columns)]
        for idx, row in stats_df.iterrows():
            table_data.append([str(idx)] + [str(v) for v in row.values])
        story.append(_table(table_data))

    # --- Charts ---
    if chart_images:
        story.append(PageBreak())
        story.append(Paragraph("4. Visualizations", styles["Section"]))
        for title, img_bytes in chart_images:
            story.append(Paragraph(title, styles["Body"]))
            story.append(Spacer(1, 6))
            try:
                img = Image(BytesIO(img_bytes), width=15 * cm, height=8 * cm)
                story.append(img)
                story.append(Spacer(1, 12))
            except Exception:
                story.append(Paragraph("(chart image could not be embedded)", styles["Body"]))

    # --- AI Insights ---
    story.append(PageBreak())
    story.append(Paragraph("5. AI-Generated Insights", styles["Section"]))
    for line in (ai_insights or "No insights generated.").split("\n"):
        if line.strip():
            story.append(Paragraph(line.replace("**", ""), styles["Body"]))
            story.append(Spacer(1, 4))

    # --- ML Results ---
    if ml_summary:
        story.append(Paragraph("6. Machine Learning Results", styles["Section"]))
        story.append(Paragraph(f"<b>Task type:</b> {ml_summary.get('task_type', 'N/A')}", styles["Body"]))
        story.append(Paragraph(f"<b>Target column:</b> {ml_summary.get('target', 'N/A')}", styles["Body"]))
        story.append(Paragraph(f"<b>Algorithm:</b> {ml_summary.get('algorithm', 'N/A')}", styles["Body"]))
        story.append(Spacer(1, 8))
        metric_rows = [["Metric", "Value"]]
        for k, v in ml_summary.get("metrics", {}).items():
            if k != "confusion_matrix":
                metric_rows.append([k.upper(), str(v)])
        story.append(_table(metric_rows, col_widths=[7 * cm, 7 * cm]))

    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "Generated by AI Data Analyst Pro — insights are derived from statistical "
        "analysis of the uploaded dataset only.",
        ParagraphStyle(name="Footer", fontSize=8, textColor=colors.grey)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
