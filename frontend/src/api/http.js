import axios from 'axios'

const http = axios.create({
    baseURL: '/api', // Vite proxy will handle this
    timeout: 60000  // 60 seconds for AI Q&A
})

// Request interceptor: Add Token
http.interceptors.request.use(
    config => {
        const token = localStorage.getItem('access_token')
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`
        }
        return config
    },
    error => {
        return Promise.reject(error)
    }
)

// Response interceptor
http.interceptors.response.use(
    response => {
        return response.data
    },
    error => {
        if (error.response) {
            // 401: Unauthorized -> Clear token & redirect to login (implement logic in store/router guards)
            if (error.response.status === 401) {
                localStorage.removeItem('access_token')
                // flexible handling
            }
            return Promise.reject(error.response.data)
        }
        return Promise.reject(error)
    }
)

export default http
