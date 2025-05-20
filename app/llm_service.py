"""
LLM service for analyzing dev.to post data and generating insights.
"""
import os
import json
from typing import Dict, Any, Optional, List


class LLMService:
    """
    Service for interacting with LLMs (OpenAI or Groq) to generate insights.
    """
    
    def __init__(self, llm_provider: str = "openai"):
        """
        Initialize the LLM service.
        
        Args:
            llm_provider: The LLM provider to use ('openai' or 'groq')
        """
        self.llm_provider = llm_provider.lower()
        
        # For now we'll use a mock implementation to avoid API dependencies
        self.use_mock = True
        
    def generate_insights(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate insights from the analysis data.
        
        Args:
            analysis_data: Dictionary containing post analysis data
            
        Returns:
            Dictionary with generated insights
        """
        if self.use_mock:
            return self._get_mock_insights(analysis_data)
        
        # In a real implementation, would call the LLM API here
        return {}
    
    def generate_topic_ideas(self, analysis_data: Dict[str, Any], num_ideas: int = 5) -> List[Dict[str, Any]]:
        """
        Generate topic ideas based on analysis data.
        
        Args:
            analysis_data: Dictionary containing post analysis data
            num_ideas: Number of topic ideas to generate
            
        Returns:
            List of topic idea dictionaries
        """
        if self.use_mock:
            return self._get_mock_topic_ideas(analysis_data, num_ideas)
        
        # In a real implementation, would call the LLM API here
        return []
    
    def _create_insight_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """
        Create a prompt for generating insights.
        
        Args:
            analysis_data: Dictionary containing post analysis data
            
        Returns:
            Formatted prompt string
        """
        prompt = """
You are an expert content strategist analyzing performance data from dev.to blog posts.
I'll provide you with analysis data for a user's posts, and I need you to generate insights and recommendations.

Please analyze this data and provide:
1. A summary of the user's content performance
2. Key patterns you notice about what performs well
3. Specific actionable recommendations to improve engagement
4. Optimal posting strategy (timing, topics, style)

Include these specific sections in your analysis:
- If the data includes series analysis, provide insights about how series perform vs. standalone posts
- If the data includes tag recommendations, evaluate those and add your own suggestions
- If the data includes optimal publishing times, interpret this data in your recommendations

Return your analysis in a structured JSON format like this:
{
    "performance_summary": "A paragraph summarizing overall performance...",
    "key_patterns": [
        "Pattern 1: Description of pattern...",
        "Pattern 2: Description of pattern..."
    ],
    "content_recommendations": [
        "Recommendation 1: Specific advice...",
        "Recommendation 2: Specific advice..."
    ],
    "optimal_posting_strategy": {
        "best_days": ["Day 1", "Day 2"],
        "best_hours": ["Hour 1", "Hour 2"],
        "recommended_tags": ["tag1", "tag2"],
        "content_type": "Description of content type that performs best...",
        "style_tips": "Recommendations on style, length, etc..."
    },
    "series_strategy": "Advice on creating and managing series of posts...",
    "engagement_boosters": "Specific tactics to increase reader engagement..."
}

Analysis data:
"""
        prompt += json.dumps(analysis_data, indent=2)
        return prompt
    
    def _create_topic_ideas_prompt(self, analysis_data: Dict[str, Any], num_ideas: int) -> str:
        """
        Create a prompt for generating topic ideas.
        
        Args:
            analysis_data: Dictionary containing post analysis data
            num_ideas: Number of topic ideas to generate
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""
You are an expert technical content creator who helps developers come up with engaging blog post ideas.
I'll provide you with analysis data for a user's dev.to posts, and I need you to generate {num_ideas} specific topic ideas 
that are likely to perform well based on their historical performance.

Focus on the following insights from their data:
- Their top performing tags: {", ".join([tag.get('tag', '') for tag in analysis_data.get('top_tags', [])][:5])}
- Their highest engagement content types
- Any tag recommendations provided in the data
- Series performance (if they publish content in series)
- Optimal posting times and days

For each topic idea, provide:
1. A catchy title
2. A brief description (2-3 sentences)
3. Suggested tags (use their highest performing tags and recommended tags)
4. Estimated reading time
5. Why you think this will perform well (based on their data)
6. Whether this would work well as a standalone post or part of a series

Return your ideas in a structured JSON array like this:
[
    {{
        "title": "Catchy Topic Title",
        "description": "Brief description of the post idea...",
        "suggested_tags": ["tag1", "tag2", "tag3"],
        "estimated_reading_time": 7,
        "performance_rationale": "Why this topic should perform well based on their data...",
        "series_potential": "Standalone post" or "Would work well as a 3-part series on [topic]"
    }},
    ...
]

Make sure the ideas are specific, actionable, and tailored to the user's niche and audience.
Prioritize ideas that align with their top-performing content and tag recommendations.

Analysis data:
"""
        prompt += json.dumps(analysis_data, indent=2)
        return prompt
    
    def _generate_title(self, pattern: str, tags: List[str], analysis_data: Dict[str, Any]) -> str:
        """
        Generate a dynamic title based on pattern and user's data.
        
        Args:
            pattern: The type of content (tutorial, guide, best-practices, etc)
            tags: List of tags to incorporate
            analysis_data: Dictionary containing post analysis data
            
        Returns:
            A dynamically generated title
        """
        # Create a prompt for title generation based on successful posts
        high_engagement_posts = analysis_data.get('highest_engagement_posts', [])
        
        # Extract titles and engagement metrics from successful posts
        successful_titles = []
        for post in high_engagement_posts:
            post_tags = post.get('tags', '').split(',') if isinstance(post.get('tags'), str) else post.get('tags', [])
            post_tags = [tag.strip().lower() for tag in post_tags if tag.strip()]
            
            # Check if the post uses any of our target tags
            if any(tag.lower() in post_tags for tag in tags):
                successful_titles.append({
                    'title': post.get('title', ''),
                    'engagement': post.get('engagement_ratio', 0),
                    'tags': post_tags
                })
        
        # Sort by engagement to prioritize most successful titles
        successful_titles.sort(key=lambda x: x['engagement'], reverse=True)
        
        # Create prompt for LLM with context about successful titles and desired focus
        prompt = f"""
Based on the following successful blog post titles and their engagement metrics,
generate a title for a new {pattern} post about {', '.join(tags)}.

Successful titles for reference:
{json.dumps(successful_titles[:5], indent=2)}

Content type: {pattern}
Primary tags: {', '.join(tags)}

The title should:
1. Follow similar patterns to the high-engagement titles
2. Be specific and actionable
3. Include the key technologies ({', '.join(tags)})
4. Be appropriate for a {pattern} post
5. Be engaging and professional
"""
        
        # For mock implementation, generate a contextual title
        import random
        
        # Extract common patterns from successful titles
        patterns = {
            'tutorial': [
                f"Building {tags[0]} Applications: A Step-by-Step Guide",
                f"How to Master {tags[0]} Development",
                f"Practical {tags[0]} Tips for Real-World Projects"
            ],
            'best-practices': [
                f"{tags[0]} Best Practices for Professional Developers",
                f"Writing Better {tags[0]} Code: Tips and Tricks",
                f"Advanced {tags[0]} Patterns You Should Know"
            ],
            'deep-dive': [
                f"Deep Dive: Advanced {tags[0]} Concepts",
                f"Understanding {tags[0]} Internals",
                f"Advanced {tags[0]} Architecture Patterns"
            ]
        }
        
        # In a real implementation, this would call the LLM API
        # For now, use patterns based on content type and successful titles
        title_patterns = patterns.get(pattern, patterns['tutorial'])
        chosen_title = random.choice(title_patterns)
        
        # If we have multiple tags, try to incorporate them
        if len(tags) > 1:
            if "with" not in chosen_title:
                chosen_title = chosen_title.replace(f"{tags[0]}", f"{tags[0]} with {tags[1]}")
        
        return chosen_title

    def _normalize_tag(self, tag: str) -> str:
        """
        Normalize tag case to match dev.to conventions.
        
        Args:
            tag: The tag to normalize
            
        Returns:
            Normalized tag string
        """
        # Common tags that should be in specific case
        special_cases = {
            'javascript': 'JavaScript',
            'typescript': 'TypeScript',
            'nodejs': 'Node.js',
            'nextjs': 'Next.js',
            'reactjs': 'React.js',
            'vuejs': 'Vue.js',
            'aws': 'AWS',
            'dotnet': '.NET',
            'csharp': 'C#',
            'cpp': 'C++',
            'devops': 'DevOps',
            'ai': 'AI',
            'ml': 'ML',
            'api': 'API',
            'graphql': 'GraphQL',
            'postgresql': 'PostgreSQL',
            'mysql': 'MySQL',
            'nosql': 'NoSQL',
            'mongodb': 'MongoDB',
            'php': 'PHP',
            'css': 'CSS',
            'html': 'HTML',
            'sass': 'Sass',
            'scss': 'SCSS',
            'ios': 'iOS',
            'macos': 'macOS',
            'linux': 'Linux',
            'windows': 'Windows',
            'ci': 'CI',
            'cd': 'CD',
            'cicd': 'CI/CD',
            'iot': 'IoT',
            'ui': 'UI',
            'ux': 'UX',
            'jwt': 'JWT',
            'oauth': 'OAuth',
            'regex': 'RegEx',
            'webdev': 'WebDev',
            'seo': 'SEO'
        }
        
        # Convert to lowercase for comparison
        tag_lower = tag.lower()
        
        # Return special case if it exists
        if tag_lower in special_cases:
            return special_cases[tag_lower]
        
        # For compound tags with hyphens, capitalize each part
        if '-' in tag:
            return '-'.join(word.capitalize() for word in tag.split('-'))
        
        # Default to capitalizing the first letter
        return tag.capitalize()

    def _get_mock_insights(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate mock insights for testing.
        
        Args:
            analysis_data: Dictionary containing post analysis data
            
        Returns:
            Dictionary with mock insights
        """
        username = analysis_data.get('username', '')
        top_tags = [tag['tag'] for tag in analysis_data.get('top_tags', [])[:3]] if 'top_tags' in analysis_data and len(analysis_data['top_tags']) > 0 else ["javascript", "webdev", "programming"]
        
        # Get series data if available
        series_strategy = "Consider creating more series content to engage your audience more deeply. Series posts tend to build reader loyalty and encourage return visits."
        if 'series_performance' in analysis_data and analysis_data['series_performance']:
            if len(analysis_data['series_performance']) > 0:
                series_strategy = "Your series content is performing well. Continue creating series posts for complex topics, ideally keeping them to 3-5 parts for optimal completion rates."
        
        # Check for optimal time data
        best_days = []
        best_hours = []
        if 'best_days' in analysis_data and analysis_data['best_days']:
            best_days = [day.get('day', '') for day in analysis_data['best_days'][:2]]
        else:
            best_days = ["Tuesday", "Thursday"]
            
        if 'best_hours' in analysis_data and analysis_data['best_hours']:
            best_hours = [f"{hour.get('hour', '')}:00" for hour in analysis_data['best_hours'][:2]]
        else:
            best_hours = ["8:00", "12:00"]
            
        # Check for tag recommendations
        recommended_tags = top_tags
        if 'tag_recommendations' in analysis_data and analysis_data['tag_recommendations']:
            for rec in analysis_data['tag_recommendations']:
                if rec.get('type') == 'top_performing' and 'tags' in rec:
                    recommended_tags = rec['tags']
                    break
        
        return {
            "performance_summary": f"Your dev.to blog posts show good engagement with healthy reaction and comment rates. Your content in the {', '.join(top_tags)} tags performs particularly well. Your posts with practical, solution-oriented content receive higher engagement than more theoretical pieces.",
            
            "key_patterns": [
                f"Tutorial-style posts with specific code examples typically get 40% more engagement",
                f"Posts with 5-10 minute reading times perform better than both shorter and longer content",
                f"Articles published on {' and '.join(best_days)} receive more reactions and comments",
                f"Content tagged with '{', '.join(top_tags)}' consistently attracts more readers",
                f"Posts that include diagrams or visual elements get 30% more reactions"
            ],
            
            "content_recommendations": [
                "Create more step-by-step tutorials with practical code examples",
                "Break complex topics into series of 5-8 minute reading time posts",
                "Include diagrams or visualizations to improve engagement on conceptual topics",
                "End posts with a clear call-to-action like a question to increase comment rates",
                "Add a personal perspective to technical content to differentiate your writing",
                f"Use the tag combination '{top_tags[0]} + {top_tags[1] if len(top_tags) > 1 else 'react'}' for highest visibility"
            ],
            
            "optimal_posting_strategy": {
                "best_days": best_days,
                "best_hours": best_hours,
                "recommended_tags": recommended_tags,
                "content_type": "In-depth tutorials with practical code examples and clear explanations of technical concepts",
                "style_tips": "Aim for 5-8 minute reading time, use headings to break up content, include code samples, and end with thought-provoking questions to encourage comments"
            },
            
            "series_strategy": series_strategy,
            
            "engagement_boosters": "Respond quickly to comments on your posts to foster community. Share your posts on Twitter and LinkedIn with thoughtful commentary. Consider cross-posting popular content to your personal blog with canonical URLs pointing to dev.to. Ask engaging questions at the end of your posts to encourage discussion."
        }
    
    def _get_mock_topic_ideas(self, analysis_data: Dict[str, Any], num_ideas: int) -> List[Dict[str, Any]]:
        """
        Generate mock topic ideas for testing.
        
        Args:
            analysis_data: Dictionary containing post analysis data
            num_ideas: Number of topic ideas to generate
            
        Returns:
            List of mock topic idea dictionaries
        """
        # Get user's top performing tags with performance metrics and normalize them
        top_tags = analysis_data.get('top_tags', [])
        top_performing_tags = [self._normalize_tag(tag['tag']) for tag in top_tags][:5]
        
        # Get best tag combinations from performance data
        high_engagement_posts = analysis_data.get('highest_engagement_posts', [])
        successful_tag_combos = {}
        
        for post in high_engagement_posts:
            tags = post.get('tags', '').split(',') if isinstance(post.get('tags'), str) else post.get('tags', [])
            tags = [self._normalize_tag(tag.strip()) for tag in tags if tag.strip()]
            if len(tags) >= 2:
                combo = tuple(sorted(tags))
                if combo not in successful_tag_combos:
                    successful_tag_combos[combo] = {
                        'engagement': post.get('engagement_ratio', 0),
                        'count': 1
                    }
                else:
                    successful_tag_combos[combo]['count'] += 1
                    successful_tag_combos[combo]['engagement'] = max(
                        successful_tag_combos[combo]['engagement'],
                        post.get('engagement_ratio', 0)
                    )
        
        # Sort tag combinations by engagement and count
        best_combos = sorted(
            successful_tag_combos.items(),
            key=lambda x: (x[1]['engagement'], x[1]['count']),
            reverse=True
        )
        
        # Check if user publishes series
        has_series = 'series_performance' in analysis_data and len(analysis_data.get('series_performance', [])) > 0
        
        # Generate ideas based on successful patterns
        ideas = []
        
        # Idea 1: Tutorial combining top two tags
        if len(top_performing_tags) >= 2:
            ideas.append({
                "title": self._generate_title("tutorial", [top_performing_tags[0], top_performing_tags[1]], analysis_data),
                "description": f"A comprehensive guide combining {top_performing_tags[0]} and {top_performing_tags[1]} to build production-ready applications. Learn best practices, optimization techniques, and real-world implementation patterns.",
                "suggested_tags": [top_performing_tags[0], top_performing_tags[1], self._normalize_tag("tutorial"), self._normalize_tag("programming")],
                "estimated_reading_time": 8,
                "performance_rationale": f"Combines your two best-performing tags ({top_performing_tags[0]}, {top_performing_tags[1]}) which have an average of {next((tag['avg_reactions'] for tag in top_tags if tag['tag'] == top_performing_tags[0].lower()), 0):.1f} reactions per post.",
                "series_potential": "Would work well as a 3-part series" if has_series else "Standalone post"
            })
        
        # Idea 2: Best practices based on top tag
        if top_performing_tags:
            ideas.append({
                "title": self._generate_title("best-practices", [top_performing_tags[0]], analysis_data),
                "description": f"Learn from real-world experience about common pitfalls in {top_performing_tags[0]} development. Includes code examples, performance tips, and maintainability guidelines.",
                "suggested_tags": [top_performing_tags[0], self._normalize_tag("bestpractices"), self._normalize_tag("programming"), self._normalize_tag("debugging")],
                "estimated_reading_time": 7,
                "performance_rationale": f"Your content in {top_performing_tags[0]} consistently performs well with {next((tag['avg_reactions'] for tag in top_tags if tag['tag'] == top_performing_tags[0].lower()), 0):.1f} average reactions.",
                "series_potential": "Standalone post"
            })
        
        # Idea 3: Based on best performing tag combination
        if best_combos:
            best_combo = list(best_combos[0][0])
            ideas.append({
                "title": self._generate_title("tutorial", best_combo, analysis_data),
                "description": f"Learn how to integrate {best_combo[0]} with {best_combo[1]} to create robust applications. Based on real-world best practices and performance optimization techniques.",
                "suggested_tags": best_combo + [self._normalize_tag("tutorial"), self._normalize_tag("webdev")],
                "estimated_reading_time": 9,
                "performance_rationale": f"This tag combination has historically performed very well, with {best_combos[0][1]['engagement']:.3f} engagement ratio across {best_combos[0][1]['count']} posts.",
                "series_potential": "Would work well as a 4-part series" if has_series else "Standalone post"
            })
        
        # Idea 4: Testing and automation for top performing tag
        if top_performing_tags:
            ideas.append({
                "title": self._generate_title("best-practices", [top_performing_tags[0], "testing"], analysis_data),
                "description": f"A comprehensive guide to testing {top_performing_tags[0]} applications. Covers unit testing, integration testing, and setting up CI/CD pipelines.",
                "suggested_tags": [top_performing_tags[0], self._normalize_tag("testing"), self._normalize_tag("automation"), self._normalize_tag("devops")],
                "estimated_reading_time": 8,
                "performance_rationale": f"Content about {top_performing_tags[0]} combined with testing/automation typically drives high engagement.",
                "series_potential": "Would work well as a 3-part testing series" if has_series else "Standalone post"
            })
        
        # Idea 5: Performance optimization with top tags
        if len(top_performing_tags) >= 2:
            ideas.append({
                "title": self._generate_title("deep-dive", [top_performing_tags[0], top_performing_tags[1]], analysis_data),
                "description": f"Deep dive into performance optimization for applications using {top_performing_tags[0]} and {top_performing_tags[1]}. Includes benchmarking, profiling, and practical optimization techniques.",
                "suggested_tags": [top_performing_tags[0], top_performing_tags[1], self._normalize_tag("performance"), self._normalize_tag("optimization")],
                "estimated_reading_time": 7,
                "performance_rationale": f"Performance-focused content using your top tags ({top_performing_tags[0]}, {top_performing_tags[1]}) consistently drives high engagement.",
                "series_potential": "Would work well as a performance optimization series" if has_series else "Standalone post"
            })
        
        # Idea 6: Security topics with top tag
        if top_performing_tags:
            ideas.append({
                "title": self._generate_title("best-practices", [top_performing_tags[0], "security"], analysis_data),
                "description": f"Essential security considerations and implementation techniques for {top_performing_tags[0]} applications. Covers common vulnerabilities, security testing, and secure coding practices.",
                "suggested_tags": [top_performing_tags[0], self._normalize_tag("security"), self._normalize_tag("webdev"), self._normalize_tag("bestpractices")],
                "estimated_reading_time": 8,
                "performance_rationale": "Security topics consistently perform well across technical audiences, especially when combined with specific technology implementations.",
                "series_potential": "Would work well as a security series" if has_series else "Standalone post"
            })
        
        # Idea 7: Architecture patterns with best performing tags
        if len(top_performing_tags) >= 2:
            ideas.append({
                "title": self._generate_title("deep-dive", [top_performing_tags[0], top_performing_tags[1]], analysis_data),
                "description": f"Explore modern software architecture patterns using {top_performing_tags[0]} and {top_performing_tags[1]}. Learn about microservices, serverless, and scalable architectures.",
                "suggested_tags": [top_performing_tags[0], top_performing_tags[1], self._normalize_tag("architecture"), self._normalize_tag("design-patterns")],
                "estimated_reading_time": 9,
                "performance_rationale": "Architecture-focused content tends to drive high engagement, especially when combined with practical implementation using top-performing technologies.",
                "series_potential": "Would work well as a 5-part architecture series" if has_series else "Standalone post"
            })
        
        return ideas[:num_ideas]