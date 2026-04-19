import { useState } from 'react';
import api from '../services/api';

export default function ReviewCard({ review, canRespond = false, onResponseAdded }) {
  const [showResponseForm, setShowResponseForm] = useState(false);
  const [responseText, setResponseText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmitResponse = async (e) => {
    e.preventDefault();
    
    if (responseText.trim().length < 10) {
      setError('Response must be at least 10 characters');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await api.post(`/reviews/${review.id}/respond`, {
        response_text: responseText
      });
      
      setShowResponseForm(false);
      if (onResponseAdded) onResponseAdded();
    } catch (err) {
      console.error('Error submitting response:', err);
      setError(err.response?.data?.detail || 'Failed to submit response');
    } finally {
      setSubmitting(false);
    }
  };

  const renderStars = (rating) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            className={`text-xl ${
              star <= rating ? 'text-yellow-400' : 'text-gray-300'
            }`}
          >
            ★
          </span>
        ))}
      </div>
    );
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h3 className="font-semibold text-gray-900">{review.business_owner_name}</h3>
            {review.package_type && (
              <span className="text-sm px-2 py-1 bg-blue-100 text-blue-700 rounded">
                {review.package_type}
              </span>
            )}
          </div>
          {renderStars(review.rating)}
        </div>
        <div className="text-right text-sm text-gray-500">
          {new Date(review.created_at).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
          })}
        </div>
      </div>

      {/* Review Text */}
      <p className="text-gray-700 mb-4 whitespace-pre-wrap">{review.review_text}</p>

      {/* Freelancer Response */}
      {review.response_text && (
        <div className="mt-4 pl-4 border-l-4 border-blue-200 bg-blue-50 p-4 rounded">
          <p className="text-sm font-medium text-blue-900 mb-2">Freelancer Response:</p>
          <p className="text-gray-700 whitespace-pre-wrap">{review.response_text}</p>
          <p className="text-xs text-gray-500 mt-2">
            Responded on {new Date(review.responded_at).toLocaleDateString()}
          </p>
        </div>
      )}

      {/* Response Form */}
      {canRespond && !review.response_text && !showResponseForm && (
        <button
          type="button"
          onClick={() => setShowResponseForm(true)}
          className="mt-4 text-blue-600 hover:text-blue-700 text-sm font-medium"
        >
          Respond to this review
        </button>
      )}

      {showResponseForm && (
        <form onSubmit={handleSubmitResponse} className="mt-4 space-y-3">
          <textarea
            value={responseText}
            onChange={(e) => setResponseText(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={4}
            placeholder="Write your response (minimum 10 characters)..."
            required
          />
          {error && (
            <p className="text-sm text-red-600">{error}</p>
          )}
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={submitting || responseText.trim().length < 10}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-sm"
            >
              {submitting ? 'Submitting...' : 'Submit Response'}
            </button>
            <button
              type="button"
              onClick={() => {
                setShowResponseForm(false);
                setResponseText('');
                setError(null);
              }}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm"
              disabled={submitting}
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
