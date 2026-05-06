<template>
  <div class="methodist-dashboard">
    <TopNavigationBar v-if="currentUser" :title="'Методист'" :user="currentUser" :tabs="tabs"
            :activeTab="activeTab" @tab-change="onTabChange" @logout="logout" />

    <!-- Контент вкладок -->
    <router-view />
  </div>
</template>

<script>
import TopNavigationBar from '../components/TopNavigationBar.vue'
import axios from '../axios'

export default {
  name: 'MethodistDashboard',
  components: { TopNavigationBar },
  data() {
    return {
      currentUser: null,
      activeTab: 'main',
      tabs: [
        { id: 'main', label: 'Главная', route: { name: 'MethodistMain' } },
        { id: 'stats', label: 'Статистика', route: { name: 'MethodistStats' } }
      ]
    }
  },
  async mounted() {
    const raw = localStorage.getItem('user')
    if (raw) this.currentUser = JSON.parse(raw)
    await this.loadUser()
    this.setActiveTabByRoute(this.$route.name)
  },
  watch: {
    '$route.name'(newName) {
      this.setActiveTabByRoute(newName)
    }
  },
  methods: {
    async loadUser() {
      try {
        const res = await axios.get('/api/auth/me/')
        this.currentUser = res.data
        localStorage.setItem('user', JSON.stringify(res.data))
      } catch (err) {
        console.warn('Не удалось загрузить пользователя', err)
      }
    },
    setActiveTabByRoute(routeName) {
      const tab = this.tabs.find(t => t.route.name === routeName)
      this.activeTab = tab ? tab.id : 'main'
    },
    onTabChange(tab) {
      this.activeTab = tab.id
      if (tab.route) this.$router.push(tab.route)
    },
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$router.push('/login')
    }
  }
}
</script>
<style scoped>
.methodist-dashboard {
    min-height: 100vh;
    padding: 20px;
}


</style>
