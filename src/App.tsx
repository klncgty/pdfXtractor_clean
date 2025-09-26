import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import { Upload, Download, Send, FileUp, Sparkles, ArrowRight, Coffee } from 'lucide-react';
import axios from 'axios';
import llmImage from './llm_formats.png';
import octoLogo from './octo.png';
import './index.css';

// Animated rolling CSV/JSON başlık bileşeni
const AnimatedLLMTitle = () => {
  const [showCSV, setShowCSV] = useState(true);
  useEffect(() => {
    const interval = setInterval(() => setShowCSV(v => !v), 1700);
    return () => clearInterval(interval);
  }, []);
  return (
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
      }}
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
    </h2>
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

const PartnerLogos = () => null;

const FloatingPanel = () => null;

interface UserInfo {
  id?: number;
  name?: string;
  email: string;
  pages_processed_this_month?: number;
  monthly_page_limit?: number;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const UserDropdown = () => {
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
        }
      });
      
      if (res.data && res.data.id) {
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
      console.log('🔄 Checking authentication...');
      const res = await axios.get(`${API_URL}/auth/me`, {
        withCredentials: true,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      });
      
      console.log('✅ Auth response:', res.data);
      
      if (res.data && res.data.id) {
        setUser(res.data);
        console.log('✅ User authenticated:', res.data);
      } else {
        setUser(null);
        console.log('❌ User not authenticated');
      }
    } catch (error) {
      console.error('❌ Auth check failed:', error);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };
  
  useEffect(() => {
    checkAuth();
    
    // Check session status every 5 minutes
    const interval = setInterval(checkAuth, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);
  
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
          <a href="#llm">LLM</a>
          {isLoading ? (
            <div className="animate-pulse h-8 w-24 bg-gray-200 rounded"></div>
          ) : user ? (
            // Wrapper handles hover so moving between button and menu doesn't close it
            <div className="relative" onMouseEnter={() => setShowDropdown(true)} onMouseLeave={() => setShowDropdown(false)}>
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
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <div className="main-bg min-h-screen w-screen flex flex-col bg-black relative" style={{ minHeight: '100vh', minWidth: '100vw' }}>
      <VantaBirdsBackground />
      <Navbar />
      <main className="main-content flex-1 flex flex-col items-center justify-center w-full" style={{ minHeight: '100vh', paddingTop: 96, boxSizing: 'border-box' }}>
        <section className="hero-section" style={{ marginBottom: 64, textAlign: 'center', zIndex: 2 }}>
          <h1 className="hero-title" style={{ fontSize: '2.7rem', color: '#fff', fontWeight: 800, marginBottom: 10, letterSpacing: 1.1, lineHeight: 1.15, fontFamily: "'Outfit', 'Space Grotesk', sans-serif" }}>
            Transform your PDF documents into actionable data
          </h1>
          <p style={{ fontSize: '1.25rem', color: '#cbd5e1', fontWeight: 500, marginBottom: 0, letterSpacing: 0.2, lineHeight: 1.3 }}>
            Extract your complex PDFs.
          </p>
          <div className="w-full flex justify-center items-center mt-9">
            {isAuthenticated === true ? (
              <Link to="/process">
                <button className="start-free-btn mx-auto">Process PDF</button>
              </Link>
            ) : (
              <button
                className="start-free-btn mx-auto"
                onClick={handleLogin}
              >
                START FOR FREE
              </button>
            )}
          </div>
        </section>
        {/* passing to llm bölümü */}
        <section id="llm" ref={llmRef} style={{ width: '100%', maxWidth: 700, margin: '80px auto 0 auto', zIndex: 2, background: 'none', textAlign: 'left' }}>
          {/* Animasyonlu başlık */}
          <AnimatedLLMTitle />
          <div className="llm-blocks-container" style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 32, gap: 0, width: '100%' }}>
            <div className={`llm-block-sentence ${showLLM ? 'fade-in-block' : ''}`} style={{ fontSize: 17, color: '#fff', fontWeight: 400, marginBottom: 16, maxWidth: 220, textAlign: 'left', transition: 'opacity 0.7s, transform 0.7s', opacity: showLLM ? 1 : 0, transform: showLLM ? 'translateX(0)' : 'translateX(-40px)', background: 'transparent', padding: '18px 18px', zIndex: 10, fontFamily: "'Share Tech Mono', 'Courier New', monospace" }}>
              Large Language Models (LLMs) process structured, standard formats like <b>CSV</b> and <b>JSON</b> with higher accuracy and efficiency.
            </div>
            <div className={`llm-block-sentence ${showLLM ? 'fade-in-block-delay1' : ''}`} style={{ fontSize: 17, color: '#fff', fontWeight: 400, marginBottom: 16, maxWidth: 320, textAlign: 'center', marginLeft: 'auto', marginRight: 'auto', transition: 'opacity 0.7s 0.3s, transform 0.7s 0.3s', opacity: showLLM ? 1 : 0, transform: showLLM ? 'translateX(0)' : 'translateX(-40px)', background: 'transparent', padding: '18px 18px', zIndex: 10, fontFamily: "'Share Tech Mono', 'Courier New', monospace" }}>
              These formats keep your data organized, consistent, and machine-readable—making it easier for the model to understand, analyze, and generate correct results.
            </div>
            <div className={`llm-block-sentence ${showLLM ? 'fade-in-block-delay2' : ''}`} style={{ fontSize: 17, color: '#fff', fontWeight: 400, marginBottom: 16, maxWidth: 220, textAlign: 'right', transition: 'opacity 0.7s 0.6s, transform 0.7s 0.6s', opacity: showLLM ? 1 : 0, transform: showLLM ? 'translateX(0)' : 'translateX(-40px)', background: 'transparent', padding: '18px 18px', zIndex: 10, fontFamily: "'Share Tech Mono', 'Courier New', monospace" }}>
              Unstructured or messy formats increase error risk and reduce model performance.
            </div>
          </div>
          <div style={{ textAlign: 'center', marginTop: 32 }}>
            <img src={llmImage} alt="llm format accuracy" style={{ width: '100%', maxWidth: 600, borderRadius: 14, boxShadow: '0 2px 12px rgba(0,0,0,0.10)' }} />
          </div>
        </section>
      </main>
    </div>
  );
};

