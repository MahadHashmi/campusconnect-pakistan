from sqlalchemy import text
from database import SessionLocal
import models

def seed_pakistan_universities():
    db = SessionLocal()
    try:
        # Reset sequence in case manual IDs were inserted
        db.execute(text("SELECT setval(pg_get_serial_sequence('universities', 'id'), COALESCE(max(id), 1)) FROM universities;"))
        db.commit()

        universities_data = [
            # Federal / Islamabad
            {"name": "National University of Sciences & Technology", "acronym": "NUST", "city": "Islamabad"},
            {"name": "COMSATS University Islamabad", "acronym": "CUI", "city": "Islamabad"},
            {"name": "FAST-NUCES Islamabad", "acronym": "FAST", "city": "Islamabad"},
            {"name": "Air University", "acronym": "AU", "city": "Islamabad"},
            {"name": "Bahria University", "acronym": "BU", "city": "Islamabad"},
            {"name": "Quaid-i-Azam University", "acronym": "QAU", "city": "Islamabad"},
            {"name": "International Islamic University", "acronym": "IIUI", "city": "Islamabad"},

            # Punjab
            {"name": "FAST-NUCES Lahore", "acronym": "FAST", "city": "Lahore"},
            {"name": "Lahore University of Management Sciences", "acronym": "LUMS", "city": "Lahore"},
            {"name": "University of Engineering & Technology", "acronym": "UET", "city": "Lahore"},
            {"name": "COMSATS Lahore", "acronym": "CUI", "city": "Lahore"},
            {"name": "University of Central Punjab", "acronym": "UCP", "city": "Lahore"},
            {"name": "Information Technology University", "acronym": "ITU", "city": "Lahore"},
            {"name": "Government College University", "acronym": "GCU", "city": "Lahore"},
            {"name": "University of Agriculture Faisalabad", "acronym": "UAF", "city": "Faisalabad"},
            {"name": "Bahauddin Zakariya University", "acronym": "BZU", "city": "Multan"},
            {"name": "Islamia University of Bahawalpur", "acronym": "IUB", "city": "Bahawalpur"},
            {"name": "University of Gujrat", "acronym": "UOG", "city": "Gujrat"},

            # Sindh
            {"name": "NED University of Engineering & Technology", "acronym": "NED", "city": "Karachi"},
            {"name": "FAST-NUCES Karachi", "acronym": "FAST", "city": "Karachi"},
            {"name": "Institute of Business Administration", "acronym": "IBA", "city": "Karachi"},
            {"name": "University of Karachi", "acronym": "UoK", "city": "Karachi"},
            {"name": "Sir Syed University of Engineering & Tech", "acronym": "SSUET", "city": "Karachi"},
            {"name": "Mehran University of Engineering & Tech", "acronym": "MUET", "city": "Jamshoro"},
            {"name": "Sukkur IBA University", "acronym": "SIBA", "city": "Sukkur"},

            # Khyber Pakhtunkhwa (KPK)
            {"name": "Ghulam Ishaq Khan Institute", "acronym": "GIKI", "city": "Topi"},
            {"name": "FAST-NUCES Peshawar", "acronym": "FAST", "city": "Peshawar"},
            {"name": "University of Peshawar", "acronym": "UoP", "city": "Peshawar"},
            {"name": "UET Peshawar", "acronym": "UET", "city": "Peshawar"},
            {"name": "Islamia College Peshawar", "acronym": "ICP", "city": "Peshawar"},
            {"name": "Institute of Management Sciences", "acronym": "IMSciences", "city": "Peshawar"},

            # Balochistan
            {"name": "BUITEMS", "acronym": "BUITEMS", "city": "Quetta"},
            {"name": "University of Balochistan", "acronym": "UoB", "city": "Quetta"},

            # Azad Jammu & Kashmir (AJK)
            {"name": "University of Azad Jammu and Kashmir", "acronym": "UAJK", "city": "Muzaffarabad"}
        ]

        print("Seeding Pakistan-wide universities...")
        for u in universities_data:
            existing = db.query(models.University).filter(
                models.University.name == u["name"],
                models.University.city == u["city"]
            ).first()
            if not existing:
                new_uni = models.University(
                    name=u["name"],
                    acronym=u["acronym"],
                    city=u["city"]
                )
                db.add(new_uni)
                db.commit()
        
        total = db.query(models.University).count()
        print(f"SUCCESS! Total universities across all Pakistan provinces: {total}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_pakistan_universities()
