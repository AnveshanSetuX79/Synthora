import { useState, useEffect, useRef } from 'react';
import api from '../services/api';

export default function DisputeChat({ disputeId, onClose }) {
  const [dispute, setDispute] = useState(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchDispute = async () => {
    try {
      const response = await api.get(`/disputes/${disputeId}`);
      setDispute(response.data);
      setLoading(false);
      setTimeout(scrollToBottom, 100);
    } catch (error) {
      console.error('Error fetching dispute:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDispute();
    const interval = setInterval(fetchDispute, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, [disputeId]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    setSending(true);
    try {
      await api.post(`/disputes/${disputeId}/messages`, { message });
      setMessage('');
      await fetchDispute();
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message');
    } finally {
      setSending(false);
    }
  };

  const handleEscalate = async () => {
    if (!confirm('Escalate this dispute to admin mediation?')) return;

    try {
      await api.post(`/disputes/${disputeId}/escalate`);
      await fetchDispute();
      alert('Dispute escalated to admin mediation');
    } catch (error) {
      console.error('Error escalating dispute:', error);
      alert('Failed to escalate dispute');
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dispute...</p>
        </div>
      </div>
    );
  }

  if (!dispute) {
    return null;
  }

  const canEscalate = dispute.status === 'self_resolution';
  const isResolved = dispute.status === 'resolved' || dispute.status === 'closed';

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="p-6 border-b">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Dispute #{dispute.id.slice(0, 8)}</h2>
              <p className="text-sm text-gray-600 mt-1">
                Raised by {dispute.raised_by_role} • {new Date(dispute.created_at).toLocaleDateString()}
              </p>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Status Badge */}
          <div className="mt-4">
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
              dispute.status === 'self_resolution' ? 'bg-yellow-100 text-yellow-800' :
              dispute.status === 'admin_mediation' ? 'bg-orange-100 text-orange-800' :
              dispute.status === 'resolved' ? 'bg-green-100 text-green-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {dispute.status === 'self_resolution' ? '⏱️ Self-Resolution Period' :
               dispute.status === 'admin_mediation' ? '👨‍⚖️ Admin Mediation' :
               dispute.status === 'resolved' ? '✅ Resolved' :
               dispute.status}
            </span>
          </div>

          {/* Dispute Details */}
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm font-medium text-gray-700">Reason:</p>
            <p className="text-gray-900 mt-1">{dispute.reason}</p>
            {dispute.description && (
              <>
                <p className="text-sm font-medium text-gray-700 mt-3">Description:</p>
                <p className="text-gray-900 mt-1">{dispute.description}</p>
              </>
            )}
          </div>

          {/* Deadline */}
          {canEscalate && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                ⏰ Self-resolution deadline: {new Date(dispute.self_resolution_deadline).toLocaleString()}
              </p>
              <p className="text-xs text-yellow-700 mt-1">
                Both parties have until this time to resolve the dispute. After that, it will be escalated to admin mediation.
              </p>
            </div>
          )}

          {/* Resolution */}
          {isResolved && dispute.resolution_type && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm font-medium text-green-800">Resolution:</p>
              <p className="text-green-900 mt-1">
                {dispute.resolution_type === 'full_payment_freelancer' && '✅ Full payment released to freelancer'}
                {dispute.resolution_type === 'partial_payment' && `💰 Partial payment: ₹${dispute.resolution_amount / 100}`}
                {dispute.resolution_type === 'full_refund_business' && '↩️ Full refund issued to business'}
              </p>
              {dispute.resolution_notes && (
                <p className="text-sm text-green-700 mt-2">{dispute.resolution_notes}</p>
              )}
            </div>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {dispute.messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.is_system_message ? 'justify-center' : 'justify-start'}`}
            >
              {msg.is_system_message ? (
                <div className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-2 max-w-2xl">
                  <p className="text-sm text-blue-800 whitespace-pre-wrap">{msg.message}</p>
                  <p className="text-xs text-blue-600 mt-1">
                    {new Date(msg.created_at).toLocaleString()}
                  </p>
                </div>
              ) : (
                <div className="bg-gray-100 rounded-lg px-4 py-3 max-w-xl">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium text-gray-900">{msg.sender_name}</span>
                    <span className={`text-xs px-2 py-0.5 rounded ${
                      msg.sender_role === 'admin' ? 'bg-purple-100 text-purple-700' :
                      msg.sender_role === 'freelancer' ? 'bg-blue-100 text-blue-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {msg.sender_role}
                    </span>
                  </div>
                  <p className="text-gray-800 whitespace-pre-wrap">{msg.message}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(msg.created_at).toLocaleString()}
                  </p>
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        {!isResolved && (
          <div className="p-6 border-t bg-gray-50">
            <form onSubmit={handleSendMessage} className="flex gap-3">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={sending}
              />
              <button
                type="submit"
                disabled={sending || !message.trim()}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {sending ? 'Sending...' : 'Send'}
              </button>
              {canEscalate && (
                <button
                  type="button"
                  onClick={handleEscalate}
                  className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
                >
                  Escalate to Admin
                </button>
              )}
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
