from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import NMF
import pandas as pd
import numpy as np
from shop.models import Product, Category  # Only Product and Category are in shop.models
from cart.models import Order, OrderItem    # Order and OrderItem are in cart.models

# Content-based Filtering: Recommends products based on similarity in descriptions and categories
def get_product_recommendations(product_name, num_recommendations=5):
    """
    Returns a list of product names similar to the given product_name based on description and category.
    Uses TF-IDF and cosine similarity for content-based filtering.
    """
    try:
        # Get all available products
        products = Product.objects.select_related('category').filter(available=True)
        
        if not products.exists():
            return []
            
        # Get product descriptions and names
        descriptions = []
        product_names = []
        for product in products:
            # Combine category name and description for better matching
            category_name = product.category.name if product.category else "Uncategorized"
            # Add more weight to category by repeating it and adding product name
            text = f"{category_name} {category_name} {category_name} {product.name} {product.name} {product.description}"
            descriptions.append(text)
            product_names.append(product.name)
        
        if product_name not in product_names:
            return []
        
        # Create TF-IDF matrix with improved parameters for small datasets
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),  # Include both unigrams and bigrams
            max_features=None,  # Don't limit features since we have few products
            min_df=1,  # Include all terms since we have few products
            max_df=0.95  # Remove terms that appear in more than 95% of products
        )
        tfidf_matrix = vectorizer.fit_transform(descriptions)
        
        # Calculate cosine similarity
        cosine_similarities = cosine_similarity(tfidf_matrix)
        
        # Get index of the target product
        product_idx = product_names.index(product_name)
        
        # Get similarity scores for the target product
        similarity_scores = list(enumerate(cosine_similarities[product_idx]))
        
        # Sort by similarity score (excluding the product itself)
        similarity_scores = sorted(
            [s for s in similarity_scores if s[0] != product_idx],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Get top N recommendations
        top_indices = [s[0] for s in similarity_scores[:num_recommendations]]
        recommendations = [product_names[i] for i in top_indices]
        
        return recommendations
        
    except Exception as e:
        return []

# Collaborative Filtering: Recommends products based on user purchase history
def get_collaborative_recommendations(user_id, num_recommendations=5):
    """
    Returns a list of product names recommended for the user based on their purchase history.
    Uses Non-negative Matrix Factorization (NMF) for collaborative filtering.
    """
    try:
        # Get all completed orders
        orders = Order.objects.filter(status='completed')
        
        if not orders.exists():
            # If no completed orders, return content-based recommendations for a popular product
            popular_product = Product.objects.filter(available=True).first()
            if popular_product:
                return get_product_recommendations(popular_product.name, num_recommendations)
            return []
            
        # Create user-product matrix
        user_product_matrix = {}
        for order in orders:
            order_user_id = order.user.id  # Use a different variable name to avoid overwriting input parameter
            if order_user_id not in user_product_matrix:
                user_product_matrix[order_user_id] = {}
            
            # Use items instead of orderitem_set (the related_name we defined)
            for item in order.items.all():
                product_name = item.product.name
                if product_name not in user_product_matrix[order_user_id]:
                    user_product_matrix[order_user_id][product_name] = 0
                user_product_matrix[order_user_id][product_name] += item.quantity
        
        if not user_product_matrix:
            return []
        
        # Convert to numpy array
        users = list(user_product_matrix.keys())
        products = list(set(p for u in user_product_matrix.values() for p in u.keys()))
        matrix = np.zeros((len(users), len(products)))
        
        for i, user in enumerate(users):
            for j, product in enumerate(products):
                matrix[i, j] = user_product_matrix[user].get(product, 0)
        
        # Apply NMF
        nmf = NMF(n_components=min(5, len(products)), random_state=42)
        nmf.fit(matrix)
        
        # Get user's row in the matrix
        if user_id not in users:
            return []
            
        user_idx = users.index(user_id)
        user_vector = matrix[user_idx:user_idx+1]
        
        # Get predicted ratings
        predicted_ratings = nmf.inverse_transform(nmf.transform(user_vector))[0]
        
        # Get all product indices sorted by predicted rating
        sorted_indices = sorted(range(len(products)), key=lambda j: predicted_ratings[j], reverse=True)
        
        # Get top N recommendations
        recommendations = [products[i] for i in sorted_indices[:num_recommendations]]
        
        return recommendations
        
    except Exception as e:
        return []

def get_hybrid_recommendations(user_id, product_name=None, num_recommendations=5):
    """
    Returns a list of product names recommended using a hybrid approach that combines
    content-based and collaborative filtering. The weights are dynamically adjusted
    based on the available data.
    """
    try:
        # Get recommendations from both methods
        content_recs = []
        collab_recs = []
        
        # Get content-based recommendations if a product is specified
        if product_name:
            content_recs = get_product_recommendations(product_name, num_recommendations)
        
        # Get collaborative recommendations
        collab_recs = get_collaborative_recommendations(user_id, num_recommendations)
        
        # Calculate weights based on available data
        content_weight = 0.4  # Base weight for content-based
        collab_weight = 0.6   # Base weight for collaborative
        
        # Adjust weights if one method has no recommendations
        if not content_recs and not collab_recs:
            return []
        elif not content_recs:
            content_weight = 0
            collab_weight = 1
        elif not collab_recs:
            content_weight = 1
            collab_weight = 0
        
        # Combine recommendations with weights
        hybrid_recs = {}
        
        # Add content-based recommendations with their weight
        for rec in content_recs:
            hybrid_recs[rec] = hybrid_recs.get(rec, 0) + content_weight
        
        # Add collaborative recommendations with their weight
        for rec in collab_recs:
            hybrid_recs[rec] = hybrid_recs.get(rec, 0) + collab_weight
        
        # Sort by combined weight and get top N
        sorted_recs = sorted(hybrid_recs.items(), key=lambda x: x[1], reverse=True)
        recommendations = [rec[0] for rec in sorted_recs[:num_recommendations]]
        
        return recommendations
        
    except Exception as e:
        return []