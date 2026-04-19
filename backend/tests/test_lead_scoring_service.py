"""Unit tests for lead scoring service.

Tests cover:
- Digital score calculation
- Rating score component (0-30 points)
- Review score component (0-25 points)
- Website score component (0 or 30 points)
- Category score component (0-15 points)
- Opportunity tag classification
- Score determinism
- Edge cases and boundary conditions
"""
import pytest
from backend.app.services.lead_scoring import (
    LeadScoringService,
    OpportunityTag,
    CategoryPriority,
    CATEGORY_SCORES
)


class TestDigitalScoreCalculation:
    """Test overall digital score calculation."""
    
    def test_perfect_score_no_website(self):
        """Should calculate maximum score for business without website."""
        # 5-star rating (30) + 100+ reviews (25) + no website (30) + restaurant (15) = 100
        result = LeadScoringService.calculate_digital_score(
            rating=5.0,
            review_count=150,
            has_website=False,
            category="Restaurant"
        )
        
        assert result["score"] == 100
        assert result["opportunity_tag"] == OpportunityTag.HIGH.value
        assert result["breakdown"]["rating"] == 30
        assert result["breakdown"]["reviews"] == 25
        assert result["breakdown"]["no_website"] == 30
        assert result["breakdown"]["category_priority"] == 15
    
    def test_minimum_score(self):
        """Should calculate minimum score for business with website and no data."""
        # 0 rating (0) + 0 reviews (0) + has website (0) + other category (5) = 5
        result = LeadScoringService.calculate_digital_score(
            rating=None,
            review_count=0,
            has_website=True,
            category="Unknown"
        )
        
        assert result["score"] == 5
        assert result["opportunity_tag"] == OpportunityTag.LOW.value
    
    def test_mid_range_score(self):
        """Should calculate mid-range score correctly."""
        # 3.5 rating (21) + 30 reviews (15) + no website (30) + cafe (12) = 78
        result = LeadScoringService.calculate_digital_score(
            rating=3.5,
            review_count=30,
            has_website=False,
            category="Cafe"
        )
        
        assert result["score"] == 78
        assert result["opportunity_tag"] == OpportunityTag.MEDIUM.value
    
    def test_score_with_website(self):
        """Should not give bonus points for businesses with websites."""
        result = LeadScoringService.calculate_digital_score(
            rating=4.5,
            review_count=100,
            has_website=True,
            category="Restaurant"
        )
        
        # 27 (rating) + 20 (100 reviews) + 0 (has website) + 15 (restaurant) = 62
        assert result["score"] == 62
        assert result["breakdown"]["no_website"] == 0
    
    def test_score_breakdown_structure(self):
        """Should return properly structured breakdown."""
        result = LeadScoringService.calculate_digital_score(
            rating=4.0,
            review_count=50,
            has_website=False,
            category="Restaurant"
        )
        
        assert "score" in result
        assert "breakdown" in result
        assert "opportunity_tag" in result
        assert "rating" in result["breakdown"]
        assert "reviews" in result["breakdown"]
        assert "no_website" in result["breakdown"]
        assert "category_priority" in result["breakdown"]


class TestRatingScore:
    """Test rating score calculation (0-30 points)."""
    
    def test_five_star_rating(self):
        """Should give 30 points for 5-star rating."""
        score = LeadScoringService._calculate_rating_score(5.0)
        assert score == 30
    
    def test_zero_rating(self):
        """Should give 0 points for 0 rating."""
        score = LeadScoringService._calculate_rating_score(0.0)
        assert score == 0
    
    def test_none_rating(self):
        """Should give 0 points for None rating."""
        score = LeadScoringService._calculate_rating_score(None)
        assert score == 0
    
    def test_mid_rating(self):
        """Should calculate proportional score for mid-range ratings."""
        # 3.0 rating = (3/5) * 30 = 18
        score = LeadScoringService._calculate_rating_score(3.0)
        assert score == 18
    
    def test_decimal_rating(self):
        """Should handle decimal ratings correctly."""
        # 4.5 rating = (4.5/5) * 30 = 27
        score = LeadScoringService._calculate_rating_score(4.5)
        assert score == 27
    
    def test_rating_linear_scale(self):
        """Should use linear scale for rating scores."""
        # Test multiple points on the scale
        assert LeadScoringService._calculate_rating_score(1.0) == 6
        assert LeadScoringService._calculate_rating_score(2.0) == 12
        assert LeadScoringService._calculate_rating_score(3.0) == 18
        assert LeadScoringService._calculate_rating_score(4.0) == 24
        assert LeadScoringService._calculate_rating_score(5.0) == 30


