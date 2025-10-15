import { useState, useEffect } from 'react'
import axios from 'axios'
import { motion } from 'framer-motion'
import { CheckCircle, XCircle, Loader2, BarChart3, History, FileText, TrendingUp } from 'lucide-react'

const API_BASE_URL = 'http://localhost:8002'

function App() {
  const [serverStatus, setServerStatus] = useState('checking')
  const [serverMessage, setServerMessage] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [reviewResult, setReviewResult] = useState(null)
  const [error, setError] = useState('')
  const [exportPdf, setExportPdf] = useState(false)
  const [activeTab, setActiveTab] = useState('upload')
  const [reviewHistory, setReviewHistory] = useState([])
  const [historyStats, setHistoryStats] = useState(null)
  const [loadingHistory, setLoadingHistory] = useState(false)

  useEffect(() => {
    checkServerConnection()
    if (activeTab === 'dashboard') {
      fetchReviewHistory()
      fetchHistoryStats()
    }
  }, [activeTab])

  const checkServerConnection = async () => {
    try {
      setServerStatus('checking')
      const response = await axios.get(`${API_BASE_URL}/ping`)
      setServerMessage(response.data.message)
      setServerStatus('connected')
    } catch (error) {
      console.error('Failed to connect to server:', error)
      setServerMessage('Failed to connect to server')
      setServerStatus('error')
    }
  }

  const getStatusIcon = () => {
    switch (serverStatus) {
      case 'checking':
        return <Loader2 className="h-5 w-5 animate-spin text-blue-500" />
      case 'connected':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />
      default:
        return null
    }
  }

  const getStatusColor = () => {
    switch (serverStatus) {
      case 'checking':
        return 'text-blue-600'
      case 'connected':
        return 'text-green-600'
      case 'error':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  const fetchReviewHistory = async () => {
    try {
      setLoadingHistory(true)
      const response = await axios.get(`${API_BASE_URL}/api/history/`)
      setReviewHistory(response.data.reviews)
    } catch (err) {
      console.error('Error fetching review history:', err)
    } finally {
      setLoadingHistory(false)
    }
  }

  const fetchHistoryStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/history/stats/summary`)
      setHistoryStats(response.data)
    } catch (err) {
      console.error('Error fetching history stats:', err)
    }
  }

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (file) {
      setSelectedFile(file)
      setError('')
      setReviewResult(null)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first')
      return
    }

    setUploading(true)
    setError('')
    setReviewResult(null)

        try {
          const formData = new FormData()
          formData.append('file', selectedFile)

          const url = exportPdf 
            ? `${API_BASE_URL}/api/upload?export_pdf=true`
            : `${API_BASE_URL}/api/upload`

          const response = await axios.post(url, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          })

          setReviewResult(response.data)
          // Refresh dashboard data if we're on the dashboard tab
          if (activeTab === 'dashboard') {
            fetchReviewHistory()
            fetchHistoryStats()
          }
        } catch (err) {
          setError(err.response?.data?.detail || 'Upload failed. Please try again.')
        } finally {
          setUploading(false)
        }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-4xl mx-auto"
        >
          {/* Header */}
          <div className="text-center mb-12">
            <motion.h1
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-5xl font-bold text-slate-900 dark:text-slate-100 mb-4"
            >
              Code Review Assistant
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="text-xl text-slate-600 dark:text-slate-400"
            >
              Automatically review source code using AI
            </motion.p>
          </div>

          {/* Tab Navigation */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="flex justify-center mb-8"
          >
            <div className="bg-white dark:bg-slate-800 rounded-lg p-1 shadow-lg">
              <button
                onClick={() => setActiveTab('upload')}
                className={`px-6 py-3 rounded-md font-medium transition-colors duration-200 flex items-center space-x-2 ${
                  activeTab === 'upload'
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
                }`}
              >
                <FileText className="h-4 w-4" />
                <span>Upload & Review</span>
              </button>
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`px-6 py-3 rounded-md font-medium transition-colors duration-200 flex items-center space-x-2 ${
                  activeTab === 'dashboard'
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
                }`}
              >
                <BarChart3 className="h-4 w-4" />
                <span>Dashboard</span>
              </button>
            </div>
          </motion.div>

          {/* Server Status Card */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-8 mb-8"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">
                Server Status
              </h2>
              <button
                onClick={checkServerConnection}
                className="px-4 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 rounded-lg transition-colors duration-200 text-sm font-medium"
              >
                Refresh
              </button>
            </div>
            
            <div className="flex items-center space-x-3">
              {getStatusIcon()}
              <span className={`font-medium ${getStatusColor()}`}>
                {serverStatus === 'checking' && 'Checking connection...'}
                {serverStatus === 'connected' && 'Connected to server'}
                {serverStatus === 'error' && 'Connection failed'}
              </span>
            </div>
            
            {serverMessage && (
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="mt-3 text-slate-600 dark:text-slate-400"
              >
                {serverMessage}
              </motion.p>
            )}
          </motion.div>

          {/* Upload Tab Content */}
          {activeTab === 'upload' && (
            <>
              {/* File Upload Section */}
              <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-8 mb-8"
          >
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100 mb-6">
              Upload Code for Review
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Select a code file
                </label>
                <input
                  type="file"
                  accept=".py,.js,.java,.cpp,.c,.ts,.go,.rs,.php,.rb,.txt"
                  onChange={handleFileSelect}
                  className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 dark:file:bg-blue-900 dark:file:text-blue-300"
                />
                <p className="text-xs text-slate-500 mt-1">
                  Supported formats: .py, .js, .java, .cpp, .c, .ts, .go, .rs, .php, .rb, .txt (max 200KB)
                </p>
              </div>

                {selectedFile && (
                  <div className="p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
                    <p className="text-sm text-slate-700 dark:text-slate-300">
                      Selected: <span className="font-medium">{selectedFile.name}</span> 
                      <span className="text-slate-500"> ({(selectedFile.size / 1024).toFixed(1)} KB)</span>
                    </p>
                  </div>
                )}

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="exportPdf"
                    checked={exportPdf}
                    onChange={(e) => setExportPdf(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="exportPdf" className="text-sm text-slate-700 dark:text-slate-300">
                    Generate PDF report
                  </label>
                </div>

              <button
                onClick={handleUpload}
                disabled={!selectedFile || uploading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center"
              >
                {uploading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin mr-2" />
                    Analyzing Code...
                  </>
                ) : (
                  'Review Code'
                )}
              </button>

              {error && (
                <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
                </div>
              )}
            </div>
          </motion.div>

          {/* Review Results */}
          {reviewResult && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-8 mb-8"
            >
              <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100 mb-6">
                Code Review Results
              </h2>
              
              <div className="space-y-6">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-2">File Information</h3>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      <strong>File:</strong> {reviewResult.filename}<br/>
                      <strong>Language:</strong> {reviewResult.language}<br/>
                      <strong>Size:</strong> {reviewResult.file_size} MB<br/>
                      <strong>Processing Time:</strong> {reviewResult.processing_time}s
                    </p>
                  </div>
                  <div>
                    <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-2">Overall Score</h3>
                    <div className="flex items-center">
                      <div className="text-3xl font-bold text-blue-600">{reviewResult.overall_score}</div>
                      <div className="text-sm text-slate-500 ml-2">/ 10</div>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-2">Summary</h3>
                  <p className="text-sm text-slate-600 dark:text-slate-400">{reviewResult.summary}</p>
                </div>

                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-2">Readability</h3>
                    <p className="text-sm text-slate-600 dark:text-slate-400">{reviewResult.readability}</p>
                  </div>
                  <div>
                    <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-2">Modularity</h3>
                    <p className="text-sm text-slate-600 dark:text-slate-400">{reviewResult.modularity}</p>
                  </div>
                  <div>
                    <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-2">Potential Bugs</h3>
                    <p className="text-sm text-slate-600 dark:text-slate-400">{reviewResult.potential_bugs}</p>
                  </div>
                </div>

                {reviewResult.suggestions && reviewResult.suggestions.length > 0 && (
                  <div>
                    <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-2">Suggestions</h3>
                    <ul className="list-disc list-inside space-y-1">
                      {reviewResult.suggestions.map((suggestion, index) => (
                        <li key={index} className="text-sm text-slate-600 dark:text-slate-400">{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {reviewResult.issues_by_severity && Object.values(reviewResult.issues_by_severity).some(issues => issues.length > 0) && (
                  <div>
                    <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-4">Issues Found</h3>
                    
                    {/* Critical Issues */}
                    {reviewResult.issues_by_severity.critical && reviewResult.issues_by_severity.critical.length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-sm font-medium text-red-600 dark:text-red-400 mb-2">
                          Critical Issues ({reviewResult.issues_by_severity.critical.length})
                        </h4>
                        <div className="space-y-2">
                          {reviewResult.issues_by_severity.critical.map((issue, index) => (
                            <div key={index} className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-sm font-medium text-slate-900 dark:text-slate-100">
                                  Line {issue.line_number} - {issue.type}
                                </span>
                                <span className="text-xs px-2 py-1 rounded bg-red-100 text-red-800">
                                  critical
                                </span>
                              </div>
                              <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">{issue.description}</p>
                              {issue.suggestion && (
                                <p className="text-xs text-blue-600 dark:text-blue-400">💡 {issue.suggestion}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* High Issues */}
                    {reviewResult.issues_by_severity.high && reviewResult.issues_by_severity.high.length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-sm font-medium text-orange-600 dark:text-orange-400 mb-2">
                          High Priority Issues ({reviewResult.issues_by_severity.high.length})
                        </h4>
                        <div className="space-y-2">
                          {reviewResult.issues_by_severity.high.map((issue, index) => (
                            <div key={index} className="p-3 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg">
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-sm font-medium text-slate-900 dark:text-slate-100">
                                  Line {issue.line_number} - {issue.type}
                                </span>
                                <span className="text-xs px-2 py-1 rounded bg-orange-100 text-orange-800">
                                  high
                                </span>
                              </div>
                              <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">{issue.description}</p>
                              {issue.suggestion && (
                                <p className="text-xs text-blue-600 dark:text-blue-400">💡 {issue.suggestion}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Medium Issues */}
                    {reviewResult.issues_by_severity.medium && reviewResult.issues_by_severity.medium.length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-sm font-medium text-yellow-600 dark:text-yellow-400 mb-2">
                          Medium Priority Issues ({reviewResult.issues_by_severity.medium.length})
                        </h4>
                        <div className="space-y-2">
                          {reviewResult.issues_by_severity.medium.map((issue, index) => (
                            <div key={index} className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-sm font-medium text-slate-900 dark:text-slate-100">
                                  Line {issue.line_number} - {issue.type}
                                </span>
                                <span className="text-xs px-2 py-1 rounded bg-yellow-100 text-yellow-800">
                                  medium
                                </span>
                              </div>
                              <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">{issue.description}</p>
                              {issue.suggestion && (
                                <p className="text-xs text-blue-600 dark:text-blue-400">💡 {issue.suggestion}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Low Issues */}
                    {reviewResult.issues_by_severity.low && reviewResult.issues_by_severity.low.length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-sm font-medium text-green-600 dark:text-green-400 mb-2">
                          Low Priority Issues ({reviewResult.issues_by_severity.low.length})
                        </h4>
                        <div className="space-y-2">
                          {reviewResult.issues_by_severity.low.map((issue, index) => (
                            <div key={index} className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-sm font-medium text-slate-900 dark:text-slate-100">
                                  Line {issue.line_number} - {issue.type}
                                </span>
                                <span className="text-xs px-2 py-1 rounded bg-green-100 text-green-800">
                                  low
                                </span>
                              </div>
                              <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">{issue.description}</p>
                              {issue.suggestion && (
                                <p className="text-xs text-blue-600 dark:text-blue-400">💡 {issue.suggestion}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Quality Metrics */}
                {reviewResult.quality_metrics && (
                  <div>
                    <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-4">Quality Metrics</h3>
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
                        <h4 className="text-sm font-medium text-slate-900 dark:text-slate-100 mb-2">Complexity Score</h4>
                        <div className="text-2xl font-bold text-blue-600">{reviewResult.quality_metrics.complexity_score}/10</div>
                      </div>
                      <div className="p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
                        <h4 className="text-sm font-medium text-slate-900 dark:text-slate-100 mb-2">Maintainability Score</h4>
                        <div className="text-2xl font-bold text-green-600">{reviewResult.quality_metrics.maintainability_score}/10</div>
                      </div>
                    </div>
                  </div>
                )}

                {/* PDF Download */}
                {reviewResult.pdf_report && (
                  <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                    <h3 className="font-medium text-blue-900 dark:text-blue-100 mb-2">📄 PDF Report Available</h3>
                    <p className="text-sm text-blue-700 dark:text-blue-300 mb-3">
                      A detailed PDF report has been generated for your code review.
                    </p>
                    <a
                      href={`http://localhost:8002${reviewResult.pdf_report}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors duration-200"
                    >
                      📥 Download PDF Report
                    </a>
                  </div>
                )}

                {reviewResult.pdf_error && (
                  <div className="mt-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                    <p className="text-sm text-yellow-700 dark:text-yellow-300">
                      ⚠️ {reviewResult.pdf_error}
                    </p>
                  </div>
                )}
              </div>
            </motion.div>
          )}

              {/* Feature Preview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="grid md:grid-cols-3 gap-6"
          >
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2">
                Code Analysis
              </h3>
              <p className="text-slate-600 dark:text-slate-400">
                Upload your code files and get comprehensive AI-powered reviews
              </p>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2">
                Quality Metrics
              </h3>
              <p className="text-slate-600 dark:text-slate-400">
                Get detailed insights on code quality, performance, and best practices
              </p>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2">
                Fast Processing
              </h3>
              <p className="text-slate-600 dark:text-slate-400">
                Quick turnaround times with our optimized AI processing pipeline
              </p>
            </div>
          </motion.div>
            </>
          )}

          {/* Dashboard Tab Content */}
          {activeTab === 'dashboard' && (
            <>
              {/* Statistics Cards */}
              {historyStats && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                  className="grid md:grid-cols-4 gap-6 mb-8"
                >
                  <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Total Reviews</p>
                        <p className="text-3xl font-bold text-slate-900 dark:text-slate-100">{historyStats.total_reviews}</p>
                      </div>
                      <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                        <FileText className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                      </div>
                    </div>
                  </div>

                  <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Average Score</p>
                        <p className="text-3xl font-bold text-slate-900 dark:text-slate-100">{historyStats.average_score}/10</p>
                      </div>
                      <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
                        <TrendingUp className="w-6 h-6 text-green-600 dark:text-green-400" />
                      </div>
                    </div>
                  </div>

                  <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Total Issues</p>
                        <p className="text-3xl font-bold text-slate-900 dark:text-slate-100">{historyStats.total_issues}</p>
                      </div>
                      <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900 rounded-lg flex items-center justify-center">
                        <BarChart3 className="w-6 h-6 text-orange-600 dark:text-orange-400" />
                      </div>
                    </div>
                  </div>

                  <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Recent Reviews</p>
                        <p className="text-3xl font-bold text-slate-900 dark:text-slate-100">{historyStats.recent_reviews}</p>
                      </div>
                      <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center">
                        <History className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Language Distribution */}
              {historyStats && historyStats.languages && Object.keys(historyStats.languages).length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.5 }}
                  className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-8 mb-8"
                >
                  <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-6">Language Distribution</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(historyStats.languages).map(([language, count]) => (
                      <div key={language} className="text-center p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
                        <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">{count}</p>
                        <p className="text-sm text-slate-600 dark:text-slate-400">{language}</p>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Review History */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.6 }}
                className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-8"
              >
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Review History</h3>
                  <button
                    onClick={() => {
                      fetchReviewHistory()
                      fetchHistoryStats()
                    }}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200 text-sm font-medium flex items-center space-x-2"
                  >
                    <History className="h-4 w-4" />
                    <span>Refresh</span>
                  </button>
                </div>

                {loadingHistory ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                    <span className="ml-2 text-slate-600 dark:text-slate-400">Loading history...</span>
                  </div>
                ) : reviewHistory.length === 0 ? (
                  <div className="text-center py-8">
                    <FileText className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                    <p className="text-slate-600 dark:text-slate-400">No reviews found. Upload some code to get started!</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {reviewHistory.map((review) => (
                      <div key={review.id} className="border border-slate-200 dark:border-slate-700 rounded-lg p-4 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors duration-200">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <h4 className="font-medium text-slate-900 dark:text-slate-100">{review.filename}</h4>
                              <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded-full">
                                {review.language}
                              </span>
                              <span className={`px-2 py-1 text-xs rounded-full ${
                                review.overall_score >= 8 ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200' :
                                review.overall_score >= 6 ? 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200' :
                                'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                              }`}>
                                {review.overall_score}/10
                              </span>
                            </div>
                            <div className="flex items-center space-x-4 text-sm text-slate-600 dark:text-slate-400">
                              <span>{review.file_size} MB</span>
                              <span>{review.processing_time}s</span>
                              <span>{review.total_issues} issues</span>
                              <span>{new Date(review.created_at).toLocaleDateString()}</span>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            {review.critical_issues > 0 && (
                              <span className="px-2 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 text-xs rounded-full">
                                {review.critical_issues} critical
                              </span>
                            )}
                            {review.high_issues > 0 && (
                              <span className="px-2 py-1 bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 text-xs rounded-full">
                                {review.high_issues} high
                              </span>
                            )}
                            {review.medium_issues > 0 && (
                              <span className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 text-xs rounded-full">
                                {review.medium_issues} medium
                              </span>
                            )}
                            {review.low_issues > 0 && (
                              <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs rounded-full">
                                {review.low_issues} low
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </motion.div>
            </>
          )}
        </motion.div>
      </div>
    </div>
  )
}

export default App
