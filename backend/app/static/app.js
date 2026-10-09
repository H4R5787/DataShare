/**
 * Secure Pass RxQ — Complete Mobile Frontend Application
 */

// Global State
const state = {
  token: localStorage.getItem('secure_pass_token') || null,
  user: JSON.parse(localStorage.getItem('secure_pass_user') || 'null'),
  currentScreen: 'splash',
  currentTab: 'home',
  
  // Send Data Flow State
  sendData: {
    phone: '',
    detectedOperator: null,
    detectedCircle: null,
    selectedPlan: null,
    activeCategory: 'BOOSTER',
    availablePlans: [],
    operators: [],
    circles: [],
    createdOrder: null,
    paymentIntent: null,
    trackingInterval: null,
  },
  
  // History & Recipients
  transactions: [],
  recipients: [],
  activeTransactionDetail: null,
};

// UI Helpers
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const msgEl = document.getElementById('toast-message');
  const iconEl = document.getElementById('toast-icon');
  
  msgEl.textContent = message;
  container.classList.remove('opacity-0', '-translate-y-4');
  container.classList.add('opacity-100', 'translate-y-0');
  
  setTimeout(() => {
    container.classList.add('opacity-0', '-translate-y-4');
    container.classList.remove('opacity-100', 'translate-y-0');
  }, 3200);
}

function updateClock() {
  const clock = document.getElementById('live-clock');
  if (clock) {
    const d = new Date();
    clock.textContent = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
}
setInterval(updateClock, 1000);

// API Client
const api = {
  async fetch(url, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    };
    if (state.token) {
      headers['Authorization'] = `Bearer ${state.token}`;
    }
    try {
      const response = await fetch(url, { ...options, headers });
      if (response.status === 401) {
        state.token = null;
        state.user = null;
        localStorage.removeItem('secure_pass_token');
        localStorage.removeItem('secure_pass_user');
        router.navigate('login');
        showToast('Session expired. Please log in again.', 'warning');
        return null;
      }
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'An unexpected error occurred.');
      }
      return data;
    } catch (err) {
      showToast(err.message, 'error');
      throw err;
    }
  }
};

// Screen Router
const router = {
  navigate(screenId, params = {}) {
    state.currentScreen = screenId;
    const viewport = document.getElementById('app-viewport');
    const bottomNav = document.getElementById('bottom-nav');
    
    // Update bottom nav visibility & active icon
    if (['home', 'send-data', 'history', 'account'].includes(screenId)) {
      bottomNav.classList.remove('hidden');
      document.querySelectorAll('.nav-item').forEach(btn => {
        const nav = btn.getAttribute('data-nav');
        if (nav === screenId) {
          btn.classList.add('text-brand-600');
          btn.classList.remove('text-slate-400');
        } else {
          btn.classList.remove('text-brand-600');
          btn.classList.add('text-slate-400');
        }
      });
    } else {
      bottomNav.classList.add('hidden');
    }

    // Render screen
    viewport.innerHTML = '';
    switch (screenId) {
      case 'splash':
        screens.renderSplash(viewport);
        break;
      case 'login':
        screens.renderLogin(viewport);
        break;
      case 'otp':
        screens.renderOTP(viewport, params.phone, params.devOtp);
        break;
      case 'home':
        screens.renderHome(viewport);
        break;
      case 'send-data':
        screens.renderSendData(viewport);
        break;
      case 'select-plan':
        screens.renderSelectPlan(viewport);
        break;
      case 'review-order':
        screens.renderReviewOrder(viewport);
        break;
      case 'tracking':
        screens.renderTracking(viewport, params.orderId);
        break;
      case 'success':
        screens.renderSuccess(viewport, params.transaction);
        break;
      case 'history':
        screens.renderHistory(viewport);
        break;
      case 'transaction-details':
        screens.renderTransactionDetails(viewport, params.orderId);
        break;
      case 'account':
        screens.renderAccount(viewport);
        break;
      default:
        screens.renderHome(viewport);
    }
    lucide.createIcons();
  }
};

