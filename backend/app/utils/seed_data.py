from sqlalchemy.orm import Session
from app.models.all_models import User, Category, Product, ProductImage, Coupon, Banner, Review, RoleEnum
from app.core.security import get_password_hash

def seed_database(db: Session):
    # Check if already seeded
    if db.query(User).first():
        return

    print("Seeding initial Sweet Crumbs database...")

    # 1. Users
    admin_user = User(
        full_name="Chef Marco Admin",
        email="admin@sweetcrumbs.com",
        hashed_password=get_password_hash("admin123"),
        phone="+1 800-555-BAKE",
        role=RoleEnum.ADMIN.value,
        loyalty_points=1000
    )
    customer_user = User(
        full_name="Sarah Jenkins",
        email="sarah@example.com",
        hashed_password=get_password_hash("customer123"),
        phone="+1 555-019-2834",
        role=RoleEnum.CUSTOMER.value,
        loyalty_points=150
    )
    db.add_all([admin_user, customer_user])
    db.commit()

    # 2. Categories
    categories_data = [
        {"name": "Bread", "slug": "bread", "icon": "Bread", "description": "Artisanal fresh baked sourdough, brioche, and baguettes."},
        {"name": "Cookies", "slug": "cookies", "icon": "Cookie", "description": "Warm, gooey chocochip & macadamia cookies."},
        {"name": "Biscuits", "slug": "biscuits", "icon": "Cookie", "description": "Crispy butter biscuits and digestive rusks."},
        {"name": "Pastries", "slug": "pastries", "icon": "Cake", "description": "Flaky French croissants & mille-feuille."},
        {"name": "Cupcakes", "slug": "cupcakes", "icon": "Cake", "description": "Gourmet frosted cupcakes with fruit compote."},
        {"name": "Birthday Cakes", "slug": "birthday-cakes", "icon": "Cake", "description": "Custom handcrafted multi-tier celebration cakes."},
        {"name": "Brownies", "slug": "brownies", "icon": "Cake", "description": "Rich Belgian dark chocolate fudge brownies."},
        {"name": "Pizza", "slug": "pizza", "icon": "Pizza", "description": "Wood-fired bakery sourdough pizzas with fresh basil."},
        {"name": "Burger", "slug": "burger", "icon": "Utensils", "description": "Gourmet bakery burgers on freshly toasted brioche."},
        {"name": "Sandwich", "slug": "sandwich", "icon": "Utensils", "description": "Artisan paninis and multi-grain deli sandwiches."},
        {"name": "Puffs", "slug": "puffs", "icon": "Utensils", "description": "Golden crispy puff pastry turners with fillings."},
        {"name": "Rolls", "slug": "rolls", "icon": "Utensils", "description": "Cinnamon rolls & savory stuffed bakery rolls."},
        {"name": "Snacks", "slug": "snacks", "icon": "Popcorn", "description": "Savory baked chips, quiches, and garlic sticks."},
        {"name": "Tea", "slug": "tea", "icon": "Coffee", "description": "Organic Earl Grey, Chamomile & Masala Chai."},
        {"name": "Coffee", "slug": "coffee", "icon": "Coffee", "description": "Freshly brewed espresso, cappuccino & caramel macchiato."},
        {"name": "Cold Drinks", "slug": "cold-drinks", "icon": "CupSoda", "description": "Iced matcha, berry coolers & cold brews."},
        {"name": "Combo Meals", "slug": "combo-meals", "icon": "Package", "description": "Breakfast & evening tea snack bundles."},
        {"name": "Festival Specials", "slug": "festival-specials", "icon": "Gift", "description": "Holiday hamper boxes & festive sweet boxes."}
    ]

    cat_map = {}
    for c in categories_data:
        cat = Category(**c)
        db.add(cat)
        db.commit()
        db.refresh(cat)
        cat_map[c["slug"]] = cat.id

    # 3. Products
    products_data = [
        {
            "name": "Artisanal Sourdough Bread",
            "slug": "artisanal-sourdough-bread",
            "category_id": cat_map["bread"],
            "description": "Naturally fermented 48-hour sourdough with a golden crispy crust and soft airy crumb inside.",
            "price": 280.0,
            "discount_price": 250.0,
            "is_veg": True,
            "is_featured": True,
            "is_todays_fresh": True,
            "is_popular": True,
            "ingredients": "Organic Wheat Flour, Water, Wild Sourdough Starter, Sea Salt",
            "nutrition_info": "Calories: 180kcal | Protein: 6g | Carbs: 36g | Fat: 1g",
            "prep_time": "Freshly baked at 6:00 AM daily",
            "rating": 4.9,
            "review_count": 48,
            "stock_quantity": 30,
            "image_url": "https://images.unsplash.com/photo-1589367920969-ab8e050bbb04?w=800&auto=format&fit=crop&q=80"
        },
        {
            "name": "Belgian Chocolate Truffle Cake",
            "slug": "belgian-chocolate-truffle-cake",
            "category_id": cat_map["birthday-cakes"],
            "description": "Layered sponge cake coated with 70% dark Belgian chocolate ganache and chocolate curls.",
            "price": 890.0,
            "discount_price": 799.0,
            "is_veg": True,
            "is_featured": True,
            "is_todays_fresh": False,
            "is_popular": True,
            "ingredients": "Belgian Dark Chocolate, Dutch Cocoa, Butter, Organic Milk, Wheat Flour",
            "nutrition_info": "Calories: 340kcal | Protein: 5g | Carbs: 42g | Fat: 18g",
            "prep_time": "30 mins setup time",
            "rating": 5.0,
            "review_count": 89,
            "stock_quantity": 12,
            "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=800&auto=format&fit=crop&q=80"
        },
        {
            "name": "Butter French Croissant",
            "slug": "butter-french-croissant",
            "category_id": cat_map["pastries"],
            "description": "Traditional 27-layer laminated puff pastry made with pure Normandy butter.",
            "price": 140.0,
            "discount_price": 120.0,
            "is_veg": True,
            "is_featured": True,
            "is_todays_fresh": True,
            "is_popular": True,
            "ingredients": "Normandy Butter, Unbleached Flour, Milk, Cane Sugar, Yeast",
            "nutrition_info": "Calories: 260kcal | Protein: 4g | Carbs: 28g | Fat: 15g",
            "prep_time": "Ready in store",
            "rating": 4.8,
            "review_count": 64,
            "stock_quantity": 40,
            "image_url": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=800&auto=format&fit=crop&q=80"
        },
        {
            "name": "Gooey Chocochip Cookies (4 Pcs)",
            "slug": "gooey-chocochip-cookies",
            "category_id": cat_map["cookies"],
            "description": "Soft-baked chocolate chip cookies with melted chocolate pockets and sea salt sprinkle.",
            "price": 220.0,
            "discount_price": None,
            "is_veg": True,
            "is_featured": False,
            "is_todays_fresh": True,
            "is_popular": True,
            "ingredients": "Semi-sweet Chocolate Chunks, Brown Sugar, Butter, Vanilla Extract",
            "nutrition_info": "Calories: 210kcal/pc | Protein: 3g | Fat: 10g",
            "prep_time": "15 mins",
            "rating": 4.9,
            "review_count": 35,
            "stock_quantity": 50,
            "image_url": "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=800&auto=format&fit=crop&q=80"
        },
        {
            "name": "Velvet Vanilla Berry Cupcake",
            "slug": "velvet-vanilla-berry-cupcake",
            "category_id": cat_map["cupcakes"],
            "description": "Madagascar vanilla sponge topped with fluffy Swiss buttercream and fresh raspberry.",
            "price": 160.0,
            "discount_price": 140.0,
            "is_veg": True,
            "is_featured": False,
            "is_todays_fresh": True,
            "is_popular": False,
            "ingredients": "Vanilla Bean, Buttercream, Berry Jam, Organic Flour",
            "nutrition_info": "Calories: 240kcal | Protein: 3g | Fat: 11g",
            "prep_time": "Ready in store",
            "rating": 4.7,
            "review_count": 22,
            "stock_quantity": 25,
            "image_url": "https://images.unsplash.com/photo-1576618148400-f54bed99fcfd?w=800&auto=format&fit=crop&q=80"
        },
        {
            "name": "Fudge Walnut Brownie",
            "slug": "fudge-walnut-brownie",
            "category_id": cat_map["brownies"],
            "description": "Ultra fudgy dark chocolate square embedded with toasted Californian walnuts.",
            "price": 180.0,
            "discount_price": 160.0,
            "is_veg": True,
            "is_featured": True,
            "is_todays_fresh": True,
            "is_popular": True,
            "ingredients": "Dark Cocoa, Toast Walnuts, Butter, Organic Sugar",
            "nutrition_info": "Calories: 310kcal | Protein: 4g | Fat: 16g",
            "prep_time": "Ready in store",
            "rating": 4.9,
            "review_count": 56,
            "stock_quantity": 35,
            "image_url": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=800&auto=format&fit=crop&q=80"
        },
        {
            "name": "Wood-Fired Margherita Sourdough Pizza",
            "slug": "margherita-sourdough-pizza",
            "category_id": cat_map["pizza"],
            "description": "10-inch artisan sourdough base topped with San Marzano tomato sauce, fresh mozzarella, and aromatic basil.",
            "price": 380.0,
            "discount_price": 349.0,
            "is_veg": True,
            "is_featured": True,
            "is_todays_fresh": True,
            "is_popular": True,
            "ingredients": "Sourdough Crust, Buffalo Mozzarella, Fresh Basil, Extra Virgin Olive Oil",
            "nutrition_info": "Calories: 580kcal | Protein: 22g | Carbs: 68g | Fat: 18g",
            "prep_time": "15-20 mins oven bake",
            "rating": 4.8,
            "review_count": 41,
            "stock_quantity": 20,
            "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800&auto=format&fit=crop&q=80"
        },
        {
            "name": "Artisan Veggie Brioche Burger",
            "slug": "artisan-veggie-brioche-burger",
            "category_id": cat_map["burger"],
            "description": "Crispy herb potato patty, sharp cheddar, caramelised onions inside our house-baked golden brioche bun.",
            "price": 260.0,
            "discount_price": None,
            "is_veg": True,
            "is_featured": False,
            "is_todays_fresh": True,
            "is_popular": True,
            "ingredients": "Brioche Bun, Potato Herb Patty, Cheddar Cheese, Secret Sauce",
            "nutrition_info": "Calories: 450kcal | Protein: 14g | Fat: 20g",
            "prep_time": "15 mins grill time",
            "rating": 4.6,
            "review_count": 19,
            "stock_quantity": 18,
            "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&auto=format&fit=crop&q=80"
        },
        {
            "name": "Golden Veggie Cheese Puff",
            "slug": "golden-veggie-cheese-puff",
            "category_id": cat_map["puffs"],
            "description": "Flaky puff pastry stuffed with spiced cottage cheese and sweet peppers.",
            "price": 75.0,
            "discount_price": 60.0,
            "is_veg": True,
            "is_featured": False,
            "is_todays_fresh": True,
            "is_popular": True,
            "ingredients": "Puff Dough, Paneer, Bell Peppers, Indian Spices",
            "nutrition_info": "Calories: 190kcal | Protein: 5g | Fat: 11g",
            "prep_time": "Ready in warm showcase",
            "rating": 4.7,
            "review_count": 52,
            "stock_quantity": 60,
            "image_url": "https://images.unsplash.com/photo-1621236378699-8597faf6a176?w=800&auto=format&fit=crop&q=80"
        },
        {
            "name": "Iced Vanilla Hazelnut Latte",
            "slug": "iced-vanilla-hazelnut-latte",
            "category_id": cat_map["coffee"],
            "description": "Double espresso shot poured over chilled milk, hazelnut syrup, and crushed ice.",
            "price": 190.0,
            "discount_price": None,
            "is_veg": True,
            "is_featured": False,
            "is_todays_fresh": True,
            "is_popular": True,
            "ingredients": "Arabica Espresso, Whole Milk, Hazelnut Syrup, Ice",
            "nutrition_info": "Calories: 160kcal | Protein: 6g | Fat: 5g",
            "prep_time": "5 mins",
            "rating": 4.9,
            "review_count": 73,
            "stock_quantity": 100,
            "image_url": "https://images.unsplash.com/photo-1517701604599-bb29b565090c?w=800&auto=format&fit=crop&q=80"
        },
        {
            "name": "High-Tea Bakery Combo",
            "slug": "high-tea-bakery-combo",
            "category_id": cat_map["combo-meals"],
            "description": "1 Butter Croissant + 1 Hazelnut Latte + 2 Chocochip Cookies for the perfect afternoon break.",
            "price": 450.0,
            "discount_price": 380.0,
            "is_veg": True,
            "is_featured": True,
            "is_todays_fresh": True,
            "is_popular": True,
            "ingredients": "Assorted fresh bakery items and fresh beverage",
            "nutrition_info": "Ideal for sharing between 2 persons",
            "prep_time": "10 mins",
            "rating": 5.0,
            "review_count": 31,
            "stock_quantity": 15,
            "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800&auto=format&fit=crop&q=80"
        },
        {
            "name": "Grand Festive Royal Hamper",
            "slug": "grand-festive-royal-hamper",
            "category_id": cat_map["festival-specials"],
            "description": "Luxury wooden gift box containing 1 Fruit Bread, 6 Assorted Macarons, 8 Butter Cookies & Artisanal Jam.",
            "price": 1250.0,
            "discount_price": 1099.0,
            "is_veg": True,
            "is_featured": True,
            "is_todays_fresh": False,
            "is_popular": True,
            "ingredients": "Assorted bakery delicacies in gift presentation box",
            "nutrition_info": "Festive Gift Pack",
            "prep_time": "Custom packed",
            "rating": 5.0,
            "review_count": 14,
            "stock_quantity": 10,
            "image_url": "https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=800&auto=format&fit=crop&q=80"
        }
    ]

    for p in products_data:
        prod = Product(**p)
        db.add(prod)
    db.commit()

    # 4. Coupons
    coupons = [
        Coupon(code="WELCOME100", discount_percent=20.0, max_discount_amount=100.0, min_order_amount=300.0, is_active=True),
        Coupon(code="SWEET50", discount_percent=15.0, max_discount_amount=50.0, min_order_amount=200.0, is_active=True),
        Coupon(code="FESTIVE25", discount_percent=25.0, max_discount_amount=250.0, min_order_amount=600.0, is_active=True)
    ]
    db.add_all(coupons)
    db.commit()

    # 5. Banners
    banners = [
        Banner(
            title="Freshly Baked Daily With Artisan Love",
            subtitle="Handcrafted sourdough, rich pastries, and signature celebration cakes straight from our oven.",
            image_url="https://images.unsplash.com/photo-1509440159596-0249088772ff?w=1600&auto=format&fit=crop&q=80",
            button_text="Order Warm Bakery",
            button_link="/shop"
        ),
        Banner(
            title="Schedule Hot Takeaway Pickup",
            subtitle="Choose your preferred date and time slot. Scan your QR code at the counter for zero waiting time!",
            image_url="https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=1600&auto=format&fit=crop&q=80",
            button_text="Schedule Pickup Now",
            button_link="/shop"
        )
    ]
    db.add_all(banners)
    db.commit()

    print("Database successfully seeded with Sweet Crumbs products & categories!")
