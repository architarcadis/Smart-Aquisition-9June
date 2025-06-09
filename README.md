# SMART Acquisition for Built Assets

A sophisticated Streamlit application for built assets intelligence, delivering comprehensive market scanning and procurement analytics for the water infrastructure sector with advanced interactive visualization capabilities.

## Features

- **SMART Sourcing**: Contract delivery management for AMP 8 programme
- **SMART Performance**: Operational excellence tracking and customer impact analysis
- **SMART Markets**: Strategic market intelligence with AI-powered live scanning
- **AMP 8 Regulatory**: Compliance tracking and regulatory monitoring
- **Interactive Dashboards**: Real-time data visualization with Plotly
- **Market Intelligence**: Google Search API and OpenAI integration for automated scanning

## Deployment on Streamlit Cloud

### 1. Fork/Clone Repository
```bash
git clone https://github.com/your-username/smart-acquisition-app.git
```

### 2. Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select your repository
4. Set the main file path to: `app.py`
5. Click "Deploy"

### 3. Configure API Secrets
After deployment, configure your API keys in Streamlit Cloud:

1. Go to your app dashboard on Streamlit Cloud
2. Click the settings gear icon (⚙️) for your app
3. Navigate to the "Secrets" section
4. Copy and paste the following configuration:

```toml
OPENAI_API_KEY = "sk-your-openai-api-key-here"
GOOGLE_API_KEY = "your-google-api-key-here"
GOOGLE_CX_ID = "your-google-cx-id-here"
```

### 4. Get Required API Keys

#### OpenAI API Key
1. Visit [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Go to API Keys section
4. Create a new secret key
5. Copy the key (starts with `sk-`)

#### Google Custom Search API
1. Visit [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable the "Custom Search API"
4. Create credentials (API Key)
5. Copy the API key

#### Google Custom Search Engine ID
1. Visit [Google Custom Search](https://cse.google.com/cse/)
2. Create a new search engine
3. Set search scope (can be entire web)
4. Copy the Search Engine ID (CX)

### 5. Save and Redeploy
After adding secrets, save them and redeploy your app. The application will automatically detect and use the configured API keys.

## Local Development

### Prerequisites
- Python 3.8+
- Required packages (install via pip)

### Installation
```bash
pip install streamlit pandas plotly openai google-api-python-client requests beautifulsoup4 trafilatura networkx
```

### Environment Variables (Local Development)
Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CX_ID=your-google-cx-id
```

### Run Locally
```bash
streamlit run app.py
```

## Usage

1. **Configure API Keys**: Set up your API keys in Streamlit Cloud secrets
2. **Load Sample Data**: Use the sidebar to download and upload data templates
3. **Market Intelligence**: Configure market scanning parameters and generate insights
4. **View Results**: Switch between Current Intelligence, Timeline View, and Historical Comparison modes
5. **Export Data**: Download insights and reports for further analysis

## Project Structure

```
├── app.py                          # Main application entry point
├── modules/
│   ├── landing.py                  # Landing page and overview
│   ├── smart_markets.py            # Market intelligence module
│   ├── smart_sourcing.py           # Sourcing and contract management
│   ├── smart_performance.py        # Performance tracking
│   └── amp8_regulatory.py          # Regulatory compliance
├── utils/
│   ├── market_scanner.py           # Market scanning utilities
│   ├── web_scraper.py              # Web scraping functions
│   ├── data_generator.py           # Sample data generation
│   └── thames_water_research.py    # Thames Water specific data
├── .streamlit/
│   ├── config.toml                 # Streamlit configuration
│   └── secrets.toml.example        # Example secrets template
└── README.md                       # This file
```

## Technologies Used

- **Streamlit**: Web application framework
- **Plotly**: Interactive data visualization
- **OpenAI**: GPT-powered content analysis
- **Google Custom Search**: Web search and data gathering
- **Pandas**: Data manipulation and analysis
- **BeautifulSoup**: Web scraping
- **Trafilatura**: Content extraction

## Security

- API keys are securely stored in Streamlit Cloud secrets
- No sensitive data is logged or stored in the repository
- All external API calls are rate-limited and error-handled

## Support

For issues or questions:
1. Check the API configuration in the sidebar
2. Verify your API keys are correctly set in Streamlit Cloud secrets
3. Review the console logs for any error messages
4. Ensure your API keys have sufficient quota/credits

## License

This project is designed for internal use within built assets procurement teams.