import axios from 'axios'

// In production (Railway/Vercel): VITE_API_URL = https://your-backend.up.railway.app
// In development: empty string → Vite proxy handles /api → localhost:8000
const BASE_URL = import.meta.env.VITE_API_URL ?? ''

const api = axios.create({ baseURL: BASE_URL })

// Attach JWT token to every request automatically
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default api
