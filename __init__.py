import uuid
from datetime import datetime
from app.models import User, Business, Deal, Transaction

class UserService:
    def __init__(self, db):
        self.db = db
        self.users_ref = db.collection('users')
    
    def get_user(self, user_id):
        """Get user by ID"""
        user_doc = self.users_ref.document(user_id).get()
        if user_doc.exists:
            return user_doc.to_dict()
        return None
    
    def create_user(self, name, email):
        """Create a new user"""
        user_id = str(uuid.uuid4())
        user = User(user_id, name, email)
        self.users_ref.document(user_id).set(user.to_dict())
        return user.to_dict()
    
    def update_user_balance(self, user_id, amount):
        """Update user token balance"""
        user_ref = self.users_ref.document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return None
        
        user_data = user_doc.to_dict()
        new_balance = user_data.get('balance', 0) + amount
        
        # Update tier based on balance
        new_tier = "Bronze"
        if new_balance >= 500:
            new_tier = "Gold"
        elif new_balance >= 200:
            new_tier = "Silver"
        
        user_ref.update({
            'balance': new_balance,
            'tier': new_tier,
            'last_active': datetime.now()
        })
        
        return {
            'user_id': user_id,
            'new_balance': new_balance,
            'tier': new_tier
        }

class BusinessService:
    def __init__(self, db):
        self.db = db
        self.businesses_ref = db.collection('businesses')
    
    def get_business(self, business_id):
        """Get business by ID"""
        business_doc = self.businesses_ref.document(business_id).get()
        if business_doc.exists:
            return business_doc.to_dict()
        return None
    
    def create_business(self, name, address, token_rate=1, location=None):
        """Create a new business"""
        business_id = str(uuid.uuid4())
        business = Business(business_id, name, address, token_rate, location)
        self.businesses_ref.document(business_id).set(business.to_dict())
        return business.to_dict()
    
    def update_token_rate(self, business_id, token_rate):
        """Update business token rate"""
        business_ref = self.businesses_ref.document(business_id)
        business_doc = business_ref.get()
        
        if not business_doc.exists:
            return None
        
        business_ref.update({'token_rate': token_rate})
        return {'business_id': business_id, 'token_rate': token_rate}
    
    def get_nearby_businesses(self, lat, lng, radius=5):
        """Get businesses near coordinates (simplified)"""
        # This is a simplified implementation without actual geo queries
        # In a real app, you'd use Firestore's geoqueries or a separate geo service
        businesses = self.businesses_ref.limit(10).stream()
        return [business.to_dict() for business in businesses]

class DealService:
    def __init__(self, db):
        self.db = db
        self.deals_ref = db.collection('deals')
    
    def create_deal(self, business_id, title, description, token_cost, expires_at=None):
        """Create a new deal"""
        deal_id = str(uuid.uuid4())
        deal = Deal(deal_id, business_id, title, description, token_cost, expires_at)
        self.deals_ref.document(deal_id).set(deal.to_dict())
        return deal.to_dict()
    
    def get_deal(self, deal_id):
        """Get deal by ID"""
        deal_doc = self.deals_ref.document(deal_id).get()
        if deal_doc.exists:
            return deal_doc.to_dict()
        return None
    
    def get_business_deals(self, business_id):
        """Get all deals for a business"""
        deals = self.deals_ref.where('business_id', '==', business_id).stream()
        return [deal.to_dict() for deal in deals]
    
    def get_all_active_deals(self):
        """Get all active deals"""
        # In a real app, you'd filter by expiration date
        deals = self.deals_ref.limit(20).stream()
        return [deal.to_dict() for deal in deals]

