<template>
  <div class="manager-dashboard">
    <TopNavigationBar :title="'Панель руководителя'" :user="currentUser" :tabs="tabs" @tab-change="onTabChange"
      @logout="logout" />

    <router-view />

    <div v-if="notification.show" :class="['notification', notification.type]">
      {{ notification.message }}
    </div>
  </div>
</template>

<script>
import TopNavigationBar from '../components/TopNavigationBar.vue'
import axios from '../axios'

export default {
  name: 'ManagerDashboard',
  components: { TopNavigationBar },
  data() {
    return {
      currentUser: null,
      notification: { show: false, message: '', type: 'info' },
      tabs: [
        { id: 'main', label: 'Главная', route: { name: 'ManagerMain' } },
        { id: 'docs', label: 'Документы', route: { name: 'ManagerDocs' } }
      ]
    }
  },
  computed: {
    activeTab() {
      const routeName = this.$route.name
      return this.tabs.find(t => t.route === routeName)?.id || 'main'
    }
  },
  mounted() {
    this.loadCurrentUser()
  },
  methods: {
    async loadCurrentUser() {
      const raw = localStorage.getItem('user')
      if (raw) this.currentUser = JSON.parse(raw)
      else {
        try {
          const res = await axios.get('/api/auth/me/')
          this.currentUser = res.data
          localStorage.setItem('user', JSON.stringify(res.data))
        } catch (e) {
          console.warn('Не удалось загрузить пользователя', e)
        }
      }
    },
    onTabChange(tabId) {
      const tab = this.tabs.find(t => t.id === tabId)
      if (tab) this.$router.push({ name: tab.route })
    },
    async logout() {
      try { await axios.post('/api/auth/logout/') } catch { }
      localStorage.clear()
      delete axios.defaults.headers.common['Authorization']
      this.$router.push('/')
    },
    showNotification(message, type = 'info') {
      this.notification = { show: true, message, type }
      setTimeout(() => (this.notification.show = false), 3000)
    }
  }
}
</script>

<style scoped>
.manager-dashboard {
  min-height: 100vh;
    padding: 20px;
  
}

.notification {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 10px 18px;
  border-radius: 6px;
  color: #fff;
  z-index: 1000;
  font-weight: bold;
}

.notification.info {
  background: #3498db;
}

.notification.success {
  background: #2ecc71;
}

.notification.error {
  background: #e74c3c;
}
</style>
