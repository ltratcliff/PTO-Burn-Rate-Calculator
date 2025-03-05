# PTO Burn Rate Calculator

A Shiny for Python application that helps calculate and visualize PTO (Paid Time Off) burn rates for employees. The application allows users to upload Excel files containing employee hours data, calculate remaining hours, and export results with conditional formatting.

## Features

- Upload Excel files with employee hours data
- Calculate remaining PTO hours based on current balance
- Export results to Excel
- Visual indicators for different PTO states:
  - Green: Negative hours (over budget)
  - Red: Less than 40 hours remaining
  - Default: Normal state

## Prerequisites

- Posit Connect Server
- Python 3.8 or higher
- Required Python packages (specified in requirements.txt)

## Local Development Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application locally:
   ```bash
   shiny run app.py
   ```

## Deploying to Posit Connect

1. **Prepare Your Environment**
   - Ensure you have the Posit Connect server URL and your API key
   - Install the `rsconnect-python` package:
     ```bash
     pip install rsconnect-python
     ```

2. **Configure rsconnect**
   ```bash
   rsconnect add --server <your-connect-server-url> --api-key <your-api-key> --name <server-nickname>
   ```

3. **Deploy the Application**
   ```bash
   rsconnect deploy shiny . --name <server-nickname> --title "PTO Burn Rate Calculator"
   ```

## Application Structure

- `app.py`: Main application file containing UI and server logic
- `requirements.txt`: Python package dependencies

## Input File Format

The application expects an Excel file with the following columns:
- Employee Name
- Pay Type
- Regular Hours

## Usage

1. Access the deployed application through your Posit Connect server
2. Enter the current PTO hours in the "Current Hours" field
3. Upload an Excel file with employee data
4. View the results table with color-coded indicators
5. Export the results using the "Export to Excel" button

## Troubleshooting

- Ensure your Excel file matches the expected format
- Check that all required columns are present
- Verify that the "Pay Type" column contains 'R' for regular hours
- Make sure the Excel file is not empty or corrupted

## Support

For issues related to:
- Application functionality: Contact the application administrator
- Posit Connect deployment: Contact your Posit Connect server administrator

## License

MIT