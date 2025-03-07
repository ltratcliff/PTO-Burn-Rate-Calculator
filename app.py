from shiny import App, render, ui, reactive
import pandas as pd
import numpy as np
from io import BytesIO

def calculate_weekly_value(input_date):
    # Define the reset date for each year (May 17)
    reset_date = pd.Timestamp(input_date.year, 5, 17)

    # If the date is before May 17 of the current year, use previous year's May 17
    if input_date < reset_date:
        reset_date = pd.Timestamp(input_date.year - 1, 5, 17)

    # Calculate the number of weeks since the reset date
    weeks_diff = (input_date - reset_date).days // 7

    # Calculate the value
    value = 1875 - (weeks_diff * 40)

    return max(value, 0)  # Ensure the value doesn't go negative



# Custom CSS for table styling
custom_css = """
.table {
    width: 100%;
    margin-bottom: 1rem;
    color: #212529;
    border-collapse: collapse;
}
.table th, .table td {
    padding: 0.75rem;
    border: 1px solid #dee2e6;
}
.table thead th {
    background-color: #f8f9fa;
    border-bottom: 2px solid #dee2e6;
}
.negative {
    background-color: lightgreen;
}
.shiny-text-output {
    font-size: 1.1em;
    font-weight: bold;
    margin: 10px 0;
    padding: 8px;
    background-color: #f8f9fa;
    border-radius: 4px;
    border: 1px solid #dee2e6;
}
"""

app_ui = ui.page_fluid(
    ui.tags.style(custom_css),
    ui.h2("Burn Rate Calculator"),
    ui.page_sidebar(
        ui.sidebar(
            ui.output_text("current_date_display"),
            ui.output_text("remaining_hours_display"),
            ui.hr(),
            ui.input_file("file", "Upload Excel File", accept=[".xlsx"]),
            ui.output_ui("download_button")
        ),
        ui.output_table("result_table", style="table-cell { background-color: lightgreen !important; }")
    )
)

def server(input, output, session):
    @output
    @render.text
    def current_date_display():
        current_date = pd.Timestamp.now()
        return f"Current Date: {current_date.strftime('%B %d, %Y')}"

    @output
    @render.text
    def remaining_hours_display():
        current_date = pd.Timestamp.now()
        hours = calculate_weekly_value(current_date)
        return f"Remaining Hours: {hours:.2f}"

    @reactive.Calc
    def process_data():
        try:
            if not input.file():
                return None

            file_path = input.file()[0]["datapath"]
            # Calculate current hours based on today's date
            current_date = pd.Timestamp.now()
            current_hours_val = calculate_weekly_value(current_date)

            # Read the Excel file
            df = pd.read_excel(file_path, usecols=['Employee Name', 'Pay Type', 'Regular Hours'])

            if df.empty:
                return pd.DataFrame({'Message': ['The uploaded file appears to be empty']})

            # Forward fill the Employee Name column
            df['Employee Name'] = df['Employee Name'].replace('', np.nan).ffill()

            # Filter for rows where Pay Type is "R"
            filtered_df = df[df['Pay Type'] == 'R'][['Employee Name', 'Pay Type', 'Regular Hours']]

            # Remove any remaining empty strings in Employee Name if any
            filtered_df = filtered_df[filtered_df['Employee Name'].str.strip() != '']
            filtered_df['Regular Hours'] = filtered_df['Regular Hours'].astype(str).str.replace(' ', '').astype(float)

            # Calculate remaining hours using the current_hours value
            def calc_hours_with_current(hours):
                return sum([current_hours_val, hours, -1875])

            filtered_df['Remaining Hours'] = filtered_df['Regular Hours'].apply(calc_hours_with_current)

            # Format numbers
            filtered_df['Regular Hours'] = filtered_df['Regular Hours'].round(2)
            filtered_df['Remaining Hours'] = filtered_df['Remaining Hours'].round(2)

            return filtered_df

        except Exception as e:
            return pd.DataFrame({'Message': [f"Error processing file: {str(e)}"]})

    @output
    @render.ui
    def download_button():
        df = process_data()
        has_data = df is not None and 'Message' not in df.columns
        return ui.download_button(
            "download",
            "Export to Excel",
            disabled=not has_data
        )

    @output
    @render.download(filename="pto_hours.xlsx")
    def download():
        df = process_data()
        if df is None or 'Message' in df.columns:
            df = pd.DataFrame({'Message': ['No data to export']})

        # Create Excel file in memory
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)  # Go to beginning of file
        return output

    @output
    @render.ui
    def result_table():
        df = process_data()
        if df is None:
            df = pd.DataFrame({'Message': ['Please upload an Excel file']})
            return ui.tags.table({"class": "table"}, [
                ui.tags.tbody([
                    ui.tags.tr([ui.tags.td(row['Message'])])
                    for _, row in df.iterrows()
                ])
            ])

        # Format numbers
        df['Regular Hours'] = df['Regular Hours'].round(2)
        df['Remaining Hours'] = df['Remaining Hours'].round(2)

        # Create table with conditional styling
        return ui.tags.table({"class": "table"}, [
            ui.tags.thead([
                ui.tags.tr([
                    ui.tags.th(col) for col in df.columns
                ])
            ]),
            ui.tags.tbody([
                ui.tags.tr([
                    ui.tags.td(
                        f"{row[col]:.2f}" if isinstance(row[col], (int, float)) else str(row[col]),
                        {"style": "background-color: " + (
                            "lightgreen" if row[col] < 0 else
                            "lightcoral" if row[col] < 40 else
                            "transparent"
                        )} if col == 'Remaining Hours' and isinstance(row[col], (int, float)) else {}
                    )
                    for col in df.columns
                ])
                for _, row in df.iterrows()
            ])
        ])

app = App(app_ui, server)
