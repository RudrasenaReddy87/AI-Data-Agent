import { useState, useEffect } from 'react'
import './Login.css'

function Login({ onLogin, onRegister }) {
  const [isLoginMode, setIsLoginMode] = useState(true)
  const [loginForm, setLoginForm] = useState({ email: '', password: '', rememberMe: false })
  const [registerForm, setRegisterForm] = useState({ name: '', email: '', password: '', confirmPassword: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [showLoginPassword, setShowLoginPassword] = useState(false)
  const [showRegisterPassword, setShowRegisterPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [displayedText, setDisplayedText] = useState('')

  const handleToggle = (mode) => {
    setIsLoginMode(mode)
    setError('')
  }

  const handleLoginChange = (e) => {
    const { name, value, type, checked } = e.target
    setLoginForm(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }))
  }

  const handleRegisterChange = (e) => {
    const { name, value } = e.target
    setRegisterForm(prev => ({ ...prev, [name]: value }))
  }

  const handleLoginSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await onLogin(loginForm.email, loginForm.password)
      setSuccessMessage('Login successful! Redirecting...')
      setTimeout(() => setSuccessMessage(''), 2000)
    } catch (err) {
      setError(err.message)
    }
    setLoading(false)
  }

  const handleRegisterSubmit = async (e) => {
    e.preventDefault()
    if (registerForm.password !== registerForm.confirmPassword) {
      setError('Passwords do not match')
      return
    }
    setLoading(true)
    setError('')
    try {
      await onRegister(registerForm.name, registerForm.email, registerForm.password)
      setSuccessMessage('Account created successfully!')
      setTimeout(() => {
        setSuccessMessage('')
        setIsLoginMode(true)
      }, 2000)
    } catch (err) {
      setError(err.message)
    }
    setLoading(false)
  }

  const handleForgotPassword = () => {
    const email = prompt('Please enter your email address:')
    if (email) {
      setSuccessMessage('Password reset instructions sent to your email.')
      setTimeout(() => setSuccessMessage(''), 3000)
    }
  }

  const handleDemoAutofill = (field) => {
    if (field === 'email' && loginForm.email === '') {
      setLoginForm(prev => ({ ...prev, email: 'example@gmail.com' }))
    } else if (field === 'password' && loginForm.password === '') {
      setLoginForm(prev => ({ ...prev, password: 'example' }))
    }
  }

  useEffect(() => {
    const fullText = 'AI Data Agent'
    let i = 0
    const interval = setInterval(() => {
      if (i < fullText.length) {
        setDisplayedText(fullText.slice(0, i + 1))
        i++
      } else {
        clearInterval(interval)
      }
    }, 100)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="login-body">
      <div className="success-message" id="successMessage" style={{ transform: successMessage ? 'translateX(0)' : 'translateX(150%)' }}>
        <i className="fas fa-check-circle"></i>
        <span id="messageText">{successMessage}</span>
      </div>

      <div className="container">
        <div className="form-container" id="formContainer" style={{ transform: isLoginMode ? 'translateX(0)' : 'translateX(100%)' }}>
          <div className="logo">
            <i className="fas fa-robot"></i>
            <h1>{displayedText}<span className="cursor">|</span></h1>
          </div>

          <div className="toggle-form">
            <button className={`toggle-btn ${isLoginMode ? 'active' : ''}`} onClick={() => handleToggle(true)}>Login</button>
            <button className={`toggle-btn ${!isLoginMode ? 'active' : ''}`} onClick={() => handleToggle(false)}>Register</button>
          </div>

          <form className={`form ${isLoginMode ? 'active' : ''}`} id="loginForm" onSubmit={handleLoginSubmit}>
            <h2>Welcome Back</h2>
            <div className="input-group">
              <i className="fas fa-envelope"></i>
              <input
                type="email"
                placeholder="Email"
                name="email"
                value={loginForm.email}
                onChange={handleLoginChange}
                onFocus={() => handleDemoAutofill('email')}
                required
              />
            </div>
            <div className="input-group">
              <i className="fas fa-lock"></i>
              <input
                type={showLoginPassword ? 'text' : 'password'}
                placeholder="Password"
                name="password"
                value={loginForm.password}
                onChange={handleLoginChange}
                onFocus={() => handleDemoAutofill('password')}
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowLoginPassword(!showLoginPassword)}
              >
                <i className={`fas ${showLoginPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
              </button>
            </div>
            <div className="remember-forgot">
              <label>
                <input
                  type="checkbox"
                  name="rememberMe"
                  checked={loginForm.rememberMe}
                  onChange={handleLoginChange}
                /> Remember me
              </label>
              <a href="#" onClick={handleForgotPassword}>Forgot Password?</a>
            </div>
            <button type="submit" className={`btn ${loading ? 'btn-loading' : ''}`} disabled={loading}>
              Login
            </button>


          </form>

          <form className={`form ${!isLoginMode ? 'active' : ''}`} id="registerForm" onSubmit={handleRegisterSubmit}>
            <h2>Create Account</h2>
            <div className="input-group">
              <i className="fas fa-user"></i>
              <input
                type="text"
                placeholder="Full Name"
                name="name"
                value={registerForm.name}
                onChange={handleRegisterChange}
                required
              />
            </div>
            <div className="input-group">
              <i className="fas fa-envelope"></i>
              <input
                type="email"
                placeholder="Email"
                name="email"
                value={registerForm.email}
                onChange={handleRegisterChange}
                required
              />
            </div>
            <div className="input-group">
              <i className="fas fa-lock"></i>
              <input
                type={showRegisterPassword ? 'text' : 'password'}
                placeholder="Password"
                name="password"
                value={registerForm.password}
                onChange={handleRegisterChange}
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowRegisterPassword(!showRegisterPassword)}
              >
                <i className={`fas ${showRegisterPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
              </button>
            </div>
            <div className="input-group">
              <i className="fas fa-lock"></i>
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                placeholder="Confirm Password"
                name="confirmPassword"
                value={registerForm.confirmPassword}
                onChange={handleRegisterChange}
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              >
                <i className={`fas ${showConfirmPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
              </button>
            </div>
            <button type="submit" className={`btn ${loading ? 'btn-loading' : ''}`} disabled={loading}>
              Register
            </button>
          </form>
        </div>

        <div className="welcome-container" id="welcomeContainer" style={{ transform: isLoginMode ? 'translateX(0)' : 'translateX(100%)' }}>
          <div className="ai-robot">
            <i className="fas fa-robot"></i>
          </div>
          <div className="welcome-content">
            <h2>Welcome to AI Data Agent</h2>
            <p>Transform your data into actionable insights with our powerful AI-driven analytics platform.</p>

            <div className="demo-account-right">
              <h3>Demo Account</h3>
              <p>Email: example@gmail.com</p>
              <p>Password: example123</p>
            </div>

            <div className="features">
              <div className="feature">
                <i className="fas fa-chart-line"></i>
                <span>Advanced Analytics</span>
              </div>
              <div className="feature">
                <i className="fas fa-brain"></i>
                <span>AI-Powered Insights</span>
              </div>
              <div className="feature">
                <i className="fas fa-shield-alt"></i>
                <span>Secure Data Handling</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      {error && <div className="error-message">{error}</div>}
    </div>
  )
}

export default Login
