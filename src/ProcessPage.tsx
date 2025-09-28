import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Upload, Download, Send, FileUp, Coffee } from 'lucide-react';
import axios from 'axios';
import octoLogo from './octo.png';
import { UserDropdown } from './App';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ProcessResponse {
  tables: ProcessedTable[];
  total_tables: number;
}

interface ProcessedTable {
  data_file?: string;
  json_file?: string;
  csv_file?: string;
  image_file: string;
}

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
        console.error('Upload error:', err);
        if (axios.isAxiosError(err)) {
          // Backend'den gelen özel hata mesajı
          const errorMessage = err.response?.data?.detail || err.response?.data?.message || err.message;
          setError(errorMessage);
        } else {
          setError(err instanceof Error ? err.message : 'An error occurred during upload');
        }
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
      );
      const newTableData: { [key: number]: any } = {};
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
      console.error('Processing error:', err);
      if (axios.isAxiosError(err)) {
        // Backend'den gelen özel hata mesajı
        const errorMessage = err.response?.data?.detail || err.response?.data?.message || err.message;
        setError(errorMessage);
      } else {
        setError(err instanceof Error ? err.message : 'An error occurred during processing');
      }
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
              <img src={octoLogo} alt="Octro Logo" className="w-8 h-8" />
              <span className="ml-2 text-xl font-bold text-white">Octro</span>
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
                  icon: <Download className="w-6 h-6 text-purple-500" />,
                  title: 'AI-Powered',
                  description: 'Advanced AI processing for accurate table extraction'
                },
                {
                  icon: <Send className="w-6 h-6 text-green-500" />,
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
                  <Send className="w-5 h-5" />
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
                        <Upload className="w-4 h-4" />
                      </Link>
                    ) : (
                      <button 
                        onClick={handleStartProcessing}
                        className="px-6 py-2 bg-blue-500 hover:bg-blue-600 
                          text-white rounded-lg transition-colors duration-200 flex items-center gap-2"
                      >
                        Process Now
                        <Send className="w-4 h-4" />
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

export default ProcessPage;