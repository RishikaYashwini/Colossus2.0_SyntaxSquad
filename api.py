from flask import Blueprint, request, jsonify
from app.services import UserService, BusinessService, DealService, TransactionService, AnalyticsService

api = Blueprint('api', __name__)

def init_api(db):
    user_service = UserService(db)
    business_service = BusinessService(db)
    deal_service = DealService(db)
    transaction_service = TransactionService(db)
    analytics_service = AnalyticsService(db)
    
    # User Routes
    @api.route('/users', methods=['POST'])
    def create_user():
        data = request.json
        name = data.get('name')
        email = data.get('email')
        
        if not name or not email:
            return jsonify({'error': 'Name and email are required'}), 400
        
        user = user_service.create_user(name, email)
        return jsonify(user), 201
    
    @api.route('/users/<user_id>', methods=['GET'])
    def get_user(user_id):
        user = user_service.get_user(user_id)
        if user:
            return jsonify(user)
        return jsonify({'error': 'User not found'}), 404
    
    # Business Routes
    @api.route('/businesses', methods=['POST'])
    def create_business():
        data = request.json
        name = data.get('name')
        address = data.get('address')
        token_rate = data.get('token_rate', 1)
        location = data.get('location')
        
        if not name or not address:
            return jsonify({'error': 'Name and address are required'}), 400
        
        business = business_service.create_business(name, address, token_rate, location)
        return jsonify(business), 201
    
    @api.route('/businesses/<business_id>', methods=['GET'])
    def get_business(business_id):
        business = business_service.get_business(business_id)
        if business:
            return jsonify(business)
        return jsonify({'error': 'Business not found'}), 404
    
    @api.route('/businesses/<business_id>/token_rate', methods=['PUT'])
    def update_token_rate(business_id):
        data = request.json
        token_rate = data.get('token_rate')
        
        if token_rate is None:
            return jsonify({'error': 'Token rate is required'}), 400
        
        result = business_service.update_token_rate(business_id, token_rate)
        if result:
            return jsonify(result)
        return jsonify({'error': 'Business not found'}), 404
    
    @api.route('/businesses/nearby', methods=['GET'])
    def get_nearby_businesses():
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        radius = request.args.get('radius', 5, type=int)
        
        if lat is None or lng is None:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        
        businesses = business_service.get_nearby_businesses(lat, lng, radius)
        return jsonify(businesses)
    
    # Deal Routes
    @api.route('/deals', methods=['POST'])
    def create_deal():
        data = request.json
        business_id = data.get('business_id')
        title = data.get('title')
        description = data.get('description')
        token_cost = data.get('token_cost')
        expires_at = data.get('expires_at')
        
        if not business_id or not title or token_cost is None:
            return jsonify({'error': 'Business ID, title, and token cost are required'}), 400
        
        deal = deal_service.create_deal(business_id, title, description, token_cost, expires_at)
        return jsonify(deal), 201
    
    @api.route('/deals/<deal_id>', methods=['GET'])
    def get_deal(deal_id):
        deal = deal_service.get_deal(deal_id)
        if deal:
            return jsonify(deal)
        return jsonify({'error': 'Deal not found'}), 404
    
    @api.route('/businesses/<business_id>/deals', methods=['GET'])
    def get_business_deals(business_id):
        deals = deal_service.get_business_deals(business_id)
        return jsonify(deals)
    
    @api.route('/deals', methods=['GET'])
    def get_all_deals():
        deals = deal_service.get_all_active_deals()
        return jsonify(deals)
    
    # Transaction Routes
    @api.route('/earn_tokens', methods=['POST'])
    def earn_tokens():
        data = request.json
        user_id = data.get('user_id')
        business_id = data.get('business_id')
        purchase_amount = data.get('purchase_amount')
        
        if not user_id or not business_id or purchase_amount is None:
            return jsonify({'error': 'User ID, business ID, and purchase amount are required'}), 400
        
        result = transaction_service.earn_tokens(user_id, business_id, purchase_amount)
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result)
    
    @api.route('/redeem_tokens', methods=['POST'])
    def redeem_tokens():
        data = request.json
        user_id = data.get('user_id')
        deal_id = data.get('deal_id')
        
        if not user_id or not deal_id:
            return jsonify({'error': 'User ID and deal ID are required'}), 400
        
        result = transaction_service.redeem_tokens(user_id, deal_id)
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result)
    
    @api.route('/send_tokens', methods=['POST'])
    def send_tokens():
        data = request.json
        sender_id = data.get('sender_id')
        recipient_id = data.get('recipient_id')
        amount = data.get('amount')
        
        if not sender_id or not recipient_id or amount is None:
            return jsonify({'error': 'Sender ID, recipient ID, and amount are required'}), 400
        
        result = transaction_service.transfer_tokens(sender_id, recipient_id, amount)
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result)
    
    @api.route('/users/<user_id>/transactions', methods=['GET'])
    def get_user_transactions(user_id):
        transactions = transaction_service.get_user_transactions(user_id)
        return jsonify(transactions)
    
    # Analytics Routes
    @api.route('/businesses/<business_id>/analytics', methods=['GET'])
    def get_business_analytics(business_id):
        analytics = analytics_service.get_business_analytics(business_id)
        return jsonify(analytics)
    
    return api
