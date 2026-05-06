<template>
  <div class="group-details">
    <header class="page-header">
      <div class="title-block">
        <button class="back-btn" @click="goBack">← Назад</button>
        <p class="eyebrow">Детали группы</p>

        <div class="title-row">
          <h1>{{ group?.name || 'Группа' }}</h1>
          <span class="level-badge" :class="`level-${group?.level || 'unknown'}`">
            {{ levelLabel(group?.level) }}
          </span>
        </div>

        <div class="meta">
          <span class="meta-item">
            Отделение: <strong>{{ departmentName }}</strong>
          </span>
          <span class="meta-item">
            Тренер: <strong>{{ coachName }}</strong>
          </span>
        </div>
      </div>

      <div class="header-actions">
        <!-- <button class="action primary" @click="openAttendance">
          Посещаемость
        </button>
        <button class="action" @click="openAddAthlete">
          Добавить спортсмена
        </button> -->
      </div>
    </header>

    <section class="stats-grid">
      <div class="stat-card">
        <p class="label">Спортсмены</p>
        <p class="value">{{ athletesCount }}</p>
      </div>

      <div class="stat-card">
        <p class="label">Средняя посещаемость</p>
        <p class="value">{{ averageAttendance }}%</p>
      </div>

      <div class="stat-card">
        <p class="label">Уровень</p>
        <p class="value">{{ levelLabel(group?.level) }}</p>
      </div>
    </section>

    <section class="card">
      <div class="card-header">
        <div>
          <p class="eyebrow">Состав группы</p>
          <h2>Список спортсменов</h2>
        </div>

        <button class="action ghost" @click="reloadGroup" :disabled="loadingGroup || loadingAthletes">
          Обновить
        </button>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>#</th>
              <th>ФИО</th>
              <th>Дата рождения</th>
              <th>Возраст</th>
              <th>Разряд</th>
              <th>Посещаемость</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="(athlete, index) in athletes" :key="athlete.id">
              <td>{{ index + 1 }}</td>

              <td class="name">
                <strong>
                  {{ athlete.last_name }}
                  {{ athlete.first_name }}
                  {{ athlete.middle_name }}
                </strong>
              </td>

              <td>{{ formatDate(athlete.birth_date) }}</td>
              <td>{{ calculateAge(athlete.birth_date) }}</td>

              <td>
                <span class="badge" :class="getRankClass(athlete.sport_rank)">
                  {{ athlete.sport_rank || 'Без разряда' }}
                </span>
              </td>

              <td>
                <span class="attendance" :class="getAttendanceClass(athlete.attendance_rate)">
                  {{ athlete.attendance_rate || 0 }}%
                </span>
              </td>
            </tr>

            <tr v-if="!loadingAthletes && athletes.length === 0">
              <td colspan="6" class="empty">
                Спортсмены не найдены
              </td>
            </tr>

            <tr v-if="loadingAthletes">
              <td colspan="6" class="empty">
                Загрузка спортсменов...
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <div v-if="notification.show" :class="['notification', notification.type]">
      {{ notification.message }}
    </div>
  </div>
</template>

<script>
import axios from '../../axios'

