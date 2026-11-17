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
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Intercept 401s to auto-logout expired sessions
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const authState = {
  getToken() {
    return localStorage.getItem('token')
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
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
  },
  clearAuth() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
}

export default api
