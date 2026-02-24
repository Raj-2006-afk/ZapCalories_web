import React, { useState, useEffect, useRef, useCallback, createContext, useContext } from "react";
import "@/App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ==================== CONTEXT ====================
const AuthContext = createContext(null);

const useAuth = () => useContext(AuthContext);

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const res = await axios.get(`${API}/auth/me`);
      setUser(res.data);
    } catch (err) {
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const res = await axios.post(`${API}/auth/login`, { email, password });
    localStorage.setItem('token', res.data.access_token);
    setToken(res.data.access_token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${res.data.access_token}`;
    setUser(res.data.user);
    return res.data;
  };

  const register = async (name, email, password) => {
    const res = await axios.post(`${API}/auth/register`, { name, email, password });
    localStorage.setItem('token', res.data.access_token);
    setToken(res.data.access_token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${res.data.access_token}`;
    setUser(res.data.user);
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  const refreshUser = async () => {
    if (token) {
      await fetchUser();
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

// ==================== ICONS ====================
const CameraIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
    <circle cx="12" cy="13" r="3"/>
  </svg>
);

const UploadIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="17 8 12 3 7 8"/>
    <line x1="12" y1="3" x2="12" y2="15"/>
  </svg>
);

const UserIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
    <circle cx="12" cy="7" r="4"/>
  </svg>
);

const HomeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
    <polyline points="9 22 9 12 15 12 15 22"/>
  </svg>
);

const HistoryIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
    <path d="M3 3v5h5"/>
    <path d="M12 7v5l4 2"/>
  </svg>
);

const TrophyIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/>
    <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/>
    <path d="M4 22h16"/>
    <path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/>
    <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/>
    <path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>
  </svg>
);

const FireIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>
  </svg>
);

const CloseIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18"/>
    <line x1="6" y1="6" x2="18" y2="18"/>
  </svg>
);

const FlipIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M16 3h5v5"/>
    <path d="M8 3H3v5"/>
    <path d="M12 22v-8.3a4 4 0 0 0-1.172-2.872L3 3"/>
    <path d="m15 9 6-6"/>
  </svg>
);

const TrashIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="3 6 5 6 21 6"/>
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
  </svg>
);

const PlusIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="5" x2="12" y2="19"/>
    <line x1="5" y1="12" x2="19" y2="12"/>
  </svg>
);

const ShareIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="18" cy="5" r="3"/>
    <circle cx="6" cy="12" r="3"/>
    <circle cx="18" cy="19" r="3"/>
    <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>
    <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
  </svg>
);

const CrownIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m2 4 3 12h14l3-12-6 7-4-7-4 7-6-7zm3 16h14"/>
  </svg>
);

const StarIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
  </svg>
);

const LightbulbIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/>
    <path d="M9 18h6"/>
    <path d="M10 22h4"/>
  </svg>
);

const LogoutIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
    <polyline points="16 17 21 12 16 7"/>
    <line x1="21" y1="12" x2="9" y2="12"/>
  </svg>
);

const LockIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="18" height="11" x="3" y="11" rx="2" ry="2"/>
    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
  </svg>
);

const CheckIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);

// ==================== COMPONENTS ====================

const ProgressCircle = ({ percentage, size = 120, strokeWidth = 10, color = "#000" }) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (Math.min(percentage, 100) / 100) * circumference;

  return (
    <svg width={size} height={size} className="progress-circle">
      <circle
        className="progress-circle-bg"
        strokeWidth={strokeWidth}
        fill="transparent"
        r={radius}
        cx={size / 2}
        cy={size / 2}
      />
      <circle
        className="progress-circle-fill"
        strokeWidth={strokeWidth}
        fill="transparent"
        r={radius}
        cx={size / 2}
        cy={size / 2}
        style={{
          strokeDasharray: circumference,
          strokeDashoffset: offset,
          stroke: color,
        }}
      />
    </svg>
  );
};

// ==================== AUTH SCREENS ====================

