import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useLocation, useNavigate } from 'react-router-dom';
import { Upload, Download, Send, FileUp, Sparkles, ArrowRight, Coffee } from 'lucide-react';
import axios from 'axios';
import llmImage from './llm_formats.png';
import octoLogo from './octo.png';
import './index.css';

// Animated rolling CSV/JSON başlık bileşeni
const AnimatedLLMTitle = () => {
  const [showCSV, setShowCSV] = useState(true);
  const [showFirstContent, setShowFirstContent] = useState(true);

  useEffect(() => {
    const csvInterval = setInterval(() => setShowCSV(v => !v), 1700);
    
    return () => {
      clearInterval(csvInterval);
    };
  }, []);

  // Kullanıcı tıklaması ile içeriği değiştir
  const toggleContent = () => {
    setShowFirstContent(prev => !prev);
  };

  return (
    <div className="space-y-6">
      {showFirstContent ? (
        <div className="animate-fade-in">
          <h2
            style={{
              fontSize: 32,
              fontWeight: 800,
              color: '#fff',
              marginBottom: 32,
              letterSpacing: 1.1,
              lineHeight: 1.1,
              textAlign: 'left',
              background: 'none',
              padding: 0,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              cursor: 'pointer',
              transition: 'opacity 0.3s'
            }}
            onClick={() => setShowFirstContent(prev => !prev)}
            className="hover:opacity-80"
          >
            Why Use
            <span
              className={showCSV ? 'llm-spin-in' : 'llm-spin-out'}
              style={{
                margin: '0 8px',
                minWidth: 54,
                display: 'inline-block',
                color: '#fff',
                fontWeight: 900,
                fontSize: 36,
                letterSpacing: 1.2,
                transition: 'color 0.3s',
              }}
            >
              {showCSV ? 'CSV' : 'JSON'}
            </span>
            for LLM Data Input?
            <span className="ml-2 text-white/80">
              {showFirstContent ? '▼' : '▲'}
            </span>
          </h2>
        </div>
      ) : (
        <div className="animate-slide-in-right">
          <h2
            style={{
              fontSize: 32,
              fontWeight: 800,
              color: '#fff',
              marginBottom: 32,
              letterSpacing: 1.1,
              lineHeight: 1.1,
              textAlign: 'left',
              background: 'none',
              padding: 0,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              cursor: 'pointer',
              transition: 'opacity 0.3s'
            }}
            onClick={() => setShowFirstContent(prev => !prev)}
            className="hover:opacity-80"
          >
            Supercharge Your RAG Apps with Clean, Structured Data
            <span className="ml-2 text-white/80">
              {!showFirstContent ? '▼' : '▲'}
            </span>
          </h2>
        </div>
      )}
    </div>
  );
};

// Landing Page Component
// Vanta.js Birds Background Effect
const VantaBirdsBackground = () => {
  const vantaRef = React.useRef<HTMLDivElement>(null);
  const [vantaEffect, setVantaEffect] = React.useState<any>(null);

  React.useEffect(() => {
    if (!vantaEffect && vantaRef.current) {
      // Load Vanta.js scripts dynamically
      const loadVanta = async () => {
        // Load Three.js first
        if (!(window as any).THREE) {
          const threeScript = document.createElement('script');
          threeScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r121/three.min.js';
          document.head.appendChild(threeScript);
          await new Promise(resolve => threeScript.onload = resolve);
        }

        // Load Vanta Birds effect
        if (!(window as any).VANTA?.BIRDS) {
          const vantaScript = document.createElement('script');
          vantaScript.src = 'https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.birds.min.js';
          document.head.appendChild(vantaScript);
          await new Promise(resolve => vantaScript.onload = resolve);
        }

        // Initialize Vanta Birds effect with your specified settings
        const effect = (window as any).VANTA.BIRDS({
          el: vantaRef.current,
          mouseControls: true,
          touchControls: true,
          gyroControls: false,
          minHeight: 200.00,
          minWidth: 200.00,
          scale: 1.00,
          scaleMobile: 1.00,
          backgroundColor: 0x465199,
          color1: 0xff0000,
          color2: 0x3059a8,
          colorMode: 'variance',
          birdSize: 2.20,
          wingSpan: 15.00,
          speedLimit: 5.00,
          separation: 20.00,
          alignment: 64.00,
          cohesion: 20.00,
          quantity: 3.00,
          backgroundAlpha: 1.00
        });
        setVantaEffect(effect);
      };

      loadVanta();
    }

    return () => {
      if (vantaEffect && vantaEffect.destroy) {
        vantaEffect.destroy();
      }
    };
  }, [vantaEffect]);

  return (
    <div 
      ref={vantaRef} 
      className="vanta-background"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        zIndex: 0,
        pointerEvents: 'none'
      }}
    />
  );
};


