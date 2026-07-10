"""Companions selectors."""
from .repositories import CompanionRepository


class CompanionSelectors:
    @staticmethod
    def get_companion(pk):
        return CompanionRepository.get_by_id(pk)

    @staticmethod
    def get_my_profile(user_id):
        return CompanionRepository.get_by_user(user_id)

    @staticmethod
    def list_available():
        return CompanionRepository.get_active_available()

    @staticmethod
    def search_companions(query):
        return CompanionRepository.search(query)
