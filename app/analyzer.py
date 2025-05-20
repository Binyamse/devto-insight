"""
Dev.to post analyzer module.
"""
import requests
import json
from datetime import datetime
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple


class DevToAnalyzer:
    """
    Analyzes Dev.to blog posts to determine performance metrics and patterns.
    """
    
    def __init__(self, username: str, api_key: Optional[str] = None):
        """
        Initialize the analyzer with user credentials.
        
        Args:
            username: Dev.to username
            api_key: Dev.to API key (optional for public endpoints)
        """
        self.username = username
        self.api_key = api_key
        self.base_url = "https://dev.to/api"
        self.headers = {"api-key": api_key} if api_key else {}
        self.articles = []
        self.detailed_articles = []
        
    def fetch_all_articles(self, max_pages: int = 5, articles_per_page: int = 30) -> List[Dict[str, Any]]:
        """
        Fetch all articles from the user's profile.
        
        Args:
            max_pages: Maximum number of pages to fetch
            articles_per_page: Number of articles per page
            
        Returns:
            List of article dictionaries
        """
        all_articles = []
        page = 1
        has_more_articles = True
        
        while has_more_articles and page <= max_pages:
            try:
                url = f"{self.base_url}/articles?username={self.username}&page={page}&per_page={articles_per_page}"
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                
                articles = response.json()
                
                if not articles:
                    has_more_articles = False
                else:
                    all_articles.extend(articles)
                    page += 1
            except requests.RequestException as e:
                print(f"Error fetching articles: {e}")
                has_more_articles = False
        
        self.articles = all_articles
        return all_articles
    
    def fetch_article_details(self, article_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed information for a specific article.
        
        Args:
            article_id: ID of the article to fetch
            
        Returns:
            Article details dictionary or None if there was an error
        """
        try:
            url = f"{self.base_url}/articles/{article_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching article {article_id}: {e}")
            return None
    
    def get_detailed_articles(self) -> List[Dict[str, Any]]:
        """
        Fetch detailed information for all articles.
        
        Returns:
            List of detailed article dictionaries
        """
        if not self.articles:
            self.fetch_all_articles()
            
        detailed_articles = []
        
        for article in self.articles:
            details = self.fetch_article_details(article['id'])
            if details:
                # Merge the basic article data with the detailed data
                merged_article = {**article, **details}
                detailed_articles.append(merged_article)
        
        self.detailed_articles = detailed_articles
        return detailed_articles
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """
        Calculate various performance metrics for the articles.
        
        Returns:
            Dictionary containing various metrics and rankings
        """
        if not self.detailed_articles:
            self.get_detailed_articles()
            
        articles_df = pd.DataFrame(self.detailed_articles)
        
        # Handle missing values
        articles_df['page_views_count'] = articles_df.get('page_views_count', 0).fillna(0)
        articles_df['public_reactions_count'] = articles_df.get('public_reactions_count', 0).fillna(0)
        articles_df['comments_count'] = articles_df.get('comments_count', 0).fillna(0)
        articles_df['reading_time_minutes'] = articles_df.get('reading_time_minutes', 0).fillna(0)
        
        # Calculate engagement and efficiency metrics
        articles_df['engagement_ratio'] = (articles_df['public_reactions_count'] + articles_df['comments_count']) / articles_df['page_views_count'].apply(lambda x: max(x, 1))
        articles_df['time_efficiency'] = articles_df['public_reactions_count'] / articles_df['reading_time_minutes'].apply(lambda x: max(x, 1))
        
        # Parse published_at dates
        articles_df['published_date'] = pd.to_datetime(articles_df['published_at'])
        articles_df['day_of_week'] = articles_df['published_date'].dt.day_name()
        articles_df['hour_of_day'] = articles_df['published_date'].dt.hour
        
        # Process tags
        tag_performance = self._analyze_tag_performance(articles_df)
        
        # Time-based analysis
        time_performance = self._analyze_time_performance(articles_df)
        
        return {
            'most_viewed': self._sort_and_format(articles_df, 'page_views_count', True),
            'most_reactions': self._sort_and_format(articles_df, 'public_reactions_count', True),
            'most_commented': self._sort_and_format(articles_df, 'comments_count', True),
            'highest_engagement': self._sort_and_format(articles_df, 'engagement_ratio', True),
            'best_time_efficiency': self._sort_and_format(articles_df, 'time_efficiency', True),
            'tag_performance': tag_performance,
            'time_performance': time_performance,
            'overall_stats': self._calculate_overall_stats(articles_df)
        }
    
    def _sort_and_format(self, df: pd.DataFrame, sort_column: str, descending: bool = True) -> List[Dict[str, Any]]:
        """
        Sort and format dataframe by the given column.
        
        Args:
            df: Pandas DataFrame to sort
            sort_column: Column to sort by
            descending: Whether to sort in descending order
            
        Returns:
            List of dictionaries with the sorted data
        """
        sorted_df = df.sort_values(by=sort_column, ascending=not descending)
        
        result = []
        for _, row in sorted_df.iterrows():
            result.append({
                'id': row.get('id'),
                'title': row.get('title', ''),
                'url': row.get('url', ''),
                'published_at': row.get('published_at', ''),
                'tags': row.get('tags', ''),
                'page_views_count': int(row.get('page_views_count', 0)),
                'public_reactions_count': int(row.get('public_reactions_count', 0)),
                'comments_count': int(row.get('comments_count', 0)),
                'reading_time_minutes': int(row.get('reading_time_minutes', 0)),
                'engagement_ratio': float(row.get('engagement_ratio', 0)),
                'time_efficiency': float(row.get('time_efficiency', 0))
            })
        
        return result
    
    def _analyze_tag_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze the performance of different tags.
        
        Args:
            df: Pandas DataFrame with article data
            
        Returns:
            Dictionary with tag performance metrics
        """
        tag_stats = {}
        
        # Extract tags and analyze performance
        for _, row in df.iterrows():
            tags = str(row.get('tags', '')).split(',')
            tags = [tag.strip() for tag in tags if tag.strip()]
            
            for tag in tags:
                if tag not in tag_stats:
                    tag_stats[tag] = {
                        'count': 0,
                        'views': 0,
                        'reactions': 0,
                        'comments': 0
                    }
                
                tag_stats[tag]['count'] += 1
                tag_stats[tag]['views'] += int(row.get('page_views_count', 0))
                tag_stats[tag]['reactions'] += int(row.get('public_reactions_count', 0))
                tag_stats[tag]['comments'] += int(row.get('comments_count', 0))
        
        # Calculate averages
        for tag, stats in tag_stats.items():
            stats['avg_views'] = stats['views'] / stats['count']
            stats['avg_reactions'] = stats['reactions'] / stats['count']
            stats['avg_comments'] = stats['comments'] / stats['count']
            stats['engagement'] = (stats['reactions'] + stats['comments']) / max(stats['views'], 1)
        
        # Convert to a list and sort by number of views
        tag_list = [{'tag': tag, **stats} for tag, stats in tag_stats.items()]
        tag_list.sort(key=lambda x: x['views'], reverse=True)
        
        return tag_list
    
    def _analyze_time_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze the performance by publish day and time.
        
        Args:
            df: Pandas DataFrame with article data
            
        Returns:
            Dictionary with time performance metrics
        """
        # Day of week analysis
        day_stats = df.groupby('day_of_week').agg({
            'id': 'count',
            'page_views_count': 'mean',
            'public_reactions_count': 'mean',
            'comments_count': 'mean'
        }).reset_index()
        
        day_stats.columns = ['day', 'article_count', 'avg_views', 'avg_reactions', 'avg_comments']
        
        # Hour of day analysis
        hour_stats = df.groupby('hour_of_day').agg({
            'id': 'count',
            'page_views_count': 'mean',
            'public_reactions_count': 'mean',
            'comments_count': 'mean'
        }).reset_index()
        
        hour_stats.columns = ['hour', 'article_count', 'avg_views', 'avg_reactions', 'avg_comments']
        
        return {
            'by_day': day_stats.to_dict(orient='records'),
            'by_hour': hour_stats.to_dict(orient='records')
        }
    
    def _calculate_overall_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate overall statistics for all articles.
        
        Args:
            df: Pandas DataFrame with article data
            
        Returns:
            Dictionary with overall statistics
        """
        return {
            'total_articles': len(df),
            'total_views': int(df['page_views_count'].sum()),
            'total_reactions': int(df['public_reactions_count'].sum()),
            'total_comments': int(df['comments_count'].sum()),
            'avg_views_per_article': float(df['page_views_count'].mean()),
            'avg_reactions_per_article': float(df['public_reactions_count'].mean()),
            'avg_comments_per_article': float(df['comments_count'].mean()),
            'avg_reading_time': float(df['reading_time_minutes'].mean()),
            'most_used_tags': self._get_most_used_tags(df),
        }
    
    def _get_most_used_tags(self, df: pd.DataFrame, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most frequently used tags.
        
        Args:
            df: Pandas DataFrame with article data
            limit: Number of tags to return
            
        Returns:
            List of dictionaries with tag information
        """
        tag_count = {}
        
        for _, row in df.iterrows():
            tags = str(row.get('tags', '')).split(',')
            tags = [tag.strip() for tag in tags if tag.strip()]
            
            for tag in tags:
                if tag not in tag_count:
                    tag_count[tag] = 0
                tag_count[tag] += 1
        
        # Convert to list and sort
        tag_list = [{'tag': tag, 'count': count} for tag, count in tag_count.items()]
        tag_list.sort(key=lambda x: x['count'], reverse=True)
        
        return tag_list[:limit]
    
    def generate_analysis_report(self) -> Dict[str, Any]:
        """
        Generate a complete analysis report.
        
        Returns:
            Dictionary with all analysis results
        """
        metrics = self.calculate_metrics()
        
        return {
            'username': self.username,
            'analysis_date': datetime.now().isoformat(),
            'overall_stats': metrics['overall_stats'],
            'top_posts': {
                'by_views': metrics['most_viewed'][:10],
                'by_reactions': metrics['most_reactions'][:10],
                'by_comments': metrics['most_commented'][:10],
                'by_engagement': metrics['highest_engagement'][:10],
                'by_time_efficiency': metrics['best_time_efficiency'][:10]
            },
            'tag_performance': metrics['tag_performance'][:15],
            'best_publishing_times': {
                'by_day': metrics['time_performance']['by_day'],
                'by_hour': metrics['time_performance']['by_hour']
            },
            'raw_data': {
                'detailed_articles': self.detailed_articles
            }
        }
    
    def export_report_to_json(self, filename: str = 'devto_analysis.json') -> str:
        """
        Export the analysis report to a JSON file.
        
        Args:
            filename: Name of the output file
            
        Returns:
            Path to the saved file
        """
        report = self.generate_analysis_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return filename
    
    def get_data_for_llm_analysis(self) -> Dict[str, Any]:
        """
        Format data specifically for LLM analysis.
        
        Returns:
            Dictionary with formatted data for LLM
        """
        metrics = self.calculate_metrics()
        
        # Format the data to be more readable for LLMs
        llm_data = {
            'username': self.username,
            'total_articles': metrics['overall_stats']['total_articles'],
            'top_performing_posts': [
                {
                    'title': post['title'],
                    'views': post['page_views_count'],
                    'reactions': post['public_reactions_count'],
                    'comments': post['comments_count'],
                    'tags': post['tags'],
                    'reading_time': post['reading_time_minutes']
                }
                for post in metrics['most_viewed'][:5]
            ],
            'highest_engagement_posts': [
                {
                    'title': post['title'],
                    'engagement_ratio': post['engagement_ratio'],
                    'views': post['page_views_count'],
                    'reactions': post['public_reactions_count'],
                    'tags': post['tags']
                }
                for post in metrics['highest_engagement'][:5]
            ],
            'top_tags': [
                {
                    'tag': tag_data['tag'],
                    'posts': tag_data['count'],
                    'avg_views': tag_data['avg_views'],
                    'avg_reactions': tag_data['avg_reactions'],
                    'engagement': tag_data['engagement']
                }
                for tag_data in metrics['tag_performance'][:10]
            ],
            'best_days': sorted(
                metrics['time_performance']['by_day'], 
                key=lambda x: x['avg_views'], 
                reverse=True
            ),
            'best_hours': sorted(
                metrics['time_performance']['by_hour'], 
                key=lambda x: x['avg_views'], 
                reverse=True
            )[:5]
        }
        
        return llm_data


# Example usage
if __name__ == "__main__":
    analyzer = DevToAnalyzer(username="your_username", api_key="your_api_key")
    report = analyzer.generate_analysis_report()
    print(json.dumps(report, indent=2, default=str))