import asyncio
import random
from sqlalchemy import select, func
from db.base import async_session
from db.models.user import User
from db.models.listing import Listing
from db.models.feedback import Feedback

class ExpertAgent:
    def __init__(self, name, focus):
        self.name = name
        self.focus = focus

    async def generate_idea(self, metrics):
        raise NotImplementedError

class GrowthExpert(ExpertAgent):
    async def generate_idea(self, metrics):
        if metrics['users'] < 50:
            return {
                "agent": self.name,
                "title": "Viral Loop Initiation",
                "content": "Add a 'Share Listing' button that gives users a small discount on their next post if a friend joins."
            }
        return {
            "agent": self.name,
            "title": "SEO & Indexing",
            "content": "Implement a public web catalog to allow Google indexing of equipment listings, driving organic search traffic."
        }

class UXExpert(ExpertAgent):
    async def generate_idea(self, metrics):
        if metrics['feedback'] > 5:
            return {
                "agent": self.name,
                "title": "Feedback Loop",
                "content": "Users are mentioning complexity in photo uploads. Simplify the process by allowing multi-photo selection in one message."
            }
        return {
            "agent": self.name,
            "title": "Onboarding Polish",
            "content": "Add a progress bar (e.g., Step 3/9) to the listing creation flow to reduce dropout rates."
        }

class MonetizationExpert(ExpertAgent):
    async def generate_idea(self, metrics):
        if metrics['listings'] > 20:
            return {
                "agent": self.name,
                "title": "Premium Tier",
                "content": "Introduce a 'Verified Seller' badge for 499 RUB/month to increase trust and platform revenue."
            }
        return {
            "agent": self.name,
            "title": "Urgency Sales",
            "content": "Implement 'Hot Deals' - 24-hour discounted rentals for equipment that hasn't been booked in over 2 weeks."
        }

async def get_growth_insights():
    """Mixture of Experts (MoMoA-inspired) analysis of bot metrics"""
    async with async_session() as session:
        metrics = {
            'users': await session.scalar(select(func.count()).select_from(User)) or 0,
            'listings': await session.scalar(select(func.count()).select_from(Listing).where(Listing.status == "active")) or 0,
            'feedback': await session.scalar(select(func.count()).select_from(Feedback)) or 0
        }

    experts = [
        GrowthExpert("GrowthAgent", "User Acquisition"),
        UXExpert("UXAgent", "Retention & Satisfaction"),
        MonetizationExpert("ProfitAgent", "Revenue & Pricing")
    ]

    # Run experts in parallel (MoMoA Work Phase Room Simulation)
    results = await asyncio.gather(*[e.generate_idea(metrics) for e in experts])

    return results