class TestReviewScore:
    """Test review score calculation (0-25 points)."""
    
    def test_zero_reviews(self):
        """Should give 0 points for 0 reviews."""
        score = LeadScoringService._calculate_review_score(0)
        assert score == 0
    
    def test_few_reviews(self):
        """Should give 5 points for 1-10 reviews."""
        assert LeadScoringService._calculate_review_score(1) == 5
        assert LeadScoringService._calculate_review_score(5) == 5
        assert LeadScoringService._calculate_review_score(10) == 5
    
    def test_low_reviews(self):
        """Should give 10 points for 11-25 reviews."""
        assert LeadScoringService._calculate_review_score(11) == 10
        assert LeadScoringService._calculate_review_score(20) == 10
        assert LeadScoringService._calculate_review_score(25) == 10
    
    def test_medium_reviews(self):
        """Should give 15 points for 26-50 reviews."""
        assert LeadScoringService._calculate_review_score(26) == 15
        assert LeadScoringService._calculate_review_score(40) == 15
        assert LeadScoringService._calculate_review_score(50) == 15
    
    def test_high_reviews(self):
        """Should give 20 points for 51-100 reviews."""
        assert LeadScoringService._calculate_review_score(51) == 20
        assert LeadScoringService._calculate_review_score(75) == 20
        assert LeadScoringService._calculate_review_score(100) == 20
    
    def test_very_high_reviews(self):
        """Should give 25 points for 100+ reviews."""
        assert LeadScoringService._calculate_review_score(101) == 25
        assert LeadScoringService._calculate_review_score(500) == 25
        assert LeadScoringService._calculate_review_score(1000) == 25
    
    def test_negative_reviews(self):
        """Should handle negative review counts as 0."""
        score = LeadScoringService._calculate_review_score(-5)
        assert score == 0


class TestWebsiteScore:
    """Test website score calculation (0 or 30 points)."""
    
    def test_no_website_bonus(self):
        """Should give 30 points bonus for no website."""
        score = LeadScoringService._calculate_website_score(False)
        assert score == 30
    
    def test_has_website_no_bonus(self):
        """Should give 0 points if business has website."""
        score = LeadScoringService._calculate_website_score(True)
        assert score == 0


class TestCategoryScore:
    """Test category score calculation (0-15 points)."""
    
    def test_restaurant_category(self):
        """Should give 15 points for restaurant (highest priority)."""
        score = LeadScoringService._calculate_category_score("Restaurant")
        assert score == 15
    
    def test_cafe_category(self):
        """Should give 12 points for cafe."""
        score = LeadScoringService._calculate_category_score("Cafe")
        assert score == 12
    
    def test_salon_category(self):
        """Should give 10 points for salon."""
        score = LeadScoringService._calculate_category_score("Salon")
        assert score == 10
    
    def test_gym_category(self):
        """Should give 10 points for gym."""
        score = LeadScoringService._calculate_category_score("Gym")
        assert score == 10
    
    def test_school_category(self):
        """Should give 8 points for school."""
        score = LeadScoringService._calculate_category_score("School")
        assert score == 8
    
    def test_unknown_category(self):
        """Should give 5 points for unknown categories."""
        score = LeadScoringService._calculate_category_score("Unknown")
        assert score == 5
    
    def test_case_insensitive_category(self):
        """Should handle case-insensitive category matching."""
        assert LeadScoringService._calculate_category_score("restaurant") == 15
        assert LeadScoringService._calculate_category_score("RESTAURANT") == 15
        assert LeadScoringService._calculate_category_score("ReStAuRaNt") == 15
    
    def test_category_with_whitespace(self):
        """Should handle categories with whitespace."""
        score = LeadScoringService._calculate_category_score("  Restaurant  ")
        assert score == 15


