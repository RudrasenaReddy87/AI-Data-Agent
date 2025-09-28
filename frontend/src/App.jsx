import { useState, useEffect, useRef } from 'react'
import { Bar, Line } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js'
import { FaBrain, FaHome, FaHistory, FaChartPie, FaCog, FaFileExcel, FaCloudUploadAlt, FaPaperPlane, FaLightbulb, FaRobot, FaChartBar, FaTable, FaTimes, FaRedo, FaUser } from 'react-icons/fa'
import dayjs from 'dayjs'
import * as XLSX from 'xlsx'
import './App.css'
import Login from './Login'

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend)

const API_BASE = 'https://backend-production-f293b.up.railway.app'

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [token, setToken] = useState('')
  const [username, setUsername] = useState('')
  const [file, setFile] = useState(null)
  const [data, setData] = useState(null)
  const [filePath, setFilePath] = useState(null)
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [chatName, setChatName] = useState('')
  const [showMenu, setShowMenu] = useState(false)
  const [darkMode, setDarkMode] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [showWelcome, setShowWelcome] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [fileList, setFileList] = useState([])
  const [dragActive, setDragActive] = useState(false)
  const [numberOfSheets, setNumberOfSheets] = useState(0)
  const [isTyping, setIsTyping] = useState(false)
  const [typingMessage, setTypingMessage] = useState('')
  const [fullTypingMessage, setFullTypingMessage] = useState('')
  const [currentResult, setCurrentResult] = useState(null)
  const messagesEndRef = useRef(null)

  const formatFileSize = (bytes) => {
    const kb = bytes / 1024;
    if (kb < 999) {
      return kb.toFixed(1) + ' KB';
    } else {
      return (kb / 1024).toFixed(1) + ' MB';
    }
  }

  const parseExcelFile = (file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const data = new Uint8Array(e.target.result);
      const workbook = XLSX.read(data, { type: 'array' });
      setNumberOfSheets(workbook.SheetNames.length);
    };
    reader.readAsArrayBuffer(file);
  }

  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    const storedUsername = localStorage.getItem('username')
    if (storedToken && storedUsername) {
      setToken(storedToken)
      setUsername(storedUsername)
      setIsLoggedIn(true)
    }
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, typingMessage])

  useEffect(() => {
    if (isTyping && fullTypingMessage) {
      const interval = setInterval(() => {
        setTypingMessage(prev => {
          const nextIndex = prev.length
          if (nextIndex < fullTypingMessage.length) {
            return prev + fullTypingMessage[nextIndex]
          } else {
            clearInterval(interval)
            setIsTyping(false)
            setMessages(prev => [...prev, { type: 'question', content: question, timestamp: dayjs() }, { type: 'answer', content: { ...currentResult, answer: fullTypingMessage }, timestamp: dayjs() }])
            setQuestion('')
            setTypingMessage('')
            setFullTypingMessage('')
            setCurrentResult(null)
            return prev
          }
        })
      }, 30) // Adjust speed as needed
      return () => clearInterval(interval)
    }
  }, [isTyping, fullTypingMessage, question, currentResult])

  const handleLogin = async (email, password) => {
    const response = await fetch(`${API_BASE}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })
    const result = await response.json()
    if (response.ok) {
      setToken(result.access_token)
      setIsLoggedIn(true)
      localStorage.setItem('token', result.access_token)

      // Fetch user info to get username
      const meResponse = await fetch(`${API_BASE}/me`, {
        headers: { 'Authorization': `Bearer ${result.access_token}` }
      })
      if (meResponse.ok) {
        const user = await meResponse.json()
        setUsername(user.username)
        localStorage.setItem('username', user.username)
      }
    } else {
      throw new Error(result.detail)
    }
  }

  const handleRegister = async (username, email, password) => {
    const response = await fetch(`${API_BASE}/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    })
    const result = await response.json()
    if (response.ok) {
      // Success handled in Login component
    } else {
      throw new Error(result.detail)
    }
  }

  const handleLogout = () => {
    setIsLoggedIn(false)
    setToken('')
    setUsername('')
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    setData(null)
    setFilePath(null)
    setMessages([])
  }

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
  }

  const handleUpload = async () => {
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    try {
      const response = await fetch(`${API_BASE}/upload-excel`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })
      const result = await response.json()
      if (response.ok) {
        setData(result)
        setFilePath(result.file_path)
        const uploadMessage = { type: 'upload', content: result, timestamp: dayjs() }
        const welcomeMessage = {
          type: 'answer',
          content: {
            answer: "Hello! I'm your Excel data assistant. I can help you analyze your data. What would you like to know?\n\nTry asking questions like:\n\nWhat are the total sales by category?\nShow me trends over time\nWhich items are performing best?\nWhat is the average value of [column]?\nHow many rows contain [condition]?\nShow me data grouped by [column]\nWhat are the top 10 values in [column]?"
          },
          timestamp: dayjs()
        }
        setMessages([uploadMessage, welcomeMessage])
        setChatName(file.name)
        setFileList(prev => [...prev, { name: file.name, path: result.file_path, uploadedAt: dayjs().format('MMM D, YYYY • h:mm A'), size: formatFileSize(file.size) }])
        setSelectedFile({ name: file.name, path: result.file_path })
        setShowWelcome(false)
      } else {
        if (response.status === 401) {
          alert('Session expired. Please log in again.')
          setIsLoggedIn(false)
          localStorage.removeItem('token')
          localStorage.removeItem('username')
          setToken('')
          setUsername('')
          return
        }
        alert(result.detail)
      }
    } catch (error) {
      console.error('Upload error:', error)
    }
  }

  const handleAsk = async () => {
    if (!question || !filePath) return
    setIsLoading(true)
    try {
      const response = await fetch(`${API_BASE}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ question, file_path: filePath })
      })
      const result = await response.json()
      if (response.ok) {
        setCurrentResult(result)
        setIsTyping(true)
        setFullTypingMessage(result.answer)
        setTypingMessage('')
      } else {
        // Handle error response
        const errorMessage = result.detail || 'An error occurred while processing your question.'
        setMessages(prev => [...prev, { type: 'question', content: question, timestamp: dayjs() }, { type: 'answer', content: { answer: `Error: ${errorMessage}` }, timestamp: dayjs() }])
        setQuestion('')
      }
    } catch (error) {
      console.error('Ask error:', error)
      setMessages(prev => [...prev, { type: 'question', content: question, timestamp: dayjs() }, { type: 'answer', content: { answer: 'Network error: Unable to connect to the server. Please try again.' }, timestamp: dayjs() }])
      setQuestion('')
    }
    setIsLoading(false)
  }

  const handleFileSelect = (fileItem) => {
    setSelectedFile(fileItem)
    setFilePath(fileItem.path)
    setData(null)
    setMessages([])
    setShowWelcome(false)
  }

  const handleUploadClick = () => {
    setShowModal(true)
  }

  const handleModalClose = () => {
    setShowModal(false)
    setFile(null)
    setDragActive(false)
    setNumberOfSheets(0)
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      setFile(droppedFile);
      parseExcelFile(droppedFile);
    }
  }

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      parseExcelFile(selectedFile);
    }
  }

  const handleConfirmUpload = async () => {
    if (!file) return
    await handleUpload()
    setShowModal(false)
  }


  if (!isLoggedIn) {
    return <Login onLogin={handleLogin} onRegister={handleRegister} />
  }

  return (
    <div className="app">
      <div className="sidebar">
        <div className="logo">
          <div className="logo-icon">
            <FaBrain />
          </div>
          <h1>Excel AI Analyzer</h1>
        </div>

        <div className="nav-section">
          <h3>Your Files</h3>
          <div className="file-list">
            {fileList.map((fileItem, index) => (
              <div key={index} className={`file-item ${selectedFile?.name === fileItem.name ? 'active' : ''}`} onClick={() => handleFileSelect(fileItem)}>
                <div className="file-icon">
                  <FaFileExcel />
                </div>
                <div className="file-info">
                  <div className="file-name">{fileItem.name}</div>
                  <div className="file-details">{fileItem.uploadedAt} • {fileItem.size}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="nav-section">
          <div className="nav-item" onClick={handleUploadClick}>
            <FaCloudUploadAlt />
            New Project
          </div>
        </div>
      </div>
      <div className="main-content">
        <div className="header">
          <h1>Data Analysis Dashboard</h1>
          <button className="upload-btn" onClick={handleUploadClick}>
            <FaCloudUploadAlt />
            Upload Excel File
          </button>
          <div className="user-info">
            <p>Welcome, {username}!</p>
            <button onClick={handleLogout} className="btn btn-secondary">Logout</button>
          </div>
        </div>
        <div className="content">
          {showWelcome ? (
            <div className="welcome-screen">
              <FaFileExcel className="welcome-icon" />
              <h2>Analyze Your Excel Data with AI</h2>
              <p>Upload an Excel file and ask questions about your data in natural language. Get instant insights, charts, and tables powered by advanced AI.</p>
              <div className="features">
                <div className="feature">
                  <FaRobot />
                  <h4>AI-Powered Analysis</h4>
                  <p>Ask complex questions about your data using natural language</p>
                </div>
                <div className="feature">
                  <FaChartBar />
                  <h4>Smart Visualizations</h4>
                  <p>Automatically generated charts and graphs for your data</p>
                </div>
                <div className="feature">
                  <FaTable />
                  <h4>Data Tables</h4>
                  <p>View summarized data in interactive, filterable tables</p>
                </div>
                <div className="feature">
                  <FaLightbulb />
                  <h4>Key Insights</h4>
                  <p>Get actionable insights and recommendations from your data</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="chat-container">
              <div className="chat-header">
                <div className="file-indicator">
                  <FaFileExcel />
                  <span>Analyzing: {selectedFile?.name}</span>
                </div>
                <div className="chat-actions">
                  <button className="btn btn-secondary" onClick={() => { setMessages([]); setQuestion('') }}>
                    <FaRedo /> New Conversation
                  </button>
                </div>
              </div>
              <div className="chat-messages">
                {messages.map((msg, i) => (
                  <div key={i} className={`message-wrapper ${msg.type === 'question' ? 'user-message-wrapper' : msg.type === 'answer' ? 'ai-message-wrapper' : ''}`}>
                    <div className={`message ${msg.type === 'question' ? 'user-message' : msg.type === 'answer' ? 'ai-message' : ''}`}>
                      <div className="message-avatar">
                        {msg.type === 'question' ? <FaUser className="user-avatar" /> : <FaRobot className="ai-avatar" />}
                      </div>
                      <div className="message-bubble">
                        <div className="message-content">
                          {msg.type === 'upload' && <p>File uploaded with {Object.keys(msg.content.sheets).length} sheets, total {msg.content.total_rows} rows.</p>}
                          {msg.type === 'question' && <p>{msg.content}</p>}
                          {msg.type === 'answer' && (
                            <div>
                              <p>{msg.content.answer}</p>
                              {msg.content.chart && (
                                <div className="chart-container">
                                  {msg.content.chart.title && <h4>{msg.content.chart.title}</h4>}
                                  {msg.content.chart.type === 'bar' && <Bar data={{
                                    labels: msg.content.chart.labels,
                                    datasets: [{ label: 'Data', data: msg.content.chart.data, backgroundColor: 'rgba(99, 102, 241, 0.6)' }]
                                  }} />}
                                  {msg.content.chart.type === 'line' && <Line data={{
                                    labels: msg.content.chart.labels,
                                    datasets: [{ label: 'Data', data: msg.content.chart.data, borderColor: 'rgba(99, 102, 241, 1)', fill: false }]
                                  }} />}
                                </div>
                              )}
                              {msg.content.table && (
                                <div className="table-container">
                                  <table className="data-table">
                                    <thead>
                                      <tr>
                                        {Object.keys(msg.content.table[0] || {}).map(col => <th key={col}>{col}</th>)}
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {msg.content.table.slice(0, 10).map((row, j) => (
                                        <tr key={j}>
                                          {Object.values(row).map((val, k) => <td key={k}>{val}</td>)}
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                  {msg.content.table.length > 10 && <p>... and {msg.content.table.length - 10} more rows</p>}
                                </div>
                              )}
                              {msg.content.insights && (
                                <div className="insights">
                                  <h4><FaLightbulb /> Key Insights</h4>
                                  <ul>
                                    {msg.content.insights.map((insight, k) => <li key={k}>{insight}</li>)}
                                  </ul>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                        <div className="message-timestamp">{dayjs(msg.timestamp).format('h:mm A')}</div>
                      </div>
                    </div>
                  </div>
                ))}
                {isTyping && (
                  <div className="message-wrapper">
                    <div className="message ai-message">
                      <div className="message-avatar">
                        <FaRobot className="ai-avatar" />
                      </div>
                      <div className="message-bubble">
                        <div className="message-content typing">
                          {typingMessage}
                        </div>
                        <div className="message-timestamp">{dayjs().format('h:mm A')}</div>
                      </div>
                    </div>
                  </div>
                )}
                {isLoading && (
                  <div className="message ai-message">
                    <div className="message-content">
                      <div className="loading"></div> Analyzing your data...
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
              <div className="chat-input">
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ask a question about your data... (e.g., 'Show sales by category')"
                  onKeyPress={(e) => e.key === 'Enter' && handleAsk()}
                />
                <button className="send-btn" onClick={handleAsk} disabled={isLoading || !question.trim()}>
                  <FaPaperPlane />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
      {showModal && (
        <div className="modal" style={{ display: 'flex' }}>
          <div className="modal-content">
            <div className="modal-header">
              <h3>Upload Excel File</h3>
              <button className="close-btn" onClick={handleModalClose}>
                <FaTimes />
              </button>
            </div>
            <div className="modal-body">
              <div className={`drop-zone ${dragActive ? 'active' : ''}`} onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop} onClick={() => document.getElementById('fileInput').click()}>
                <FaFileExcel />
                <h3>Drag & Drop Your Excel File</h3>
                <p>or click to browse files</p>
                <p className="small">Supports .xlsx, .xls files up to 10MB</p>
              </div>
              {file && (
                <div className="file-info-modal" style={{ display: 'block' }}>
                  <p><strong>File:</strong> <span>{file.name}</span></p>
                  <p><strong>Size:</strong> <span>{formatFileSize(file.size)}</span></p>
                  <p><strong>Sheets detected:</strong> <span>{numberOfSheets || 'Detecting...'}</span></p>
                </div>
              )}
              <input type="file" id="fileInput" accept=".xlsx,.xls" style={{ display: 'none' }} onChange={handleFileInputChange} />
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={handleModalClose}>Cancel</button>
              <button className="btn btn-primary" onClick={handleConfirmUpload} disabled={!file}>
                {isLoading ? <div className="loading"></div> : 'Upload & Analyze'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
