"""Backfill AI enrichment data for existing leads.

This script adds AI enrichment data to businesses that were discovered
before the AI enrichment feature was implemented.
"""
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine
from sqlalchemy import text
from app.services.ai_enrichment import ai_enrichment_service
from datetime import datetime


def backfill_ai_enrichment():
    """Add AI enrichment to existing business insights."""
    db = SessionLocal()
    
    try:
        print("🤖 Backfilling AI enrichment data...")
        
        # Get all business insights without AI enrichment
        result = db.execute(text("""
            SELECT 
                bi.id,
                bi.business_id,
                b.name,
                b.category,
                b.address,
                b.city,
                b.phone,
                bi.rating,
                bi.review_count,
                bi.has_website,
                bi.website_url
            FROM business_insights bi
            JOIN businesses b ON bi.business_id = b.id
            WHERE bi.ai_description IS NULL
            ORDER BY bi.created_at DESC
            LIMIT 50
        """))
        
        insights_to_enrich = result.fetchall()
        
        if not insights_to_enrich:
            print("✅ All business insights already have AI enrichment!")
            return
        
        print(f"Found {len(insights_to_enrich)} businesses to enrich")
        
        enriched_count = 0
        
        for insight in insights_to_enrich:
            (insight_id, business_id, name, category, address, city, phone,
             rating, review_count, has_website, website_url) = insight
            
            print(f"\n📍 Enriching: {name} ({category})")
            
            try:
                # Generate AI enrichment
                ai_data = ai_enrichment_service.enrich_business_data(
                    business_name=name,
                    category=category,
                    address=address,
                    city=city,
                    rating=rating,
                    review_count=review_count,
                    has_website=has_website,
                    website_url=website_url,
                    phone=phone
                )
                
                # Get pitch suggestions
                pitch_suggestions = ai_enrichment_service.get_pitch_suggestions(ai_data)
                
                # Update database with JSON-encoded data
                db.execute(text("""
                    UPDATE business_insights
                    SET 
                        ai_description = :description,
                        ai_specialties = CAST(:specialties AS jsonb),
                        ai_target_customers = CAST(:target_customers AS jsonb),
                        ai_pain_points = CAST(:pain_points AS jsonb),
                        ai_recommended_solutions = CAST(:recommended_solutions AS jsonb),
                        ai_competitive_advantages = CAST(:competitive_advantages AS jsonb),
                        ai_digital_maturity = :digital_maturity,
                        ai_growth_potential = :growth_potential,
                        ai_estimated_size = :estimated_size,
                        ai_online_presence_score = :online_presence_score,
                        ai_urgency_score = :urgency_score,
                        ai_enrichment_confidence = :enrichment_confidence,
                        ai_enriched_at = :enriched_at,
                        ai_pitch_suggestions = CAST(:pitch_suggestions AS jsonb)
                    WHERE id = :insight_id
                """), {
                    "insight_id": insight_id,
                    "description": ai_data.get("business_description"),
                    "specialties": json.dumps(ai_data.get("specialties", [])),
                    "target_customers": json.dumps(ai_data.get("target_customers", [])),
                    "pain_points": json.dumps(ai_data.get("pain_points", [])),
                    "recommended_solutions": json.dumps(ai_data.get("recommended_solutions", [])),
                    "competitive_advantages": json.dumps(ai_data.get("competitive_advantages", [])),
                    "digital_maturity": ai_data.get("digital_maturity"),
                    "growth_potential": ai_data.get("growth_potential"),
                    "estimated_size": ai_data.get("estimated_size"),
                    "online_presence_score": ai_data.get("online_presence_score"),
                    "urgency_score": ai_data.get("urgency_score"),
                    "enrichment_confidence": ai_data.get("enrichment_confidence"),
                    "enriched_at": datetime.utcnow(),
                    "pitch_suggestions": json.dumps(pitch_suggestions)
                })
                
                # Commit after each update
                db.commit()
                
                enriched_count += 1
                print(f"   ✅ Enriched with {len(ai_data.get('specialties', []))} specialties")
                print(f"   📊 Scores: Digital={ai_data.get('digital_maturity')}, Growth={ai_data.get('growth_potential')}")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                db.rollback()
                continue
        
        print(f"\n✅ Successfully enriched {enriched_count} businesses!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("BACKFILL AI ENRICHMENT DATA")
    print("=" * 60)
    
    backfill_ai_enrichment()
    
    print("\n" + "=" * 60)
    print("DONE - Restart your backend to see the changes!")
    print("=" * 60)
