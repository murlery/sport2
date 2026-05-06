<template>
  <div class="coach-groups-page">

    <!-- Обёртка-карточка -->
    <div class="content-card">

      <!-- Заголовок -->
      <div class="page-header">
        <h2>Мои группы</h2>
        <span class="groups-count">Всего: {{ groups.length }}</span>
      </div>

      <!-- Сетка групп -->
      <div class="groups-grid">

        <div v-for="group in groups" :key="group.id" class="group-card">

          <!-- Заголовок карточки -->
          <div class="group-header">
            <h3 class="group-name">{{ group.name }}</h3>
            <span class="group-level" :class="levelClass(group.level)">
              {{ levelLabel(group.level) }}
            </span>
          </div>

          <!-- Информация -->
          <div class="group-info">
            <div class="info-row">
              <span class="info-label">Спортсменов</span>
              <span class="info-value">
                {{ group.athletes_count || 0 }}
              </span>
            </div>
          </div>

          <!-- Кнопка -->
          <button @click="viewGroup(group.id)" class="btn-primary">
            Перейти к группе →
          </button>

        </div>

        <div v-if="groups.length === 0 && !loadingGroups" class="empty-state">
          У вас пока нет групп
        </div>

        <div v-if="loadingGroups" class="loading-state">
          Загрузка групп...
        </div>

      </div>

    </div>

    <!-- Уведомление -->
    <div v-if="notification.show" :class="['notification', notification.type]">
      {{ notification.message }}
    </div>

  </div>
</template>

<script>
import axios from '../../axios'

export default {
  name: 'CoachGroups',
  data() {
    return {
      groups: [],
      loadingGroups: false,
      coachInfo: null,
      currentUser: null,
      notification: { show: false, message: '', type: 'info' }
    }
  },
  async mounted() {
    await this.loadCurrentUser()
    await this.loadCoachInfo()
    await this.loadGroups()
  },
  methods: {
    async loadCurrentUser() {
      try {
        const cached = localStorage.getItem('user')
        if (cached) this.currentUser = JSON.parse(cached)
        const res = await axios.get('/api/auth/me/')
        this.currentUser = res.data
        localStorage.setItem('user', JSON.stringify(res.data))
      } catch (err) {
        console.error('Ошибка загрузки пользователя:', err)
      }
    },
    async loadCoachInfo() {
      try {
        const userId = this.currentUser?.id
        if (userId) {
          const res = await axios.get(`/api/coaches/?user=${userId}`)
          if (res.data.length) this.coachInfo = res.data[0]
        }
      } catch (err) {
        console.error('Ошибка загрузки информации о тренере:', err)
      }
    },
    async loadGroups() {
      if (!this.coachInfo?.id) return
      this.loadingGroups = true
      try {
        const res = await axios.get(`/api/groups/?coach=${this.coachInfo.id}`)
        this.groups = res.data
        this.showNotification(`Загружено ${this.groups.length} групп`, 'success')
      } catch (err) {
        console.error('Ошибка загрузки групп:', err)
        this.showNotification('Ошибка загрузки групп', 'error')
      } finally {
        this.loadingGroups = false
      }
    },
    viewGroup(groupId) {
  this.$router.push({
    name: 'CoachAttendance',
    query: { group: groupId }
  })
},
    showNotification(message, type = 'info') {
      this.notification = { show: true, message, type }
      setTimeout(() => (this.notification.show = false), 3000)
    },
    levelLabel(level) {
      const levels = {
        beginner: 'НП',
        training: 'УТ',
        improvement: 'ССМ',
        high: 'ВСМ'
      }
      return levels[level] || 'Без уровня'
    },
    levelClass(level) {
      return `level-${level}`
    }
  }
}
</script>

<style scoped>
.coach-groups-page {
  padding: 30px;
  min-height: 100vh;
}

/* Главная белая карточка */
.content-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e4e7;
}

/* Заголовок */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
}

.groups-count {
  background: #dae3eb;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 20px;
  color: #2c3e50;
}

/* Сетка */
.groups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

/* Карточка группы */
.group-card {
  background: #eceeef;
  border-radius: 12px;
  padding: 20px;
  transition: 0.25s ease;
  border: 1px solid #e2e4e7;
}

.group-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
}

/* Заголовок карточки */
.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.group-name {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.group-level {
  background: linear-gradient(135deg, #3498db, #18b85b);
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

/* Информация */
.group-info {
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
}

.info-label {
  color: #4c5455;
  font-size: 14px;
}

.info-value {
  font-size: 16px;
  font-weight: 700;
  color: #2c3e50;
}

/* Кнопка */
.btn-primary {
  width: 100%;
  padding: 10px 16px;
  border-radius: 10px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  background: #3498db;
  color: white;
  transition: 0.25s ease;
}

.btn-primary:hover {
  background: #2980b9;
}

/* Empty / Loading */
.empty-state,
.loading-state {
  text-align: center;
  padding: 30px;
  color: #95a5a6;
  grid-column: 1 / -1;
}

/* Уведомления */
.notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 15px 25px;
  border-radius: 12px;
  color: white;
  font-weight: 500;
  z-index: 1000;
}

.notification.success {
  background: #2ecc71;
}

.notification.error {
  background: #e74c3c;
}

.notification.info {
  background: #3498db;
}
</style>