const AuthScreen = ({ onSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await register(name, email, password);
      }
      onSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-screen">
      <div className="auth-container">
        <div className="auth-logo">
          <div className="logo-icon">
            <CameraIcon />
          </div>
          <h1 className="logo-text">ZapCalories</h1>
          <p className="logo-tagline">AI-Powered Calorie Tracking</p>
        </div>

        <div className="auth-promo-banner">
          <span className="promo-badge">50% OFF</span>
          <span>Launch offer until Oct 26!</span>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {!isLogin && (
            <div className="form-group">
              <label>Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                required={!isLogin}
              />
            </div>
          )}

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Min 6 characters"
              required
              minLength={6}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Create Account')}
          </button>
        </form>

        <div className="auth-switch">
          {isLogin ? (
            <p>Don't have an account? <button onClick={() => setIsLogin(false)}>Sign up</button></p>
          ) : (
            <p>Already have an account? <button onClick={() => setIsLogin(true)}>Sign in</button></p>
          )}
        </div>

        <div className="auth-features">
          <div className="feature-item">
            <CameraIcon />
            <span>2 Free Scans</span>
          </div>
          <div className="feature-item">
            <FireIcon />
            <span>Streak Rewards</span>
          </div>
          <div className="feature-item">
            <TrophyIcon />
            <span>Achievements</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// ==================== DASHBOARD ====================

const Dashboard = ({ onNavigate, dailyProgress, tdeeData, subscriptionStatus, stats }) => {
  const { user } = useAuth();
  const hasProfile = user?.age && user?.height && user?.weight;
  
  const caloriePercentage = tdeeData ? (dailyProgress.total_calories / tdeeData.goal_calories) * 100 : 0;
  const proteinPercentage = tdeeData ? (dailyProgress.total_protein / tdeeData.protein_goal) * 100 : 0;
  const carbsPercentage = tdeeData ? (dailyProgress.total_carbs / tdeeData.carbs_goal) * 100 : 0;
  const fatPercentage = tdeeData ? (dailyProgress.total_fat / tdeeData.fat_goal) * 100 : 0;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1 className="heading-2">Hey, {user?.name?.split(' ')[0] || 'there'}!</h1>
          <p className="body-small">Track your nutrition goals</p>
        </div>
        <div className="streak-badge" onClick={() => onNavigate('achievements')}>
          <FireIcon />
          <span>{stats?.current_streak || 0}</span>
        </div>
      </div>

      {/* Subscription Banner */}
      {!subscriptionStatus?.has_subscription && (
        <div className="upgrade-banner" onClick={() => onNavigate('pricing')}>
          <div className="upgrade-content">
            <CrownIcon />
            <div>
              <strong>Free Scans: {subscriptionStatus?.free_scans_remaining || 0} left</strong>
              <p>Upgrade to unlock unlimited scans</p>
            </div>
          </div>
          <span className="upgrade-arrow">→</span>
        </div>
      )}

      {!hasProfile ? (
        <div className="setup-prompt">
          <div className="setup-icon">
            <UserIcon />
          </div>
          <h2 className="heading-3">Complete Your Profile</h2>
          <p className="body-medium">Set up your goals to get personalized calorie targets</p>
          <button className="btn-primary" onClick={() => onNavigate('profile')}>
            Set Up Profile
          </button>
        </div>
      ) : (
        <>
          <div className="calorie-card">
            <div className="calorie-circle-container">
              <ProgressCircle 
                percentage={caloriePercentage} 
                size={160} 
                strokeWidth={12}
                color={caloriePercentage > 100 ? "#ef4444" : "#000"}
              />
              <div className="calorie-text">
                <span className="calorie-current">{Math.round(dailyProgress.total_calories)}</span>
                <span className="calorie-divider">/</span>
                <span className="calorie-goal">{tdeeData?.goal_calories || 0}</span>
                <span className="calorie-label">kcal</span>
              </div>
            </div>
            <div className="calorie-info">
              <div className="info-item">
                <span className="info-label">BMR</span>
                <span className="info-value">{tdeeData?.bmr || 0} kcal</span>
              </div>
              <div className="info-item">
                <span className="info-label">TDEE</span>
                <span className="info-value">{tdeeData?.tdee || 0} kcal</span>
              </div>
              <div className="info-item">
                <span className="info-label">Goal</span>
                <span className="info-value capitalize">{tdeeData?.goal_type || 'maintain'}</span>
              </div>
            </div>
          </div>

          <div className="macros-grid">
            <div className="macro-card protein">
              <div className="macro-header">
                <span className="macro-name">Protein</span>
                <span className="macro-percentage">{Math.round(proteinPercentage)}%</span>
              </div>
              <div className="macro-bar">
                <div className="macro-bar-fill" style={{ width: `${Math.min(proteinPercentage, 100)}%` }} />
              </div>
              <div className="macro-values">
                <span>{Math.round(dailyProgress.total_protein)}g</span>
                <span className="macro-goal">/ {tdeeData?.protein_goal || 0}g</span>
              </div>
            </div>

            <div className="macro-card carbs">
              <div className="macro-header">
                <span className="macro-name">Carbs</span>
                <span className="macro-percentage">{Math.round(carbsPercentage)}%</span>
              </div>
              <div className="macro-bar">
                <div className="macro-bar-fill" style={{ width: `${Math.min(carbsPercentage, 100)}%` }} />
              </div>
              <div className="macro-values">
                <span>{Math.round(dailyProgress.total_carbs)}g</span>
                <span className="macro-goal">/ {tdeeData?.carbs_goal || 0}g</span>
              </div>
            </div>

            <div className="macro-card fat">
              <div className="macro-header">
                <span className="macro-name">Fat</span>
                <span className="macro-percentage">{Math.round(fatPercentage)}%</span>
              </div>
              <div className="macro-bar">
                <div className="macro-bar-fill" style={{ width: `${Math.min(fatPercentage, 100)}%` }} />
              </div>
              <div className="macro-values">
                <span>{Math.round(dailyProgress.total_fat)}g</span>
                <span className="macro-goal">/ {tdeeData?.fat_goal || 0}g</span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="quick-actions">
            <button className="action-btn" onClick={() => onNavigate('suggestions')}>
              <LightbulbIcon />
              <span>Meal Ideas</span>
            </button>
            <button className="action-btn" onClick={() => onNavigate('leaderboard')}>
              <TrophyIcon />
              <span>Leaderboard</span>
            </button>
          </div>

          <button className="scan-cta" onClick={() => onNavigate('scan')}>
            <CameraIcon />
            <span>Scan Food</span>
          </button>
        </>
      )}
    </div>
  );
};

