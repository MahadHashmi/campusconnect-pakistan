from sqlalchemy import text
from database import SessionLocal, engine
import models

def seed_social_and_marketplace():
    # 1. Migrate existing tables to add any missing columns safely
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE posts ADD COLUMN IF NOT EXISTS author_name VARCHAR(150) DEFAULT 'Student';
            ALTER TABLE posts ADD COLUMN IF NOT EXISTS campus_name VARCHAR(150) DEFAULT 'PU • New Campus';
            ALTER TABLE posts ADD COLUMN IF NOT EXISTS media_url TEXT;
            ALTER TABLE posts ADD COLUMN IF NOT EXISTS media_type VARCHAR(50) DEFAULT 'photo';
            ALTER TABLE posts ADD COLUMN IF NOT EXISTS likes_count INT DEFAULT 0;
            DO $$ 
            BEGIN 
                ALTER TABLE posts ALTER COLUMN user_id DROP NOT NULL;
                ALTER TABLE posts ALTER COLUMN university_id DROP NOT NULL;
            EXCEPTION 
                WHEN OTHERS THEN NULL;
            END $$;
        """))
        conn.commit()

    # 2. Ensure all other tables (including marketplace_items) exist
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 3. Seed Social Posts if empty
        if db.query(models.Post).count() == 0:
            posts = [
                models.Post(
                    author_name="Mahad Hashmi",
                    campus_name="PU • FCIT (New Campus)",
                    content="Annual Department Cricket Match at New Campus ground! Best day of the semester so far 🏏🔥 Good luck to BSCS 4th semester team!",
                    media_url="https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=800",
                    media_type="photo",
                    likes_count=142
                ),
                models.Post(
                    author_name="Shahmeer Zaidi",
                    campus_name="NUST • SEECS (H-12 Islamabad)",
                    content="Presenting our AI computer vision project at the National Tech Expo today! Huge turnout from FAST, UET and GIKI teams 🇵🇰💻",
                    media_url="https://images.unsplash.com/photo-1531482615713-2afd69097998?w=800",
                    media_type="photo",
                    likes_count=289
                ),
                models.Post(
                    author_name="Sara Tariq",
                    campus_name="FAST • Lahore Campus",
                    content="Post-midterm canteen session with the gang! Nothing beats chai paratha after a brutal Data Structures paper ☕✨",
                    media_url="https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=800",
                    media_type="photo",
                    likes_count=98
                )
            ]
            db.add_all(posts)
            db.commit()
            print("Successfully seeded initial social posts!")

        # 4. Seed Marketplace Items if empty
        if db.query(models.MarketplaceItem).count() == 0:
            items = [
                models.MarketplaceItem(
                    title="Casio fx-991EX ClassWiz Calculator",
                    description="Original scientific calculator in 10/10 condition. Used for 2 semesters only. Original battery working perfectly.",
                    price=2500,
                    category="calculator",
                    image_url="https://images.unsplash.com/photo-1587145820266-a5951ee6f620?w=600",
                    seller_name="Usman Ali (BSIT 6th)",
                    whatsapp_number="923001234567",
                    campus_name="PU • New Campus (Lahore)"
                ),
                models.MarketplaceItem(
                    title="Thomas Calculus (14th Edition) Hardcover",
                    description="Original textbook with solved chapter exercise notes for Calculus 1 & 2. Completely clean pages.",
                    price=900,
                    category="book",
                    image_url="https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600",
                    seller_name="Hamza Sheikh",
                    whatsapp_number="923129876543",
                    campus_name="FAST • Lahore Campus"
                ),
                models.MarketplaceItem(
                    title="I will design your Project PowerPoint Presentation",
                    description="Professional PPT / Canva design for semester presentations, FYP proposals, or research defense. Delivery in 24 hours.",
                    price=500,
                    category="gig",
                    image_url="https://images.unsplash.com/photo-1557804506-669a67965ba0?w=600",
                    seller_name="Ayesha Malik",
                    whatsapp_number="923335551234",
                    campus_name="NUST • Islamabad"
                ),
                models.MarketplaceItem(
                    title="Mini Hostel Room Cooler / Fan",
                    description="Perfect for hostel room. Low electricity consumption, runs on UPS easily. Good condition.",
                    price=3500,
                    category="hostel",
                    image_url="https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=600",
                    seller_name="Bilal Raza",
                    whatsapp_number="923454321987",
                    campus_name="PU • Hostel 4 (New Campus)"
                )
            ]
            db.add_all(items)
            db.commit()
            print("Successfully seeded initial marketplace items!")

        print(f"DATABASE READY! Total Posts: {db.query(models.Post).count()} | Total Market Items: {db.query(models.MarketplaceItem).count()}")

    finally:
        db.close()

if __name__ == "__main__":
    seed_social_and_marketplace()
