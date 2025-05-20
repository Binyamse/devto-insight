# DEV.TO POST ANALYZER

A comprehensive tool for analyzing your dev.to blog posts' performance and getting AI-powered content recommendations.

![Dev.to Post Analyzer Screenshot](https://via.placeholder.com/800x450?text=Dev.to+Post+Analyzer)

## Features

- **Performance Analysis**: Track views, reactions, comments, and engagement metrics
- **Tag Analysis**: Discover which tags perform best with your audience
- **Timing Optimization**: Find the best days and times to publish
- **AI-Powered Insights**: Get content strategy recommendations from AI
- **Content Ideas**: Generate topic ideas based on your historical performance
- **Visualization**: Interactive charts to visualize your data
- **Export Options**: Download your analysis in JSON or CSV format

## Quick Start with Docker

The easiest way to run the application is with Docker:

```bash
# Clone the repository
git clone https://github.com/yourusername/devto-analyzer.git
cd devto-analyzer

# Start with Docker Compose
docker-compose up
```

Then open your browser to http://localhost:5000

## Manual Setup

If you prefer to run the application without Docker:

```bash
# Clone the repository
git clone https://github.com/yourusername/devto-analyzer.git
cd devto-analyzer

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the application
python app/app.py
```

## Configuration

For AI-powered insights, you'll need API keys for one of the following:

- **OpenAI**: Set the `OPENAI_API_KEY` environment variable
- **Groq**: Set the `GROQ_API_KEY` environment variable

You can set these directly in your environment or create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

## Usage Guide

1. **Enter Your DEV.TO Username**: Start by entering your dev.to username on the home page
2. **API Key (Optional)**: Add your dev.to API key for access to private statistics
3. **Select LLM Provider**: Choose which AI provider to use for content recommendations
4. **Analyze**: Click "Analyze My Posts" to start the analysis
5. **View Results**: Explore the different tabs and visualizations
6. **Get Recommendations**: Review AI-generated insights and content ideas

## API Endpoints

The application provides several API endpoints for programmatic access:

- `POST /api/analyze`: Analyze posts for a given username
- `POST /api/generate-insights`: Generate AI insights from analysis data
- `POST /api/generate-topic-ideas`: Generate content topic ideas based on analysis

## Development

Want to improve or extend the analyzer? Here's how to set up your development environment:

```bash
# Clone the repository
git clone https://github.com/yourusername/devto-analyzer.git
cd devto-analyzer

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the application in development mode
FLASK_ENV=development python app/app.py
```

### Project Structure

- `app/`: Application code
  - `analyzer.py`: Core analysis logic
  - `llm_service.py`: LLM service for insights
  - `app.py`: Flask web application
  - `static/`: Static assets (CSS, JS)
  - `templates/`: HTML templates
- `Dockerfile` & `docker-compose.yml`: Docker configuration
- `requirements.txt`: Python dependencies

## Extending the Tool

Here are some ideas for extending the analyzer:

- **Add More LLM Providers**: Integrate with additional AI services
- **Historical Tracking**: Track post performance over time
- **Competitor Analysis**: Compare your stats with other dev.to users
- **Content Calendar**: Schedule posts based on optimal timing
- **SEO Analysis**: Analyze SEO factors in your top-performing posts
- **Email Reports**: Set up scheduled email reports

## Troubleshooting

**API Rate Limits**: The dev.to API has rate limits. If you encounter rate limit errors, wait a few minutes before retrying.

**LLM Integration**: If you're not seeing AI-powered insights, check that you've set the appropriate API keys.

**Docker Issues**: If you encounter problems with Docker, try rebuilding the container:

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgements

- [Dev.to API](https://developers.forem.com/api)
- [Flask](https://flask.palletsprojects.com/)
- [Plotly.js](https://plotly.com/javascript/)
- [OpenAI](https://openai.com/)
- [Groq](https://groq.com/)
