from datetime import datetime

class User:
    def __init__(self, user_id, name, email, balance=0, tier="Bronze"):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.balance = balance
        self.tier = tier
        self.created_at = datetime.now()
        self.last_active = datetime.now()
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "balance": self.balance,
            "tier": self.tier,
            "created_at": self.created_at,
            "last_active": self.last_active
        }

class Business:
    def __init__(self, business_id, name, address, token_rate=1, location=None):
        self.business_id = business_id
        self.name = name
        self.address = address
        self.token_rate = token_rate  # Tokens per dollar spent
        self.location = location or {"lat": 0, "lng": 0}
        self.created_at = datetime.now()
    
    def to_dict(self):
        return {
            "business_id": self.business_id,
            "name": self.name,
            "address": self.address,
            "token_rate": self.token_rate,
            "location": self.location,
            "created_at": self.created_at
        }

class Deal:
    def __init__(self, deal_id, business_id, title, description, token_cost, expires_at=None):
        self.deal_id = deal_id
        self.business_id = business_id
        self.title = title
        self.description = description
        self.token_cost = token_cost
        self.expires_at = expires_at
        self.created_at = datetime.now()
    
    def to_dict(self):
        return {
            "deal_id": self.deal_id,
            "business_id": self.business_id,
            "title": self.title,
            "description": self.description,
            "token_cost": self.token_cost,
            "expires_at": self.expires_at,
            "created_at": self.created_at
        }

class Transaction:
    def __init__(self, transaction_id, user_id, business_id=None, recipient_id=None, 
                amount=0, transaction_type="earn", description=""):
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.business_id = business_id
        self.recipient_id = recipient_id
        self.amount = amount
        self.transaction_type = transaction_type  # earn, redeem, transfer
        self.description = description
        self.timestamp = datetime.now()
    
    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "user_id": self.user_id,
            "business_id": self.business_id,
            "recipient_id": self.recipient_id,
            "amount": self.amount,
            "transaction_type": self.transaction_type,
            "description": self.description,
            "timestamp": self.timestamp
        }