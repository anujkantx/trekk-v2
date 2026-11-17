import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Attach JWT token from localStorage to every outgoing request
api.interceptors.request.use(
  (config) => {
    const token = authState.getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Intercept 401s / 422s to auto-logout expired/corrupted sessions
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && (error.response.status === 401 || error.response.status === 422)) {
      authState.clearAuth()
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const authState = {
  getToken() {
    const token = localStorage.getItem('token')
    return (token && token !== 'undefined' && token !== 'null') ? token : null
  },
  getUser() {
    const userStr = localStorage.getItem('user')
    try {
      return userStr ? JSON.parse(userStr) : null
    } catch {
      return null
    }
  },
  getRole() {
    const user = this.getUser()
    return user ? user.role : null
  },
  isAuthenticated() {
    return !!this.getToken()
  },
  setAuth(token, user) {
    if (token) {
      localStorage.setItem('token', token)
    } else {
      localStorage.removeItem('token')
    }
    if (user) {
      localStorage.setItem('user', JSON.stringify(user))
    } else {
      localStorage.removeItem('user')
    }
  },
  clearAuth() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
}

export default api
