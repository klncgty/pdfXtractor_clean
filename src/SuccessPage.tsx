import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { CheckCircle, ArrowRight, Coffee } from 'lucide-react';
import axios from 'axios';
import octoLogo from './octo.png';
import { UserDropdown } from './App';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const SuccessPage = () => {
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [subscriptionData, setSubscriptionData] = useState<any>(null);
  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    const fetchSubscriptionStatus = async () => {
      try {
        const response = await axios.get(`${API_URL}/stripe/subscription-status`, {
          withCredentials: true
        });
        setSubscriptionData(response.data);
      } catch (error) {
        console.error('Failed to fetch subscription status:', error);
      } finally {
        setLoading(false);
      }
    };

    if (sessionId) {
      // Stripe checkout tamamlandı, subscription durumunu kontrol et
      setTimeout(fetchSubscriptionStatus, 2000); // 2 saniye bekle webhook'un işlenmesi için
    } else {
      setLoading(false);
    }
  }, [sessionId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 border-4 border-t-transparent border-white rounded-full animate-spin" />
          <div className="text-white">Processing your subscription...</div>
        </div>
      </div>
    );
  }

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
                href="https://github.com/klncgty"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-300 hover:text-white transition-colors"
              >
                GitHub
              </a>
              <UserDropdown />
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <div className="flex justify-center mb-8">
            <CheckCircle className="w-24 h-24 text-green-500" />
          </div>
          
          <h1 className="text-4xl sm:text-5xl font-bold text-white mb-6">
            Welcome to Octro {subscriptionData?.plan_type === 'standard' ? 'Standard' : subscriptionData?.plan_type === 'pro' ? 'Pro' : ''}!
          </h1>
          
          <p className="text-xl text-gray-400 mb-8">
            Your subscription has been activated successfully.
          </p>

          {subscriptionData && subscriptionData.has_subscription && (
            <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-8 border border-white/10 mb-8 max-w-md mx-auto">
              <h3 className="text-xl font-semibold text-white mb-4">Your Plan Details</h3>
              <div className="space-y-3 text-left">
                <div className="flex justify-between">
                  <span className="text-gray-400">Plan:</span>
                  <span className="text-white font-medium capitalize">{subscriptionData.plan_type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Monthly Pages:</span>
                  <span className="text-white font-medium">{subscriptionData.monthly_page_limit.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Status:</span>
                  <span className="text-green-400 font-medium capitalize">{subscriptionData.status}</span>
                </div>
                {subscriptionData.current_period_end && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Next Billing:</span>
                    <span className="text-white font-medium">
                      {new Date(subscriptionData.current_period_end).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/process"
              className="inline-flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-8 py-3 rounded-lg font-medium transition-colors"
            >
              Start Processing PDFs
              <ArrowRight className="w-5 h-5" />
            </Link>
            
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white px-8 py-3 rounded-lg font-medium transition-colors border border-white/20"
            >
              Go to Dashboard
            </Link>
          </div>

          <div className="mt-12 text-center">
            <p className="text-gray-400 mb-4">
              Need help getting started? Check out our documentation or contact support.
            </p>
            <div className="flex justify-center gap-6">
              <a
                href="/api-docs"
                className="text-blue-400 hover:text-blue-300 transition-colors"
              >
                API Documentation
              </a>
              <a
                href="mailto:support@octro.com"
                className="text-blue-400 hover:text-blue-300 transition-colors"
              >
                Contact Support
              </a>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default SuccessPage;