class TestOpportunityClassification:
    """Test opportunity tag classification."""
    
    def test_high_opportunity_threshold(self):
        """Should classify 80+ as High opportunity."""
        assert LeadScoringService._classify_opportunity(80) == OpportunityTag.HIGH
        assert LeadScoringService._classify_opportunity(90) == OpportunityTag.HIGH
        assert LeadScoringService._classify_opportunity(100) == OpportunityTag.HIGH
    
    def test_medium_opportunity_threshold(self):
        """Should classify 50-79 as Medium opportunity."""
        assert LeadScoringService._classify_opportunity(50) == OpportunityTag.MEDIUM
        assert LeadScoringService._classify_opportunity(65) == OpportunityTag.MEDIUM
        assert LeadScoringService._classify_opportunity(79) == OpportunityTag.MEDIUM
    
    def test_low_opportunity_threshold(self):
        """Should classify 0-49 as Low opportunity."""
        assert LeadScoringService._classify_opportunity(0) == OpportunityTag.LOW
        assert LeadScoringService._classify_opportunity(25) == OpportunityTag.LOW
        assert LeadScoringService._classify_opportunity(49) == OpportunityTag.LOW
    
    def test_boundary_values(self):
        """Should correctly classify boundary values."""
        assert LeadScoringService._classify_opportunity(49) == OpportunityTag.LOW
        assert LeadScoringService._classify_opportunity(50) == OpportunityTag.MEDIUM
        assert LeadScoringService._classify_opportunity(79) == OpportunityTag.MEDIUM
        assert LeadScoringService._classify_opportunity(80) == OpportunityTag.HIGH


class TestScoreDeterminism:
    """Test that scoring is deterministic."""
    
    def test_same_inputs_same_output(self):
        """Should produce identical results for identical inputs."""
        inputs = {
            "rating": 4.2,
            "review_count": 75,
            "has_website": False,
            "category": "Restaurant"
        }
        
        result1 = LeadScoringService.calculate_digital_score(**inputs)
        result2 = LeadScoringService.calculate_digital_score(**inputs)
        result3 = LeadScoringService.calculate_digital_score(**inputs)
        
        assert result1["score"] == result2["score"] == result3["score"]
        assert result1["breakdown"] == result2["breakdown"] == result3["breakdown"]
        assert result1["opportunity_tag"] == result2["opportunity_tag"] == result3["opportunity_tag"]
    
    def test_multiple_scenarios_deterministic(self):
        """Should be deterministic across multiple scenarios."""
        scenarios = [
            {"rating": 5.0, "review_count": 200, "has_website": False, "category": "Restaurant"},
            {"rating": 3.0, "review_count": 10, "has_website": True, "category": "School"},
            {"rating": None, "review_count": 0, "has_website": False, "category": "Cafe"},
            {"rating": 4.5, "review_count": 50, "has_website": False, "category": "Gym"},
        ]
        
        for scenario in scenarios:
            result1 = LeadScoringService.calculate_digital_score(**scenario)
            result2 = LeadScoringService.calculate_digital_score(**scenario)
            assert result1 == result2


