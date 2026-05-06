<template>
  <div class="schedule-page">
    <header class="page-header">
      <div class="left">
        <button class="back-btn" @click="goBack">← Назад</button>
        <p class="eyebrow">Расписание</p>
        <h1>Занятия и часы</h1>
        <div class="controls">
          <label class="field">
            <span>Группа</span>
            <select v-model="selectedGroup" @change="onGroupChange">
              <option value="">Все группы</option>
              <option v-for="g in groups" :key="g.id" :value="String(g.id)">
                {{ g.name }}
              </option>
            </select>
          </label>
          <label class="field">
            <span>Месяц</span>
            <select v-model="selectedMonth" @change="loadSchedule">
              <option v-for="m in months" :key="m.value" :value="m.value">{{ m.label }}</option>
            </select>
          </label>
          <label class="field">
            <span>Год</span>
            <select v-model="selectedYear" @change="loadSchedule">
              <option v-for="y in years" :key="y" :value="String(y)">{{ y }}</option>
            </select>
          </label>
          <button class="action ghost" :disabled="loadingSchedule" @click="loadSchedule">
            Обновить
          </button>
        </div>
        <div class="meta">
          <span>Группа: <strong>{{ currentGroupName }}</strong></span>
          <span>Тренер: <strong>{{ coachName }}</strong></span>
        </div>
      </div>
      <div class="stats-mini">
        <div class="stat">
          <p class="label">Записей</p>
          <p class="value">{{ schedule.length }}</p>
        </div>
        <div class="stat">
          <p class="label">Часы за период</p>
          <p class="value primary">{{ totalHours }}</p>
        </div>
      </div>
    </header>

    <section class="card">
      <div class="card-header">
        <div>
          <p class="eyebrow">Новая запись</p>
          <h2>Добавить тренировку</h2>
        </div>
      </div>

      <div class="form-grid">
        <label class="field">
          <span>Группа</span>
          <select v-model="form.group_id" @change="loadAthletes">
            <option value="">Выберите группу</option>
            <option v-for="g in groups" :key="g.id" :value="String(g.id)">{{ g.name }}</option>
          </select>
        </label>

        <label class="field">
          <span>Спортсмен</span>
          <select v-model="form.athlete_id">
            <option value="">Выберите спортсмена</option>
            <option v-for="ath in athletes" :key="ath.id" :value="String(ath.id)">
              {{ athleteName(ath) }}
            </option>
          </select>
        </label>

        <label class="field">
          <span>Тип тренировки</span>
          <select v-model="form.training_type_id">
            <option value="">Выберите тип</option>
            <option v-for="t in trainingTypes" :key="t.id" :value="String(t.id)">
              {{ t.name }}
            </option>
          </select>
        </label>

        <label class="field">
          <span>Месяц</span>
          <select v-model="form.month">
            <option v-for="m in months" :key="m.value" :value="m.value">{{ m.label }}</option>
          </select>
        </label>

        <label class="field">
          <span>Год</span>
          <select v-model="form.year">
            <option v-for="y in years" :key="y" :value="String(y)">{{ y }}</option>
          </select>
        </label>

        <label class="field">
          <span>Часы</span>
          <input type="number" min="0" step="0.5" v-model="form.hours" placeholder="Например, 2" />
        </label>
      </div>

      <div class="actions">
        <button class="action ghost" @click="resetForm">Очистить</button>
        <button class="action primary" :disabled="saving" @click="saveEntry">
          {{ saving ? 'Сохраняем...' : 'Добавить' }}
        </button>
      </div>
    </section>

    <section class="card">
      <div class="card-header">
        <div>
          <p class="eyebrow">Расписание</p>
          <h2>Тренировки</h2>
        </div>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Группа</th>
              <th>Спортсмен</th>
              <th>Тип</th>
              <th>Период</th>
              <th>Часы</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in schedule" :key="item.id">
              <td>{{ index + 1 }}</td>
              <td>{{ item.group?.name || item.group }}</td>
              <td>{{ item.athlete ? athleteName(item.athlete) : '-' }}</td>
              <td>{{ item.training_type?.name || item.training_type || '-' }}</td>
              <td>{{ formatPeriod(item.month, item.year) }}</td>
              <td><strong>{{ item.hours }}</strong></td>
            </tr>
            <tr v-if="!loadingSchedule && schedule.length === 0">
              <td colspan="6" class="empty">Нет тренировок за выбранный период</td>
            </tr>
            <tr v-if="loadingSchedule">
              <td colspan="6" class="empty">Загружаем расписание...</td>
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

