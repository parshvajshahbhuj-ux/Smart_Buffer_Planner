/* ===== Smart Buffet Planner - Auth & API Utilities ===== */

function getToken() {
  return localStorage.getItem('access');
}

function getUser() {
  try {
    return JSON.parse(localStorage.getItem('user'));
  } catch { return null; }
}

function isLoggedIn() {
  return !!getToken();
}

function logout() {
  const token = getToken();
  const refresh = localStorage.getItem('refresh');
  if (refresh) {
    fetch('/api/auth/logout/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token},
      body: JSON.stringify({refresh})
    }).catch(() => {});
  }
  localStorage.clear();
  window.location.href = '/login/';
}

// Redirect to login if not authenticated
function requireAuth(adminOnly = false) {
  if (!isLoggedIn()) {
    window.location.href = '/login/';
    return;
  }
  if (adminOnly) {
    const user = getUser();
    if (!user?.is_staff && user?.role !== 'admin') {
      window.location.href = '/dashboard/';
    }
  }
}

// Update navbar based on auth state
function updateNav() {
  const user = getUser();
  if (isLoggedIn() && user) {
    document.getElementById('navDashboard')?.classList.remove('d-none');
    document.getElementById('navAnalytics')?.classList.remove('d-none');
    document.getElementById('navLogout')?.classList.remove('d-none');
    document.getElementById('navUser')?.classList.remove('d-none');
    document.getElementById('navLogin')?.classList.add('d-none');
    const nameEl = document.getElementById('navUsername');
    if (nameEl) nameEl.textContent = `👤 ${user.username || user.email}`;
    if (user.is_staff || user.role === 'admin') {
      document.getElementById('navAdmin')?.classList.remove('d-none');
    }
  }
}

// Generic API helpers
async function apiGet(url) {
  try {
    const res = await fetch(url, {
      headers: {'Authorization': 'Bearer ' + getToken()}
    });
    if (res.status === 401) { logout(); return null; }
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    console.error('API GET error:', e);
    return null;
  }
}

async function apiDelete(url) {
  try {
    const res = await fetch(url, {
      method: 'DELETE',
      headers: {'Authorization': 'Bearer ' + getToken()}
    });
    if (res.status === 401) { logout(); return null; }
    return res.ok || res.status === 204 ? true : null;
  } catch (e) {
    console.error('API DELETE error:', e);
    return null;
  }
}

// Show alert helper
function showAlert(containerId, message, type = 'info') {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.className = `alert alert-${type}`;
  el.innerHTML = message;
  el.classList.remove('d-none');
  if (type === 'success') {
    setTimeout(() => el.classList.add('d-none'), 4000);
  }
}

// Auto-refresh token
async function refreshToken() {
  const refresh = localStorage.getItem('refresh');
  if (!refresh) return;
  try {
    const res = await fetch('/api/auth/token/refresh/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({refresh})
    });
    if (res.ok) {
      const data = await res.json();
      localStorage.setItem('access', data.access);
    } else {
      logout();
    }
  } catch {}
}

// Run on every page load
document.addEventListener('DOMContentLoaded', () => {
  updateNav();
  // Refresh token every 20 minutes
  if (isLoggedIn()) {
    setInterval(refreshToken, 20 * 60 * 1000);
  }
});
