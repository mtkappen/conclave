from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    # First-time admin setup (must come before login/register)
    path('setup/', views.first_time_admin_setup, name='first_time_setup'),
    
        # Authentication
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    path('voluntary-change-password/', views.voluntary_change_password, name='voluntary_change_password'),
    
    # Database reset (admin only)
    path('admin/database-reset/', views.database_reset, name='database_reset'),
    
    # User Management (Super Admin only) - accessible at /users/
    path('users/', views.admin_user_list, name='admin_user_list'),
    path('users/create/', views.admin_create_user, name='admin_create_user'),
    path('users/<int:pk>/delete/', views.delete_user, name='delete_user'),
    
    # Admin Campaign Management
    path('admin/campaigns/', views.admin_campaign_list, name='admin_campaign_list'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Campaigns
    path('campaign/create/', views.create_campaign, name='create_campaign'),
    path('campaign/<int:pk>/', views.campaign_detail, name='campaign_detail'),
    
    # Characters
    path('campaign/<int:campaign_pk>/character/create/', views.create_character, name='create_character'),
    path('character/<int:pk>/', views.character_detail, name='character_detail'),
    path('character/<int:pk>/edit/', views.edit_character, name='edit_character'),
    path('character/<int:character_pk>/inventory/add/', views.add_inventory_item, name='add_inventory_item'),
    
    # DM Tools
    path('campaign/<int:campaign_pk>/dm/roster/', views.dm_character_roster, name='dm_roster'),
    
    # Delete actions
    path('campaign/<int:pk>/delete/', views.delete_campaign, name='delete_campaign'),
    path('character/<int:pk>/delete/', views.delete_character, name='delete_character'),
    
    # Chat endpoints
    path('campaign/<int:campaign_pk>/chat/messages/', views.get_chat_messages, name='get_chat_messages'),
    path('campaign/<int:campaign_pk>/chat/post/', views.post_chat_message, name='post_chat_message'),
    path('campaign/<int:campaign_pk>/dice/post/', views.post_dice_roll, name='post_dice_roll'),
    path('chat/message/<int:message_pk>/edit/', views.edit_chat_message, name='edit_chat_message'),
    path('chat/message/<int:message_pk>/delete/', views.delete_chat_message, name='delete_chat_message'),
    
    # Member management endpoints
    path('campaign/<int:campaign_pk>/members/', views.manage_campaign_members, name='manage_members'),
    path('campaign/<int:campaign_pk>/members/add/', views.add_campaign_member, name='add_member'),
    path('membership/<int:membership_pk>/role/', views.update_member_role, name='update_role'),
    path('membership/<int:membership_pk>/remove/', views.remove_campaign_member, name='remove_member'),
    path('campaign/<int:campaign_pk>/leave/', views.leave_campaign, name='leave_campaign'),
    
    # Admin secret whisper viewer
    path('admin/campaign/<int:campaign_pk>/secrets/', views.admin_view_secret_whispers, name='admin_view_secrets'),
    
        # Personal Notebook
    path('campaign/<int:campaign_pk>/notebook/', views.my_personal_notebook, name='personal_notebook'),
    path('notebook/<int:pk>/delete/', views.delete_personal_notebook, name='delete_personal_notebook'),
    
    # Campaign Rule Book
    path('campaign/<int:campaign_pk>/rule-book/', views.view_campaign_rule_book, name='view_rule_book'),
    path('campaign/<int:campaign_pk>/rule-book/edit/', views.edit_campaign_rule_book, name='edit_rule_book'),
]