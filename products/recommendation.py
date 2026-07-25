from collections import Counter
from django.contrib.auth.models import User
from products.models import Product
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Important skincare ingredients recognized by our ML model
KNOWN_INGREDIENTS = [
    "niacinamide",
    "hyaluronic acid",
    "sodium hyaluronate",
    "glycerin",
    "ceramide",
    "centella asiatica",
    "cica",
    "green tea",
    "green tea extract",
    "green plum",
    "green plum extract",
    "snail mucin",
    "retinol",
    "vitamin c",
    "panthenol",
    "allantoin",
    "salicylic acid",
    "glycolic acid",
    "rice extract",
    "propolis",
    "honey",
    "collagen",
    "peptide",
    "ginseng",
    "betaine",
    "squalane",
    "aloe vera",
    "camellia",
    "zinc oxide",
    "titanium dioxide",
]
PRODUCT_GROUPS = {
    "eye cream": "eye",
    "eye patch": "eye",
    "foot cream": "foot",
    "foot": "foot",
    "body lotion": "body",
    "body scrub": "body",
    "body mist": "body",
    "soap": "body",
    "shampoo": "hair",
    "conditioner": "hair",
    "hair": "hair",
    "scalp": "hair",
    "cleanser": "face",
    "face wash": "face",
    "serum": "face",
    "essence": "face",
    "toner": "face",
    "moisturizer": "face",
    "sunscreen": "face",
    "mask": "face",
    "cream": "face",
    "lip": "lip",
}

GENERIC_WORDS = {
    "cream",
    "gel",
    "mask",
    "soap",
    "oil",
    "lotion",
    "wash",
    "cleanser",
    "serum",
    "essence",
    "toner",
    "mist",
    "moisturizer",
    "sunscreen",
    "scrub",
    "conditioner",
    "shampoo",
    "product",
    "skin",
    "beauty",
}

COMPATIBLE_GROUPS = {
    "face": ["face", "eye"],
    "eye": ["eye", "face"],
    "body": ["body"],
    "foot": ["foot"],
    "hair": ["hair"],
    "lip": ["lip"],
}

MIN_SIMILARITY = 0.12


def extract_important_ingredients(text):
    """
    Extract only important skincare ingredients.
    """

    text = text.lower()

    found = []

    for ingredient in KNOWN_INGREDIENTS:

        if ingredient in text:
            found.append(ingredient)

    return found


def ingredient_overlap_score(product1, product2):
    """
    Reward products that share important skincare ingredients.
    """

    ingredients1 = set(extract_important_ingredients(product1.ingredients))
    ingredients2 = set(extract_important_ingredients(product2.ingredients))

    shared = sorted(list(ingredients1.intersection(ingredients2)))

    overlap_bonus = len(shared) * 0.10

    return overlap_bonus, shared


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


# CONTENT BASED RECOMMENDATION
def extract_skin_benefits(text):
    """
    Convert ingredient names into skincare benefits.
    """

    text = text.lower()

    benefits = []

    ingredient_benefits = {
        "niacinamide": ["brightening", "oil-control"],
        "hyaluronic acid": ["hydrating"],
        "sodium hyaluronate": ["hydrating"],
        "ceramide": ["barrier-repair"],
        "centella": ["soothing"],
        "centella asiatica": ["soothing"],
        "cica": ["soothing"],
        "salicylic acid": ["acne"],
        "retinol": ["anti-aging"],
        "peptide": ["anti-aging"],
        "vitamin c": ["brightening"],
        "glycerin": ["hydrating"],
        "panthenol": ["barrier-repair"],
        "snail": ["repair"],
        "snail mucin": ["repair"],
        "green tea": ["soothing"],
        "ginseng": ["anti-aging"],
    }

    for ingredient, tags in ingredient_benefits.items():
        if ingredient in text:
            benefits.extend(tags)

    return benefits