// View Components
const screens = {

  // Splash Screen
  renderSplash(container) {
    container.innerHTML = `
      <div class="flex-1 flex flex-col items-center justify-between p-8 bg-gradient-to-b from-slate-900 via-slate-900 to-brand-900 text-white select-none">
        <div class="w-full flex justify-end">
          <span class="text-[10px] font-mono tracking-widest text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-2.5 py-1 rounded-full uppercase">
            MOCK DEV ENGINE ACTIVE
          </span>
        </div>
        
        <div class="flex flex-col items-center text-center my-auto">
          <div class="w-20 h-20 rounded-3xl bg-brand-600 flex items-center justify-center shadow-2xl shadow-brand-500/50 mb-6">
            <i data-lucide="shield-check" class="w-10 h-10 text-white"></i>
          </div>
          <h1 class="text-3xl font-extrabold tracking-tight">SECURE PASS <span class="text-brand-400">RxQ</span></h1>
          <p class="text-slate-400 text-sm mt-2 max-w-[260px]">
            Instant, friction-free mobile data pack gifting across all Indian carriers.
          </p>
        </div>

        <div class="w-full space-y-3">
          <button onclick="router.navigate('login')" class="w-full py-4 bg-brand-600 hover:bg-brand-500 text-white font-semibold rounded-2xl shadow-lg shadow-brand-600/30 transition transform active:scale-95 flex items-center justify-center space-x-2">
            <span>Get Started</span>
            <i data-lucide="arrow-right" class="w-4 h-4"></i>
          </button>
          <div class="flex items-center justify-center space-x-2 text-xs text-slate-400">
            <i data-lucide="lock" class="w-3.5 h-3.5 text-emerald-400"></i>
            <span>Bank-Grade Encryption • 100% Idempotent</span>
          </div>
        </div>
      </div>
    `;
    setTimeout(() => {
      if (state.token) {
        router.navigate('home');
      }
    }, 1200);
  },

  // Login Screen
  renderLogin(container) {
    container.innerHTML = `
      <div class="flex-1 flex flex-col p-6 bg-white justify-between">
        <div>
          <div class="flex items-center justify-between mb-8">
            <div class="w-10 h-10 rounded-2xl bg-brand-50 flex items-center justify-center text-brand-600">
              <i data-lucide="smartphone" class="w-5 h-5"></i>
            </div>
            <span class="text-xs font-semibold text-slate-400">Step 1 of 2</span>
          </div>
          
          <h2 class="text-2xl font-extrabold text-slate-900 tracking-tight">Enter Mobile Number</h2>
          <p class="text-slate-500 text-sm mt-1">We'll send a 6-digit one-time password to verify your account.</p>

          <div class="mt-8">
            <label class="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">Phone Number</label>
            <div class="relative flex items-center">
              <div class="absolute left-4 flex items-center space-x-1.5 text-slate-500 font-bold border-r border-slate-200 pr-3">
                <span class="text-lg">🇮🇳</span>
                <span class="text-sm">+91</span>
              </div>
              <input id="login-phone" type="tel" maxlength="10" placeholder="98765 43210" value="9876543210"
                class="w-full pl-24 pr-4 py-4 bg-slate-50 border border-slate-200 rounded-2xl text-lg font-bold tracking-wider focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white transition" />
            </div>
            <p class="text-xs text-slate-400 mt-2 flex items-center space-x-1">
              <i data-lucide="info" class="w-3.5 h-3.5"></i>
              <span>Default test number pre-filled for convenience</span>
            </p>
          </div>
        </div>

        <div>
          <button id="btn-send-otp" onclick="actions.requestLoginOTP()" class="w-full py-4 bg-brand-600 hover:bg-brand-700 text-white font-semibold rounded-2xl shadow-lg shadow-brand-500/25 transition transform active:scale-95 flex items-center justify-center space-x-2">
            <span>Send Verification Code</span>
            <i data-lucide="arrow-right" class="w-4 h-4"></i>
          </button>
          <p class="text-center text-[11px] text-slate-400 mt-4">
            By continuing you agree to our Terms of Service & Privacy Policy.
          </p>
        </div>
      </div>
    `;
  },

  // OTP Verification Screen
  renderOTP(container, phone, devOtp) {
    container.innerHTML = `
      <div class="flex-1 flex flex-col p-6 bg-white justify-between">
        <div>
          <div class="flex items-center justify-between mb-8">
            <button onclick="router.navigate('login')" class="w-10 h-10 rounded-2xl bg-slate-100 flex items-center justify-center text-slate-600 hover:bg-slate-200 transition">
              <i data-lucide="chevron-left" class="w-5 h-5"></i>
            </button>
            <span class="text-xs font-semibold text-slate-400">Step 2 of 2</span>
          </div>

          <h2 class="text-2xl font-extrabold text-slate-900 tracking-tight">Verify Code</h2>
          <p class="text-slate-500 text-sm mt-1">
            Sent to <span class="font-bold text-slate-800">${phone}</span>
          </p>

          ${devOtp ? `
            <div class="mt-4 p-3 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center justify-between">
              <div class="flex items-center space-x-2 text-xs text-emerald-800">
                <i data-lucide="key" class="w-4 h-4 text-emerald-600"></i>
                <span>Development Mock Code: <strong>${devOtp}</strong></span>
              </div>
              <button onclick="document.getElementById('otp-code').value='${devOtp}'" class="text-xs bg-emerald-600 text-white px-2 py-1 rounded-md font-semibold hover:bg-emerald-700">
                Fill
              </button>
            </div>
          ` : ''}

          <div class="mt-8">
            <label class="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">6-Digit Code</label>
            <input id="otp-code" type="text" maxlength="6" placeholder="123456" value="${devOtp || '123456'}"
              class="w-full text-center tracking-[0.5em] py-4 bg-slate-50 border border-slate-200 rounded-2xl text-2xl font-mono font-bold focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white transition" />
          </div>

          <div class="flex justify-between items-center mt-4 text-xs">
            <span class="text-slate-400">Didn't receive code?</span>
            <button onclick="actions.requestLoginOTP('${phone}')" class="font-semibold text-brand-600 hover:underline">
              Resend OTP
            </button>
          </div>
        </div>

        <div>
          <button id="btn-verify-otp" onclick="actions.verifyLoginOTP('${phone}')" class="w-full py-4 bg-brand-600 hover:bg-brand-700 text-white font-semibold rounded-2xl shadow-lg shadow-brand-500/25 transition transform active:scale-95 flex items-center justify-center space-x-2">
            <span>Verify & Enter</span>
            <i data-lucide="check" class="w-4 h-4"></i>
          </button>
        </div>
      </div>
    `;
  },

  // Home Dashboard
  async renderHome(container) {
    container.innerHTML = `
      <div class="flex-1 flex flex-col bg-slate-50">
        <!-- Top App Header -->
        <header class="bg-slate-900 text-white px-6 pt-5 pb-6 rounded-b-[32px] shadow-lg">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-2">
              <div class="w-8 h-8 rounded-xl bg-brand-600 flex items-center justify-center shadow-md">
                <i data-lucide="shield-check" class="w-4 h-4 text-white"></i>
              </div>
              <span class="text-sm font-extrabold tracking-tight">SECURE PASS <span class="text-brand-400">RxQ</span></span>
            </div>
            <div class="flex items-center space-x-2">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span class="text-[11px] font-mono text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded-full border border-emerald-800/60">LIVE READY</span>
            </div>
          </div>

          <div class="mt-2">
            <span class="text-xs text-slate-400">Welcome back 👋</span>
            <h2 class="text-xl font-extrabold text-white tracking-tight">${state.user?.phone_number_masked || '+91 98765 •••••'}</h2>
          </div>
        </header>

        <!-- Main Body -->
        <div class="flex-1 p-5 space-y-6">
          <!-- Primary Hero Action Card -->
          <div class="bg-gradient-to-br from-brand-600 to-brand-800 text-white p-5 rounded-3xl shadow-xl shadow-brand-500/20 relative overflow-hidden">
            <div class="absolute -right-6 -bottom-6 w-32 h-32 bg-white/10 rounded-full blur-2xl"></div>
            <div class="relative z-10">
              <div class="inline-flex items-center space-x-1.5 px-2.5 py-1 bg-white/15 rounded-full text-[11px] font-semibold mb-3">
                <i data-lucide="zap" class="w-3.5 h-3.5 text-amber-300"></i>
                <span>Fast 10-Second Gifting</span>
              </div>
              <h3 class="text-xl font-extrabold leading-tight">Gift Mobile Data</h3>
              <p class="text-xs text-brand-100 mt-1 max-w-[240px]">
                Direct authorized retail booster pack recharge for any Jio, Airtel, Vi, or BSNL number.
              </p>
              
              <button onclick="router.navigate('send-data')" class="mt-5 w-full py-3.5 bg-white hover:bg-slate-100 text-brand-700 font-bold text-sm rounded-2xl shadow transition transform active:scale-95 flex items-center justify-center space-x-2">
                <i data-lucide="send" class="w-4 h-4"></i>
                <span>Send Data Pack Now</span>
              </button>
            </div>
          </div>

          <!-- Quick Frequent Recipients -->
          <div>
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wider">Quick Gifting Contacts</h4>
              <button onclick="router.navigate('account')" class="text-xs font-semibold text-brand-600 hover:underline">Manage</button>
            </div>
            <div class="flex space-x-3 overflow-x-auto pb-2 custom-scrollbar">
              <button onclick="actions.quickSend('+919820012345', 'Arjun Dorm')" class="flex-shrink-0 flex flex-col items-center p-3 bg-white border border-slate-200/80 rounded-2xl shadow-sm hover:border-brand-500 transition w-24">
                <div class="w-10 h-10 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs mb-1.5">
                  AS
                </div>
                <span class="text-xs font-bold text-slate-800 truncate w-full text-center">Arjun</span>
                <span class="text-[9px] text-slate-400">Jio</span>
              </button>

              <button onclick="actions.quickSend('+919812345678', 'Priya Sis')" class="flex-shrink-0 flex flex-col items-center p-3 bg-white border border-slate-200/80 rounded-2xl shadow-sm hover:border-brand-500 transition w-24">
                <div class="w-10 h-10 rounded-full bg-red-100 text-red-700 flex items-center justify-center font-bold text-xs mb-1.5">
                  PN
                </div>
                <span class="text-xs font-bold text-slate-800 truncate w-full text-center">Priya</span>
                <span class="text-[9px] text-slate-400">Airtel</span>
              </button>

              <button onclick="actions.quickSend('+919112345678', 'Rohan Roomie')" class="flex-shrink-0 flex flex-col items-center p-3 bg-white border border-slate-200/80 rounded-2xl shadow-sm hover:border-brand-500 transition w-24">
                <div class="w-10 h-10 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center font-bold text-xs mb-1.5">
                  RR
                </div>
                <span class="text-xs font-bold text-slate-800 truncate w-full text-center">Rohan</span>
                <span class="text-[9px] text-slate-400">Vi</span>
              </button>

              <button onclick="router.navigate('send-data')" class="flex-shrink-0 flex flex-col items-center justify-center p-3 bg-slate-100 border border-dashed border-slate-300 rounded-2xl hover:bg-slate-200 transition w-24">
                <div class="w-10 h-10 rounded-full bg-white text-slate-400 flex items-center justify-center font-bold mb-1.5">
                  <i data-lucide="plus" class="w-4 h-4"></i>
                </div>
                <span class="text-xs font-semibold text-slate-600">New</span>
              </button>
            </div>
          </div>

          <!-- Recent Transactions -->
          <div>
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wider">Recent Activity</h4>
              <button onclick="router.navigate('history')" class="text-xs font-semibold text-brand-600 hover:underline">View All</button>
            </div>
            <div id="home-recent-txns" class="space-y-2.5">
              <div class="text-center py-6 text-xs text-slate-400">Loading recent transactions...</div>
            </div>
          </div>
        </div>
      </div>
    `;
    actions.loadHomeTransactions();
  },

  // Send Data Step 1: Recipient & Operator Detection
  renderSendData(container) {
    container.innerHTML = `
      <div class="flex-1 flex flex-col bg-white">
        <!-- Top Nav Header -->
        <header class="flex items-center justify-between p-5 border-b border-slate-100">
          <button onclick="router.navigate('home')" class="w-10 h-10 rounded-2xl bg-slate-100 flex items-center justify-center text-slate-600 hover:bg-slate-200 transition">
            <i data-lucide="arrow-left" class="w-5 h-5"></i>
          </button>
          <span class="text-sm font-bold text-slate-900">Step 1 — Recipient</span>
          <div class="w-10"></div>
        </header>

        <div class="flex-1 p-6 flex flex-col justify-between">
          <div>
            <h2 class="text-2xl font-extrabold text-slate-900 tracking-tight">Who are you sending to?</h2>
            <p class="text-slate-500 text-sm mt-1">Enter the recipient's 10-digit mobile number.</p>

            <div class="mt-6">
              <label class="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">Recipient Number</label>
              <div class="relative flex items-center">
                <div class="absolute left-4 flex items-center space-x-1.5 text-slate-500 font-bold border-r border-slate-200 pr-3">
                  <span class="text-lg">🇮🇳</span>
                  <span class="text-sm">+91</span>
                </div>
                <input id="recipient-phone" type="tel" maxlength="10" placeholder="98200 12345" value="${state.sendData.phone ? state.sendData.phone.replace('+91', '') : '9820012345'}"
                  oninput="actions.onRecipientPhoneInput(this.value)"
                  class="w-full pl-24 pr-12 py-4 bg-slate-50 border border-slate-200 rounded-2xl text-lg font-bold tracking-wider focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white transition" />
                <div id="detection-spinner" class="absolute right-4 hidden">
                  <div class="w-5 h-5 border-2 border-brand-600 border-t-transparent rounded-full animate-spin"></div>
                </div>
              </div>
            </div>

            <!-- Auto-Detected Operator Card -->
            <div id="operator-detection-card" class="mt-6 p-4 rounded-2xl border transition duration-200 ${state.sendData.detectedOperator ? 'bg-slate-50 border-slate-200' : 'hidden'}">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <div id="detected-op-icon" class="w-10 h-10 rounded-xl bg-brand-600 text-white font-extrabold text-xs flex items-center justify-center">
                    ${state.sendData.detectedOperator?.code || 'TEL'}
                  </div>
                  <div>
                    <h4 id="detected-op-name" class="text-sm font-bold text-slate-900">${state.sendData.detectedOperator?.name || 'Operator Detected'}</h4>
                    <span id="detected-cir-name" class="text-xs text-slate-500">${state.sendData.detectedCircle?.name || 'Circle'}</span>
                  </div>
                </div>
                <span class="text-[10px] font-semibold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full flex items-center space-x-1">
                  <i data-lucide="check" class="w-3 h-3"></i>
                  <span>AUTO-DETECTED</span>
                </span>
              </div>
            </div>

            <!-- Test Simulation Notes -->
            <div class="mt-6 p-3 bg-amber-50 border border-amber-200/80 rounded-xl text-[11px] text-amber-900 space-y-1">
              <div class="font-bold flex items-center space-x-1">
                <i data-lucide="alert-circle" class="w-3.5 h-3.5 text-amber-700"></i>
                <span>Testing Simulation Numbers:</span>
              </div>
              <p>• Number ending in <strong>000</strong>: Simulates carrier decline &amp; triggers automated refund.</p>
              <p>• Other numbers: Instant operator confirmation.</p>
            </div>
          </div>

          <div>
            <button id="btn-continue-plan" onclick="actions.proceedToPlans()" class="w-full py-4 bg-brand-600 hover:bg-brand-700 text-white font-semibold rounded-2xl shadow-lg shadow-brand-500/25 transition transform active:scale-95 flex items-center justify-center space-x-2">
              <span>View Data Packs</span>
              <i data-lucide="arrow-right" class="w-4 h-4"></i>
            </button>
          </div>
        </div>
      </div>
    `;
    actions.onRecipientPhoneInput(document.getElementById('recipient-phone').value);
  },

  // Send Data Step 2: Select Data Pack
  renderSelectPlan(container) {
    container.innerHTML = `
      <div class="flex-1 flex flex-col bg-slate-50">
        <!-- Header -->
        <header class="bg-white px-5 pt-4 pb-3 border-b border-slate-200">
          <div class="flex items-center justify-between mb-3">
            <button onclick="router.navigate('send-data')" class="w-9 h-9 rounded-xl bg-slate-100 flex items-center justify-center text-slate-600 hover:bg-slate-200 transition">
              <i data-lucide="arrow-left" class="w-4 h-4"></i>
            </button>
            <div class="text-center">
              <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Step 2 of 3</span>
              <h3 class="text-sm font-extrabold text-slate-900">Select Data Pack</h3>
            </div>
            <div class="w-9"></div>
          </div>

          <!-- Recipient Pill -->
          <div class="flex items-center justify-between px-3 py-2 bg-slate-50 rounded-xl text-xs">
            <div class="flex items-center space-x-2">
              <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span class="font-bold text-slate-800">${state.sendData.phone}</span>
              <span class="text-slate-400">• ${state.sendData.detectedOperator?.name}</span>
            </div>
            <button onclick="router.navigate('send-data')" class="text-brand-600 font-semibold hover:underline">Edit</button>
          </div>

          <!-- Plan Categories Tabs -->
          <div class="flex space-x-2 mt-3">
            <button onclick="actions.switchPlanCategory('BOOSTER')" class="plan-tab flex-1 py-2 text-xs font-bold rounded-xl transition ${state.sendData.activeCategory === 'BOOSTER' ? 'bg-brand-600 text-white shadow' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}">
              ⚡ Boosters (1–3GB)
            </button>
            <button onclick="actions.switchPlanCategory('WORK')" class="plan-tab flex-1 py-2 text-xs font-bold rounded-xl transition ${state.sendData.activeCategory === 'WORK' ? 'bg-brand-600 text-white shadow' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}">
              💼 Work (6–12GB)
            </button>
            <button onclick="actions.switchPlanCategory('BULK')" class="plan-tab flex-1 py-2 text-xs font-bold rounded-xl transition ${state.sendData.activeCategory === 'BULK' ? 'bg-brand-600 text-white shadow' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}">
              📦 Bulk (50GB)
            </button>
          </div>
        </header>

        <!-- Plans Grid -->
        <div id="plans-container" class="flex-1 p-5 space-y-3 overflow-y-auto custom-scrollbar">
          <div class="text-center py-10 text-xs text-slate-400">Loading data packs...</div>
        </div>
      </div>
    `;
    actions.loadPlans();
  },

  // Send Data Step 3: Order Review & Checkout
  renderReviewOrder(container) {
    const plan = state.sendData.selectedPlan;
    const op = state.sendData.detectedOperator;
    const phone = state.sendData.phone;

    container.innerHTML = `
      <div class="flex-1 flex flex-col bg-slate-50 justify-between">
        <!-- Header -->
        <header class="bg-white px-5 py-4 border-b border-slate-200 flex items-center justify-between">
          <button onclick="router.navigate('select-plan')" class="w-9 h-9 rounded-xl bg-slate-100 flex items-center justify-center text-slate-600 hover:bg-slate-200 transition">
            <i data-lucide="arrow-left" class="w-4 h-4"></i>
          </button>
          <span class="text-sm font-bold text-slate-900">Order Summary</span>
          <div class="w-9"></div>
        </header>

        <div class="flex-1 p-5 space-y-5 overflow-y-auto">
          <!-- Main Pack Card -->
          <div class="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm">
            <div class="flex justify-between items-start pb-4 border-b border-slate-100">
              <div>
                <span class="text-xs font-bold text-brand-600 uppercase tracking-wider">Data Pack</span>
                <h3 class="text-2xl font-extrabold text-slate-900 mt-0.5">${plan.data_amount}</h3>
                <span class="text-xs text-slate-500">Validity: ${plan.validity_desc}</span>
              </div>
              <div class="text-right">
                <span class="text-2xl font-black text-slate-900">${plan.price_formatted}</span>
              </div>
            </div>

            <!-- Recipient Detail -->
            <div class="pt-4 space-y-2.5 text-xs">
              <div class="flex justify-between">
                <span class="text-slate-500">Recipient Phone:</span>
                <span class="font-bold text-slate-800">${phone}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-500">Carrier:</span>
                <span class="font-bold text-slate-800">${op.name}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-500">Service Area:</span>
                <span class="font-bold text-slate-800">${state.sendData.detectedCircle?.name || 'National'}</span>
              </div>
            </div>
          </div>

          <!-- Price Breakdown -->
          <div class="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm space-y-2.5 text-xs">
            <div class="flex justify-between text-slate-600">
              <span>Pack Base Price</span>
              <span>${plan.price_formatted}</span>
            </div>
            <div class="flex justify-between text-slate-600">
              <span>Platform Fee</span>
              <span class="text-emerald-600 font-semibold">FREE (₹0)</span>
            </div>
            <div class="flex justify-between text-slate-600">
              <span>Taxes (GST Included)</span>
              <span>₹0</span>
            </div>
            <div class="pt-2 border-t border-slate-100 flex justify-between font-extrabold text-sm text-slate-900">
              <span>Total Payable</span>
              <span class="text-brand-600 text-lg">${plan.price_formatted}</span>
            </div>
          </div>

          <!-- Statutory Business Disclaimer -->
          <div class="p-3.5 bg-slate-100 rounded-2xl flex items-start space-x-2.5 text-[11px] text-slate-600">
            <i data-lucide="shield" class="w-4 h-4 text-brand-600 flex-shrink-0 mt-0.5"></i>
            <div>
              <strong>Authorized Telecom Recharge:</strong> This transaction purchases an authorized carrier data top-up pack for the recipient. Data balance will be credited directly to recipient SIM.
            </div>
          </div>
        </div>

        <!-- Checkout Bottom Bar -->
        <div class="p-5 bg-white border-t border-slate-200">
          <button onclick="actions.openPaymentModal()" class="w-full py-4 bg-brand-600 hover:bg-brand-700 text-white font-bold rounded-2xl shadow-lg shadow-brand-500/25 transition transform active:scale-95 flex items-center justify-center space-x-2">
            <i data-lucide="lock" class="w-4 h-4"></i>
            <span>Pay &amp; Send Data (${plan.price_formatted})</span>
          </button>
        </div>
      </div>
    `;
  },

  // Live Tracking Screen
  renderTracking(container, orderId) {
    container.innerHTML = `
      <div class="flex-1 flex flex-col p-6 bg-slate-900 text-white justify-between">
        <div>
          <div class="flex items-center justify-between mb-8">
            <div class="flex items-center space-x-2">
              <div class="w-3 h-3 rounded-full bg-amber-400 animate-ping"></div>
              <span class="text-xs font-mono font-bold text-amber-400 uppercase tracking-widest">PROCESSING RECHARGE</span>
            </div>
            <span class="text-xs font-mono text-slate-500">${orderId}</span>
          </div>

          <div class="text-center my-6">
            <h2 class="text-2xl font-extrabold tracking-tight">Activating Data Pack</h2>
            <p class="text-slate-400 text-sm mt-1">Please do not press back or close the app.</p>
          </div>

          <!-- Stepper Container -->
          <div class="mt-8 space-y-6 relative pl-6 border-l-2 border-slate-700 ml-4">
            <!-- Step 1 -->
            <div class="relative">
              <div class="absolute -left-[33px] top-0 w-6 h-6 rounded-full bg-emerald-500 flex items-center justify-center text-white text-xs">
                <i data-lucide="check" class="w-3.5 h-3.5"></i>
              </div>
              <h4 class="font-bold text-sm text-white">Payment Confirmed</h4>
              <p class="text-xs text-slate-400">Gateway verified authorization token</p>
            </div>

            <!-- Step 2 -->
            <div id="step-telecom" class="relative">
              <div class="absolute -left-[33px] top-0 w-6 h-6 rounded-full bg-brand-500 flex items-center justify-center text-white text-xs animate-pulse">
                <i data-lucide="radio" class="w-3.5 h-3.5"></i>
              </div>
              <h4 class="font-bold text-sm text-white">Carrier Dispatching</h4>
              <p class="text-xs text-slate-400">Communicating with operator network...</p>
            </div>

            <!-- Step 3 -->
            <div id="step-confirm" class="relative">
              <div class="absolute -left-[33px] top-0 w-6 h-6 rounded-full bg-slate-700 flex items-center justify-center text-slate-400 text-xs">
                <i data-lucide="shield-check" class="w-3.5 h-3.5"></i>
              </div>
              <h4 class="font-bold text-sm text-slate-400">Activation Confirmation</h4>
              <p class="text-xs text-slate-500">Awaiting operator reference ID</p>
            </div>
          </div>
        </div>

        <div class="p-4 bg-slate-800/80 rounded-2xl border border-slate-700 text-center text-xs text-slate-400">
          <i data-lucide="lock" class="w-3.5 h-3.5 inline mr-1 text-emerald-400"></i>
          <span>Protected by Idempotency Key Lock • Zero Duplicate Deductions</span>
        </div>
      </div>
    `;
    actions.pollTransactionStatus(orderId);
  },

  // Success Screen
  renderSuccess(container, txn) {
    container.innerHTML = `
      <div class="flex-1 flex flex-col p-6 bg-slate-50 justify-between">
        <div class="flex flex-col items-center text-center mt-6">
          <div class="w-20 h-20 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shadow-xl shadow-emerald-500/20 mb-4 animate-bounce">
            <i data-lucide="check-check" class="w-10 h-10"></i>
          </div>
          <span class="text-xs font-bold text-emerald-700 uppercase tracking-widest bg-emerald-100 px-3 py-1 rounded-full">RECHARGE SUCCESSFUL</span>
          <h2 class="text-2xl font-black text-slate-900 mt-2">Data Pack Sent!</h2>
          <p class="text-slate-500 text-sm mt-1 max-w-[260px]">
            ${txn.plan_data} successfully activated on <strong>${txn.recipient_phone}</strong>.
          </p>

          <!-- Receipt Card -->
          <div class="w-full bg-white p-5 rounded-3xl border border-slate-200 shadow-sm mt-6 text-left text-xs space-y-3">
            <div class="flex justify-between items-center pb-3 border-b border-slate-100">
              <span class="text-slate-400">Order ID:</span>
              <span class="font-mono font-bold text-slate-800">${txn.order_id}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-slate-400">Carrier Reference:</span>
              <span class="font-mono font-bold text-emerald-700">${txn.telecom_reference_id || 'CONFIRMED'}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-slate-400">Operator:</span>
              <span class="font-bold text-slate-800">${txn.operator_name}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-slate-400">Data Allowance:</span>
              <span class="font-bold text-slate-800">${txn.plan_data}</span>
            </div>
            <div class="flex justify-between items-center pt-2 border-t border-slate-100 text-sm font-extrabold text-slate-900">
              <span>Amount Paid:</span>
              <span class="text-brand-600">${txn.amount_formatted}</span>
            </div>
          </div>
        </div>

        <div class="space-y-3">
          <button onclick="actions.saveRecentRecipient('${txn.recipient_phone}')" class="w-full py-3.5 bg-slate-200 hover:bg-slate-300 text-slate-800 font-bold rounded-2xl transition flex items-center justify-center space-x-2 text-xs">
            <i data-lucide="bookmark" class="w-4 h-4"></i>
            <span>Bookmark Recipient in Address Book</span>
          </button>
          <button onclick="router.navigate('home')" class="w-full py-4 bg-brand-600 hover:bg-brand-700 text-white font-bold rounded-2xl shadow-lg shadow-brand-500/25 transition transform active:scale-95">
            Return to Home
          </button>
        </div>
      </div>
    `;
  },

  // Transaction History
  renderHistory(container) {
    container.innerHTML = `
      <div class="flex-1 flex flex-col bg-slate-50">
        <header class="bg-white p-5 border-b border-slate-200 flex items-center justify-between">
          <h2 class="text-lg font-extrabold text-slate-900">Transaction History</h2>
          <span class="text-xs text-slate-400 font-mono" id="history-count">0 records</span>
        </header>

        <div id="history-list" class="flex-1 p-5 space-y-3 overflow-y-auto custom-scrollbar">
          <div class="text-center py-12 text-xs text-slate-400">Loading history...</div>
        </div>
      </div>
    `;
    actions.loadHistory();
  },

  // Transaction Details & Stepper Timeline
  renderTransactionDetails(container, orderId) {
    container.innerHTML = `
      <div class="flex-1 flex flex-col bg-slate-50 justify-between">
        <header class="bg-white px-5 py-4 border-b border-slate-200 flex items-center justify-between">
          <button onclick="router.navigate('history')" class="w-9 h-9 rounded-xl bg-slate-100 flex items-center justify-center text-slate-600 hover:bg-slate-200 transition">
            <i data-lucide="arrow-left" class="w-4 h-4"></i>
          </button>
          <span class="text-sm font-bold text-slate-900">Transaction Timeline</span>
          <div class="w-9"></div>
        </header>

        <div id="txn-details-content" class="flex-1 p-5 space-y-5 overflow-y-auto custom-scrollbar">
          <div class="text-center py-10 text-xs text-slate-400">Loading timeline...</div>
        </div>
      </div>
    `;
    actions.loadTransactionTimeline(orderId);
  },

  // User Account Screen
  renderAccount(container) {
    container.innerHTML = `
      <div class="flex-1 flex flex-col bg-slate-50">
        <header class="bg-slate-900 text-white p-6 rounded-b-3xl">
          <div class="flex items-center space-x-3">
            <div class="w-12 h-12 rounded-2xl bg-brand-600 flex items-center justify-center font-extrabold text-lg text-white">
              <i data-lucide="user" class="w-6 h-6"></i>
            </div>
            <div>
              <h3 class="font-extrabold text-base">${state.user?.phone_number || '+91 98765 43210'}</h3>
              <span class="text-xs text-emerald-400 font-semibold flex items-center space-x-1">
                <i data-lucide="shield-check" class="w-3.5 h-3.5"></i>
                <span>Verified Account</span>
              </span>
            </div>
          </div>
        </header>

        <div class="flex-1 p-5 space-y-4 overflow-y-auto">
          <!-- Saved Contacts Book -->
          <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
            <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">Saved Frequent Recipients</h4>
            <div id="account-recipients-list" class="space-y-2 text-xs">
              <div class="text-slate-400">Loading contacts...</div>
            </div>
          </div>

          <!-- Security & Compliance -->
          <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wider">Security &amp; Privacy</h4>
            
            <div class="flex justify-between items-center text-xs py-1.5 border-b border-slate-100">
              <div class="flex items-center space-x-2 text-slate-700">
                <i data-lucide="lock" class="w-4 h-4 text-slate-400"></i>
                <span>Idempotency Protection</span>
              </div>
              <span class="text-emerald-600 font-bold">ACTIVE</span>
            </div>

            <div class="flex justify-between items-center text-xs py-1.5 border-b border-slate-100">
              <div class="flex items-center space-x-2 text-slate-700">
                <i data-lucide="server" class="w-4 h-4 text-slate-400"></i>
                <span>Engine Mode</span>
              </div>
              <span class="text-brand-600 font-bold uppercase">MOCK DEV ENGINE</span>
            </div>

            <div class="flex justify-between items-center text-xs py-1.5">
              <div class="flex items-center space-x-2 text-slate-700">
                <i data-lucide="file-text" class="w-4 h-4 text-slate-400"></i>
                <span>Open API Documentation</span>
              </div>
              <a href="/docs" target="_blank" class="text-brand-600 font-bold hover:underline">/docs</a>
            </div>
          </div>

          <!-- Logout Button -->
          <button onclick="actions.logout()" class="w-full py-3.5 bg-rose-50 border border-rose-200 text-rose-700 font-bold text-xs rounded-2xl hover:bg-rose-100 transition flex items-center justify-center space-x-2">
            <i data-lucide="log-out" class="w-4 h-4"></i>
            <span>Log Out</span>
          </button>
        </div>
      </div>
    `;
    actions.loadAccountRecipients();
  }
};

