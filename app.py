from shiny import App, render, ui, reactive
import pandas as pd
import numpy as np

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
"""

app_ui = ui.page_fluid(
    ui.tags.style(custom_css),
    ui.h2("PTO Hours Calculator"),
    ui.page_sidebar(
        ui.sidebar(
            ui.input_numeric("current_hours", "Current Hours", value=580),
            ui.input_file("file", "Upload Excel File", accept=[".xlsx"])
        ),
        ui.output_table("result_table", style="table-cell { background-color: lightgreen !important; }")
    )
)

def server(input, output, session):
    @reactive.Calc
    def process_data():
        try:
            if not input.file():
                return None

            file_path = input.file()[0]["datapath"]
            current_hours_val = input.current_hours()

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
                        {"style": "background-color: lightgreen"} if col == 'Remaining Hours' and isinstance(row[col], (int, float)) and row[col] < 0 else {}
                    )
                    for col in df.columns
                ])
                for _, row in df.iterrows()
            ])
        ])

app = App(app_ui, server)