// ==================== SCANNER ====================

const Scanner = ({ onFoodAnalyzed, onBack, subscriptionStatus }) => {
  const [isCapturing, setIsCapturing] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);
  const [facingMode, setFacingMode] = useState('environment');
  const [mealType, setMealType] = useState('snack');
  const [streamActive, setStreamActive] = useState(false);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const streamRef = useRef(null);

  const canScan = subscriptionStatus?.can_scan;

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setStreamActive(false);
    setIsCapturing(false);
  }, []);

  const startCamera = useCallback(async () => {
    if (!canScan) {
      setError('Scan limit reached. Please upgrade to continue.');
      return;
    }
    setError(null);
    try {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode, width: { ideal: 1280 }, height: { ideal: 720 } }
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        setStreamActive(true);
        setIsCapturing(true);
      }
    } catch (err) {
      setError('Camera access denied. Try uploading an image instead.');
      setIsCapturing(false);
    }
  }, [facingMode, canScan]);

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const flipCamera = async () => {
    const newMode = facingMode === 'environment' ? 'user' : 'environment';
    setFacingMode(newMode);
    if (isCapturing) {
      stopCamera();
      setTimeout(() => startCamera(), 100);
    }
  };

  const captureImage = () => {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    setCapturedImage(imageData);
    stopCamera();
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (!canScan) {
      setError('Scan limit reached. Please upgrade to continue.');
      return;
    }
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file');
      return;
    }
    const reader = new FileReader();
    reader.onload = (event) => setCapturedImage(event.target.result);
    reader.readAsDataURL(file);
  };

  const analyzeFood = async () => {
    if (!capturedImage) return;
    setIsAnalyzing(true);
    setError(null);
    try {
      const response = await axios.post(`${API}/analyze-food`, { image_base64: capturedImage });
      setAnalysisResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const saveToLog = async () => {
    if (!analysisResult) return;
    try {
      await axios.post(`${API}/food-log`, {
        food_name: analysisResult.food_name,
        calories: analysisResult.calories,
        protein: analysisResult.protein,
        carbs: analysisResult.carbs,
        fat: analysisResult.fat,
        fiber: analysisResult.fiber,
        serving_size: analysisResult.serving_size,
        meal_type: mealType
      });
      onFoodAnalyzed();
    } catch (err) {
      setError('Failed to save. Please try again.');
    }
  };

  const resetScanner = () => {
    setCapturedImage(null);
    setAnalysisResult(null);
    setError(null);
  };

  return (
    <div className="scanner-page">
      <div className="scanner-header">
        <button className="back-btn" onClick={onBack}><CloseIcon /></button>
        <h1 className="heading-3">Scan Food</h1>
        <div style={{ width: 40 }} />
      </div>

      {!canScan && (
        <div className="limit-banner">
          <LockIcon />
          <span>Scan limit reached. Upgrade to continue!</span>
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      {!capturedImage ? (
        <div className="scanner-view">
          <div className={`camera-container ${isCapturing && streamActive ? 'active' : 'hidden'}`}>
            <video ref={videoRef} autoPlay playsInline muted className="camera-preview" />
            <div className="camera-controls">
              <button className="capture-btn" onClick={captureImage}>
                <div className="capture-btn-inner" />
              </button>
              <button className="flip-btn" onClick={flipCamera}><FlipIcon /></button>
            </div>
          </div>
          <canvas ref={canvasRef} style={{ display: 'none' }} />

          {!isCapturing && (
            <div className="scanner-options">
              <button className="option-btn" onClick={startCamera} disabled={!canScan}>
                <CameraIcon />
                <span>Take Photo</span>
              </button>
              <button className="option-btn" onClick={() => fileInputRef.current?.click()} disabled={!canScan}>
                <UploadIcon />
                <span>Upload Image</span>
              </button>
              <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileUpload} style={{ display: 'none' }} />
            </div>
          )}
        </div>
      ) : (
        <div className="analysis-view">
          <div className="captured-image-container">
            <img src={capturedImage} alt="Captured food" className="captured-image" />
          </div>

          {!analysisResult && !isAnalyzing && (
            <div className="analyze-actions">
              <button className="btn-secondary" onClick={resetScanner}>Retake</button>
              <button className="btn-primary" onClick={analyzeFood}>Analyze Food</button>
            </div>
          )}

          {isAnalyzing && (
            <div className="analyzing-state">
              <div className="spinner" />
              <p>Analyzing your food...</p>
            </div>
          )}

          {analysisResult && (
            <div className="analysis-result">
              <div className="result-header">
                <h2 className="heading-3">{analysisResult.food_name}</h2>
                <span className="confidence-badge">{Math.round(analysisResult.confidence * 100)}% confident</span>
              </div>

              <div className="nutrition-grid">
                <div className="nutrition-item calories">
                  <span className="nutrition-value">{Math.round(analysisResult.calories)}</span>
                  <span className="nutrition-label">Calories</span>
                </div>
                <div className="nutrition-item">
                  <span className="nutrition-value">{Math.round(analysisResult.protein)}g</span>
                  <span className="nutrition-label">Protein</span>
                </div>
                <div className="nutrition-item">
                  <span className="nutrition-value">{Math.round(analysisResult.carbs)}g</span>
                  <span className="nutrition-label">Carbs</span>
                </div>
                <div className="nutrition-item">
                  <span className="nutrition-value">{Math.round(analysisResult.fat)}g</span>
                  <span className="nutrition-label">Fat</span>
                </div>
              </div>

              <p className="serving-info">Serving: {analysisResult.serving_size}</p>
              <p className="analysis-details">{analysisResult.details}</p>

              <div className="meal-type-selector">
                <label className="body-small">Add to:</label>
                <div className="meal-buttons">
                  {['breakfast', 'lunch', 'dinner', 'snack'].map(type => (
                    <button key={type} className={`meal-btn ${mealType === type ? 'active' : ''}`} onClick={() => setMealType(type)}>
                      {type.charAt(0).toUpperCase() + type.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              <div className="result-actions">
                <button className="btn-secondary" onClick={resetScanner}>Scan Again</button>
                <button className="btn-primary" onClick={saveToLog}>Add to Log</button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ==================== PROFILE ====================

const Profile = ({ onSave, onBack }) => {
  const { user, logout, refreshUser } = useAuth();
  const [formData, setFormData] = useState({
    name: user?.name || '',
    age: user?.age || '',
    gender: user?.gender || 'male',
    height: user?.height || '',
    weight: user?.weight || '',
    goal_weight: user?.goal_weight || '',
    activity_level: user?.activity_level || 'moderate'
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const data = {
        ...formData,
        age: parseInt(formData.age),
        height: parseFloat(formData.height),
        weight: parseFloat(formData.weight),
        goal_weight: parseFloat(formData.goal_weight)
      };
      await axios.put(`${API}/profile`, data);
      await refreshUser();
      onSave();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save profile');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="profile-page">
      <div className="profile-header">
        <button className="back-btn" onClick={onBack}><CloseIcon /></button>
        <h1 className="heading-3">Profile</h1>
        <button className="logout-btn" onClick={logout}><LogoutIcon /></button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="profile-stats">
        <div className="stat-item">
          <FireIcon />
          <span className="stat-value">{user?.current_streak || 0}</span>
          <span className="stat-label">Day Streak</span>
        </div>
        <div className="stat-item">
          <StarIcon />
          <span className="stat-value">{user?.total_points || 0}</span>
          <span className="stat-label">Points</span>
        </div>
        <div className="stat-item">
          <TrophyIcon />
          <span className="stat-value">Lv {user?.level || 1}</span>
          <span className="stat-label">Level</span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="profile-form">
        <div className="form-group">
          <label>Name</label>
          <input type="text" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} placeholder="Your name" />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Age</label>
            <input type="number" value={formData.age} onChange={(e) => setFormData({ ...formData, age: e.target.value })} placeholder="25" required />
          </div>
          <div className="form-group">
            <label>Gender</label>
            <select value={formData.gender} onChange={(e) => setFormData({ ...formData, gender: e.target.value })}>
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label>Height (cm)</label>
          <input type="number" value={formData.height} onChange={(e) => setFormData({ ...formData, height: e.target.value })} placeholder="170" required />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Current Weight (kg)</label>
            <input type="number" step="0.1" value={formData.weight} onChange={(e) => setFormData({ ...formData, weight: e.target.value })} placeholder="70" required />
          </div>
          <div className="form-group">
            <label>Goal Weight (kg)</label>
            <input type="number" step="0.1" value={formData.goal_weight} onChange={(e) => setFormData({ ...formData, goal_weight: e.target.value })} placeholder="65" required />
          </div>
        </div>

        <div className="form-group">
          <label>Activity Level</label>
          <select value={formData.activity_level} onChange={(e) => setFormData({ ...formData, activity_level: e.target.value })}>
            <option value="sedentary">Sedentary (little/no exercise)</option>
            <option value="light">Light (1-3 days/week)</option>
            <option value="moderate">Moderate (3-5 days/week)</option>
            <option value="active">Active (6-7 days/week)</option>
            <option value="very_active">Very Active (physical job)</option>
          </select>
        </div>

        <button type="submit" className="btn-primary" disabled={saving}>
          {saving ? 'Saving...' : 'Save Profile'}
        </button>
      </form>
    </div>
  );
};

// ==================== HISTORY ====================

const History = ({ foodLogs, onDelete, onShare, onBack }) => {
  const groupedLogs = foodLogs.reduce((acc, log) => {
    const date = new Date(log.logged_at).toLocaleDateString();
    if (!acc[date]) acc[date] = [];
    acc[date].push(log);
    return acc;
  }, {});

  return (
    <div className="history-page">
      <div className="history-header">
        <button className="back-btn" onClick={onBack}><CloseIcon /></button>
        <h1 className="heading-3">Food History</h1>
        <div style={{ width: 40 }} />
      </div>

      {Object.keys(groupedLogs).length === 0 ? (
        <div className="empty-state">
          <HistoryIcon />
          <p>No food logged yet</p>
          <span className="body-small">Start scanning your meals!</span>
        </div>
      ) : (
        <div className="history-list">
          {Object.entries(groupedLogs).map(([date, logs]) => (
            <div key={date} className="date-group">
              <h3 className="date-header">{date}</h3>
              {logs.map(log => (
                <div key={log.id} className="food-log-item">
                  <div className="log-info">
                    <span className="log-name">{log.food_name}</span>
                    <span className="log-meal">{log.meal_type}</span>
                  </div>
                  <div className="log-nutrition">
                    <span className="log-calories">{Math.round(log.calories)} kcal</span>
                    <span className="log-macros">P: {Math.round(log.protein)}g | C: {Math.round(log.carbs)}g | F: {Math.round(log.fat)}g</span>
                  </div>
                  <div className="log-actions">
                    <button className="share-btn" onClick={() => onShare(log.id)}><ShareIcon /></button>
                    <button className="delete-btn" onClick={() => onDelete(log.id)}><TrashIcon /></button>
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ==================== ACHIEVEMENTS ====================

const Achievements = ({ onBack }) => {
  const [achievements, setAchievements] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [achRes, statsRes] = await Promise.all([
          axios.get(`${API}/achievements`),
          axios.get(`${API}/stats`)
        ]);
        setAchievements(achRes.data);
        setStats(statsRes.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const unlocked = achievements.filter(a => a.unlocked);
  const locked = achievements.filter(a => !a.unlocked);

  if (loading) {
    return <div className="loading-screen"><div className="spinner" /></div>;
  }

  return (
    <div className="achievements-page">
      <div className="page-header">
        <button className="back-btn" onClick={onBack}><CloseIcon /></button>
        <h1 className="heading-3">Achievements</h1>
        <div style={{ width: 40 }} />
      </div>

      <div className="achievements-stats">
        <div className="big-stat">
          <span className="big-stat-value">{stats?.total_points || 0}</span>
          <span className="big-stat-label">Total Points</span>
        </div>
        <div className="stats-row">
          <div className="mini-stat">
            <FireIcon />
            <span>{stats?.current_streak || 0} day streak</span>
          </div>
          <div className="mini-stat">
            <TrophyIcon />
            <span>{unlocked.length}/{achievements.length} badges</span>
          </div>
        </div>
      </div>

      <div className="achievements-section">
        <h2 className="section-title">Unlocked ({unlocked.length})</h2>
        <div className="achievements-grid">
          {unlocked.map(ach => (
            <div key={ach.id} className="achievement-card unlocked">
              <div className="achievement-icon"><TrophyIcon /></div>
              <div className="achievement-info">
                <span className="achievement-name">{ach.name}</span>
                <span className="achievement-desc">{ach.description}</span>
                <span className="achievement-points">+{ach.points} pts</span>
              </div>
            </div>
          ))}
          {unlocked.length === 0 && <p className="empty-text">Complete tasks to unlock badges!</p>}
        </div>
      </div>

      <div className="achievements-section">
        <h2 className="section-title">Locked ({locked.length})</h2>
        <div className="achievements-grid">
          {locked.map(ach => (
            <div key={ach.id} className="achievement-card locked">
              <div className="achievement-icon"><LockIcon /></div>
              <div className="achievement-info">
                <span className="achievement-name">{ach.name}</span>
                <span className="achievement-desc">{ach.description}</span>
                <span className="achievement-points">+{ach.points} pts</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ==================== LEADERBOARD ====================

const Leaderboard = ({ onBack }) => {
  const { user } = useAuth();
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const res = await axios.get(`${API}/leaderboard`);
        setLeaderboard(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchLeaderboard();
  }, []);

  if (loading) {
    return <div className="loading-screen"><div className="spinner" /></div>;
  }

  return (
    <div className="leaderboard-page">
      <div className="page-header">
        <button className="back-btn" onClick={onBack}><CloseIcon /></button>
        <h1 className="heading-3">Leaderboard</h1>
        <div style={{ width: 40 }} />
      </div>

      <div className="leaderboard-list">
        {leaderboard.map((entry, idx) => (
          <div key={entry.user_id} className={`leaderboard-item ${entry.user_id === user?.id ? 'current-user' : ''}`}>
            <div className="rank-badge">
              {idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `#${entry.rank}`}
            </div>
            <div className="leader-info">
              <span className="leader-name">{entry.name}</span>
              <span className="leader-stats">Lv {entry.level} • {entry.streak} day streak</span>
            </div>
            <div className="leader-points">
              <span>{entry.points}</span>
              <span className="points-label">pts</span>
            </div>
          </div>
        ))}
        {leaderboard.length === 0 && (
          <div className="empty-state"><p>No users yet. Be the first!</p></div>
        )}
      </div>
    </div>
  );
};

// ==================== PRICING ====================

const Pricing = ({ onBack }) => {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activating, setActivating] = useState(null);

  useEffect(() => {
    const fetchPricing = async () => {
      try {
        const res = await axios.get(`${API}/pricing`);
        setPlans(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchPricing();
  }, []);

  const handleSubscribe = async (planId) => {
    setActivating(planId);
    try {
      await axios.post(`${API}/subscription/activate?plan_id=${planId}`);
      alert('Subscription activated! (Demo mode - Stripe integration pending)');
      onBack();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to activate subscription');
    } finally {
      setActivating(null);
    }
  };

  if (loading) {
    return <div className="loading-screen"><div className="spinner" /></div>;
  }

  const isPromo = plans[0]?.is_promo_active;

  return (
    <div className="pricing-page">
      <div className="page-header">
        <button className="back-btn" onClick={onBack}><CloseIcon /></button>
        <h1 className="heading-3">Upgrade</h1>
        <div style={{ width: 40 }} />
      </div>

      {isPromo && (
        <div className="promo-banner">
          <CrownIcon />
          <div>
            <strong>50% OFF Launch Sale!</strong>
            <p>Offer ends October 26, 2025</p>
          </div>
        </div>
      )}

      <div className="pricing-cards">
        {plans.map(plan => (
          <div key={plan.id} className={`pricing-card ${plan.id === 'annual' ? 'featured' : ''}`}>
            {plan.id === 'annual' && <div className="best-value">Best Value</div>}
            <h3 className="plan-name">{plan.name}</h3>
            <div className="plan-price">
              {isPromo && (
                <span className="original-price">${plan.price.toFixed(2)}</span>
              )}
              <span className="current-price">${isPromo ? plan.promo_price.toFixed(2) : plan.price.toFixed(2)}</span>
              <span className="price-period">/{plan.id === 'monthly' ? 'mo' : plan.id === 'quarterly' ? '3mo' : 'yr'}</span>
            </div>
            <ul className="plan-features">
              <li><CheckIcon /> {plan.scans_per_month === -1 ? 'Unlimited' : plan.scans_per_month} scans/month</li>
              <li><CheckIcon /> AI-powered analysis</li>
              <li><CheckIcon /> Macro tracking</li>
              <li><CheckIcon /> Streak rewards</li>
              {plan.id === 'annual' && <li><CheckIcon /> Priority support</li>}
            </ul>
            <button 
              className="btn-primary" 
              onClick={() => handleSubscribe(plan.id)}
              disabled={activating === plan.id}
            >
              {activating === plan.id ? 'Processing...' : 'Subscribe'}
            </button>
          </div>
        ))}
      </div>

      <p className="pricing-note">Stripe payment integration coming soon. Demo mode active.</p>
    </div>
  );
};

// ==================== MEAL SUGGESTIONS ====================

const MealSuggestions = ({ onBack }) => {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mealType, setMealType] = useState('lunch');

  useEffect(() => {
    fetchSuggestions();
  }, [mealType]);

  const fetchSuggestions = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/meal-suggestions?meal_type=${mealType}`);
      setSuggestions(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="suggestions-page">
      <div className="page-header">
        <button className="back-btn" onClick={onBack}><CloseIcon /></button>
        <h1 className="heading-3">Meal Ideas</h1>
        <div style={{ width: 40 }} />
      </div>

      <div className="meal-type-tabs">
        {['breakfast', 'lunch', 'dinner', 'snack'].map(type => (
          <button 
            key={type} 
            className={`tab-btn ${mealType === type ? 'active' : ''}`}
            onClick={() => setMealType(type)}
          >
            {type.charAt(0).toUpperCase() + type.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="loading-state"><div className="spinner" /><p>Getting AI suggestions...</p></div>
      ) : suggestions.length === 0 ? (
        <div className="empty-state">
          <LightbulbIcon />
          <p>No suggestions available</p>
          <span className="body-small">Complete your profile and log some meals first</span>
        </div>
      ) : (
        <div className="suggestions-list">
          {suggestions.map((meal, idx) => (
            <div key={idx} className="suggestion-card">
              <h3 className="meal-name">{meal.meal_name}</h3>
              <p className="meal-description">{meal.description}</p>
              <div className="meal-macros">
                <span className="macro-tag calories">{Math.round(meal.calories)} kcal</span>
                <span className="macro-tag">P: {Math.round(meal.protein)}g</span>
                <span className="macro-tag">C: {Math.round(meal.carbs)}g</span>
                <span className="macro-tag">F: {Math.round(meal.fat)}g</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ==================== MAIN APP ====================

function AppContent() {
  const { user, loading: authLoading, refreshUser } = useAuth();
  const [currentPage, setCurrentPage] = useState('home');
  const [dailyProgress, setDailyProgress] = useState({ total_calories: 0, total_protein: 0, total_carbs: 0, total_fat: 0, meal_count: 0 });
  const [tdeeData, setTdeeData] = useState(null);
  const [foodLogs, setFoodLogs] = useState([]);
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    if (!user) return;
    try {
      const [progressRes, logsRes, subRes, statsRes] = await Promise.all([
        axios.get(`${API}/daily-progress`),
        axios.get(`${API}/food-log?limit=50`),
        axios.get(`${API}/subscription/status`),
        axios.get(`${API}/stats`)
      ]);
      setDailyProgress(progressRes.data);
      setFoodLogs(logsRes.data);
      setSubscriptionStatus(subRes.data);
      setStats(statsRes.data);

      if (user.age && user.height && user.weight) {
        const tdeeRes = await axios.get(`${API}/calculate-tdee`);
        setTdeeData(tdeeRes.data);
      }
    } catch (err) {
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (user) {
      fetchData();
    } else {
      setLoading(false);
    }
  }, [user, fetchData]);

  const handleDeleteLog = async (logId) => {
    try {
      await axios.delete(`${API}/food-log/${logId}`);
      fetchData();
    } catch (err) {
      console.error('Delete error:', err);
    }
  };

  const handleShareMeal = async (logId) => {
    try {
      const res = await axios.post(`${API}/share-meal`, { log_id: logId });
      alert(`Meal shared! Share link: ${window.location.origin}${res.data.share_url}`);
      fetchData();
    } catch (err) {
      console.error('Share error:', err);
    }
  };

  if (authLoading || loading) {
    return <div className="loading-screen"><div className="spinner" /><p>Loading...</p></div>;
  }

  if (!user) {
    return <AuthScreen onSuccess={() => window.location.reload()} />;
  }

  return (
    <div className="app-container">
      {currentPage === 'home' && (
        <Dashboard 
          onNavigate={setCurrentPage} 
          dailyProgress={dailyProgress} 
          tdeeData={tdeeData} 
          subscriptionStatus={subscriptionStatus}
          stats={stats}
        />
      )}
      {currentPage === 'scan' && (
        <Scanner 
          onFoodAnalyzed={() => { fetchData(); refreshUser(); setCurrentPage('home'); }} 
          onBack={() => setCurrentPage('home')}
          subscriptionStatus={subscriptionStatus}
        />
      )}
      {currentPage === 'profile' && (
        <Profile onSave={() => { fetchData(); setCurrentPage('home'); }} onBack={() => setCurrentPage('home')} />
      )}
      {currentPage === 'history' && (
        <History foodLogs={foodLogs} onDelete={handleDeleteLog} onShare={handleShareMeal} onBack={() => setCurrentPage('home')} />
      )}
      {currentPage === 'achievements' && (
        <Achievements onBack={() => setCurrentPage('home')} />
      )}
      {currentPage === 'leaderboard' && (
        <Leaderboard onBack={() => setCurrentPage('home')} />
      )}
      {currentPage === 'pricing' && (
        <Pricing onBack={() => setCurrentPage('home')} />
      )}
      {currentPage === 'suggestions' && (
        <MealSuggestions onBack={() => setCurrentPage('home')} />
      )}

      {!['scan', 'pricing'].includes(currentPage) && (
        <nav className="bottom-nav">
          <button className={`nav-item ${currentPage === 'home' ? 'active' : ''}`} onClick={() => setCurrentPage('home')}>
            <HomeIcon /><span>Home</span>
          </button>
          <button className={`nav-item ${currentPage === 'history' ? 'active' : ''}`} onClick={() => setCurrentPage('history')}>
            <HistoryIcon /><span>History</span>
          </button>
          <button className="nav-item scan-btn" onClick={() => setCurrentPage('scan')}>
            <CameraIcon />
          </button>
          <button className={`nav-item ${currentPage === 'achievements' ? 'active' : ''}`} onClick={() => setCurrentPage('achievements')}>
            <TrophyIcon /><span>Badges</span>
          </button>
          <button className={`nav-item ${currentPage === 'profile' ? 'active' : ''}`} onClick={() => setCurrentPage('profile')}>
            <UserIcon /><span>Profile</span>
          </button>
        </nav>
      )}
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
