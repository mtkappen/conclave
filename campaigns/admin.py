from django.contrib import admin
from .models import User, Campaign, CampaignMembership, Character, InventoryItem, PartyGroup, PartyGroupMember, ChatMessage, DiceRollLog


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'real_name', 'email']
    search_fields = ['username', 'real_name', 'email']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['title']


@admin.register(CampaignMembership)
class CampaignMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'campaign', 'role']
    list_filter = ['role']
    search_fields = ['user__username', 'campaign__title']


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ['name', 'class_name', 'level', 'user', 'campaign']
    list_filter = ['campaign', 'class_name']
    search_fields = ['name', 'user__username']


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'character']
    search_fields = ['name', 'character__name']


@admin.register(PartyGroup)
class PartyGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'campaign', 'created_at']
    search_fields = ['name', 'campaign__title']


@admin.register(PartyGroupMember)
class PartyGroupMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'group']
    search_fields = ['user__username', 'group__name']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'campaign', 'visibility_type', 'message_type', 'created_at']
    list_filter = ['visibility_type', 'message_type', 'campaign']
    search_fields = ['content', 'sender__username']


@admin.register(DiceRollLog)
class DiceRollLogAdmin(admin.ModelAdmin):
    list_display = ['sender', 'formula', 'result', 'visibility', 'created_at']
    list_filter = ['visibility', 'campaign']
    search_fields = ['sender__username', 'formula']