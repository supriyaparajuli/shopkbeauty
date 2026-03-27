from collections import Counter
from django.contrib.auth.models import User
from products.models import Product

def get_collaborative_recommendations(user, limit=5):
    """
    Basic collaborative filtering:
    - Finds products purchased by similar users.
    - Excludes products the current user already bought.
    """

    if not user.is_authenticated:
        return []

    # Get products purchased by the current user
    user_products = Product.objects.filter(
        orderlineitem__order__user=user
    ).distinct()

    if not user_products.exists():
        return []

    # Find similar users who bought at least one same product
    similar_users = User.objects.filter(
        order__orderlineitem__product__in=user_products
    ).exclude(id=user.id).distinct()

    if not similar_users.exists():
        return []

    # Get products bought by similar users, excluding user's own purchases
    similar_user_products = Product.objects.filter(
        orderlineitem__order__user__in=similar_users
    ).exclude(id__in=user_products.values_list('id', flat=True))

    # Convert queryset to list for counting
    similar_user_products_list = list(similar_user_products)

    # Rank products by purchase frequency
    product_counts = Counter(similar_user_products_list)
    recommendations = [product for product, _ in product_counts.most_common(limit)]

    return recommendations
