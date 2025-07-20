"""
Basic tests for Flask Analytics Microservice
"""

import pytest
import os
import sys

# Add analytics directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db
from config import TestingConfig


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'analytics-microservice'


def test_analytics_info(client):
    """Test analytics info endpoint."""
    response = client.get('/analytics')
    assert response.status_code == 200
    data = response.get_json()
    assert data['service'] == 'Library Analytics API'
    assert 'endpoints' in data
    assert len(data['endpoints']) == 4


def test_config():
    """Test application configuration."""
    app = create_app(TestingConfig)
    assert app.config['TESTING'] is True
    assert 'sqlite:///:memory:' in app.config['SQLALCHEMY_DATABASE_URI']
