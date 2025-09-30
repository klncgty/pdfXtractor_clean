import React from 'react';
import { Link } from 'react-router-dom';
import { Check, Coffee } from 'lucide-react';
import axios from 'axios';
import { UserDropdown } from './App';
import octoLogo from './octo.png';

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
      "30 pages per month",
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
      "300 pages per month",
      "CSV & JSON export",
      "Priority support",
      "AI-powered table detection",
      "Batch processing",
      "API access"
    ],
    isPopular: true
  },
  {
    name: "Pro",
    price: 70,
    pages: 1000,
    features: [
      "1000 pages per month",
      "CSV & JSON export",
      "Premium support",
      "AI-powered table detection",
      "Batch processing",
      "API access",
      "Custom integrations"
    ]
  }
];

export const PricingPage = () => {
  const handleSubscribe = async (tier: PricingTier) => {
    // Free tier için login sayfasına yönlendir
    if (tier.price === 0) {
      window.location.href = `${API_URL}/auth/login`;
      return;
    }
    
    try {
      // Paid tiers için Stripe checkout - plan_type olarak gönder
      const response = await axios.post(`${API_URL}/stripe/create-checkout-session`, {
        plan_type: tier.name.toLowerCase(),
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

              <button
                onClick={() => handleSubscribe(tier)}
                className={`w-full py-3 px-4 rounded-lg font-medium transition-colors duration-200
                  ${tier.price === 0 
                    ? 'bg-white/10 text-white hover:bg-white/20' 
                    : 'bg-blue-500 text-white hover:bg-blue-600'
                  }`}
              >
                {tier.price === 0 ? 'Get Started' : 'Subscribe Now'}
              </button>
            </div>
          ))}
        </div>

        <div className="mt-16 text-center">
          <p className="text-gray-400">
            All plans include SSL security, real-time updates, and 99.9% uptime guarantee
          </p>
        </div>
      </main>
    </div>
  );
};

export default PricingPage;