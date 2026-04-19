import { useState, useEffect } from 'react';
import api from '../services/api';
import ReviewCard from './ReviewCard';

export default function ReviewList({ freelancerId, canRespond = false }) {
  const [reviews, setReviews] = useState([]);
  const [freelancerInfo, setFreelancerInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchReviews = async () => {
    try {
      const response = await api.get(`/reviews/freelancer/${freelancerId}`);
      setReviews(response.data.reviews);
      setFreelancerInfo({
        name: response.data.freelancer_name,
        average_rating: response.data.average_rating,
        review_count: response.data.review_count
      });
      setLoading(false);
    } catch (err) {
      console.error('Error fetching reviews:', err);
      setError('Failed to load reviews');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReviews();
  }, [freelancerId]);

  const renderStars = (rating) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            className={`text-2xl ${
              star <= Math.round(rating) ? 'text-yellow-400' : 'text-gray-300'
            }`}
          >
            ★
          </span>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary */}
      {freelancerInfo && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Reviews for {freelancerInfo.name}
          </h2>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              {renderStars(freelancerInfo.average_rating)}
              <span className="text-2xl font-bold text-gray-900">
                {freelancerInfo.average_rating.toFixed(1)}
              </span>
            </div>
            <span className="text-gray-600">
              ({freelancerInfo.review_count} {freelancerInfo.review_count === 1 ? 'review' : 'reviews'})
            </span>
          </div>
        </div>
      )}

      {/* Reviews */}
      {reviews.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded-lg p-8 text-center">
          <p className="text-gray-500">No reviews yet</p>
        </div>
      ) : (
        <div className="space-y-4">
          {reviews.map((review) => (
            <ReviewCard
              key={review.id}
              review={review}
              canRespond={canRespond}
              onResponseAdded={fetchReviews}
            />
          ))}
        </div>
      )}
    </div>
  );
}
