"""
Pytest configuration and fixtures for D&D Tabletop application tests.
"""
import pytest
from django.contrib.auth import get_user_model
from campaigns.models import Campaign, Character, CampaignMembership

User = get_user_model()


@pytest.fixture
def db_setup(django_db_setup, django_db_blocker):
    """Set up test database with initial data."""
    with django_db_blocker.unblock():
        # Create test users
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        
        regular_user = User.objects.create_user(
            username='player1',
            email='player1@test.com',
            password='player123'
        )
        
        another_user = User.objects.create_user(
            username='player2',
            email='player2@test.com',
            password='player223'
        )
        
        # Create test campaign (using 'title' instead of 'name')
        campaign = Campaign.objects.create(
            title='Test Campaign',
            description='A testing campaign for automated tests'
        )
        
        # Create membership for regular user (using CampaignMembership)
        CampaignMembership.objects.create(
            user=regular_user,
            campaign=campaign,
            role='PLAYER'  # Use 'PLAYER' constant from model choices
        )
        
        # Add superuser as DM
        CampaignMembership.objects.create(
            user=superuser,
            campaign=campaign,
            role='DM'
        )
        
        # Create character for regular user (using class_name instead of class_type)
        character = Character.objects.create(
            name='Test Character',
            campaign=campaign,
            user=regular_user,  # Use 'user' instead of 'owner'
            class_name='Fighter',  # Use 'class_name' instead of 'class_type'
            level=1
        )
        
        return {
            'superuser': superuser,
            'regular_user': regular_user,
            'another_user': another_user,
            'campaign': campaign,
            'character': character
        }


@pytest.fixture
def client_auth(client, db_setup):
    """Authenticated client fixture for testing authenticated views."""
    client.force_login(db_setup['regular_user'])
    return client


@pytest.fixture
def admin_client(client, db_setup):
    """Admin client fixture for testing admin views."""
    client.force_login(db_setup['superuser'])
    return client