class TestScoreBounds:
    """Test that scores stay within valid bounds."""
    
    def test_score_never_exceeds_100(self):
        """Should cap score at 100."""
        # Even with maximum values, score should not exceed 100
        result = LeadScoringService.calculate_digital_score(
            rating=5.0,
            review_count=1000,
            has_website=False,
            category="Restaurant"
        )
        assert result["score"] <= 100
    
    def test_score_never_below_0(self):
        """Should never return negative score."""
        result = LeadScoringService.calculate_digital_score(
            rating=None,
            review_count=0,
            has_website=True,
            category="Unknown"
        )
        assert result["score"] >= 0
    
    def test_component_scores_within_bounds(self):
        """Should keep all component scores within their max values."""
        result = LeadScoringService.calculate_digital_score(
            rating=5.0,
            review_count=1000,
            has_website=False,
            category="Restaurant"
        )
        
        assert result["breakdown"]["rating"] <= 30
        assert result["breakdown"]["reviews"] <= 25
        assert result["breakdown"]["no_website"] <= 30
        assert result["breakdown"]["category_priority"] <= 15


class TestRequirementValidation:
    """Test that requirements are met."""
    
    def test_no_website_score_below_40(self):
        """Requirement 3.5: Business with no website should score below 40 if other factors are low."""
        # Minimum other factors: 0 rating + 0 reviews + 5 category = 5
        # With no website bonus: 5 + 30 = 35 (below 40)
        result = LeadScoringService.calculate_digital_score(
            rating=None,
            review_count=0,
            has_website=False,
            category="Unknown"
        )
        assert result["score"] < 40
    
    def test_score_range_0_to_100(self):
        """Requirement 3.1: Score should be between 0 and 100."""
        test_cases = [
            {"rating": None, "review_count": 0, "has_website": True, "category": "Unknown"},
            {"rating": 5.0, "review_count": 1000, "has_website": False, "category": "Restaurant"},
            {"rating": 2.5, "review_count": 50, "has_website": False, "category": "Cafe"},
        ]
        
        for case in test_cases:
            result = LeadScoringService.calculate_digital_score(**case)
            assert 0 <= result["score"] <= 100
    
    def test_considers_website_presence(self):
        """Requirement 3.2: Should consider website presence."""
        result_no_website = LeadScoringService.calculate_digital_score(
            rating=4.0,
            review_count=50,
            has_website=False,
            category="Restaurant"
        )
        
        result_with_website = LeadScoringService.calculate_digital_score(
            rating=4.0,
            review_count=50,
            has_website=True,
            category="Restaurant"
        )
        
        # Scores should differ by 30 points (website bonus)
        assert result_no_website["score"] - result_with_website["score"] == 30
    
    def test_considers_review_count(self):
        """Requirement 3.3: Should consider review count."""
        result_no_reviews = LeadScoringService.calculate_digital_score(
            rating=4.0,
            review_count=0,
            has_website=False,
            category="Restaurant"
        )
        
        result_many_reviews = LeadScoringService.calculate_digital_score(
            rating=4.0,
            review_count=150,
            has_website=False,
            category="Restaurant"
        )
        
        # Score with more reviews should be higher
        assert result_many_reviews["score"] > result_no_reviews["score"]
    
    def test_breakdown_shows_contributing_factors(self):
        """Requirement 3.6: Should display breakdown of contributing factors."""
        result = LeadScoringService.calculate_digital_score(
            rating=4.0,
            review_count=50,
            has_website=False,
            category="Restaurant"
        )
        
        breakdown = result["breakdown"]
        assert "rating" in breakdown
        assert "reviews" in breakdown
        assert "no_website" in breakdown
        assert "category_priority" in breakdown
        
        # Breakdown should sum to total score
        total = sum(breakdown.values())
        assert total == result["score"]
    
    def test_opportunity_tag_assignment(self):
        """Requirement 3.7: Should assign opportunity tag based on score."""
        high_score = LeadScoringService.calculate_digital_score(
            rating=5.0, review_count=150, has_website=False, category="Restaurant"
        )
        assert high_score["opportunity_tag"] == "High"
        
        medium_score = LeadScoringService.calculate_digital_score(
            rating=3.5, review_count=30, has_website=False, category="Cafe"
        )
        assert medium_score["opportunity_tag"] == "Medium"
        
        low_score = LeadScoringService.calculate_digital_score(
            rating=2.0, review_count=5, has_website=True, category="Unknown"
        )
        assert low_score["opportunity_tag"] == "Low"
