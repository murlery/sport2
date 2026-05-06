<template>
  <div class="login-container">
    <div class="login-card">
      <h1>Вход в систему</h1>
      
      <div v-if="alreadyLoggedIn" class="already-logged-in">
        <p>Вы уже авторизованы как {{ currentUser?.first_name }} {{ currentUser?.last_name }}</p>
        <button @click="logoutAndReload" class="logout-btn">
          Выйти и войти под другим пользователем
        </button>
      </div>
      
      <form v-else @submit.prevent="login" class="login-form">
        <div class="form-group">
          <input 
            v-model="username" 
            placeholder="Имя пользователя" 
            required
          />
        </div>
        <div class="form-group">
          <input 
            v-model="password" 
            type="password" 
            placeholder="Пароль" 
            required
          />
        </div>
        <button type="submit" :disabled="loading" class="submit-btn">
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
      </form>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from '../axios'

export default {
  name: 'LoginPage',
  
  data() {
    return {
      username: '',
      password: '',
      error: '',
      loading: false,
      alreadyLoggedIn: false,
      currentUser: null
    }
  },
  
  mounted() {
    this.checkAuthStatus()
  },
  
  methods: {
    async checkAuthStatus() {
      const token = localStorage.getItem('token')
      const user = localStorage.getItem('user')
      
      if (token && user) {
        try {
          await axios.get('/api/departments/')
          this.alreadyLoggedIn = true
          this.currentUser = JSON.parse(user)
          this.redirectToDashboard()
        } catch (err) {
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          this.alreadyLoggedIn = false
        }
      }
    },
    
    async login() {
      this.loading = true
      this.error = ''
      
      try {
        const response = await axios.post('/api/auth/login/', {
          username: this.username,
          password: this.password
        })
        
        localStorage.setItem('token', response.data.token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        axios.defaults.headers.common['Authorization'] = `Token ${response.data.token}`
        
        this.redirectByRole(response.data.user.role)
        
      } catch (err) {
        console.error('Ошибка входа:', err)
        
        if (err.response?.status === 400) {
          this.error = 'Неверное имя пользователя или пароль'
        } else if (err.response?.status === 401 || err.response?.status === 403) {
          this.error = 'Доступ запрещен'
        } else if (err.message.includes('Network Error')) {
          this.error = 'Не удалось подключиться к серверу'
        } else {
          this.error = 'Произошла ошибка. Попробуйте еще раз.'
        }
      } finally {
        this.loading = false
      }
    },
    
    async logoutAndReload() {
      try {
        await axios.post('/api/auth/logout/')
      } catch (err) {
        // Игнорируем ошибки
      }
      
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      delete axios.defaults.headers.common['Authorization']
      window.location.reload()
    },
    
    redirectToDashboard() {
      if (!this.currentUser) return
      
      const routes = {
        manager: '/manager',
        coach: '/coach',
        methodist: '/methodist'
      }
      
      if (routes[this.currentUser.role]) {
        this.$router.push(routes[this.currentUser.role])
      }
    },
    
    redirectByRole(role) {
      const routes = {
        manager: '/manager',
        coach: '/coach',
        methodist: '/methodist'
      }
      
      if (routes[role]) {
        this.$router.push(routes[role])
      } else {
        this.error = 'Неизвестная роль пользователя'
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
 
}

.login-card {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 400px;
  margin: 20px;
}

.login-card h1 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
  font-size: 1.8rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.form-group {
  margin-bottom: 1.2rem;
  width: 100%;
}

.form-group input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #011985;
  box-shadow: 0 0 0 3px rgba(1, 25, 133, 0.1);
}

.submit-btn {
  width: 100%;
  padding: 0.8rem;
  background: linear-gradient(135deg, #011985 0%, #011985 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  text-align: center;
  box-sizing: border-box;
  transition: transform 0.2s, box-shadow 0.2s;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(1, 25, 133, 0.3);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  margin-top: 1rem;
  color: #e74c3c;
  text-align: center;
  padding: 0.5rem;
  background: #fdf0ed;
  border-radius: 6px;
}

.already-logged-in {
  text-align: center;
  margin-bottom: 1.5rem;
}

.already-logged-in p {
  margin-bottom: 1rem;
  color: #333;
}

.logout-btn {
  padding: 0.6rem 1.5rem;
  border: none;
  border-radius: 6px;
  background: #ff6b6b;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s, transform 0.2s;
  width: 100%;
  box-sizing: border-box;
}

.logout-btn:hover {
  background: #ff4b4b;
  transform: translateY(-2px);
}
</style>