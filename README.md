# 🌸 ShopKBeauty

A full-stack skincare e-commerce web application developed using **Django** that provides users with a secure online shopping experience, personalized skincare product recommendations, and efficient order management.

---

## 📖 Project Overview

ShopKBeauty is a modern skincare e-commerce platform designed to simplify online skincare shopping. The application allows customers to browse products, search products based on categories, manage shopping carts, securely complete payments using Stripe, and receive personalized product recommendations.

The project focuses on:

- Secure online transactions
- User-friendly shopping experience
- Intelligent product recommendation
- Efficient order and inventory management
- Personalized skincare product discovery

---

## ✨ Features

### 👤 User Features
- User Registration
- User Login & Logout
- Password Reset
- User Profile Management
- Address Management
- Order History
- Secure Authentication

### 🛍 Shopping Features
- Browse Products
- Product Categories
- Product Subcategories
- Featured Products
- Product Details Page
- Product Images
- Related Products
- Personalized Product Recommendations

### 🔍 Search & Filtering
- Search products by name
- Filter by category
- Filter by subcategory
- Browse featured products
- View similar products

### 🛒 Shopping Cart
- Add to Cart
- Remove from Cart
- Update Quantity
- Cart Summary
- Session-based Cart Management

### 💳 Checkout & Payment
- Secure Checkout
- Shipping Information Form
- Billing Information Form
- Stripe Payment Integration
- Payment Confirmation
- Order Confirmation

### 📦 Order Management
- Place Orders
- View Order History
- View Order Details
- Save Delivery Information
- Order Confirmation Email

### ⭐ Reviews & Ratings
- Product Reviews
- Product Ratings
- Customer Feedback System

### 👨‍💼 Admin Features
- Add Products
- Update Products
- Delete Products
- Manage Categories
- Manage Subcategories
- Manage Orders
- Manage Customers
- Inventory Management

---

## 🤖 Recommendation System

ShopKBeauty includes an intelligent recommendation system to improve the shopping experience.

### Recommendation Techniques Used

#### 1. Content-Based Filtering (Machine Learning)
- Uses product features such as ingredients, category, subcategory, and skincare attributes.
- Converts product information into numerical feature vectors.
- Calculates similarity between products using machine learning techniques.
- Recommends products that are most similar to the product currently viewed by the user.

#### 2. User-Based Collaborative Filtering
- Analyzes user interactions and purchase behavior.
- Finds users with similar preferences.
- Suggests products liked by similar users.

#### 3. Related Product Recommendation
- Recommends products from the same subcategory or category.
- Helps users discover similar skincare products.

### Benefits
- Personalized shopping experience
- Better product discovery
- Increased customer engagement
- Improved recommendation accuracy

---

## 💳 Payment Integration

Payment processing is implemented using **Stripe**.

### Payment Features
- Secure Online Payment
- Stripe Checkout
- Payment Intent API
- Card Validation
- Payment Confirmation
- Automatic Order Creation after Successful Payment

---

## 🔐 Authentication & Security

Authentication is handled using Django’s built-in authentication system.

### Security Features
- User Registration & Login
- Password Hashing
- Session Authentication
- CSRF Protection
- Form Validation
- Secure Payment Processing with Stripe
- SQL Injection Protection via Django ORM
- XSS Protection

---

## 🧠 Algorithms Used

### Recommendation Algorithms
- Content-Based Filtering (Machine Learning)
- User-Based Collaborative Filtering
- Similar Product Matching

### Search & Filtering Algorithms
- Django ORM Query Filtering
- Keyword Matching
- Category/Subcategory Filtering

### Product Similarity Calculation
Products are recommended based on:
- Product ingredients
- Category
- Subcategory
- Product attributes
- User interaction patterns

---

## 🗄 Database Models

Main models used in the project:

- User
- Profile
- Product
- Category
- Subcategory
- Wishlist
- Cart
- Order
- OrderLineItem
- Review

---

## 🛠 Technology Stack

### Backend
- Python
- Django

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap

### Database
- SQLite (Development)

### Machine Learning
- Content-Based Filtering Recommendation Model
- Similarity Calculation Techniques

### Payment Gateway
- Stripe

### Version Control
- Git
- GitHub

---

## 📁 Project Structure

```
shopkbeauty/
│
├── products/
├── checkout/
├── profiles/
├── cart/
├── wishlist/
├── reviews/
├── templates/
├── static/
├── media/
├── shopkbeauty/
├── manage.py
└── requirements.txt
```

---

## 🚀 Installation

### Clone the Repository
```bash
git clone https://github.com/supriyaparajuli/shopkbeauty.git
```

### Navigate to Project Directory
```bash
cd shopkbeauty
```

### Create Virtual Environment
```bash
python -m venv venv
```

### Activate Virtual Environment
```bash
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Apply Migrations
```bash
python manage.py migrate
```

### Run the Development Server
```bash
python manage.py runserver
```

---

## 📸 Screenshots

Add screenshots of:

- Home Page
- Product Listing
- Product Details
- Cart Page
- Checkout Page
- Stripe Payment Page
- Recommendation Section
- Order History
- User Profile
- Admin Dashboard

---

## 🎯 Project Objectives

- Provide a secure skincare e-commerce platform.
- Improve user experience through personalized recommendations.
- Ensure safe online payment processing.
- Build an efficient product and order management system.
- Demonstrate full-stack web development and machine learning integration.

---

## 📈 Expected Outcomes

- Better User Experience
- Stronger Customer Trust
- Efficient Order & Inventory Management
- Personalized Product Discovery
- Improved Product Recommendation Accuracy
- Secure and Reliable Online Shopping

---

## 🚀 Future Improvements

- AI-based Skin Analysis
- Image-based Product Recommendation
- Product Comparison Feature
- Coupon & Discount System
- Live Chat Support
- Email Notifications
- Multi-language Support
- Advanced Machine Learning Recommendation Engine
- Mobile Application Version

---

## 👨‍💻 Developer

**Supriya Parajuli**

- BCA Student
- Frontend & Django Developer
- Interested in AI/ML and Web Development

GitHub: https://github.com/supriyaparajuli

---

## 📄 License

This project was developed for educational and portfolio purposes.
