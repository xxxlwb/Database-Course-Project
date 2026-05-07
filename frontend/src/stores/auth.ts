import { defineStore } from 'pinia'
import { ref } from 'vue'
import client from '../api/client'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<{ id: number; username: string; role: string } | null>(
    JSON.parse(localStorage.getItem('nkg_user') || 'null')
  )

  async function login(username: string, password: string) {
    const r = await client.post('/auth/login', { username, password })
    localStorage.setItem('nkg_token', r.data.access_token)
    localStorage.setItem('nkg_user', JSON.stringify(r.data.user))
    user.value = r.data.user
  }

  async function register(username: string, email: string, password: string) {
    const r = await client.post('/auth/register', { username, email, password })
    localStorage.setItem('nkg_token', r.data.access_token)
    localStorage.setItem('nkg_user', JSON.stringify(r.data.user))
    user.value = r.data.user
  }

  function logout() {
    localStorage.removeItem('nkg_token')
    localStorage.removeItem('nkg_user')
    user.value = null
  }

  return { user, login, register, logout }
})