interface UserInfo {
  id?: number;
  name?: string;
  email: string;
  pages_processed_this_month?: number;
  monthly_page_limit?: number;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const UserDropdown = () => {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  // Hover davranışı için Effect
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showDropdown && !(event.target as Element).closest('.user-dropdown')) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showDropdown]);
  
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
        setUser(res.data);
      } else {
        setUser(null);
      }
    } catch (error) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };
  
  useEffect(() => {
    checkAuth();
    const interval = setInterval(checkAuth, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);
  
  const handleLogout = async () => {
    try {
      await axios.post(`${API_URL}/auth/logout`, {}, { 
        withCredentials: true,
        headers: { 'Content-Type': 'application/json' }
      });
      
      setUser(null);
      setShowDropdown(false);
      window.location.href = '/';
    } catch (error) {
      setUser(null);
      setShowDropdown(false);
      window.location.href = '/';
    }
  };

  if (isLoading) {
    return <div className="animate-pulse h-8 w-24 bg-gray-600 rounded"></div>;
  }

  if (!user) {
    return null;
  }

  return (
    <div className="relative user-dropdown">
      <button 
        onClick={() => setShowDropdown(!showDropdown)}
        className="flex items-center gap-2 text-white font-medium px-4 py-2 rounded-lg hover:bg-white/10 transition-colors"
      >
        <span>{user.name || user.email}</span>
        <svg width="12" height="8" viewBox="0 0 12 8" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M1 1.5L6 6.5L11 1.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
      {showDropdown && (
        <div 
          className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg py-1 z-50 border border-gray-200"
        >
          <div className="px-4 py-2 text-sm text-gray-500 border-b border-gray-100">
            <div className="font-medium text-gray-900">{user.name || user.email}</div>
            <div className="text-xs">
              {user.pages_processed_this_month || 0}/{user.monthly_page_limit || 100} pages used
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
          >
            Logout
          </button>
        </div>
      )}
    </div>
  );
};

const Navbar = () => {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
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
          return status === 200 || status === 401; // 401'i geçerli yanıt olarak kabul et
        }
      });
      
      if (res.status === 200 && res.data && res.data.id) {
        setUser(res.data);
      } else {
        setUser(null);
      }
    } catch (error) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };
  
  useEffect(() => {
    checkAuth();
    
    // Check session status every 5 minutes
    const interval = setInterval(checkAuth, 5 * 60 * 1000);

    // Add click event listener to close dropdown when clicking outside
    const handleClickOutside = (event: MouseEvent) => {
      if (showDropdown && !(event.target as Element).closest('.nav-dropdown')) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    
    return () => {
      clearInterval(interval);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showDropdown]);
  
  const handleLogin = () => {
    window.location.href = `${API_URL}/auth/login`;
  };
  
  const handleLogout = async () => {
    try {
      console.log('🔄 Logging out...');
      const response = await axios.post(`${API_URL}/auth/logout`, {}, { 
        withCredentials: true,
        headers: { 'Content-Type': 'application/json' }
      });
      
      console.log('✅ Logout response:', response.data);
      
      // Clear local state
      setUser(null);
      setShowDropdown(false);
      
      // Redirect to home page
      window.location.href = '/';
    } catch (error) {
      console.error('❌ Logout failed:', error);
      // Even if logout fails, clear local state
      setUser(null);
      setShowDropdown(false);
      window.location.href = '/';
    }
  }; 

  return (
    <nav className="navbar-glass">
      <div className="navbar-content">
        <div className="flex items-center gap-3">
          <img src={octoLogo} alt="pdfXtractor Logo" className="w-9 h-9" />
          <span className="logo-gradient">pdfXtractor</span>
        </div>
        <div className="nav-links">
          {isLoading ? (
            <div className="animate-pulse h-8 w-24 bg-gray-200 rounded"></div>
          ) : user ? (
            <div className="relative nav-dropdown">
              <button 
                onClick={() => setShowDropdown(!showDropdown)}
                className="flex items-center gap-2 text-white font-medium px-4 py-2 rounded-lg hover:bg-white/10 transition-colors"
              >
                <span>{user.name || user.email}</span>
                <svg width="12" height="8" viewBox="0 0 12 8" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M1 1.5L6 6.5L11 1.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
              {showDropdown && (
                <div 
                  className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg py-1 z-50 border border-gray-200"
                >
                  <div className="px-4 py-2 text-sm text-gray-500 border-b border-gray-100">
                    <div className="font-medium text-gray-900">{user.name || user.email}</div>
                    <div className="text-xs">
                      {user.pages_processed_this_month || 0}/{user.monthly_page_limit || 100} pages used
                    </div>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          ) : (
            <button
              className="cta-btn-border flex items-center gap-2"
              onClick={handleLogin}
              style={{ marginLeft: 16 }}
              disabled={isLoading}
            >
              {isLoading ? 'Loading...' : 'Get Started'}
            </button>
          )}
        </div>
      </div>
    </nav>
  );
};

const Landing = () => {
  // Animasyon için state
  const [showLLM, setShowLLM] = React.useState(false);
  const [showFirstContent] = React.useState(true);
  const llmRef = React.useRef<HTMLDivElement>(null);
  const [isAuthenticated, setIsAuthenticated] = React.useState<boolean | null>(null);

  React.useEffect(() => {
    let mounted = true;
    const checkAuth = async () => {
      try {
        const res = await axios.get(`${API_URL}/auth/me`, { withCredentials: true });
        if (!mounted) return;
        setIsAuthenticated(Boolean(res.data && res.data.id));
      } catch (err) {
        if (!mounted) return;
        setIsAuthenticated(false);
      }
    };

    checkAuth();
    return () => { mounted = false; };
  }, []);
  
  const handleLogin = () => {
    window.location.href = `${API_URL}/auth/login`;
  };

  React.useEffect(() => {
    const onScroll = () => {
      if (llmRef.current) {
        const rect = llmRef.current.getBoundingClientRect();
        if (rect.top < window.innerHeight - 100) {
          setShowLLM(true);
        }
      }
    };
    window.addEventListener('scroll', onScroll);

    return () => {
      window.removeEventListener('scroll', onScroll);
    };
  }, []);

  return (
    <div className="main-bg min-h-screen w-screen flex flex-col bg-black relative" style={{ minWidth: '100vw' }}>
      <VantaBirdsBackground />
      <Navbar />
      <main className="main-content flex-1 flex flex-col items-center w-full" style={{ paddingTop: 96, paddingBottom: 64, boxSizing: 'border-box' }}>
        <section className="hero-section relative overflow-hidden" style={{ marginBottom: 64, textAlign: 'center', zIndex: 2, width: '100%', maxWidth: 800 }}>
          {/* Ana başlık - Sabit */}
          <div className="relative z-10">
            <h1 className="hero-title" style={{ fontSize: '2.7rem', color: '#fff', fontWeight: 800, marginBottom: 10, letterSpacing: 1.1, lineHeight: 1.15, fontFamily: "'Outfit', 'Space Grotesk', sans-serif" }}>
              Transform your PDF documents into actionable data
            </h1>
            <p style={{ fontSize: '1.25rem', color: '#cbd5e1', fontWeight: 500, marginBottom: 0, letterSpacing: 0.2, lineHeight: 1.3 }}>
              Extract your complex PDFs with our advanced AI technology.
            </p>
            <div className="w-full flex justify-center items-center mt-8">
              {isAuthenticated === true ? (
                <Link to="/process">
                  <button className="start-free-btn mx-auto text-sm px-6 py-2.5">Process PDF</button>
                </Link>
              ) : (
                <button
                  className="start-free-btn mx-auto text-sm px-6 py-2.5"
                  onClick={handleLogin}
                >
                  START FOR FREE
                </button>
              )}
            </div>
          </div>
          
          {/* Alt kısımdaki değişen içerik */}
          <div className={`mt-16 transition-all duration-700 ${!showFirstContent ? 'opacity-0 translate-y-12' : 'opacity-100 translate-y-0'}`}>
            <div className="text-left max-w-2xl mx-auto">
              {/* Feature list kaldırıldı */}
            </div>
          </div>
          
          {/* Oklar kaldırıldı */}
        </section>
        {/* passing to llm bölümü */}
        <section id="llm" ref={llmRef} style={{ width: '100%', maxWidth: 700, margin: '80px auto 0 auto', zIndex: 2, background: 'none', textAlign: 'left' }}>
          {/* Animasyonlu başlık */}
          <AnimatedLLMTitle />
          <div className="llm-blocks-container" style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 32, gap: 0, width: '100%' }}>
            {showFirstContent ? (
              <>
                <div className={`llm-block-sentence ${showLLM ? 'fade-in-block' : ''}`} style={{ fontSize: 17, color: '#fff', fontWeight: 400, marginBottom: 16, maxWidth: 260, textAlign: 'left', transition: 'opacity 0.7s, transform 0.7s', opacity: showLLM ? 1 : 0, transform: showLLM ? 'translateX(0)' : 'translateX(-40px)', background: 'transparent', padding: '18px 18px', zIndex: 10, fontFamily: "'Share Tech Mono', 'Courier New', monospace" }}>
                  Large Language Models (LLMs) process structured, standard formats like <b>CSV</b> and <b>JSON</b> with higher accuracy and efficiency. Transform your data seamlessly.
                </div>
                <div className={`llm-block-sentence ${showLLM ? 'fade-in-block-delay1' : ''}`} style={{ fontSize: 17, color: '#fff', fontWeight: 400, marginBottom: 16, maxWidth: 320, textAlign: 'center', marginLeft: 'auto', marginRight: 'auto', transition: 'opacity 0.7s 0.3s, transform 0.7s 0.3s', opacity: showLLM ? 1 : 0, transform: showLLM ? 'translateX(0)' : 'translateX(-40px)', background: 'transparent', padding: '18px 18px', zIndex: 10, fontFamily: "'Share Tech Mono', 'Courier New', monospace" }}>
                  Our advanced AI technology ensures your data is organized, consistent, and machine-readable, making it perfect for integration with modern AI applications and analysis tools.
                </div>
                <div className={`llm-block-sentence ${showLLM ? 'fade-in-block-delay2' : ''}`} style={{ fontSize: 17, color: '#fff', fontWeight: 400, marginBottom: 16, maxWidth: 260, textAlign: 'right', transition: 'opacity 0.7s 0.6s, transform 0.7s 0.6s', opacity: showLLM ? 1 : 0, transform: showLLM ? 'translateX(0)' : 'translateX(-40px)', background: 'transparent', padding: '18px 18px', zIndex: 10, fontFamily: "'Share Tech Mono', 'Courier New', monospace" }}>
                  Eliminate errors and boost performance with our structured data formats. Perfect for machine learning pipelines and data analysis workflows.
                </div>
              </>
            ) : (
              <>
                <div className={`llm-block-sentence ${showLLM ? 'fade-in-block' : ''}`} style={{ fontSize: 17, color: '#fff', fontWeight: 400, marginBottom: 16, maxWidth: 280, textAlign: 'left', transition: 'opacity 0.7s, transform 0.7s', opacity: showLLM ? 1 : 0, transform: showLLM ? 'translateX(0)' : 'translateX(-40px)', background: 'transparent', padding: '18px 18px', zIndex: 10, fontFamily: "'Share Tech Mono', 'Courier New', monospace" }}>
                  Hey there! 👋 Building a RAG application? Our <b>perfectly structured JSON data</b> is your new best friend for creating lightning-fast vector stores.
                </div>
                <div className={`llm-block-sentence ${showLLM ? 'fade-in-block-delay1' : ''}`} style={{ fontSize: 17, color: '#fff', fontWeight: 400, marginBottom: 16, maxWidth: 340, textAlign: 'center', marginLeft: 'auto', marginRight: 'auto', transition: 'opacity 0.7s 0.3s, transform 0.7s 0.3s', opacity: showLLM ? 1 : 0, transform: showLLM ? 'translateX(0)' : 'translateX(-40px)', background: 'transparent', padding: '18px 18px', zIndex: 10, fontFamily: "'Share Tech Mono', 'Courier New', monospace" }}>
                  Skip the messy PDF parsing and data cleaning. Get <b>clean, chunked, and context-rich data</b> ready for embedding generation and semantic search.
                </div>
                <div className={`llm-block-sentence ${showLLM ? 'fade-in-block-delay2' : ''}`} style={{ fontSize: 17, color: '#fff', fontWeight: 400, marginBottom: 16, maxWidth: 280, textAlign: 'right', transition: 'opacity 0.7s 0.6s, transform 0.7s 0.6s', opacity: showLLM ? 1 : 0, transform: showLLM ? 'translateX(0)' : 'translateX(-40px)', background: 'transparent', padding: '18px 18px', zIndex: 10, fontFamily: "'Share Tech Mono', 'Courier New', monospace" }}>
                  Perfect for <b>question-answering, chat interfaces, and data analysis</b>. Your RAG apps will love this structured goodness! ✨
                </div>
              </>
            )}
          </div>
          <div style={{ textAlign: 'center', marginTop: 32 }}>
            <img src={llmImage} alt="llm format accuracy" style={{ width: '100%', maxWidth: 600, borderRadius: 14, boxShadow: '0 2px 12px rgba(0,0,0,0.10)', opacity: showLLM ? 1 : 0, transition: 'opacity 0.7s' }} />
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
};

// PDF Processing Page Component
const ProcessPage = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadInfo, setUploadInfo] = useState<{ pdf_id?: number; pages_total?: number; pages_processed?: number; limit_left?: number } | null>(null);
  const [showUploadPopup, setShowUploadPopup] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      setFile(droppedFile);
      setError(null);
      
      // Automatically start upload when file is dropped
      setUploading(true);
      try {
        const formData = new FormData();
        formData.append('file', droppedFile);

        const uploadResponse = await axios.post(`${API_URL}/upload_pdf`, formData, { 
          withCredentials: true,
          headers: {
            'Content-Type': 'multipart/form-data',
          }
        });
        setUploadInfo(uploadResponse.data);
        setShowUploadPopup(true); // Show upload info popup
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred during upload');
      } finally {
        setUploading(false);
      }
    }
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const selectedFile = event.target.files[0];
      setFile(selectedFile);
      setError(null);
      
      // Automatically start upload when file is selected
      setUploading(true);
      try {
        const formData = new FormData();
        formData.append('file', selectedFile);

        const uploadResponse = await axios.post(`${API_URL}/upload_pdf`, formData, { 
          withCredentials: true,
          headers: {
            'Content-Type': 'multipart/form-data',
          }
        });
        setUploadInfo(uploadResponse.data);
        setShowUploadPopup(true); // Show upload info popup
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred during upload');
      } finally {
        setUploading(false);
      }
    }
  };



  const handleStartProcessing = async () => {
    if (!file || !uploadInfo) return;
    setProcessing(true);
    setShowUploadPopup(false);
    try {
      const processResponse = await axios.get<ProcessResponse>(
        `${API_URL}/process/${file.name}?output_format=both&pages_limit=${uploadInfo.pages_total}`,
        { withCredentials: true }
      );      const newTableData: { [key: number]: any } = {};
      for (let i = 0; i < processResponse.data.tables.length; i++) {
        const table = processResponse.data.tables[i];
        if (table.json_file) {
          const jsonResponse = await axios.get(`${API_URL}/download/${table.json_file}`);
          newTableData[i] = jsonResponse.data;
        }
      }

      // Navigate to results page with data
      navigate('/results', { state: { results: processResponse.data, tableData: newTableData } });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during processing');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-black">
      {/* Loading overlay shown during upload or processing */}
      {(uploading || processing) && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
          <div className="flex flex-col items-center gap-4">
            <div className="w-16 h-16 border-4 border-t-transparent border-white rounded-full animate-spin" />
            <div className="text-white">{uploading ? 'Uploading...' : 'Processing PDF...'}</div>
          </div>
        </div>
      )}
      <nav className="border-b border-white/10 bg-black/20 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center">
              <Sparkles className="w-8 h-8 text-blue-500" />
              <span className="ml-2 text-xl font-bold text-white">pdfXtractor</span>
            </Link>
            <div className="flex items-center gap-6">
              <a
                href="https://buymeacoffee.com/cgtyklnc1t"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-300 hover:text-amber-400 transition-colors flex items-center gap-2"
              >
                <Coffee className="w-5 h-5" />
                <span>buy me cup of coffee :)</span>
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
        <div className="max-w-3xl mx-auto processing-page-mobile">
          <div className="text-center mb-12">
            <h1 className="text-4xl sm:text-5xl font-bold text-white mb-6 leading-tight overflow-hidden">
              <span className="animate-slide-in-left-right inline-block [animation-delay:500ms]">
                Transform Your PDF Tables
              </span>{' '}
              <span className="animate-slide-in-right-left inline-block [animation-delay:800ms]">
                with AI
              </span>
            </h1>
            <p className="text-xl text-gray-400 mb-8">
              Extract, analyze, and get insights from your PDF tables instantly
            </p>
          </div>

          <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-8 shadow-2xl border border-white/10 upload-area-mobile">
            <div className="flex flex-col items-center">
              <div className="mb-8">
                <div className="p-4 bg-blue-500/10 rounded-full">
                  <FileUp className="w-8 h-8 text-blue-500" />
                </div>
              </div>
              <div 
                className={`w-full border-2 border-dashed rounded-xl p-8 mb-6 text-center
                  ${dragActive ? 'border-blue-500 bg-blue-500/10' : 'border-white/10 hover:border-white/20'}
                  transition-all duration-200`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf"
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer text-gray-400 hover:text-white transition-colors"
                >
                  <span className="block mb-2">
                    {file ? file.name : 'Drop your PDF here or click to browse'}
                  </span>
                  <span className="text-sm text-gray-500">
                    {!file && 'Supports: PDF files'}
                  </span>
                </label>
              </div>

            {error && (
              <div className="mb-6 py-3 px-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-red-400 text-sm">
                  <span className="font-medium">Error:</span> {error}
                </p>
              </div>
            )}

            <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 feature-grid-mobile">
              {[
                {
                  icon: <Upload className="w-6 h-6 text-blue-500" />,
                  title: 'Easy Upload',
                  description: 'Drag & drop your PDF files or browse to upload'
                },
                {
                  icon: <Sparkles className="w-6 h-6 text-purple-500" />,
                  title: 'AI-Powered',
                  description: 'Advanced AI processing for accurate table extraction'
                },
                {
                  icon: <Download className="w-6 h-6 text-green-500" />,
                  title: 'Multiple Formats',
                  description: 'Download results in JSON or CSV format'
                }
              ].map((feature, index) => (
                <div key={index} className="bg-white/5 backdrop-blur-xl rounded-xl p-6 border border-white/10">
                  <div className="p-3 bg-white/5 rounded-lg inline-block mb-4">
                    {feature.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                  <p className="text-gray-400">{feature.description}</p>
                </div>
              ))}
            </div>
            
            {/* Upload status indicator */}
            {uploading && (
              <div className="mt-4 text-blue-400 flex items-center gap-2">
                <Upload className="w-5 h-5 animate-spin" />
                <span>Uploading PDF...</span>
              </div>
            )}
            
            {/* Process button - only show after successful upload */}
            {uploadInfo && !uploading && (
              <button
                onClick={handleStartProcessing}
                className="mt-6 px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg 
                  transition-colors duration-200 flex items-center gap-2"
                disabled={processing}
              >
                {processing ? (
                  <Upload className="w-5 h-5 animate-spin" />
                ) : (
                  <ArrowRight className="w-5 h-5" />
                )}
                {processing ? 'Processing PDF...' : 'Process PDF'}
              </button>
            )}
            {showUploadPopup && uploadInfo && (
              <div className="fixed inset-0 z-60 flex items-center justify-center">
                <div className="absolute inset-0 bg-black/70" onClick={() => setShowUploadPopup(false)} />
                <div className="relative bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl p-8 w-full max-w-md z-70 shadow-2xl">
                  <h3 className="text-xl font-bold text-white mb-4">Upload Complete</h3>
                  
                  {/* Main info section */}
                  <div className="space-y-3 mb-6">
                    <div className="flex justify-between items-center py-2 px-3 bg-white/5 rounded-lg">
                      <span className="text-gray-300">Total Pages in PDF:</span>
                      <span className="text-white font-medium">{uploadInfo.pages_total || 0}</span>
                    </div>
                    
                    <div className="flex justify-between items-center py-2 px-3 bg-white/5 rounded-lg">
                      <span className="text-gray-300">Available Quota:</span>
                      <span className="text-white font-medium">{uploadInfo.limit_left || 0} pages</span>
                    </div>
                    
                    <div className="flex justify-between items-center py-2 px-3 bg-white/5 rounded-lg">
                      <span className="text-gray-300">Pages to Process:</span>
                      <span className="text-white font-medium">{Math.min(uploadInfo.pages_total || 0, uploadInfo.limit_left || 0)}</span>
                    </div>
                    
                    <div className="flex justify-between items-center py-2 px-3 bg-white/5 rounded-lg">
                      <span className="text-gray-300">Remaining Quota After:</span>
                      <span className="text-white font-medium">
                        {(uploadInfo.limit_left || 0) - Math.min(uploadInfo.pages_total || 0, uploadInfo.limit_left || 0)} pages
                      </span>
                    </div>
                  </div>
                  
                  {/* Warning message for quota limit */}
                  {(uploadInfo.pages_total || 0) > (uploadInfo.limit_left || 0) && (
                    <div className="py-3 px-4 bg-amber-500/10 border border-amber-500/20 rounded-lg mb-6">
                      <p className="text-amber-400 text-sm">
                        <span className="font-medium">Note:</span> Due to your current quota limit, only the first {uploadInfo.limit_left || 0} pages will be processed.
                        {uploadInfo.limit_left === 0 && " Please upgrade your plan or wait for quota reset to process more pages."}
                      </p>
                    </div>
                  )}
                  
                  {/* Action buttons */}
                  <div className="flex justify-end gap-3">
                    <button 
                      onClick={() => setShowUploadPopup(false)} 
                      className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
                    >
                      Cancel
                    </button>
                    {uploadInfo.limit_left === 0 ? (
                      <Link
                        to="/pricing"
                        className="px-6 py-2 bg-green-500 hover:bg-green-600
                          text-white rounded-lg transition-colors duration-200 flex items-center gap-2"
                      >
                        Upgrade Now
                        <ArrowRight className="w-4 h-4" />
                      </Link>
                    ) : (
                      <button 
                        onClick={handleStartProcessing}
                        className="px-6 py-2 bg-blue-500 hover:bg-blue-600 
                          text-white rounded-lg transition-colors duration-200 flex items-center gap-2"
                      >
                        Process Now
                        <ArrowRight className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )}
              </div>
            </div>
          </div>
      </main>
    </div>
  );
};

// Results Page Component
const ResultsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [results, setResults] = useState<ProcessResponse | null>(null);
  const [tableData, setTableData] = useState<{ [key: number]: any }>({});
  const [tableQuestions, setTableQuestions] = useState<{ [key: number]: TableQuestion }>({});
  const [loadingQuestions, setLoadingQuestions] = useState<{ [key: number]: boolean }>({});

  useEffect(() => {
    if (location.state) {
      const { results: resResults, tableData: resTableData } = location.state as any;
      setResults(resResults);
      setTableData(resTableData || {});
    } else {
      // If no state, redirect to process page
      navigate('/process');
    }
  }, [location.state, navigate]);

  const handleDownload = async (filename: string) => {
    try {
      const response = await axios.get(`${API_URL}/download/${filename}`, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  const handleQuestionChange = (tableIndex: number, value: string) => {
    setTableQuestions(prev => ({
      ...prev,
      [tableIndex]: {
        question: value,
        answer: null
      }
    }));
  };

  const handleSubmitQuestion = async (tableIndex: number) => {
    const tableQuestion = tableQuestions[tableIndex];
    if (!tableQuestion?.question || !tableData[tableIndex]) return;

    setLoadingQuestions(prev => ({ ...prev, [tableIndex]: true }));

    try {
      const response = await axios.post(`${API_URL}/ask`, {
        question: tableQuestion.question,
        table: Array.isArray(tableData[tableIndex]) 
          ? tableData[tableIndex] 
          : [tableData[tableIndex]]
      });

      setTableQuestions(prev => ({
        ...prev,
        [tableIndex]: {
          ...prev[tableIndex],
          answer: response.data.answer
        }
      }));
    } catch (err) {
      console.error('Error:', err);
      // Handle error with toast or console
    } finally {
      setLoadingQuestions(prev => ({ ...prev, [tableIndex]: false }));
    }
  };

  if (!results) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white">Loading results...</div>
      </div>
    );
  }

  const handleDownloadAllJson = async () => {
    if (!results) return;

    try {
      // Tüm JSON dosyalarını indirip birleştir
      const allJsonData: { [key: string]: any } = {};
      for (let i = 0; i < results.tables.length; i++) {
        const table = results.tables[i];
        if (table.json_file) {
          const jsonData = tableData[i];
          if (jsonData) {
            allJsonData[`table_${i + 1}`] = jsonData;
          }
        }
      }

      // JSON'u indirilebilir dosya olarak hazırla
      const blob = new Blob([JSON.stringify(allJsonData, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'all_tables.json');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Failed to download combined JSON:', err);
    }
  };

  return (
    <div className="min-h-screen bg-black">
      <nav className="border-b border-white/10 bg-black/20 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center">
              <Sparkles className="w-8 h-8 text-blue-500" />
              <span className="ml-2 text-xl font-bold text-white">pdfXtractor</span>
            </Link>
            <div className="flex items-center gap-6">
              <a
                href="https://buymeacoffee.com/cgtyklnc1t"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-300 hover:text-amber-400 transition-colors flex items-center gap-2"
              >
                <Coffee className="w-5 h-5" />
                <span>buy me cup of coffee :)</span>
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
        <div className="max-w-4xl mx-auto space-y-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-white mb-4">
              Processed Tables ({results.total_tables})
            </h2>
            <p className="text-gray-400 mb-6">Download your extracted data in JSON or CSV format</p>
            <button
              onClick={handleDownloadAllJson}
              className="inline-flex items-center px-6 py-3 bg-blue-500/20 hover:bg-blue-500/30 
                text-blue-400 rounded-lg transition-colors duration-200 mb-8"
            >
              <Download className="w-5 h-5 mr-2" />
              Download All Tables as Single JSON
            </button>
          </div>
          
          {results.tables.map((table, index) => (
            <div key={index} className="bg-white/5 backdrop-blur-xl rounded-xl p-6 border border-white/10">
              <h3 className="text-xl font-semibold mb-6 text-white">Table {index + 1}</h3>
              <div className="space-y-6">
                <img
                  src={`${API_URL}/download/${table.image_file}`}
                  alt={`Table ${index + 1}`}
                  className="w-full rounded-lg border border-white/10"
                />
                
                <div className="flex gap-4">
                  {table.json_file && (
                    <button
                      onClick={() => handleDownload(table.json_file!)}
                      className="flex items-center px-4 py-2 bg-green-500/20 hover:bg-green-500/30 
                        text-green-400 rounded-lg transition-colors duration-200"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Download JSON
                    </button>
                  )}
                  {table.csv_file && (
                    <button
                      onClick={() => handleDownload(table.csv_file!)}
                      className="flex items-center px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 
                        text-purple-400 rounded-lg transition-colors duration-200"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Download CSV
                    </button>
                  )}
                </div>

                <div className="space-y-4">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={tableQuestions[index]?.question || ''}
                      onChange={(e) => handleQuestionChange(index, e.target.value)}
                      className="flex-1 px-4 py-2 bg-black/20 border border-white/10 rounded-lg
                        focus:outline-none focus:border-blue-500/50 text-white placeholder-gray-500"
                      placeholder="Ask a question about this table..."
                    />
                    <button
                      onClick={() => handleSubmitQuestion(index)}
                      disabled={!tableData[index] || loadingQuestions[index]}
                      className="px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400
                        disabled:bg-blue-500/10 disabled:text-blue-500/50 disabled:cursor-not-allowed 
                        rounded-lg transition-colors duration-200 flex items-center"
                    >
                      {loadingQuestions[index] ? (
                        <Upload className="w-5 h-5 animate-spin" />
                      ) : (
                        <Send className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                  
                  {tableQuestions[index]?.answer && (
                    <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                      <p className="text-blue-300">{tableQuestions[index].answer}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          <div className="text-center">
            <Link
              to="/process"
              className="inline-flex items-center px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors duration-200"
            >
              <ArrowRight className="w-5 h-5 mr-2" />
              Process Another PDF
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
};

// Interface tanımlamaları burada

// Interfaces
interface ProcessedTable {
  data_file?: string;
  json_file?: string;
  csv_file?: string;
  image_file: string;
}

interface ProcessResponse {
  tables: ProcessedTable[];
  total_tables: number;
}

interface TableQuestion {
  question: string;
  answer: string | null;
}



// Import PricingPage and Legal Pages
import PricingPage from './PricingPage';

// Legal Pages Components
const Footer = () => (
  <footer className="w-full py-8 text-center text-gray-400 text-sm border-t border-white/10 bg-black/30 backdrop-blur-sm mt-auto">
    <div className="max-w-7xl mx-auto px-4">
      <div className="flex justify-center items-center space-x-4">
        <Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link>
        <span className="text-white/20">|</span>
        <Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
        <span className="text-white/20">|</span>
        <Link to="/cookies" className="hover:text-white transition-colors">Cookie Policy</Link>
      </div>
      <div className="mt-4">
        © {new Date().getFullYear()} pdfXtractor. All Rights Reserved.
      </div>
    </div>
  </footer>
);

const TermsOfService = () => (
  <div className="min-h-screen bg-black text-white px-4 py-16">
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Terms of Service</h1>
      <div className="space-y-6 text-gray-300">
        <h2 className="text-2xl font-semibold text-white">1. Terms</h2>
        <p>By accessing the website at https://pdfxtractor.com, you are agreeing to be bound by these terms of service, all applicable laws and regulations, and agree that you are responsible for compliance with any applicable local laws.</p>
        
        <h2 className="text-2xl font-semibold text-white">2. Use License</h2>
        <p>Permission is granted to temporarily use the pdfXtractor service for personal or commercial use. This is the grant of a license, not a transfer of title, and under this license you may not:</p>
        <ul className="list-disc pl-6 space-y-2">
          <li>modify or copy the materials;</li>
          <li>use the materials for any commercial purpose, or for any public display (commercial or non-commercial) without explicit permission;</li>
          <li>attempt to decompile or reverse engineer any software contained in pdfXtractor;</li>
          <li>remove any copyright or other proprietary notations from the materials;</li>
          <li>transfer the materials to another person or "mirror" the materials on any other server.</li>
        </ul>

        <h2 className="text-2xl font-semibold text-white">3. Disclaimer</h2>
        <p>The materials on pdfXtractor's website are provided on an 'as is' basis. pdfXtractor makes no warranties, expressed or implied, and hereby disclaims and negates all other warranties including, without limitation, implied warranties or conditions of merchantability, fitness for a particular purpose, or non-infringement of intellectual property or other violation of rights.</p>
      </div>
      <Link to="/" className="inline-block mt-8 text-blue-400 hover:text-blue-300">← Back to Home</Link>
    </div>
  </div>
);

const PrivacyPolicy = () => (
  <div className="min-h-screen bg-black text-white px-4 py-16">
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Privacy Policy</h1>
      <div className="space-y-6 text-gray-300">
        <p>At pdfXtractor, we take your privacy seriously. This Privacy Policy describes how we collect, use, and handle your information when you use our services.</p>
        
        <h2 className="text-2xl font-semibold text-white">Information Collection</h2>
        <p>We collect information that you provide directly to us:</p>
        <ul className="list-disc pl-6 space-y-2">
          <li>Account information (email, name)</li>
          <li>PDF documents you upload for processing</li>
          <li>Usage data and analytics</li>
          <li>Payment information when you subscribe to paid plans</li>
        </ul>

        <h2 className="text-2xl font-semibold text-white">Use of Information</h2>
        <p>We use the information we collect to:</p>
        <ul className="list-disc pl-6 space-y-2">
          <li>Provide, maintain, and improve our services</li>
          <li>Process your transactions</li>
          <li>Send you technical notices and support messages</li>
          <li>Respond to your comments and questions</li>
        </ul>

        <h2 className="text-2xl font-semibold text-white">Data Storage and Security</h2>
        <p>We implement appropriate security measures to protect your personal information. Your PDF files are automatically deleted from our servers after processing unless you explicitly request otherwise.</p>
      </div>
      <Link to="/" className="inline-block mt-8 text-blue-400 hover:text-blue-300">← Back to Home</Link>
    </div>
  </div>
);

const CookiePolicy = () => (
  <div className="min-h-screen bg-black text-white px-4 py-16">
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Cookie Policy</h1>
      <div className="space-y-6 text-gray-300">
        <p>This Cookie Policy explains how pdfXtractor uses cookies and similar technologies to recognize you when you visit our website.</p>
        
        <h2 className="text-2xl font-semibold text-white">What are cookies?</h2>
        <p>Cookies are small data files that are placed on your computer or mobile device when you visit a website. They are widely used by website owners to make their websites work, or to work more efficiently, as well as to provide reporting information.</p>

        <h2 className="text-2xl font-semibold text-white">How we use cookies</h2>
        <p>We use cookies for the following purposes:</p>
        <ul className="list-disc pl-6 space-y-2">
          <li>Authentication - To remember your login state</li>
          <li>Preferences - To remember your preferences and settings</li>
          <li>Analytics - To understand how you use our service</li>
          <li>Security - To help maintain the security of our service</li>
        </ul>

        <h2 className="text-2xl font-semibold text-white">Your choices regarding cookies</h2>
        <p>You can set your browser to refuse all or some browser cookies, or to alert you when websites set or access cookies. If you disable or refuse cookies, please note that some parts of the website may become inaccessible or not function properly.</p>
      </div>
      <Link to="/" className="inline-block mt-8 text-blue-400 hover:text-blue-300">← Back to Home</Link>
    </div>
  </div>
);

// Main App Component
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/process" element={<ProcessPage />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/terms" element={<TermsOfService />} />
        <Route path="/privacy" element={<PrivacyPolicy />} />
        <Route path="/cookies" element={<CookiePolicy />} />
      </Routes>
    </Router>
  );
}

export default App;
