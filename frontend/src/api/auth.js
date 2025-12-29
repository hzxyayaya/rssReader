import http from './http'
import { jwtDecode } from 'jwt-decode' // Need to install jwt-decode or just store token

export async function login(username, password) {
    const data = new URLSearchParams()
    data.append('username', username)
    data.append('password', password)

    const res = await http.post('/auth/login', data, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })

    if (res.access_token) {
        localStorage.setItem('access_token', res.access_token)
        return res.access_token
    }
    return null
}

export async function register(username, email, password) {
    const res = await http.post('/auth/register', {
        username,
        email,
        password
    })
    return res
}

export function logout() {
    localStorage.removeItem('access_token')
}

export function getToken() {
    return localStorage.getItem('access_token')
}

export function isAuthenticated() {
    return !!getToken()
}

export async function fetchUserProfile() {
    return http.get('/auth/me')
}
