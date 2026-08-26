# 📊 Database Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    USERS ||--o{ ORDERS : places
    USERS ||--o{ CART_ITEMS : maintains
    USERS ||--o{ WISHLIST_ITEMS : saves
    USERS ||--o{ REVIEWS : writes
    USERS ||--o{ ADDRESSES : owns
    
    CATEGORIES ||--o{ PRODUCTS : contains
    PRODUCTS ||--o{ PRODUCT_IMAGES : has
    PRODUCTS ||--o{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ REVIEWS : receives
    
    ORDERS ||--o{ ORDER_ITEMS : includes
    ORDERS ||--o| PAYMENTS : has

    USERS {
        int id PK
        string full_name
        string email UK
        string hashed_password
        string phone
        string role
        int loyalty_points
        boolean is_active
        datetime created_at
    }

    CATEGORIES {
        int id PK
        string name
        string slug UK
        string icon
        string description
    }

    PRODUCTS {
        int id PK
        string name
        string slug UK
        int category_id FK
        text description
        float price
        float discount_price
        boolean is_veg
        boolean is_todays_fresh
        float rating
        int stock_quantity
        string image_url
    }

    ORDERS {
        int id PK
        string order_number UK
        int user_id FK
        float total_amount
        float final_amount
        string order_type
        string pickup_date
        string pickup_time_slot
        string pickup_number
        text qr_code_data
        string status
        string payment_method
        string payment_status
        datetime created_at
    }

    ORDER_ITEMS {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        float price
    }

    COUPONS {
        int id PK
        string code UK
        float discount_percent
        float max_discount_amount
        float min_order_amount
        boolean is_active
    }
```
