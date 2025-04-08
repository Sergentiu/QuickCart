from django.utils import timezone
from .models import UserBehavior, Product
from django.db.models import Count, Q
from datetime import timedelta

class BehaviorTracker:
    @staticmethod
    def track_behavior(user, product, interaction_type, metadata=None):
        """
        Track a user's interaction with a product.
        
        Args:
            user: The user performing the action
            product: The product being interacted with
            interaction_type: Type of interaction (from UserBehavior.InteractionType)
            metadata: Additional data about the interaction (dict)
        """
        if metadata is None:
            metadata = {}
            
        UserBehavior.objects.create(
            user=user,
            product=product,
            interaction_type=interaction_type,
            metadata=metadata
        )

    @staticmethod
    def get_user_interests(user, days=30):
        """
        Get a user's interests based on their recent behavior.
        
        Args:
            user: The user to analyze
            days: Number of days to look back
            
        Returns:
            dict: Dictionary of category interests with scores
        """
        # Get all user behaviors within the time period
        behaviors = UserBehavior.objects.filter(
            user=user,
            timestamp__gte=timezone.now() - timedelta(days=days)
        )
        
        # Calculate category interests
        category_scores = {}
        for behavior in behaviors:
            category = behavior.product.category
            if category:
                # Different weights for different interaction types
                weight = {
                    'view': 1,
                    'search': 2,
                    'cart_add': 3,
                    'purchase': 5,
                    'rating': 4
                }.get(behavior.interaction_type, 1)
                
                category_scores[category] = category_scores.get(category, 0) + weight
        
        return category_scores

    @staticmethod
    def get_similar_users(user, days=30):
        """
        Find users with similar behavior patterns.
        
        Args:
            user: The user to find similar users for
            days: Number of days to look back
            
        Returns:
            QuerySet: Users with similar behavior patterns
        """
        # Get the user's recent behaviors
        user_behaviors = UserBehavior.objects.filter(
            user=user,
            timestamp__gte=timezone.now() - timedelta(days=days)
        )
        
        # Get products the user has interacted with
        user_products = set(user_behaviors.values_list('product_id', flat=True))
        
        # Find users who have interacted with the same products
        similar_users = UserBehavior.objects.filter(
            product_id__in=user_products,
            timestamp__gte=timezone.now() - timedelta(days=days)
        ).exclude(user=user).values('user').annotate(
            common_interactions=Count('product', distinct=True)
        ).order_by('-common_interactions')
        
        return similar_users

    @staticmethod
    def get_popular_products(category=None, days=30):
        """
        Get popular products based on user behavior.
        
        Args:
            category: Optional category to filter by
            days: Number of days to look back
            
        Returns:
            QuerySet: Popular products
        """
        # Base query for behaviors
        behaviors = UserBehavior.objects.filter(
            timestamp__gte=timezone.now() - timedelta(days=days)
        )
        
        # Filter by category if specified
        if category:
            behaviors = behaviors.filter(product__category=category)
        
        # Get product popularity scores
        product_scores = behaviors.values('product').annotate(
            score=Count('id', filter=Q(interaction_type='purchase')) * 5 +
                  Count('id', filter=Q(interaction_type='cart_add')) * 3 +
                  Count('id', filter=Q(interaction_type='view')) * 1
        ).order_by('-score')
        
        # Get the actual products
        product_ids = [item['product'] for item in product_scores]
        products = Product.objects.filter(id__in=product_ids)
        
        # Preserve the order
        return sorted(products, key=lambda p: product_ids.index(p.id)) 