import { useState, useEffect } from 'react';
import api from '../../services/api';
import DisputeChat from '../../components/DisputeChat';

export default function AdminDisputesPage() {
  const [disputes, setDisputes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDispute, setSelectedDispute] = useState(null);
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [resolveForm, setResolveForm] = useState({
    resolution_type: 'full_payment_freelancer',
    resolution_amount: '',
    resolution_notes: ''
  });

  const fetchDisputes = async () => {
    try {
      const response = await api.get('/disputes');
      setDisputes(response.data.disputes);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching disputes:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDisputes();
    const interval = setInterval(fetchDisputes, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleResolve = async (e) => {
    e.preventDefault();
    
    const payload = {
      resolution_type: resolveForm.resolution_type,
      resolution_notes: resolveForm.resolution_notes
    };

    if (resolveForm.resolution_type === 'partial_payment') {
      const amount = parseFloat(resolveForm.resolution_amount);
      if (!amount || amount <= 0) {
        alert('Please enter a valid amount for partial payment');
        return;
      }
      payload.resolution_amount = Math.round(amount * 100); // Convert to paise
    }

    try {
      await api.post(`/disputes/${selectedDispute}/resolve`, payload);
      alert('Dispute resolved successfully');
      setShowResolveModal(false);
      setSelectedDispute(null);
      fetchDisputes();
    } catch (error) {
      console.error('Error resolving dispute:', error);
      alert('Failed to resolve dispute: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleClose = async (disputeId) => {
    if (!confirm('Close this resolved dispute?')) return;

    try {
      await api.post(`/disputes/${disputeId}/close`);
      alert('Dispute closed successfully');
      fetchDisputes();
    } catch (error) {
      console.error('Error closing dispute:', error);
      alert('Failed to close dispute');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const pendingDisputes = disputes.filter(d => d.status === 'admin_mediation');
  const resolvedDisputes = disputes.filter(d => d.status === 'resolved' || d.status === 'closed');

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dispute Resolution</h1>

      {/* Pending Disputes */}
      <div className="mb-12">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">
          Pending Admin Mediation ({pendingDisputes.length})
        </h2>
        {pendingDisputes.length === 0 ? (
          <div className="bg-white border border-gray-200 rounded-lg p-8 text-center">
            <p className="text-gray-500">No disputes pending mediation</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {pendingDisputes.map((dispute) => (
              <div
                key={dispute.id}
                className="bg-white border border-orange-200 rounded-lg p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-semibold text-gray-900">
                        Dispute #{dispute.id.slice(0, 8)}
                      </h3>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                        Needs Admin Review
                      </span>
                    </div>
                    <p className="text-gray-600 mt-2 font-medium">{dispute.reason}</p>
                    <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                      <span>Raised by: {dispute.raised_by_role}</span>
                      <span>•</span>
                      <span>Created: {new Date(dispute.created_at).toLocaleDateString()}</span>
                      {dispute.escalated_at && (
                        <>
                          <span>•</span>
                          <span>Escalated: {new Date(dispute.escalated_at).toLocaleDateString()}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2 ml-4">
                    <button
                      type="button"
                      onClick={() => setSelectedDispute(dispute.id)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      View Chat
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedDispute(dispute.id);
                        setShowResolveModal(true);
                      }}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                    >
                      Resolve
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Resolved Disputes */}
      <div>
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">
          Resolved Disputes ({resolvedDisputes.length})
        </h2>
        {resolvedDisputes.length === 0 ? (
          <div className="bg-white border border-gray-200 rounded-lg p-8 text-center">
            <p className="text-gray-500">No resolved disputes</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {resolvedDisputes.map((dispute) => (
              <div
                key={dispute.id}
                className="bg-white border border-green-200 rounded-lg p-6"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-semibold text-gray-900">
                        Dispute #{dispute.id.slice(0, 8)}
                      </h3>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        {dispute.status}
                      </span>
                    </div>
                    <p className="text-gray-600 mt-2">{dispute.reason}</p>
                    <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                      <span>Resolved: {new Date(dispute.resolved_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div className="flex gap-2 ml-4">
                    <button
                      type="button"
                      onClick={() => setSelectedDispute(dispute.id)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      View Details
                    </button>
                    {dispute.status === 'resolved' && (
                      <button
                        type="button"
                        onClick={() => handleClose(dispute.id)}
                        className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                      >
                        Close
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Dispute Chat Modal */}
      {selectedDispute && !showResolveModal && (
        <DisputeChat
          disputeId={selectedDispute}
          onClose={() => {
            setSelectedDispute(null);
            fetchDisputes();
          }}
        />
      )}

      {/* Resolve Modal */}
      {showResolveModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Resolve Dispute</h2>
            
            <form onSubmit={handleResolve} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Resolution Type
                </label>
                <select
                  value={resolveForm.resolution_type}
                  onChange={(e) => setResolveForm({ ...resolveForm, resolution_type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="full_payment_freelancer">Full Payment to Freelancer</option>
                  <option value="partial_payment">Partial Payment</option>
                  <option value="full_refund_business">Full Refund to Business</option>
                </select>
              </div>

              {resolveForm.resolution_type === 'partial_payment' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Amount (₹)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={resolveForm.resolution_amount}
                    onChange={(e) => setResolveForm({ ...resolveForm, resolution_amount: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter amount to pay freelancer"
                    required
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Resolution Notes (Reasoning)
                </label>
                <textarea
                  value={resolveForm.resolution_notes}
                  onChange={(e) => setResolveForm({ ...resolveForm, resolution_notes: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={4}
                  placeholder="Explain your decision to both parties..."
                  required
                />
              </div>

              <div className="flex gap-3 justify-end">
                <button
                  type="button"
                  onClick={() => {
                    setShowResolveModal(false);
                    setSelectedDispute(null);
                  }}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Resolve Dispute
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