const MONTHS = [
  { value: '1', label: 'Январь' },
  { value: '2', label: 'Февраль' },
  { value: '3', label: 'Март' },
  { value: '4', label: 'Апрель' },
  { value: '5', label: 'Май' },
  { value: '6', label: 'Июнь' },
  { value: '7', label: 'Июль' },
  { value: '8', label: 'Август' },
  { value: '9', label: 'Сентябрь' },
  { value: '10', label: 'Октябрь' },
  { value: '11', label: 'Ноябрь' },
  { value: '12', label: 'Декабрь' }
]

export default {
  name: 'CoachSchedule',

  data() {
    const today = new Date()
    return {
      currentUser: null,
      coachInfo: null,
      groups: [],
      trainingTypes: [],
      athletes: [],
      schedule: [],
      selectedGroup: '',
      selectedMonth: String(today.getMonth() + 1),
      selectedYear: String(today.getFullYear()),
      loadingGroups: false,
      loadingTypes: false,
      loadingAthletes: false,
      loadingSchedule: false,
      saving: false,
      form: {
        group_id: '',
        athlete_id: '',
        training_type_id: '',
        month: String(today.getMonth() + 1),
        year: String(today.getFullYear()),
        hours: ''
      },
      notification: {
        show: false,
        message: '',
        type: 'info'
      }
    }
  },

  computed: {
    months() {
      return MONTHS
    },
    years() {
      const current = new Date().getFullYear()
      return [current - 1, current, current + 1]
    },
    totalHours() {
      return this.schedule.reduce((sum, item) => sum + (Number(item.hours) || 0), 0)
    },
    currentGroupName() {
      if (!this.selectedGroup) return 'Все'
      return this.groups.find(g => String(g.id) === String(this.selectedGroup))?.name || 'Группа'
    },
    coachName() {
      const coach = this.coachInfo
      if (!coach?.user) return '—'
      return `${coach.user.last_name || ''} ${coach.user.first_name || ''}`.trim()
    }
  },

  watch: {
    '$route.query.group'(val) {
      if (val && String(val) !== this.selectedGroup) {
        this.selectedGroup = String(val)
        this.form.group_id = String(val)
        this.loadAthletes()
        this.loadSchedule()
      }
    },
    selectedMonth(val) {
      this.form.month = String(val)
    },
    selectedYear(val) {
      this.form.year = String(val)
    }
  },

  async mounted() {
    await this.loadCurrentUser()
    await this.loadCoachInfo()
    await Promise.all([this.loadGroups(), this.loadTrainingTypes()])
    this.applyInitialGroup()
  },

  methods: {
    async loadCurrentUser() {
      const raw = localStorage.getItem('user')
      if (raw) this.currentUser = JSON.parse(raw)
    },

    async loadCoachInfo() {
      try {
        const userId = this.currentUser?.id
        if (!userId) return
        const res = await axios.get(`/api/coaches/?user=${userId}`)
        if (res.data.length) this.coachInfo = res.data[0]
      } catch (error) {
        console.error('Ошибка загрузки тренера', error)
      }
    },

    async loadGroups() {
      this.loadingGroups = true
      try {
        const params = {}
        if (this.coachInfo?.id) params.coach = this.coachInfo.id
        const res = await axios.get('/api/groups/', { params })
        this.groups = res.data
      } catch (error) {
        console.error('Ошибка загрузки групп', error)
        this.showNotification('Не удалось загрузить группы', 'error')
      } finally {
        this.loadingGroups = false
      }
    },

    async loadTrainingTypes() {
      this.loadingTypes = true
      try {
        const res = await axios.get('/api/training-types/')
        this.trainingTypes = res.data
      } catch (error) {
        console.error('Ошибка загрузки типов', error)
        this.showNotification('Не удалось загрузить типы тренировок', 'error')
      } finally {
        this.loadingTypes = false
      }
    },

    applyInitialGroup() {
      const queryGroup = this.$route.query.group
      if (queryGroup) {
        this.selectedGroup = String(queryGroup)
        this.form.group_id = String(queryGroup)
        this.loadAthletes()
      }
      this.loadSchedule()
    },

    async loadAthletes() {
      if (!this.form.group_id) {
        this.athletes = []
        return
      }
      this.loadingAthletes = true
      try {
        const res = await axios.get('/api/athletes/', { params: { group: this.form.group_id } })
        this.athletes = res.data
      } catch (error) {
        console.error('Ошибка загрузки спортсменов', error)
        this.showNotification('Не удалось загрузить спортсменов', 'error')
      } finally {
        this.loadingAthletes = false
      }
    },

    async loadSchedule() {
      this.loadingSchedule = true
      try {
        const params = {
          group: this.selectedGroup || undefined,
          coach: this.coachInfo?.id || undefined,
          month: this.selectedMonth ? Number(this.selectedMonth) : undefined,
          year: this.selectedYear ? Number(this.selectedYear) : undefined
        }
        const res = await axios.get('/api/training-hours/', { params })
        this.schedule = res.data
      } catch (error) {
        console.error('Ошибка загрузки расписания', error)
        this.showNotification('Не удалось загрузить расписание', 'error')
      } finally {
        this.loadingSchedule = false
      }
    },

    async saveEntry() {
      if (
        !this.form.group_id ||
        !this.form.athlete_id ||
        !this.form.training_type_id ||
        !this.form.month ||
        !this.form.year ||
        !this.form.hours
      ) {
        this.showNotification('Заполните все обязательные поля', 'error')
        return
      }
      this.saving = true
      try {
        const payload = {
          group_id: this.form.group_id,
          athlete_id: this.form.athlete_id,
          training_type_id: this.form.training_type_id,
          month: Number(this.form.month),
          year: Number(this.form.year),
          hours: Number(this.form.hours)
        }
        await axios.post('/api/training-hours/', payload)
        this.showNotification('Запись добавлена', 'success')
        await this.loadSchedule()
        this.resetForm()
      } catch (error) {
        console.error('Ошибка сохранения записи', error)
        this.showNotification('Не удалось сохранить запись', 'error')
      } finally {
        this.saving = false
      }
    },

    resetForm() {
      this.form = {
        group_id: this.selectedGroup || this.form.group_id,
        athlete_id: '',
        training_type_id: '',
        month: this.selectedMonth,
        year: this.selectedYear,
        hours: ''
      }
    },

    onGroupChange() {
      this.$router.replace({
        name: 'CoachSchedule',
        query: this.selectedGroup ? { group: this.selectedGroup } : {}
      })
      this.form.group_id = this.selectedGroup
      this.loadAthletes()
      this.loadSchedule()
    },

    athleteName(athlete) {
      if (!athlete) return ''
      const obj = athlete.user || athlete
      return `${obj.last_name || ''} ${obj.first_name || ''} ${obj.middle_name || ''}`.trim()
    },

    formatPeriod(month, year) {
      if (!month || !year) return '-'
      const found = MONTHS.find(m => Number(m.value) === Number(month))
      const monthLabel = found ? found.label : month
      return `${monthLabel} ${year}`
    },

    goBack() {
      this.$router.push({ name: 'CoachDashboard' })
    },

    showNotification(message, type = 'info') {
      this.notification = { show: true, message, type }
      setTimeout(() => (this.notification.show = false), 3000)
    }
  }
}
</script>

<style scoped>
.schedule-page {
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
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  gap: 16px;
}

.left {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: flex-end;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: #4b5563;
  font-weight: 700;
}

.field select,
.field input {
  min-width: 180px;
  padding: 10px;
  border: 1px solid #d1d9e0;
  border-radius: 8px;
  font-size: 14px;
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

.meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  color: #4b5563;
}

.stats-mini {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
  min-width: 200px;
}

.stat {
  background: #f8fafc;
  border: 1px solid #e3e8ef;
  border-radius: 10px;
  padding: 12px;
}

.stat .label {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
}

.stat .value {
  margin: 6px 0 0;
  font-size: 20px;
  font-weight: 800;
  color: #1f2937;
}

.stat .value.primary {
  color: #3498db;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-header h2 {
  margin: 4px 0 0;
  color: #2c3e50;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-top: 12px;
}

.actions {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.action {
  padding: 10px 16px;
  border-radius: 8px;
  border: 1px solid #d0d7e1;
  background: #f8fafc;
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
  background: white;
}

.action:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
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

  .stats-mini {
    width: 100%;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  }
}
</style>
