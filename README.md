# NEM Studios Invoice Generator

Online invoice generation tool deployed on Streamlit Cloud.

## Features

- PDF invoice generation with NEM Studios branding
- Password protected access
- Works on any device with a browser

## Setup Password

Set the `INVOICE_PWD` environment variable in Streamlit Cloud:
1. Go to your app → Settings → Secrets
2. Add: `INVOICE_PWD = your_password`

## Tech Stack

- **Streamlit** — Web framework
- **ReportLab** — PDF generation
- **Python 3**