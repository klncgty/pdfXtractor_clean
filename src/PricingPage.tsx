import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Check, Coffee, X, Gift } from 'lucide-react';
import axios from 'axios';
import { UserDropdown } from './App';
import octoLogo from './octo.png';
import octo2Image from './octo_2.jpeg';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface PricingTier {
  name: string;
  price: number;
  pages: number;
  features: string[];
  isPopular?: boolean;
}

const pricingTiers: PricingTier[] = [
  {
    name: "Free",
    price: 0,
    pages: 30,
    features: [
      
      "10MB max file size per upload",
      "CSV & JSON export",
      "Basic support",
      "AI-powered table detection",
      "No credit card required"
    ]
  },
  {
    name: "Standard",
    price: 30,
    pages: 300,
    features: [
      "50MB max file size per upload",
      "CSV & JSON export",
      "Priority support",
      "AI-powered table detection",
      "API access"
    ],
    isPopular: true
  },
  {
    name: "Pro (Ideal For Business)",
    price: 70,
    pages: 1000,
    features: [
      "100MB max file size per upload",
      "CSV & JSON export",
      "Premium support",
      "AI-powered table detection",
      "Batch processing",
      "API access",
      "Custom integrations"
    ]
  }
];

// PromoModal Component
interface PromoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const PromoModal: React.FC<PromoModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [promoCode, setPromoCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);

  // Handle keyboard events
  React.useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        handleClose();
      } else if (event.key === 'Enter' && !isLoading && !showSuccess) {
        handleActivate();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, isLoading, showSuccess]);

  const handleActivate = async () => {
    if (!promoCode.trim()) {
      setError('Please enter a promotion code');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/promo/validate`, {
        code: promoCode.trim()
      }, {
        withCredentials: true,
        timeout: 10000 // 10 second timeout
      });

      if (response.data.success) {
        setShowSuccess(true);
        setTimeout(() => {
          setShowSuccess(false);
          onSuccess();
          onClose();
        }, 2000);
      } else {
        setError(response.data.message || 'Invalid promotion code');
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 401) {
          setError('Please log in to activate promotion codes');
        } else if (err.response?.status === 429) {
          setError('Too many attempts. Please try again later.');
        } else if (err.code === 'ECONNABORTED') {
          setError('Request timed out. Please try again.');
        } else {
          setError(err.response?.data?.detail || err.response?.data?.message || 'Invalid promotion code');
        }
      } else {
        setError('An error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setPromoCode('');
    setError(null);
    setShowSuccess(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/70" onClick={handleClose} />
      <div className="relative bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-8 w-full max-w-md mx-4 shadow-2xl">
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
        >
          <X className="w-6 h-6" />
        </button>

        <div className="text-center mb-6">
          <img 
            src={octo2Image} 
            alt="Octro Promotion" 
            className="w-24 h-24 mx-auto mb-4 rounded-full"
          />
          <h3 className="text-xl font-bold text-white mb-2">Promotion Code</h3>
          <p className="text-gray-300 text-sm leading-relaxed">
            If you have a promotion code, you can unlock 1 week of unlimited page processing.
          </p>
        </div>

        {showSuccess ? (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <Check className="w-8 h-8 text-green-400" />
            </div>
            <h4 className="text-lg font-semibold text-white mb-2">Congratulations!</h4>
            <p className="text-green-400">You have unlocked 1 week of unlimited page processing.</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <input
                type="text"
                value={promoCode}
                onChange={(e) => setPromoCode(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !isLoading && promoCode.trim()) {
                    handleActivate();
                  }
                }}
                placeholder="Enter promotion code"
                className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500/50 transition-colors"
                disabled={isLoading}
                autoFocus
              />
            </div>

            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            <button
              onClick={handleActivate}
              disabled={isLoading || !promoCode.trim()}
              className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-blue-500/50 disabled:cursor-not-allowed text-white py-3 px-4 rounded-lg font-medium transition-colors duration-200"
            >
              {isLoading ? 'Activating...' : 'Activate'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export const PricingPage = () => {
  const [showPromoModal, setShowPromoModal] = useState(false);
  const [userData, setUserData] = useState<any>(null);
  const [subscriptionData, setSubscriptionData] = useState<any>(null);

  // Check if user is logged in
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await axios.get(`${API_URL}/auth/me`, {
          withCredentials: true,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          },
          validateStatus: (status) => {
            return status === 200 || status === 401;
          }
        });
        
        if (res.status === 200 && res.data && res.data.id) {
          setUserData(res.data);
          // fetch subscription status when logged in
          try {
            const subRes = await axios.get(`${API_URL}/stripe/subscription-status`, { withCredentials: true });
            setSubscriptionData(subRes.data);
          } catch (err) {
            setSubscriptionData(null);
          }
        } else {
          setUserData(null);
        }
      } catch (error) {
        setUserData(null);
      } finally {
        // finished auth check
      }
    };

    checkAuth();
  }, []);

  const handlePromoSuccess = () => {
    // Close modal and optionally refresh user data
    setShowPromoModal(false);
    // You could emit an event or use a context to refresh user data
    // For now, a simple page refresh ensures all components get updated data
    setTimeout(() => {
      window.location.reload();
    }, 100);
  };
  const handleSubscribe = async (tier: PricingTier) => {
    // If free tier, check authentication status from the state
    if (tier.price === 0) {
      if (userData) {
        // User is logged in, redirect to process page
        window.location.href = `/process`;
      } else {
        // User is not logged in, redirect to login page
        window.location.href = `${API_URL}/auth/login`;
      }
      return;
    }
    
    try {
      // Extract the base plan type from tier name
      const planType = tier.name.toLowerCase().includes('pro') ? 'pro' : 
                      tier.name.toLowerCase().includes('standard') ? 'standard' : 
                      tier.name.toLowerCase();

      // If user already has this plan, show appropriate action
      if (subscriptionData && subscriptionData.has_subscription && subscriptionData.plan_type === planType) {
        // If same plan, show cancel action instead (handled elsewhere)
        // No-op here
        return;
      }

      // Paid tiers için Stripe checkout - plan_type olarak gönder
      const response = await axios.post(`${API_URL}/stripe/create-checkout-session`, {
        plan_type: planType,
      }, {
        withCredentials: true
      });

      // Redirect to Stripe checkout page
      window.location.href = response.data.checkout_url;
    } catch (error) {
      console.error('Subscription error:', error);
      // Hata durumunda kullanıcıya bilgi ver
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        // Kullanıcı giriş yapmamış, login sayfasına yönlendir
        window.location.href = `${API_URL}/auth/login`;
      } else {
        alert('Ödeme işlemi başlatılamadı. Lütfen tekrar deneyin.');
      }
    }
  };

  const handleCancel = async () => {
    try {
      const res = await axios.post(`${API_URL}/stripe/cancel-subscription`, {}, { withCredentials: true });
      alert(res.data.message || 'Subscription cancellation scheduled');
      // Refresh subscription status
      const subRes = await axios.get(`${API_URL}/stripe/subscription-status`, { withCredentials: true });
      setSubscriptionData(subRes.data);
      window.location.reload();
    } catch (err) {
      console.error('Cancel error', err);
      alert('Failed to cancel subscription.');
    }
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#262624' }}>
      <nav className="border-b border-white/10 backdrop-blur-xl" style={{ backgroundColor: '#262624aa' }}>
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

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl sm:text-5xl font-bold text-white mb-6 leading-tight">
            Choose Your Plan
          </h1>
          <p className="text-xl text-gray-400">
            Start with our free tier or upgrade for more pages and features
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {pricingTiers.map((tier) => (
            <div 
              key={tier.name}
              className={`relative bg-white/5 backdrop-blur-xl rounded-2xl p-8 border 
                ${tier.isPopular ? 'border-blue-500/50' : 'border-white/10'}
              `}
            >
              {tier.isPopular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-blue-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                    Most Popular
                  </span>
                </div>
              )}

              <div className="text-center mb-8">
                <h3 className="text-xl font-semibold text-white mb-2">{tier.name}</h3>
                <div className="flex items-end justify-center gap-1 mb-2">
                  <span className="text-4xl font-bold text-white">${tier.price}</span>
                  <span className="text-gray-400 mb-1">/month</span>
                </div>
                <p className="text-gray-400">
                  Process up to {tier.pages.toLocaleString()} pages/month
                </p>
              </div>

              <ul className="space-y-4 mb-8">
                {tier.features.map((feature, index) => (
                  <li key={index} className="flex items-center gap-3 text-gray-300">
                    <Check className="w-5 h-5 text-green-500 flex-shrink-0" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              {/* Conditional buttons based on subscription status */}
              {tier.price > 0 ? (
                // Paid tiers
                subscriptionData && subscriptionData.has_subscription ? (
                  (() => {
                    const planType = tier.name.toLowerCase().includes('pro') ? 'pro' : 
                                    tier.name.toLowerCase().includes('standard') ? 'standard' : 
                                    tier.name.toLowerCase();
                    return subscriptionData.plan_type === planType ? (
                      // User is on this plan -> show Cancel
                      <button onClick={handleCancel} className="w-full py-3 px-4 rounded-lg font-medium bg-red-500 hover:bg-red-600 text-white">Cancel subscription</button>
                    ) : (
                      // User is on another paid plan or free -> show Subscribe/Upgrade
                      <button onClick={() => handleSubscribe(tier)} className="w-full py-3 px-4 rounded-lg font-medium bg-blue-500 hover:bg-blue-600 text-white">
                        {subscriptionData && subscriptionData.plan_type === 'standard' && planType === 'pro' ? 'Upgrade to Pro' : `Subscribe Now`}
                      </button>
                    );
                  })()
                ) : (
                  // Not subscribed
                  <button onClick={() => handleSubscribe(tier)} className="w-full py-3 px-4 rounded-lg font-medium bg-blue-500 hover:bg-blue-600 text-white">Subscribe Now</button>
                )
              ) : (
                // Free tier button
                tier.price === 0 ? (
                  userData ? (
                    <button onClick={() => window.location.href = '/process'} className="w-full py-3 px-4 rounded-lg font-medium bg-white/10 text-white hover:bg-white/20">Process PDF</button>
                  ) : (
                    <button onClick={() => window.location.href = `${API_URL}/auth/login`} className="w-full py-3 px-4 rounded-lg font-medium bg-white/10 text-white hover:bg-white/20">Get Started</button>
                  )
                ) : null
              )}
            </div>
          ))}
        </div>

        <div className="mt-16 text-center">
          <p className="text-gray-400 mb-6">
            All plans include SSL security, real-time updates, and 99.9% uptime guarantee
          </p>
          
          <button
            onClick={() => setShowPromoModal(true)}
            className="inline-flex items-center gap-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 transform hover:scale-105"
          >
            <Gift className="w-5 h-5" />
            Have a promotion code?
          </button>
        </div>

        <PromoModal
          isOpen={showPromoModal}
          onClose={() => setShowPromoModal(false)}
          onSuccess={handlePromoSuccess}
        />
      </main>
    </div>
  );
};

export default PricingPage;