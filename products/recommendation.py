from collections import Counter
from django.contrib.auth.models import User
from products.models import Product
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


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
        orderlineitem__order__user_profile__user=user
    ).distinct()

    print("Current User:", user.username)
    print("Purchased Products:", list(user_products))

    if not user_products.exists():
        return []

    # Find similar users who bought at least one same product
    similar_users = (
        User.objects.filter(userprofile__orders__lineitems__product__in=user_products)
        .exclude(id=user.id)
        .distinct()
    )

    print("Similar Users:", list(similar_users))

    if not similar_users.exists():
        return []

    # Get products bought by similar users, excluding user's own purchases
    similar_user_products = Product.objects.filter(
        orderlineitem__order__user_profile__user__in=similar_users
    ).exclude(id__in=user_products.values_list("id", flat=True))

    print("Products Bought By Similar Users:", list(similar_user_products))

    # Convert queryset to list for counting
    similar_user_products_list = list(similar_user_products)

    # Rank products by purchase frequency
    product_counts = Counter(similar_user_products_list)
    recommendations = [product for product, _ in product_counts.most_common(limit)]

    print("Final Recommendations:", recommendations)

    return recommendations


# Download only once
try:
    nltk.data.find("tokenizers/punkt")
except:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/stopwords")
except:
    nltk.download("stopwords")

STOP_WORDS = set(stopwords.words("english"))

# ======================================
# INGREDIENT DICTIONARY
# ======================================

INGREDIENTS = [
    "green plum extract",
    "glycolic acid",
    "green tea extract",
    "camellia",
    "sodium hyaluronate",
    "hyaluronic acid",
    "aloe vera",
    "centella asiatica",
    "cica",
    "lime extract",
    "niacinamide",
    "ceramide",
    "retinol",
    "vitamin c",
    "peptide",
    "collagen",
    "snail mucin",
    "panthenol",
    "allantoin",
    "glycerin",
    "betaine",
    "salicylic acid",
    "rice extract",
    "ginseng",
    "propolis",
    "honey",
    "squalane",
    "zinc oxide",
    "titanium dioxide",
]

# ======================================
# BENEFIT DICTIONARY
# ======================================

BENEFIT_KEYWORDS = {
    "hydrating": [
        "hyaluronic acid",
        "sodium hyaluronate",
        "aloe vera",
        "glycerin",
        "betaine",
        "snail mucin",
        "squalane",
    ],
    "soothing": [
        "centella asiatica",
        "cica",
        "green tea extract",
        "camellia",
        "aloe vera",
        "allantoin",
        "panthenol",
    ],
    "brightening": [
        "niacinamide",
        "vitamin c",
        "green plum extract",
        "lime extract",
        "rice extract",
    ],
    "anti-aging": ["retinol", "peptide", "collagen", "ginseng"],
    "barrier-repair": ["ceramide", "panthenol", "squalane"],
    "acne-care": ["salicylic acid", "niacinamide"],
}

# ======================================
# TEXT PREPROCESSING (NLTK)
# ======================================


def preprocess_text(text):

    text = text.lower()

    tokens = word_tokenize(text)

    tokens = [token for token in tokens if token.isalnum() and token not in STOP_WORDS]

    return " ".join(tokens)


# ======================================
# EXTRACT INGREDIENTS
# ======================================


def extract_ingredients(text):

    text = preprocess_text(text)

    found = []

    for ingredient in INGREDIENTS:

        if ingredient.lower() in text:
            found.append(ingredient)

    return set(found)


# ======================================
# EXTRACT BENEFITS
# ======================================


def extract_benefits(text):

    ingredients = extract_ingredients(text)

    benefits = set()

    for benefit, keywords in BENEFIT_KEYWORDS.items():

        for keyword in keywords:

            if keyword in ingredients:

                benefits.add(benefit)

    return benefits


# ======================================
# CONTENT BASED RECOMMENDER
# ======================================


def get_content_based_recommendations(product, limit=5):

    current_ingredients = extract_ingredients(product.ingredients)

    current_benefits = extract_benefits(product.ingredients)

    recommendations = []

    products = Product.objects.exclude(id=product.id)

    for other in products:

        other_ingredients = extract_ingredients(other.ingredients)

        other_benefits = extract_benefits(other.ingredients)

        ingredient_matches = len(current_ingredients.intersection(other_ingredients))

        benefit_matches = len(current_benefits.intersection(other_benefits))

        score = 0

        # ingredient similarity
        score += ingredient_matches * 5

        # benefit similarity
        score += benefit_matches * 10

        # same category boost
        if other.subcategory == product.subcategory:
            score += 20

        recommendations.append((other, score))

    recommendations.sort(key=lambda x: x[1], reverse=True)

    return [item[0] for item in recommendations[:limit]]