def detect_product_group(product):

    text = (
        f"{product.name} " f"{product.subcategory.name if product.subcategory else ''}"
    ).lower()

    for keyword, group in PRODUCT_GROUPS.items():

        if keyword in text:

            return group

    return "other"


def create_product_text(product):
    """
    Create one text document representing a product.
    Important features are repeated to give them higher importance.
    """

    category = product.category.name if product.category else ""
    subcategory = product.subcategory.name if product.subcategory else ""
    brand = product.brand.name if product.brand else ""

    # Extract only important skincare ingredients
    important_ingredients = extract_important_ingredients(product.ingredients)

    skin_benefits = extract_skin_benefits(product.ingredients)

    name = product.name.lower()

    description = product.description.lower()

    name = product.name
    description = product.description

    text = f"""
    {name}
    {name}

    {subcategory}
    {subcategory}

    {category}

    {brand}

    {description}

    {' '.join(important_ingredients)}
    {' '.join(important_ingredients)}
    {' '.join(important_ingredients)}
    {' '.join(important_ingredients)}

    {' '.join(skin_benefits)}
    {' '.join(skin_benefits)}

    {product.how_to_use}
    """

    return text.lower()


def get_content_based_recommendations(product, limit=5):
    """
    Machine Learning Content-Based Recommendation
    using TF-IDF + Cosine Similarity
    """

    products = list(Product.objects.all())

    # Find current product index
    current_index = None

    for i, p in enumerate(products):
        if p.id == product.id:
            current_index = i
            break

    if current_index is None:
        return []

    vectorizer = TfidfVectorizer(
        stop_words=list(GENERIC_WORDS),
        lowercase=True,
        ngram_range=(1, 2),
        min_df=1,
    )

    documents = [create_product_text(p) for p in products]

    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(tfidf_matrix)

    similarity_scores = list(enumerate(similarity[current_index]))

    current_group = detect_product_group(product)

    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    scored_products = []

    recommendations = []

    for index, score in similarity_scores:

        if products[index].id == product.id:
            continue

        if score < MIN_SIMILARITY:
            continue

        candidate = products[index]

        candidate_group = detect_product_group(candidate)

        # --------------------------------------------------
        # Only recommend products from compatible groups
        # --------------------------------------------------

        allowed_groups = COMPATIBLE_GROUPS.get(current_group, [current_group])

        if candidate_group not in allowed_groups:
            continue

        compatibility_bonus = 0.10

        # NEW
        ingredient_bonus, shared_ingredients = ingredient_overlap_score(
            product,
            candidate,
        )

        final_score = (
            score * 0.60 + ingredient_bonus * 0.30 + compatibility_bonus * 0.10
        )

        print(f"{products[index].name:<55}" f"Similarity Score = {score:.4f}")

        scored_products.append(
            (
                final_score,
                candidate,
                score,
                compatibility_bonus,
                ingredient_bonus,
                shared_ingredients,
            )
        )

        if len(recommendations) == limit:
            break

    scored_products.sort(
        key=lambda x: x[0],
        reverse=True,
    )

    recommendations = []

    for (
        final_score,
        candidate,
        similarity_score,
        compatibility_bonus,
        ingredient_bonus,
        shared_ingredients,
    ) in scored_products:

        print(
            f"{candidate.name:<40}"
            f"Similarity={similarity_score:.3f}   "
            f"Compatibility={compatibility_bonus:.2f}   "
            f"Ingredients={ingredient_bonus:.2f}   "
            f"Final={final_score:.3f}"
        )

        print("Shared Ingredients:", shared_ingredients)
        print("-" * 70)

        recommendations.append(
            {
                "product": candidate,
                "score": round(final_score, 3),
                "shared_ingredients": shared_ingredients,
            }
        )

        if len(recommendations) == limit:
            break

    print("\n")
    print("=" * 70)
    print(f"CURRENT PRODUCT : {product.name}")
    print("=" * 70)
    print("Top Similar Products")
    print("-" * 70)

    return recommendations