// PDF Processing Page Component
const ProcessPage = () => {
  const [file, setFile] = useState<File | null>(null);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState<ProcessResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadInfo, setUploadInfo] = useState<{ pdf_id?: number; pages_total?: number; pages_processed?: number; limit_left?: number } | null>(null);
  const [showUploadPopup, setShowUploadPopup] = useState(false);
  const [tableQuestions, setTableQuestions] = useState<{ [key: number]: TableQuestion }>({});
  const [tableData, setTableData] = useState<{ [key: number]: any }>({});
  const [loadingQuestions, setLoadingQuestions] = useState<{ [key: number]: boolean }>({});
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

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError(null);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a PDF file');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Authenticated upload to endpoint that counts pages and reserves quota
      const uploadResponse = await axios.post(`${API_URL}/upload_pdf`, formData, { withCredentials: true });

      // Show popup with upload info
      setUploadInfo(uploadResponse.data);
      setShowUploadPopup(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setUploading(false);
    }
  };

  const handleStartProcessing = async () => {
    if (!file || !uploadInfo) return;
    setProcessing(true);
    setShowUploadPopup(false);
    try {
      // pages_processed tells how many pages will be processed for this upload
      const pagesToProcess = uploadInfo.pages_processed || 0;
      const processResponse = await axios.get<ProcessResponse>(
        `${API_URL}/process/${file.name}?output_format=both&pages_limit=${pagesToProcess}`,
        { withCredentials: true }
      );

      setResults(processResponse.data);

      for (let i = 0; i < processResponse.data.tables.length; i++) {
        const table = processResponse.data.tables[i];
        if (table.json_file) {
          const jsonResponse = await axios.get(`${API_URL}/download/${table.json_file}`);
          setTableData(prev => ({
            ...prev,
            [i]: jsonResponse.data
          }));
        }
      }

      // refresh user quota in dropdown by triggering a re-check; simple approach: reload page or refetch user
      window.location.reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during processing');
    } finally {
      setProcessing(false);
    }
  };

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
      setError(err instanceof Error ? err.message : 'Download failed');
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
      setError(err instanceof Error ? err.message : 'Failed to get answer');
    } finally {
      setLoadingQuestions(prev => ({ ...prev, [tableIndex]: false }));
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
        {!results ? (
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
            
            {file && (
              <button
                onClick={handleUpload}
                className="mt-6 px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg 
                  transition-colors duration-200 flex items-center gap-2"
                disabled={uploading}
              >
                {uploading ? (
                  <Upload className="w-5 h-5 animate-spin" />
                ) : (
                  <ArrowRight className="w-5 h-5" />
                )}
                {uploading ? 'Uploading...' : 'Process PDF'}
              </button>
            )}
            {showUploadPopup && uploadInfo && (
              <div className="fixed inset-0 z-60 flex items-center justify-center">
                <div className="absolute inset-0 bg-black/50" onClick={() => setShowUploadPopup(false)} />
                <div className="relative bg-white rounded-lg p-6 w-full max-w-md z-70">
                  <h3 className="text-lg font-semibold">Upload complete</h3>
                  <p className="mt-2 text-sm text-gray-600">Pages in file: {uploadInfo.pages_total}</p>
                  <p className="mt-1 text-sm text-gray-600">Pages reserved for processing: {uploadInfo.pages_processed}</p>
                  <p className="mt-1 text-sm text-gray-600">Your remaining quota after this: {uploadInfo.limit_left}</p>
                  <div className="mt-4 flex justify-end gap-2">
                    <button onClick={() => setShowUploadPopup(false)} className="px-4 py-2 bg-gray-200 rounded">Cancel</button>
                    <button onClick={handleStartProcessing} className="px-4 py-2 bg-blue-600 text-white rounded">Process</button>
                  </div>
                </div>
              </div>
            )}
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-8">
            <h2 className="text-3xl font-bold text-white text-center mb-8">
              Processed Tables ({results.total_tables})
            </h2>
            
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
                        JSON
                      </button>
                    )}
                    {table.csv_file && (
                      <button
                        onClick={() => handleDownload(table.csv_file!)}
                        className="flex items-center px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 
                          text-purple-400 rounded-lg transition-colors duration-200"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        CSV
                      </button>
                    )}
                  </div>

                  <div className="space-y-4">
                    <div className="flex gap-2 question-input-mobile">
                      <input
                        type="text"
                        value={tableQuestions[index]?.question || ''}
                        onChange={(e) => handleQuestionChange(index, e.target.value)}
                        className="flex-1 px-4 py-2 bg-black/20 border border-white/10 rounded-lg
                          focus:outline-none focus:border-blue-500/50 text:white placeholder-gray-500"
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
          </div>
        )}
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



// Main App Component
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/process" element={<ProcessPage />} />
      </Routes>
    </Router>
  );
}

export default App;
