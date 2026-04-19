import { useState, useEffect } from 'react';
import api from '../services/api';
import DisputeChat from './DisputeChat';

export default function DisputeList({ userRole = 'freelancer' }) {
  const [disputes, setDisputes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDispute, setSelectedDispute] = useState(null);
  const [filter, setFilter] = useState('all');

  const fetchDisputes = async () => {
    try {
      const params = filter !== 'all' ? { status: filter } : {};
      const response = await api.get('/disputes', { params });
      setDisputes(response.data.disputes);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching disputes:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDisputes();
    const interval = setInterval(fetchDisputes, 10000); // Poll every 10 seconds
    return () => clearInterval(interval);
  }, [filter]);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filter */}
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg ${
            filter === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All
        </button>
        <button
          type="button"
          onClick={() => setFilter('self_resolution')}
          className={`px-4 py-2 rounded-lg ${
            filter === 'self_resolution'
              ? 'bg-yellow-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Self-Resolution
        </button>
        <button
          type="button"
          onClick={() => setFilter('admin_mediation')}
          className={`px-4 py-2 rounded-lg ${
            filter === 'admin_mediation'
              ? 'bg-orange-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Admin Mediation
        </button>
        <button
          type="button"
          onClick={() => setFilter('resolved')}
          className={`px-4 py-2 rounded-lg ${
            filter === 'resolved'
              ? 'bg-green-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Resolved
        </button>
      </div>

      {/* Disputes List */}
      {disputes.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No disputes found</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {disputes.map((dispute) => (
            <div
              key={dispute.id}
              className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => setSelectedDispute(dispute.id)}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold text-gray-900">
                      Dispute #{dispute.id.slice(0, 8)}
                    </h3>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      dispute.status === 'self_resolution' ? 'bg-yellow-100 text-yellow-800' :
                      dispute.status === 'admin_mediation' ? 'bg-orange-100 text-orange-800' :
                      dispute.status === 'resolved' ? 'bg-green-100 text-green-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {dispute.status.replace('_', ' ')}
                    </span>
                  </div>
                  <p className="text-gray-600 mt-2">{dispute.reason}</p>
                  <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                    <span>Raised by: {dispute.raised_by_role}</span>
                    <span>•</span>
                    <span>{new Date(dispute.created_at).toLocaleDateString()}</span>
                  </div>
                  {dispute.status === 'self_resolution' && dispute.self_resolution_deadline && (
                    <p className="text-sm text-yellow-700 mt-2">
                      ⏰ Deadline: {new Date(dispute.self_resolution_deadline).toLocaleString()}
                    </p>
                  )}
                </div>
                <button
                  type="button"
                  className="ml-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Dispute Chat Modal */}
      {selectedDispute && (
        <DisputeChat
          disputeId={selectedDispute}
          onClose={() => {
            setSelectedDispute(null);
            fetchDisputes();
          }}
        />
      )}
    </div>
  );
}