// Application Business Actions
const actions = {

  // Auth: Request OTP
  async requestLoginOTP(customPhone = null) {
    const phoneInput = document.getElementById('login-phone');
    const rawDigits = customPhone || (phoneInput ? phoneInput.value : '9876543210');
    try {
      const data = await api.fetch('/api/v1/auth/request-otp', {
        method: 'POST',
        body: JSON.stringify({ phone_number: rawDigits }),
      });
      if (data) {
        showToast(data.message, 'success');
        router.navigate('otp', { phone: `+91 ${rawDigits.replace('+91', '')}`, devOtp: data.dev_otp });
      }
    } catch (e) {}
  },

  // Auth: Verify OTP
  async verifyLoginOTP(phone) {
    const otpInput = document.getElementById('otp-code');
    const code = otpInput ? otpInput.value.trim() : '123456';
    try {
      const data = await api.fetch('/api/v1/auth/verify-otp', {
        method: 'POST',
        body: JSON.stringify({ phone_number: phone, otp: code }),
      });
      if (data && data.access_token) {
        state.token = data.access_token;
        state.user = data.user;
        localStorage.setItem('secure_pass_token', data.access_token);
        localStorage.setItem('secure_pass_user', JSON.stringify(data.user));
        showToast('Successfully authenticated!', 'success');
        router.navigate('home');
      }
    } catch (e) {}
  },

  // Logout
  logout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem('secure_pass_token');
    localStorage.removeItem('secure_pass_user');
    showToast('Logged out safely.', 'info');
    router.navigate('login');
  },

  // Recipient input handler & live MNP detection
  async onRecipientPhoneInput(val) {
    const clean = val.replace(/\D/g, '');
    const card = document.getElementById('operator-detection-card');
    const spinner = document.getElementById('detection-spinner');
    
    if (clean.length === 10) {
      if (spinner) spinner.classList.remove('hidden');
      try {
        const data = await api.fetch('/api/v1/operators/detect', {
          method: 'POST',
          body: JSON.stringify({ phone_number: clean }),
        });
        if (data) {
          state.sendData.phone = data.phone_number;
          state.sendData.detectedOperator = data.operator;
          state.sendData.detectedCircle = data.circle;

          if (card) {
            card.classList.remove('hidden');
            document.getElementById('detected-op-name').textContent = data.operator.name;
            document.getElementById('detected-op-icon').textContent = data.operator.code;
            document.getElementById('detected-cir-name').textContent = data.circle.name;
          }
        }
      } catch (e) {} finally {
        if (spinner) spinner.classList.add('hidden');
      }
    } else {
      if (card) card.classList.add('hidden');
    }
  },

  // Quick Send from home contact
  quickSend(phone, nickname) {
    state.sendData.phone = phone;
    router.navigate('send-data');
  },

  // Proceed to plans view
  proceedToPlans() {
    if (!state.sendData.detectedOperator) {
      showToast('Please enter a valid 10-digit mobile number.', 'warning');
      return;
    }
    router.navigate('select-plan');
  },

  // Switch Plan Category Tab
  switchPlanCategory(category) {
    state.sendData.activeCategory = category;
    router.navigate('select-plan');
  },

  // Load Plans from API
  async loadPlans() {
    const container = document.getElementById('plans-container');
    const op = state.sendData.detectedOperator;
    if (!container || !op) return;

    try {
      const plans = await api.fetch(`/api/v1/plans?operator_id=${op.id}&category=${state.sendData.activeCategory}`);
      if (!plans || plans.length === 0) {
        container.innerHTML = `<div class="text-center py-10 text-xs text-slate-400">No packs found in this category.</div>`;
        return;
      }
      state.sendData.availablePlans = plans;

      container.innerHTML = plans.map(p => `
        <div onclick="actions.selectPlan('${p.id}')" class="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm hover:border-brand-500 hover:shadow-md transition cursor-pointer flex justify-between items-center group">
          <div class="space-y-1">
            <div class="flex items-center space-x-2">
              <span class="text-base font-extrabold text-slate-900">${p.data_amount}</span>
              <span class="text-[10px] font-bold bg-brand-50 text-brand-700 px-2 py-0.5 rounded-full">${p.validity_desc}</span>
            </div>
            <p class="text-xs text-slate-500 max-w-[220px]">${p.description}</p>
          </div>
          <div class="text-right flex flex-col items-end">
            <span class="text-lg font-black text-slate-900 group-hover:text-brand-600 transition">${p.price_formatted}</span>
            <button class="mt-1 text-xs font-bold text-brand-600 bg-brand-50 group-hover:bg-brand-600 group-hover:text-white px-3 py-1 rounded-xl transition">
              Select
            </button>
          </div>
        </div>
      `).join('');
      lucide.createIcons();
    } catch (e) {
      container.innerHTML = `<div class="text-center py-10 text-xs text-rose-500">Failed to load plans.</div>`;
    }
  },

  // Select Plan and move to Review
  selectPlan(planId) {
    const plan = state.sendData.availablePlans.find(p => p.id === planId);
    if (!plan) return;
    state.sendData.selectedPlan = plan;
    router.navigate('review-order');
  },

  // Payment Checkout Modal
  openPaymentModal() {
    const plan = state.sendData.selectedPlan;
    const modalHtml = `
      <div id="payment-modal-overlay" class="absolute inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-end justify-center">
        <div class="w-full bg-white rounded-t-[36px] p-6 space-y-5 animate-slide-up">
          <div class="w-12 h-1.5 bg-slate-200 rounded-full mx-auto"></div>
          
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-extrabold text-slate-900">Choose Payment Method</h3>
            <button onclick="document.getElementById('payment-modal-overlay').remove()" class="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-500">
              <i data-lucide="x" class="w-4 h-4"></i>
            </button>
          </div>

          <div class="space-y-2.5">
            <button onclick="actions.processPaymentWithMethod('UPI')" class="w-full p-4 border border-slate-200 rounded-2xl hover:border-brand-500 hover:bg-brand-50/50 flex items-center justify-between transition">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center font-bold text-xs">UPI</div>
                <div class="text-left">
                  <h4 class="text-sm font-bold text-slate-900">Google Pay / PhonePe / Paytm</h4>
                  <span class="text-xs text-slate-400">Instant UPI Direct Debit</span>
                </div>
              </div>
              <i data-lucide="chevron-right" class="w-5 h-5 text-slate-400"></i>
            </button>

            <button onclick="actions.processPaymentWithMethod('CARD')" class="w-full p-4 border border-slate-200 rounded-2xl hover:border-brand-500 hover:bg-brand-50/50 flex items-center justify-between transition">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs">
                  <i data-lucide="credit-card" class="w-5 h-5"></i>
                </div>
                <div class="text-left">
                  <h4 class="text-sm font-bold text-slate-900">Credit / Debit Card</h4>
                  <span class="text-xs text-slate-400">Visa, Mastercard, RuPay</span>
                </div>
              </div>
              <i data-lucide="chevron-right" class="w-5 h-5 text-slate-400"></i>
            </button>

            <!-- Test Hook Button -->
            <button onclick="actions.processPaymentWithMethod('FAIL_TEST')" class="w-full p-3 border border-dashed border-rose-200 rounded-2xl bg-rose-50/50 flex items-center justify-between hover:bg-rose-100/50 transition">
              <div class="text-left text-xs">
                <span class="font-bold text-rose-800">🧪 Simulate Card Decline (Test Hook)</span>
                <p class="text-rose-600 text-[10px]">Tests payment failure state transition</p>
              </div>
              <i data-lucide="alert-triangle" class="w-4 h-4 text-rose-600"></i>
            </button>
          </div>
        </div>
      </div>
    `;
    document.getElementById('app-viewport').insertAdjacentHTML('beforeend', modalHtml);
    lucide.createIcons();
  },

  // Create Order and Execute Payment
  async processPaymentWithMethod(method) {
    const overlay = document.getElementById('payment-modal-overlay');
    if (overlay) overlay.remove();

    // 1. Generate client UUIDv4 idempotency key
    const idempotencyKey = crypto.randomUUID ? crypto.randomUUID() : 'idem-' + Date.now() + '-' + Math.random().toString(36).substring(2, 9);

    try {
      // 2. Place Order (idempotent)
      const order = await api.fetch('/api/v1/orders', {
        method: 'POST',
        headers: { 'X-Idempotency-Key': idempotencyKey },
        body: JSON.stringify({
          recipient_phone: state.sendData.phone,
          operator_id: state.sendData.detectedOperator.id,
          circle_id: state.sendData.detectedCircle?.id,
          plan_id: state.sendData.selectedPlan.id,
        })
      });
      if (!order) return;
      state.sendData.createdOrder = order;

      // 3. Create Payment Intent
      const intent = await api.fetch('/api/v1/payments/create-intent', {
        method: 'POST',
        body: JSON.stringify({
          order_id: order.order_id,
          payment_method: method,
        })
      });
      if (!intent) return;

      // 4. Navigate to live tracking screen
      router.navigate('tracking', { orderId: order.order_id });

      // 5. Verify payment (simulated client callback)
      const verifyRes = await api.fetch('/api/v1/payments/verify', {
        method: 'POST',
        body: JSON.stringify({
          order_id: order.order_id,
          payment_id: intent.payment_id,
          gateway_payment_id: `pay_mock_${Date.now()}`,
          payment_method: method,
          signature: 'mock_valid_sig',
        })
      });

    } catch (e) {}
  },

  // Poll transaction status on Tracking view
  pollTransactionStatus(orderId) {
    let attempts = 0;
    const interval = setInterval(async () => {
      attempts++;
      try {
        const txn = await api.fetch(`/api/v1/transactions/${orderId}`);
        if (!txn) return;

        // If reached SUCCESS
        if (txn.current_state === 'SUCCESS') {
          clearInterval(interval);
          setTimeout(() => {
            router.navigate('success', { transaction: txn });
          }, 800);
        }
        // If reached REFUNDED (due to telecom rejection)
        else if (txn.current_state === 'REFUNDED') {
          clearInterval(interval);
          showToast('Telecom carrier rejected recharge. Automated refund completed!', 'warning');
          setTimeout(() => {
            router.navigate('transaction-details', { orderId: orderId });
          }, 800);
        }
        else if (attempts > 12) {
          clearInterval(interval);
        }
      } catch (e) {
        clearInterval(interval);
      }
    }, 1000);
  },

  // Save Recent Recipient
  async saveRecentRecipient(phone) {
    try {
      await api.fetch('/api/v1/recipients', {
        method: 'POST',
        body: JSON.stringify({
          phone_number: phone,
          nickname: 'Saved Contact',
          operator_id: state.sendData.detectedOperator?.id,
        })
      });
      showToast('Contact saved to your address book!', 'success');
    } catch (e) {}
  },

  // Load Home recent transactions
  async loadHomeTransactions() {
    const list = document.getElementById('home-recent-txns');
    if (!list) return;
    try {
      const txns = await api.fetch('/api/v1/transactions?limit=3');
      if (!txns || txns.length === 0) {
        list.innerHTML = `<div class="p-4 bg-white rounded-2xl border border-slate-200 text-center text-xs text-slate-400">No transactions yet. Send your first data pack!</div>`;
        return;
      }
      list.innerHTML = txns.map(t => `
        <div onclick="router.navigate('transaction-details', { orderId: '${t.order_id}' })" class="p-3.5 bg-white rounded-2xl border border-slate-200/80 shadow-sm flex items-center justify-between hover:border-brand-500 cursor-pointer transition">
          <div class="flex items-center space-x-3">
            <div class="w-9 h-9 rounded-xl bg-slate-100 flex items-center justify-center font-bold text-xs text-slate-700">
              ${t.operator_code}
            </div>
            <div>
              <h5 class="text-xs font-bold text-slate-900">${t.recipient_phone_masked}</h5>
              <span class="text-[10px] text-slate-400">${t.operator_name} • ${t.plan_data}</span>
            </div>
          </div>
          <div class="text-right">
            <span class="text-xs font-bold text-slate-900">${t.amount_formatted}</span>
            <div>
              <span class="text-[9px] font-bold px-1.5 py-0.5 rounded-full ${
                t.status === 'SUCCESS' ? 'bg-emerald-100 text-emerald-800' :
                t.status === 'REFUNDED' ? 'bg-sky-100 text-sky-800' : 'bg-amber-100 text-amber-800'
              }">${t.status}</span>
            </div>
          </div>
        </div>
      `).join('');
      lucide.createIcons();
    } catch (e) {}
  },

  // Load History view
  async loadHistory() {
    const list = document.getElementById('history-list');
    const countEl = document.getElementById('history-count');
    if (!list) return;

    try {
      const txns = await api.fetch('/api/v1/transactions?limit=50');
      if (!txns || txns.length === 0) {
        list.innerHTML = `<div class="text-center py-12 text-xs text-slate-400">No transaction records found.</div>`;
        return;
      }
      if (countEl) countEl.textContent = `${txns.length} records`;

      list.innerHTML = txns.map(t => `
        <div onclick="router.navigate('transaction-details', { orderId: '${t.order_id}' })" class="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm hover:border-brand-500 cursor-pointer transition flex items-center justify-between">
          <div class="space-y-1">
            <div class="flex items-center space-x-2">
              <span class="text-xs font-extrabold text-slate-900">${t.recipient_phone_masked}</span>
              <span class="text-[10px] font-bold bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">${t.operator_code}</span>
            </div>
            <p class="text-[11px] text-slate-500">${t.plan_data} • ${new Date(t.created_at).toLocaleDateString()}</p>
          </div>
          <div class="text-right">
            <span class="text-sm font-black text-slate-900">${t.amount_formatted}</span>
            <div>
              <span class="text-[10px] font-bold px-2 py-0.5 rounded-full ${
                t.status === 'SUCCESS' ? 'bg-emerald-100 text-emerald-800' :
                t.status === 'REFUNDED' ? 'bg-sky-100 text-sky-800' : 'bg-amber-100 text-amber-800'
              }">${t.status}</span>
            </div>
          </div>
        </div>
      `).join('');
      lucide.createIcons();
    } catch (e) {
      list.innerHTML = `<div class="text-center py-12 text-xs text-rose-500">Failed to load history.</div>`;
    }
  },

  // Load Transaction timeline
  async loadTransactionTimeline(orderId) {
    const content = document.getElementById('txn-details-content');
    if (!content) return;

    try {
      const txn = await api.fetch(`/api/v1/transactions/${orderId}`);
      if (!txn) return;

      content.innerHTML = `
        <div class="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm space-y-3">
          <div class="flex justify-between items-start pb-3 border-b border-slate-100">
            <div>
              <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Transaction ID</span>
              <h4 class="font-mono font-bold text-sm text-slate-900">${txn.order_id}</h4>
            </div>
            <span class="text-xs font-bold px-2.5 py-1 rounded-full ${
              txn.current_state === 'SUCCESS' ? 'bg-emerald-100 text-emerald-800' :
              txn.current_state === 'REFUNDED' ? 'bg-sky-100 text-sky-800' : 'bg-amber-100 text-amber-800'
            }">${txn.current_state}</span>
          </div>

          <div class="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span class="text-slate-400">Recipient:</span>
              <p class="font-bold text-slate-800">${txn.recipient_phone}</p>
            </div>
            <div>
              <span class="text-slate-400">Carrier:</span>
              <p class="font-bold text-slate-800">${txn.operator_name}</p>
            </div>
            <div>
              <span class="text-slate-400">Pack:</span>
              <p class="font-bold text-slate-800">${txn.plan_data} (${txn.plan_validity})</p>
            </div>
            <div>
              <span class="text-slate-400">Amount:</span>
              <p class="font-bold text-brand-600">${txn.amount_formatted}</p>
            </div>
          </div>
        </div>

        <!-- Audit Timeline Stepper -->
        <div class="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm">
          <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wider mb-4">State Machine Timeline</h4>
          <div class="space-y-4 pl-4 border-l-2 border-slate-200 ml-2">
            ${txn.timeline.map(e => `
              <div class="relative">
                <div class="absolute -left-[23px] top-0.5 w-3.5 h-3.5 rounded-full ${e.state === 'SUCCESS' ? 'bg-emerald-500' : e.state === 'REFUNDED' ? 'bg-sky-500' : 'bg-brand-600'}"></div>
                <h5 class="text-xs font-bold text-slate-800">${e.label}</h5>
                <span class="text-[10px] text-slate-400 font-mono">${new Date(e.timestamp).toLocaleTimeString()}</span>
              </div>
            `).join('')}
          </div>
        </div>
      `;
      lucide.createIcons();
    } catch (e) {
      content.innerHTML = `<div class="text-center py-10 text-xs text-rose-500">Failed to load transaction details.</div>`;
    }
  },

  // Load Account Saved Contacts
  async loadAccountRecipients() {
    const list = document.getElementById('account-recipients-list');
    if (!list) return;
    try {
      const recs = await api.fetch('/api/v1/recipients');
      if (!recs || recs.length === 0) {
        list.innerHTML = `<div class="text-slate-400 py-2">No saved recipients yet.</div>`;
        return;
      }
      list.innerHTML = recs.map(r => `
        <div class="flex items-center justify-between p-2.5 bg-slate-50 rounded-xl">
          <div class="flex items-center space-x-2.5">
            <div class="w-8 h-8 rounded-full bg-brand-100 text-brand-700 font-bold text-xs flex items-center justify-center">
              ${r.nickname.substring(0, 2).toUpperCase()}
            </div>
            <div>
              <h5 class="font-bold text-slate-800 text-xs">${r.nickname}</h5>
              <span class="text-[10px] text-slate-400">${r.phone_number_masked}</span>
            </div>
          </div>
          <button onclick="actions.quickSend('${r.phone_number}', '${r.nickname}')" class="text-xs font-bold text-brand-600 hover:underline">
            Gift Data
          </button>
        </div>
      `).join('');
    } catch (e) {}
  }
};

// Bootstrap application on page load
window.addEventListener('DOMContentLoaded', () => {
  if (state.token) {
    router.navigate('home');
  } else {
    router.navigate('splash');
  }
});
