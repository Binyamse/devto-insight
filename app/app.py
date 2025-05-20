"""
Flask web application for Dev.to post analyzer.
"""
import os
import json
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from analyzer import DevToAnalyzer
from llm_service import LLMService


# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-to-analyzer-secret")

# Default LLM provider
DEFAULT_LLM_PROVIDER = "openai"


@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze the user's dev.to posts."""
    username = request.form.get('username')
    api_key = request.form.get('api_key')
    llm_provider = request.form.get('llm_provider', DEFAULT_LLM_PROVIDER)
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    # Store in session for future use
    session['username'] = username
    session['llm_provider'] = llm_provider
    
    try:
        # Create analyzer and generate report
        analyzer = DevToAnalyzer(username=username, api_key=api_key)
        
        # Fetch all articles
        analyzer.fetch_all_articles()
        
        # Generate a comprehensive report
        report = analyzer.generate_analysis_report()
        
        # Store the report in session
        session['report'] = json.dumps(report, default=str)
        
        # Get data for LLM analysis
        llm_data = analyzer.get_data_for_llm_analysis()
        
        # Get insights from LLM if API keys are available
        insights = None
        topic_ideas = None
        
        llm_enabled = False
        if llm_provider == "openai" and os.getenv("OPENAI_API_KEY"):
            llm_enabled = True
        elif llm_provider == "groq" and os.getenv("GROQ_API_KEY"):
            llm_enabled = True
        elif llm_provider == "none":
            llm_enabled = False
        else:
            # Use mock data if provider specified but API keys not configured
            llm_enabled = True
            llm_provider = "mock"
        
        if llm_enabled:
            llm_service = LLMService(llm_provider=llm_provider)
            insights = llm_service.generate_insights(llm_data)
            topic_ideas = llm_service.generate_topic_ideas(llm_data, num_ideas=5)
        
        # Render the results page
        return render_template(
            'results.html',
            username=username,
            report=report,
            insights=insights,
            topic_ideas=topic_ideas,
            llm_enabled=llm_enabled,
            llm_provider=llm_provider
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for analysis."""
    data = request.json
    username = data.get('username')
    api_key = data.get('api_key')
    llm_provider = data.get('llm_provider', DEFAULT_LLM_PROVIDER)
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    try:
        # Create analyzer and generate report
        analyzer = DevToAnalyzer(username=username, api_key=api_key)
        report = analyzer.generate_analysis_report()
        
        # Get data for LLM analysis
        llm_data = analyzer.get_data_for_llm_analysis()
        
        # Get insights from LLM if API keys are available
        insights = None
        topic_ideas = None
        
        llm_enabled = False
        if llm_provider == "openai" and os.getenv("OPENAI_API_KEY"):
            llm_enabled = True
        elif llm_provider == "groq" and os.getenv("GROQ_API_KEY"):
            llm_enabled = True
        elif llm_provider == "none":
            llm_enabled = False
        else:
            # Use mock data if provider specified but API keys not configured
            llm_enabled = True
            llm_provider = "mock"
        
        if llm_enabled:
            llm_service = LLMService(llm_provider=llm_provider)
            insights = llm_service.generate_insights(llm_data)
            topic_ideas = llm_service.generate_topic_ideas(llm_data, num_ideas=5)
        
        response = {
            'username': username,
            'report': report,
            'insights': insights,
            'topic_ideas': topic_ideas,
            'llm_enabled': llm_enabled,
            'llm_provider': llm_provider
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-insights', methods=['POST'])
def api_generate_insights():
    """API endpoint to generate insights using the specified LLM."""
    data = request.json
    report = data.get('report')
    llm_provider = data.get('llm_provider', DEFAULT_LLM_PROVIDER)
    
    if not report:
        return jsonify({'error': 'Report data is required'}), 400
    
    try:
        llm_service = LLMService(llm_provider=llm_provider)
        insights = llm_service.generate_insights(report)
        
        return jsonify({'insights': insights}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-topic-ideas', methods=['POST'])
def api_generate_topic_ideas():
    """API endpoint to generate topic ideas using the specified LLM."""
    data = request.json
    report = data.get('report')
    llm_provider = data.get('llm_provider', DEFAULT_LLM_PROVIDER)
    num_ideas = data.get('num_ideas', 5)
    
    if not report:
        return jsonify({'error': 'Report data is required'}), 400
    
    try:
        llm_service = LLMService(llm_provider=llm_provider)
        topic_ideas = llm_service.generate_topic_ideas(report, num_ideas=num_ideas)
        
        return jsonify({'topic_ideas': topic_ideas}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)