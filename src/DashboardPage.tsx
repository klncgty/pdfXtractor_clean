import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  User, 
  CreditCard, 
  FileText, 
  Key, 
  Settings, 
  Coffee,
  ExternalLink,
  Copy,
  Trash2,
  Plus,
  CheckCircle,
  XCircle
} from 'lucide-react';
import axios from 'axios';
import octoLogo from './octo.png';
import { UserDropdown } from './App';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface UserData {
  id: number;
  name: string;
  email: string;
  pages_processed_this_month: number;
  monthly_page_limit: number;
}

interface SubscriptionData {
  has_subscription: boolean;
  plan_type: string;
  status: string;
  monthly_page_limit: number;
  current_period_end?: string;
  cancel_at_period_end: boolean;
}

interface APIKey {
  id: number;
  name: string;
  api_key: string;
  is_active: boolean;
  created_at: string;
  last_used?: string;
  requests_made_this_month: number;
  monthly_request_limit: number;
}

export const DashboardPage = () => {
  const [userData, setUserData] = useState<UserData | null>(null);
  const [subscriptionData, setSubscriptionData] = useState<SubscriptionData | null>(null);
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateKey, setShowCreateKey] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [creatingKey, setCreatingKey] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [userResponse, subscriptionResponse, apiKeysResponse] = await Promise.all([
        axios.get(`${API_URL}/auth/me`, { withCredentials: true }),
        axios.get(`${API_URL}/stripe/subscription-status`, { withCredentials: true }),
        axios.get(`${API_URL}/auth/api-keys`, { withCredentials: true })
      ]);

      setUserData(userResponse.data);
      setSubscriptionData(subscriptionResponse.data);
      setApiKeys(apiKeysResponse.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleManageSubscription = async () => {
    try {
      const response = await axios.post(`${API_URL}/stripe/create-portal-session`, {}, {
        withCredentials: true
      });
      window.open(response.data.portal_url, '_blank');
    } catch (error) {
      console.error('Failed to create portal session:', error);
      alert('Failed to open subscription management. Please try again.');
    }
  };

  const handleCreateAPIKey = async () => {
    if (!newKeyName.trim()) return;
    
    setCreatingKey(true);
    try {
      const response = await axios.post(
        `${API_URL}/auth/api-keys?name=${encodeURIComponent(newKeyName)}`,
        {},
        { withCredentials: true }
      );
      
      setApiKeys([...apiKeys, response.data]);
      setNewKeyName('');
      setShowCreateKey(false);
    } catch (error) {
      console.error('Failed to create API key:', error);
      alert('Failed to create API key. Please try again.');
    } finally {
      setCreatingKey(false);
    }
  };

  const handleDeleteAPIKey = async (keyId: number) => {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      return;
    }

    try {
      await axios.delete(`${API_URL}/auth/api-keys/${keyId}`, {
        withCredentials: true
      });
      
      setApiKeys(apiKeys.filter(key => key.id !== keyId));
    } catch (error) {
      console.error('Failed to delete API key:', error);
      alert('Failed to delete API key. Please try again.');
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // You could add a toast notification here
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 border-4 border-t-transparent border-white rounded-full animate-spin" />
          <div className="text-white">Loading dashboard...</div>
        </div>
      </div>
    );
  }

  const usagePercentage = userData ? (userData.pages_processed_this_month / userData.monthly_page_limit) * 100 : 0;

  return (
    <div className="min-h-screen bg-black">
      <nav className="border-b border-white/10 bg-black/20 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center">
              <img src={octoLogo} alt="Octro Logo" className="w-8 h-8" />
              <span className="ml-2 text-xl font-bold text-white">OCTRO</span>
            </Link>
            <div className="flex items-center gap-6">
              <a
                href="https://buymeacoffee.com/cgtyklnc1t"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-300 hover:text-amber-400 transition-colors flex items-center gap-2"
              >
                <Coffee className="w-5 h-5" />
                <span>Support❤️</span>
              </a>
              <a
                href="/api-docs"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-300 hover:text-white transition-colors flex items-center gap-2"
              >
                <FileText className="w-4 h-4" />
                API Docs
              </a>
              <UserDropdown />
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
          <p className="text-gray-400">Manage your account, subscription, and API keys</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Account Overview */}
          <div className="lg:col-span-2 space-y-6">
            {/* Usage Stats */}
            <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10">
              <div className="flex items-center gap-3 mb-4">
                <FileText className="w-6 h-6 text-blue-500" />
                <h2 className="text-xl font-semibold text-white">Usage This Month</h2>
              </div>
              
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Pages Processed</span>
                  <span className="text-white font-medium">
                    {userData?.pages_processed_this_month || 0} / {userData?.monthly_page_limit || 30}
                  </span>
                </div>
                
                <div className="w-full bg-gray-700 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${Math.min(usagePercentage, 100)}%` }}
                  />
                </div>
                
                <div className="text-sm text-gray-400">
                  {usagePercentage >= 100 ? (
                    <span className="text-red-400">Quota exceeded</span>
                  ) : usagePercentage >= 80 ? (
                    <span className="text-yellow-400">Quota almost full</span>
                  ) : (
                    <span>{(100 - usagePercentage).toFixed(1)}% remaining</span>
                  )}
                </div>
              </div>
            </div>

            {/* API Keys Management */}
            <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <Key className="w-6 h-6 text-green-500" />
                  <h2 className="text-xl font-semibold text-white">API Keys</h2>
                </div>
                <button
                  onClick={() => setShowCreateKey(true)}
                  className="flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  Create Key
                </button>
              </div>

              {showCreateKey && (
                <div className="mb-4 p-4 bg-white/5 rounded-lg border border-white/10">
                  <div className="flex gap-3">
                    <input
                      type="text"
                      placeholder="API Key Name (e.g., My App Integration)"
                      value={newKeyName}
                      onChange={(e) => setNewKeyName(e.target.value)}
                      className="flex-1 bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                    />
                    <button
                      onClick={handleCreateAPIKey}
                      disabled={creatingKey || !newKeyName.trim()}
                      className="bg-green-500 hover:bg-green-600 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors"
                    >
                      {creatingKey ? 'Creating...' : 'Create'}
                    </button>
                    <button
                      onClick={() => {
                        setShowCreateKey(false);
                        setNewKeyName('');
                      }}
                      className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              <div className="space-y-3">
                {apiKeys.length === 0 ? (
                  <p className="text-gray-400 text-center py-4">No API keys created yet</p>
                ) : (
                  apiKeys.map((key) => (
                    <div key={key.id} className="bg-white/5 rounded-lg p-4 border border-white/10">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <span className="text-white font-medium">{key.name}</span>
                          {key.is_active ? (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          ) : (
                            <XCircle className="w-4 h-4 text-red-500" />
                          )}
                        </div>
                        <button
                          onClick={() => handleDeleteAPIKey(key.id)}
                          className="text-red-400 hover:text-red-300 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      
                      <div className="flex items-center gap-2 mb-2">
                        <code className="bg-black/50 px-2 py-1 rounded text-sm text-gray-300 flex-1">
                          {key.api_key}
                        </code>
                        <button
                          onClick={() => copyToClipboard(key.api_key)}
                          className="text-blue-400 hover:text-blue-300 transition-colors"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                      
                      <div className="text-xs text-gray-400 space-y-1">
                        <div>Usage: {key.requests_made_this_month} / {key.monthly_request_limit} requests</div>
                        <div>Created: {new Date(key.created_at).toLocaleDateString()}</div>
                        {key.last_used && (
                          <div>Last used: {new Date(key.last_used).toLocaleDateString()}</div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Account Info */}
            <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10">
              <div className="flex items-center gap-3 mb-4">
                <User className="w-6 h-6 text-purple-500" />
                <h2 className="text-xl font-semibold text-white">Account</h2>
              </div>
              
              <div className="space-y-3">
                <div>
                  <label className="text-gray-400 text-sm">Name</label>
                  <p className="text-white">{userData?.name || 'Not provided'}</p>
                </div>
                <div>
                  <label className="text-gray-400 text-sm">Email</label>
                  <p className="text-white">{userData?.email}</p>
                </div>
              </div>
            </div>

            {/* Subscription Info */}
            <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10">
              <div className="flex items-center gap-3 mb-4">
                <CreditCard className="w-6 h-6 text-yellow-500" />
                <h2 className="text-xl font-semibold text-white">Subscription</h2>
              </div>
              
              <div className="space-y-3">
                <div>
                  <label className="text-gray-400 text-sm">Current Plan</label>
                  <p className="text-white font-medium capitalize">
                    {subscriptionData?.plan_type || 'Free'}
                  </p>
                </div>
                
                <div>
                  <label className="text-gray-400 text-sm">Status</label>
                  <p className={`font-medium capitalize ${
                    subscriptionData?.status === 'active' ? 'text-green-400' : 
                    subscriptionData?.status === 'past_due' ? 'text-red-400' : 
                    'text-gray-400'
                  }`}>
                    {subscriptionData?.status || 'Inactive'}
                  </p>
                </div>

                {subscriptionData?.current_period_end && (
                  <div>
                    <label className="text-gray-400 text-sm">
                      {subscriptionData.cancel_at_period_end ? 'Expires' : 'Next Billing'}
                    </label>
                    <p className="text-white">
                      {new Date(subscriptionData.current_period_end).toLocaleDateString()}
                    </p>
                  </div>
                )}

                <div className="pt-3 space-y-2">
                  {subscriptionData?.has_subscription ? (
                    <button
                      onClick={handleManageSubscription}
                      className="w-full flex items-center justify-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
                    >
                      <Settings className="w-4 h-4" />
                      Manage Subscription
                    </button>
                  ) : (
                    <Link
                      to="/pricing"
                      className="w-full flex items-center justify-center gap-2 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors"
                    >
                      <CreditCard className="w-4 h-4" />
                      Upgrade Plan
                    </Link>
                  )}
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10">
              <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
              
              <div className="space-y-3">
                <Link
                  to="/process"
                  className="w-full flex items-center gap-3 text-white hover:text-blue-400 transition-colors"
                >
                  <FileText className="w-5 h-5" />
                  Process New PDF
                </Link>
                
                <a
                  href="/api-docs"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full flex items-center gap-3 text-white hover:text-blue-400 transition-colors"
                >
                  <ExternalLink className="w-5 h-5" />
                  API Documentation
                </a>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;