class TransactionService:
    def __init__(self, db):
        self.db = db
        self.transactions_ref = db.collection('transactions')
        self.user_service = UserService(db)
    
    def create_transaction(self, user_id, business_id=None, recipient_id=None, 
                        amount=0, transaction_type="earn", description=""):
        """Create a new transaction"""
        transaction_id = str(uuid.uuid4())
        transaction = Transaction(
            transaction_id, user_id, business_id, recipient_id,
            amount, transaction_type, description
        )
        self.transactions_ref.document(transaction_id).set(transaction.to_dict())
        return transaction.to_dict()
    
    def earn_tokens(self, user_id, business_id, purchase_amount):
        """Earn tokens from a purchase"""
        business_service = BusinessService(self.db)
        business = business_service.get_business(business_id)
        
        if not business:
            return {'error': 'Business not found'}
        
        token_rate = business.get('token_rate', 1)
        tokens_earned = int(purchase_amount * token_rate)
        
        # Update user balance
        self.user_service.update_user_balance(user_id, tokens_earned)
        
        # Create transaction record
        transaction = self.create_transaction(
            user_id=user_id,
            business_id=business_id,
            amount=tokens_earned,
            transaction_type="earn",
            description=f"Earned from purchase at {business.get('name')}"
        )
        
        return {
            'user_id': user_id,
            'business_id': business_id,
            'tokens_earned': tokens_earned,
            'transaction_id': transaction.get('transaction_id')
        }
    
    def redeem_tokens(self, user_id, deal_id):
        """Redeem tokens for a deal"""
        deal_service = DealService(self.db)
        deal = deal_service.get_deal(deal_id)
        
        if not deal:
            return {'error': 'Deal not found'}
        
        token_cost = deal.get('token_cost', 0)
        user = self.user_service.get_user(user_id)
        
        if not user:
            return {'error': 'User not found'}
        
        if user.get('balance', 0) < token_cost:
            return {'error': 'Insufficient tokens'}
        
        # Update user balance (negative amount for redemption)
        self.user_service.update_user_balance(user_id, -token_cost)
        
        # Create transaction record
        transaction = self.create_transaction(
            user_id=user_id,
            business_id=deal.get('business_id'),
            amount=token_cost,
            transaction_type="redeem",
            description=f"Redeemed for deal: {deal.get('title')}"
        )
        
        return {
            'user_id': user_id,
            'deal_id': deal_id,
            'tokens_spent': token_cost,
            'transaction_id': transaction.get('transaction_id')
        }
    
    def transfer_tokens(self, sender_id, recipient_id, amount):
        """Transfer tokens between users"""
        sender = self.user_service.get_user(sender_id)
        recipient = self.user_service.get_user(recipient_id)
        
        if not sender or not recipient:
            return {'error': 'User not found'}
        
        if sender.get('balance', 0) < amount:
            return {'error': 'Insufficient tokens'}
        
        # Update sender balance (negative)
        self.user_service.update_user_balance(sender_id, -amount)
        
        # Update recipient balance (positive)
        self.user_service.update_user_balance(recipient_id, amount)
        
        # Create transaction record
        transaction = self.create_transaction(
            user_id=sender_id,
            recipient_id=recipient_id,
            amount=amount,
            transaction_type="transfer",
            description=f"Transfer to user {recipient.get('name')}"
        )
        
        return {
            'sender_id': sender_id,
            'recipient_id': recipient_id,
            'amount': amount,
            'transaction_id': transaction.get('transaction_id')
        }
    
    def get_user_transactions(self, user_id):
        """Get all transactions for a user"""
        transactions = self.transactions_ref.where('user_id', '==', user_id).stream()
        return [tx.to_dict() for tx in transactions]
    
    def get_business_transactions(self, business_id):
        """Get all transactions for a business"""
        transactions = self.transactions_ref.where('business_id', '==', business_id).stream()
        return [tx.to_dict() for tx in transactions]

class AnalyticsService:
    def __init__(self, db):
        self.db = db
        self.transactions_ref = db.collection('transactions')
    
    def get_business_analytics(self, business_id):
        """Get analytics for a business"""
        # Get all transactions for the business
        transactions = self.transactions_ref.where('business_id', '==', business_id).stream()
        transactions_list = [tx.to_dict() for tx in transactions]
        
        # Count unique users
        unique_users = set()
        tokens_awarded = 0
        tokens_redeemed = 0
        
        for tx in transactions_list:
            unique_users.add(tx.get('user_id'))
            if tx.get('transaction_type') == 'earn':
                tokens_awarded += tx.get('amount', 0)
            elif tx.get('transaction_type') == 'redeem':
                tokens_redeemed += tx.get('amount', 0)
        
        return {
            'business_id': business_id,
            'total_transactions': len(transactions_list),
            'unique_customers': len(unique_users),
            'tokens_awarded': tokens_awarded,
            'tokens_redeemed': tokens_redeemed
        }
