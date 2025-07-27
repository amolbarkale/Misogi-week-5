sql_agent_demo/
├── .env
├── requirements.txt
├── main.py # Streamlit Web App
├── config.py # Configuration and environment handling
├── database/
│ └── ecommerce.sqlite # Sample DB with 50+ tables (mock or real)
├── agent/
│ ├── sql_toolkit.py # LangChain SQL Agent setup
│ ├── planner.py # Multi-step query planning logic
│ └── table_selector.py # Semantic table selection module
└── utils/
├── security.py # Rate limiting and query validation
└── helpers.py # Common utilities like chunking, sampling

id, first_name, last_name, age, signup_date