import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ProductHuntAPI:
    """Product Hunt API客户端"""
    
    def __init__(self, developer_token: str, api_url: str):
        """
        初始化Product Hunt API客户端
        
        Args:
            developer_token: Product Hunt开发者令牌
            api_url: API端点URL
        """
        self.developer_token = developer_token
        self.api_url = api_url
        self.headers = {
            'Authorization': f'Bearer {developer_token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, query: str, variables: Dict = None) -> Dict[str, Any]:
        """
        发送GraphQL请求
        
        Args:
            query: GraphQL查询语句
            variables: 查询变量
            
        Returns:
            API响应数据
        """
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {e}")
            raise
    
    def get_daily_posts(self, date: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取指定日期的产品列表
        
        Args:
            date: 日期字符串 (YYYY-MM-DD)，默认为今天
            limit: 返回产品数量限制
            
        Returns:
            产品列表
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        query = """
        query($postedAfter: DateTime!, $postedBefore: DateTime!, $first: Int!) {
            posts(postedAfter: $postedAfter, postedBefore: $postedBefore, first: $first, order: VOTES) {
                edges {
                    node {
                        id
                        name
                        tagline
                        description
                        url
                        votesCount
                        commentsCount
                        createdAt
                        website
                        thumbnail {
                            url
                        }
                        user {
                            name
                            username
                        }
                        topics {
                            edges {
                                node {
                                    name
                                }
                            }
                        }
                        comments(first: 5) {
                            edges {
                                node {
                                    id
                                    body
                                    createdAt
                                    user {
                                        name
                                        username
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        
        # 设置时间范围为指定日期的00:00-23:59
        posted_after = f"{date}T00:00:00Z"
        posted_before = f"{date}T23:59:59Z"
        
        variables = {
            'postedAfter': posted_after,
            'postedBefore': posted_before,
            'first': limit
        }
        
        response = self._make_request(query, variables)
        
        if 'errors' in response:
            logger.error(f"GraphQL错误: {response['errors']}")
            return []
        
        posts = []
        for edge in response.get('data', {}).get('posts', {}).get('edges', []):
            post = edge['node']
            # 提取话题标签
            topics = [topic['node']['name'] for topic in post.get('topics', {}).get('edges', [])]
            
            # 提取评论
            comments = []
            for comment_edge in post.get('comments', {}).get('edges', []):
                comment = comment_edge['node']
                comments.append({
                    'id': comment['id'],
                    'body': comment['body'],
                    'created_at': comment['createdAt'],
                    'user_name': comment.get('user', {}).get('name', ''),
                    'user_username': comment.get('user', {}).get('username', '')
                })
            
            posts.append({
                'id': post['id'],
                'name': post['name'],
                'tagline': post['tagline'],
                'description': post['description'],
                'url': post['url'],
                'website': post.get('website', ''),
                'votes_count': post['votesCount'],
                'comments_count': post['commentsCount'],
                'created_at': post['createdAt'],
                'thumbnail_url': post.get('thumbnail', {}).get('url', ''),
                'user_name': post.get('user', {}).get('name', ''),
                'user_username': post.get('user', {}).get('username', ''),
                'topics': topics,
                'comments': comments
            })
        
        return posts
    
    def get_weekly_posts(self, start_date: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取一周内的热门产品
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)，默认为7天前
            limit: 返回产品数量限制
            
        Returns:
            产品列表
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        query = """
        query($postedAfter: DateTime!, $postedBefore: DateTime!, $first: Int!) {
            posts(postedAfter: $postedAfter, postedBefore: $postedBefore, first: $first, order: VOTES) {
                edges {
                    node {
                        id
                        name
                        tagline
                        description
                        url
                        votesCount
                        commentsCount
                        createdAt
                        website
                        thumbnail {
                            url
                        }
                        user {
                            name
                            username
                        }
                        topics {
                            edges {
                                node {
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        
        posted_after = f"{start_date}T00:00:00Z"
        posted_before = f"{end_date}T23:59:59Z"
        
        variables = {
            'postedAfter': posted_after,
            'postedBefore': posted_before,
            'first': limit
        }
        
        response = self._make_request(query, variables)
        
        if 'errors' in response:
            logger.error(f"GraphQL错误: {response['errors']}")
            return []
        
        posts = []
        for edge in response.get('data', {}).get('posts', {}).get('edges', []):
            post = edge['node']
            topics = [topic['node']['name'] for topic in post.get('topics', {}).get('edges', [])]
            
            posts.append({
                'id': post['id'],
                'name': post['name'],
                'tagline': post['tagline'],
                'description': post['description'],
                'url': post['url'],
                'website': post.get('website', ''),
                'votes_count': post['votesCount'],
                'comments_count': post['commentsCount'],
                'created_at': post['createdAt'],
                'thumbnail_url': post.get('thumbnail', {}).get('url', ''),
                'user_name': post.get('user', {}).get('name', ''),
                'user_username': post.get('user', {}).get('username', ''),
                'topics': topics,
                'comments': []  # 周报不包含评论，降低API复杂度
            })
        
        return posts
    
    def get_monthly_posts(self, start_date: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取一个月内的热门产品
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)，默认为30天前
            limit: 返回产品数量限制
            
        Returns:
            产品列表
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        query = """
        query($postedAfter: DateTime!, $postedBefore: DateTime!, $first: Int!) {
            posts(postedAfter: $postedAfter, postedBefore: $postedBefore, first: $first, order: VOTES) {
                edges {
                    node {
                        id
                        name
                        tagline
                        description
                        url
                        votesCount
                        commentsCount
                        createdAt
                        website
                        thumbnail {
                            url
                        }
                        user {
                            name
                            username
                        }
                        topics {
                            edges {
                                node {
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        
        posted_after = f"{start_date}T00:00:00Z"
        posted_before = f"{end_date}T23:59:59Z"
        
        variables = {
            'postedAfter': posted_after,
            'postedBefore': posted_before,
            'first': limit
        }
        
        response = self._make_request(query, variables)
        
        if 'errors' in response:
            logger.error(f"GraphQL错误: {response['errors']}")
            return []
        
        posts = []
        for edge in response.get('data', {}).get('posts', {}).get('edges', []):
            post = edge['node']
            topics = [topic['node']['name'] for topic in post.get('topics', {}).get('edges', [])]
            
            posts.append({
                'id': post['id'],
                'name': post['name'],
                'tagline': post['tagline'],
                'description': post['description'],
                'url': post['url'],
                'website': post.get('website', ''),
                'votes_count': post['votesCount'],
                'comments_count': post['commentsCount'],
                'created_at': post['createdAt'],
                'thumbnail_url': post.get('thumbnail', {}).get('url', ''),
                'user_name': post.get('user', {}).get('name', ''),
                'user_username': post.get('user', {}).get('username', ''),
                'topics': topics,
                'comments': []  # 月报不包含评论，降低API复杂度
            })
        
        return posts