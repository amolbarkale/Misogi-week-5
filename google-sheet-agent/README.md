streamlit run app.py

# 🤖 LangChain Google Sheets Agent

A Streamlit web app that lets you analyze and automate Google Sheets using natural language, powered by [LangChain](https://github.com/langchain-ai/langchain), Google Gemini, and the Google Sheets API.

## Features

- **Natural Language Sheet Operations:** Filter, aggregate, pivot, sort, and modify Google Sheets using plain English.
- **Conversation Memory:** Remembers context and previous queries for a smoother experience.
- **Structured Tool Calling:** Uses validated, robust tools for all sheet operations.
- **Automatic Sheet Context:** Always operates on the selected worksheet.
- **Error Handling:** Friendly error messages and recovery suggestions.

## Example Queries

- "Filter employees with salary > 50000"
- "Group by department and sum salaries"
- "Create pivot table with regions as rows and products as columns"
- "Sort by date descending"
- "Add a bonus column that's 10% of salary"
- "Add a new employee: John Doe, age 30, salary 75000"

## Setup

### 1. Clone the Repository

```sh
git clone <your-repo-url>
cd google-sheet-agent
```

### 2. Install Dependencies

Make sure you have Python 3.10+ installed.

```sh
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```sh
cp .env.example .env
```

Edit `.env` and set:

- `GEMINI_API_KEY` — Your Google Gemini API key
- `SHEET_ID` — Your Google Sheets spreadsheet ID

### 4. Add Google Service Account

- Place your Google Cloud service account JSON file as `service_account.json` in the project root.
- Share your target Google Sheet with the email found in the `client_email` field of `service_account.json` (e.g., `google-sheets-agent-676@slack-clone-461720.iam.gserviceaccount.com`) with **Editor** access.

### 5. Run the App

```sh
streamlit run app.py
```

The app will open in your browser.

## Project Structure

```
.
├── app.py                      # Streamlit app entry point
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment variables
├── service_account.json        # Google Cloud service account credentials
├── agents/
│   ├── langchain_agent.py      # LangChain agent logic
│   └── langchain_tools.py      # Google Sheets tool implementations
```

## How It Works

- The app uses [Streamlit](https://streamlit.io/) for the UI.
- All Google Sheets operations are performed via tools defined in [`agents/langchain_tools.py`](agents/langchain_tools.py).
- The agent in [`agents/langchain_agent.py`](agents/langchain_agent.py) uses LangChain's tool-calling and memory features to process your queries.
- The service account authenticates with the Google Sheets API.

## Troubleshooting

- **Authentication errors:** Make sure your service account email has access to the Google Sheet.
- **API errors:** Check your `.env` values and that your Google Cloud project has Sheets API enabled.
- **Gemini errors:** Ensure your Gemini API key is correct and has quota.

## Credits

- [LangChain](https://github.com/langchain-ai/langchain)
- [Streamlit](https://streamlit.io/)
- [Google Gemini](https://ai.google.dev/)
- [Google Sheets API](https://developers.google.com/sheets/api)

---