export default {
  name: 'GroupDetails',

  data() {
    return {
      group: null,
      allAthletes: [],
      loadingGroup: false,
      loadingAthletes: false,
      notification: {
        show: false,
        message: '',
        type: 'info'
      }
    }
  },

  computed: {
    groupId() {
      return Number(this.$route.params.id)
    },

    athletes() {
      return this.allAthletes.filter(
        a => Number(a.group?.id) === this.groupId
      )
    },

    athletesCount() {
      return this.athletes.length
    },

    averageAttendance() {
      if (!this.athletes.length) return 0
      const total = this.athletes.reduce(
        (sum, a) => sum + (Number(a.attendance_rate) || 0),
        0
      )
      return Math.round(total / this.athletes.length)
    },

    departmentName() {
      const dep = this.group?.department
      return dep?.name || 'Не указано'
    },

    coachName() {
      const user = this.group?.coach?.user
      if (!user) return 'Не назначен'
      return `${user.last_name} ${user.first_name} ${user.middle_name || ''}`.trim()
    }
  },

  watch: {
    '$route.params.id': {
      immediate: true,
      handler() {
        this.reloadGroup()
      }
    }
  },

  methods: {
    async reloadGroup() {
      this.group = null
      this.athletes = []
      await this.loadGroup()
    },

    async loadGroup() {
      if (!this.groupId) return

      this.loadingGroup = true
      try {
        const res = await axios.get(`/api/groups/${this.groupId}/`)
        this.group = res.data

        // 🔥 КЛЮЧЕВОЙ МОМЕНТ
        await this.loadAthletes()
      } catch {
        this.showNotification('Не удалось загрузить данные группы', 'error')
      } finally {
        this.loadingGroup = false
      }
    },

    async loadAthletes() {
      if (!this.groupId) return

      this.loadingAthletes = true
      this.allAthletes = []

      try {
        const res = await axios.get('/api/athletes/', {
          params: { group: this.groupId }
        })
        this.allAthletes = res.data
      } catch {
        this.showNotification('Не удалось загрузить спортсменов', 'error')
      } finally {
        this.loadingAthletes = false
      }
    }
    ,

    openAttendance() {
      this.$router.push({
        name: 'CoachGroupAttendance',
        params: { id: this.groupId }
      })
    },

    openAddAthlete() {
      this.$router.push({
        name: 'CoachAddAthlete',
        query: { group: this.groupId }
      })
    },

    goBack() {
      this.$router.push({ name: 'CoachDashboard' })
    },

    showNotification(message, type = 'info') {
      this.notification = { show: true, message, type }
      setTimeout(() => (this.notification.show = false), 3000)
    },

    levelLabel(level) {
      const map = {
        beginner: 'Начальный',
        training: 'Учебный',
        improvement: 'Повышение мастерства',
        high: 'Высокий'
      }
      return map[level] || 'Не указано'
    },

    formatDate(date) {
      return date ? new Date(date).toLocaleDateString('ru-RU') : '-'
    },

    calculateAge(date) {
      if (!date) return '-'
      const now = new Date()
      const birth = new Date(date)
      let age = now.getFullYear() - birth.getFullYear()
      if (
        now.getMonth() < birth.getMonth() ||
        (now.getMonth() === birth.getMonth() &&
          now.getDate() < birth.getDate())
      ) {
        age--
      }
      return age
    },

    getRankClass(rank) {
      const map = {
        MSMK: 'rank-msmk',
        MS: 'rank-ms',
        KMS: 'rank-kms'
      }
      return map[rank] || 'rank-default'
    },

    getAttendanceClass(rate) {
      if (rate >= 90) return 'attendance-good'
      if (rate >= 70) return 'attendance-medium'
      return 'attendance-poor'
    }
  }
}
</script>


<style scoped>
.group-details {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  gap: 16px;
}

.title-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.back-btn {
  align-self: flex-start;
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid #dce3eb;
  background: #f8fafc;
  color: #2c3e50;
  cursor: pointer;
}

.eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #7f8c8d;
  font-size: 12px;
  font-weight: 700;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-row h1 {
  margin: 0;
  color: #2c3e50;
}

.level-badge {
  padding: 6px 12px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 13px;
  background: #eef2f7;
  color: #2c3e50;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  color: #4b5563;
}

.meta-item strong {
  color: #2c3e50;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.action {
  padding: 10px 16px;
  border: 1px solid #d0d7e1;
  border-radius: 8px;
  background: white;
  color: #2c3e50;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.action.primary {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  border: none;
}

.action.ghost {
  background: #f8fafc;
}

.action:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.stat-card {
  padding: 16px;
  background: #ffffff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.stat-card .label {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
}

.stat-card .value {
  margin: 6px 0 0;
  color: #1f2937;
  font-size: 22px;
  font-weight: 700;
}

.card {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.card-header h2 {
  margin: 4px 0 0;
  color: #2c3e50;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 12px;
  background: #f8fafc;
  color: #4b5563;
  font-weight: 700;
  border-bottom: 1px solid #e5e7eb;
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid #f0f2f5;
  color: #1f2937;
}

.data-table tr:hover td {
  background: #f9fafb;
}

.name {
  font-weight: 700;
  color: #2c3e50;
}

.badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.rank-msmk {
  background: #ff6b6b;
  color: #fff;
}

.rank-ms {
  background: #ff9f43;
  color: #fff;
}

.rank-kms {
  background: #feca57;
  color: #333;
}

.rank-1 {
  background: #48dbfb;
  color: #fff;
}

.rank-2 {
  background: #1dd1a1;
  color: #fff;
}

.rank-3 {
  background: #10ac84;
  color: #fff;
}

.rank-junior1 {
  background: #5f27cd;
  color: #fff;
}

.rank-junior2 {
  background: #341f97;
  color: #fff;
}

.rank-junior3 {
  background: #0abde3;
  color: #fff;
}

.rank-default {
  background: #e5e7eb;
  color: #374151;
}

.attendance {
  font-weight: 700;
}

.attendance-good {
  color: #2ecc71;
}

.attendance-medium {
  color: #f39c12;
}

.attendance-poor {
  color: #e74c3c;
}

.empty {
  text-align: center;
  color: #6b7280;
  padding: 20px !important;
}

.notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 14px 18px;
  border-radius: 10px;
  color: white;
  font-weight: 700;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  animation: slideIn 0.3s ease;
}

.notification.info {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
}

.notification.success {
  background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
}

.notification.error {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }

  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }
}
</style>
