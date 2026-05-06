<template>
  <div class="attendance-page">
    <div class="content-card">

      <!-- Шапка -->
      <div class="page-header">
        <div class="left">
          <h2>Посещаемость тренировок</h2>
        </div>
      </div>

      <!-- Фильтры -->
      <div class="filters">
        <label>
          <span>Группа</span>
          <select v-model="selectedGroupId">
            <option value="">Выберите группу</option>
            <option v-for="g in groups" :key="g.id" :value="g.id">
              {{ g.name }}
            </option>
          </select>
        </label>

        <label>
          <span>Месяц</span>
          <select v-model="selectedMonth">
            <option v-for="m in months" :key="m.value" :value="m.value">
              {{ m.label }}
            </option>
          </select>
        </label>

        <label>
          <span>Год</span>
          <select v-model="selectedYear">
            <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
          </select>
        </label>
      </div>

      <!-- Информация -->
      <div v-if="selectedGroup" class="group-info">
        <div class="group-meta">
          <span>{{ filteredAthletes.length }} спортсменов</span>
          <span>{{ trainingDays.length }} тренировочных дней</span>
        </div>
      </div>

      <!-- LOADING -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Загрузка данных...</p>
      </div>

      <!-- EMPTY STATES -->
      <div v-else-if="!selectedGroupId" class="no-group-message">
        Выберите группу
      </div>

      <div v-else-if="trainingDays.length === 0" class="no-training-message">
        На этот месяц нет тренировок
        <button class="create-plan-btn" @click="goToPlanCreation">
          Создать план тренировок
        </button>
      </div>

      <div v-else-if="filteredAthletes.length === 0" class="no-athletes-message">
        В этой группе нет спортсменов
      </div>

      <!-- ================= DESKTOP ================= -->
      <div v-else-if="!isMobile" class="table-container">
        <table class="attendance-table">
          <thead>
            <tr>
              <th class="sticky-col">№</th>
              <th class="sticky-col name-col">Спортсмен</th>
              <th class="sticky-col rate-col">%</th>

              <th v-for="day in trainingDays" :key="day.id" class="date-col" :class="getDayClass(day.date)">
                <div class="date-header">
                  <span class="day-number">{{ formatDay(day.date) }}</span>
                  <span class="weekday">{{ formatShortWeekday(day.date) }}</span>
                </div>
              </th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="(athlete, index) in filteredAthletes" :key="athlete.id">
              <td class="sticky-col">{{ index + 1 }}</td>

              <td class="sticky-col name-col">
                <strong>{{ athlete.last_name }} {{ athlete.first_name }}</strong>
              </td>

              <td class="sticky-col rate-col">
                <div class="attendance-rate">
                  <div class="rate-bar">
                    <div class="rate-fill" :style="{ width: calculateAthleteRate(athlete.id) + '%' }"
                      :class="{ high: calculateAthleteRate(athlete.id) > 70 }">
                    </div>
                  </div>
                  <span class="rate-text">
                    {{ calculateAthleteRate(athlete.id) }}%
                  </span>
                </div>
              </td>

              <td v-for="day in trainingDays" :key="day.id" class="attendance-cell"
                :class="getAttendanceCellClass(athlete.id, day.id)" @click="toggleAttendance(athlete.id, day.id)">

                <div class="cell-content">
                  <span v-if="getAttendance(athlete.id, day.id)?.status === 'present'">✅</span>
                  <span v-else-if="getAttendance(athlete.id, day.id)?.status === 'absent'">❌</span>
                  <span v-else>○</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- ================= MOBILE ================= -->
      <div v-else class="mobile-attendance">

        <!-- Выбор дня -->
        <div class="day-selector">
          <button v-for="day in trainingDays" :key="day.id" :class="[
            { active: selectedDayId === day.id },
            { today: isToday(day.date) }
          ]" @click="selectedDayId = day.id">
            {{ formatDay(day.date) }}
          </button>
        </div>

        <!-- Список спортсменов -->
        <div class="athlete-list">
          <div v-for="athlete in filteredAthletes" :key="athlete.id" class="athlete-card">

            <div class="athlete-top">
              <strong>{{ athlete.last_name }} {{ athlete.first_name }}</strong>
              <span class="mobile-rate">
                {{ calculateAthleteRate(athlete.id) }}%
              </span>
            </div>

            <div class="mobile-actions">
              <button class="present-btn" :class="{ active: getMobileStatus(athlete.id) === 'present' }"
                @click="setMobileAttendance(athlete.id, 'present')">
                ✅
              </button>

              <button class="absent-btn" :class="{ active: getMobileStatus(athlete.id) === 'absent' }"
                @click="setMobileAttendance(athlete.id, 'absent')">
                ❌
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- SAVE PANEL -->
      <div v-if="hasChanges" class="save-panel" :class="{ mobile: isMobile }">

        <span class="changes-count">
          Есть несохраненные изменения
        </span>

        <button class="save-btn" @click="saveAllAttendance" :disabled="saving">
          {{ saving ? 'Сохранение...' : 'Сохранить изменения' }}
        </button>
      </div>

      <!-- Notification -->
      <div v-if="notification.show" :class="['notification', notification.type]">
        {{ notification.message }}
      </div>

    </div>
  </div>
</template>
<script>
import axios from '../../axios'

export default {
  name: 'AttendanceTable',

  data() {
    const today = new Date()

    return {
      groups: [],
      selectedGroupId: '',
      selectedMonth: today.getMonth() + 1,
      selectedYear: today.getFullYear(),

      allAthletes: [],
      trainingPlans: [],
      attendanceMap: new Map(),
      localChanges: new Map(),

      loading: false,
      saving: false,
      isMobile: window.innerWidth <= 1000,
      selectedDayId: null,

      notification: { show: false, message: '', type: 'info' },

      months: [
        { value: 1, label: 'Январь' }, { value: 2, label: 'Февраль' },
        { value: 3, label: 'Март' }, { value: 4, label: 'Апрель' },
        { value: 5, label: 'Май' }, { value: 6, label: 'Июнь' },
        { value: 7, label: 'Июль' }, { value: 8, label: 'Август' },
        { value: 9, label: 'Сентябрь' }, { value: 10, label: 'Октябрь' },
        { value: 11, label: 'Ноябрь' }, { value: 12, label: 'Декабрь' }
      ]
    }
  },

  computed: {
    years() {
      const y = new Date().getFullYear()
      return [y - 1, y, y + 1]
    },

    selectedGroup() {
      return this.groups.find(g => g.id === this.selectedGroupId)
    },

    filteredAthletes() {
      return this.allAthletes.filter(a =>
        (a.group?.id || a.group_id) === this.selectedGroupId
      )
    },

    trainingDays() {
      return this.trainingPlans.map(p => ({
        id: p.id,
        date: p.date
      }))
    },

    hasChanges() {
      return this.localChanges.size > 0
    }
  },

  watch: {
    selectedGroupId() { this.loadData() },
    selectedMonth() { this.loadData() },
    selectedYear() { this.loadData() }
  },

  mounted() {
    this.loadGroups()
  this.handleResize()

  const groupFromQuery = this.$route.query.group
  if (groupFromQuery) {
    this.selectedGroupId = Number(groupFromQuery)
  }

  window.addEventListener('resize', this.handleResize)
  },

  methods: {
    isToday(date) {
      const d = new Date(date)
      const today = new Date()

      return (
        d.getDate() === today.getDate() &&
        d.getMonth() === today.getMonth() &&
        d.getFullYear() === today.getFullYear()
      )
    },
    setTodayAsSelected() {
      if (!this.trainingDays.length) {
        this.selectedDayId = null
        return
      }

      const today = new Date()
      const todayStr = today.toISOString().split('T')[0]

      const todayPlan = this.trainingDays.find(d =>
        d.date.startsWith(todayStr)
      )

      if (todayPlan) {
        this.selectedDayId = todayPlan.id
      } else {
        this.selectedDayId = this.trainingDays[0].id
      }
    },

    /* ================= LOAD ================= */

    async loadGroups() {
      const res = await axios.get('/api/groups/')
      this.groups = res.data
    },

    async loadData() {
      if (!this.selectedGroupId) return

      this.loading = true
      this.localChanges.clear()
      this.attendanceMap.clear()

      try {
        // спортсмены
        const athletesRes = await axios.get('/api/athletes/')
        this.allAthletes = athletesRes.data

        // планы
        const plansRes = await axios.get('/api/training-plans/', {
          params: {
            group_id: this.selectedGroupId,
            month: this.selectedMonth,
            year: this.selectedYear
          }
        })

        this.trainingPlans = plansRes.data
        this.$nextTick(() => {
          this.setTodayAsSelected()
        })

        // ЗАГРУЗКА ПОСЕЩАЕМОСТИ
        for (const plan of this.trainingPlans) {
          const attendanceRes = await axios.get('/api/attendance/', {
            params: { training_plan: plan.id }
          })

          attendanceRes.data.forEach(record => {
            const key = `${record.athlete.id}_${plan.id}`

            this.attendanceMap.set(key, {
              id: record.id,
              status: record.status,
              reason: record.absence_reason,
              athlete_id: record.athlete.id,
              training_plan_id: plan.id
            })
          })
        }

      } catch (e) {
        this.showNotification('Ошибка загрузки данных', 'error')
      } finally {
        this.loading = false
      }
    },
    goToPlanCreation() {
  if (!this.selectedGroupId) return

  this.$router.push({
    name: 'training-plan-generate',
    query: {
      tab: 'form',
      group: this.selectedGroupId
    }
  })
},

    /* ================= UTILS ================= */

    getKey(a, p) { return `${a}_${p}` },

    getAttendance(a, p) {
      const key = this.getKey(a, p)
      return this.localChanges.get(key) || this.attendanceMap.get(key)
    },

    /* ================= TOGGLE ================= */

    toggleAttendance(a, p) {
      const key = this.getKey(a, p)
      const current = this.getAttendance(a, p)

      let newStatus = null

      if (!current) newStatus = 'present'
      else if (current.status === 'present') newStatus = 'absent'
      else if (current.status === 'absent') newStatus = null

      if (newStatus === null) {
        this.localChanges.delete(key)
      } else {
        this.localChanges.set(key, {
          ...(current || {}),
          status: newStatus,
          athlete_id: a,
          training_plan_id: p,
          isNew: !current?.id
        })
      }
    },

    setMobileAttendance(a, status) {
      if (!this.selectedDayId) return

      const key = this.getKey(a, this.selectedDayId)
      const current = this.getAttendance(a, this.selectedDayId)

      this.localChanges.set(key, {
        ...(current || {}),
        status,
        athlete_id: a,
        training_plan_id: this.selectedDayId,
        isNew: !current?.id
      })
    },

    getMobileStatus(a) {
      if (!this.selectedDayId) return null
      return this.getAttendance(a, this.selectedDayId)?.status
    },

    /* ================= SAVE ================= */

    async saveAllAttendance() {
      if (!this.hasChanges) return

      this.saving = true
      let success = 0
      let errors = 0

      try {
        for (const [key, attendance] of this.localChanges) {
          const [athleteId, planId] = key.split('_').map(Number)
          const existing = this.attendanceMap.get(key)

          const data = {
            athlete_id: athleteId,
            training_plan_id: planId,
            status: attendance.status,
            absence_reason: attendance.reason || ''
          }

          try {
            if (existing?.id) {
              await axios.put(`/api/attendance/${existing.id}/`, data)
            } else if (attendance.status) {
              const res = await axios.post('/api/attendance/', data)
              attendance.id = res.data.id
            }

            success++
          } catch (e) {
            errors++
          }
        }

        if (errors === 0) {
          this.showNotification('Изменения сохранены', 'success')
          await this.loadData()
          this.localChanges.clear()
        } else {
          this.showNotification(`Сохранено: ${success}, ошибок: ${errors}`, 'error')
        }

      } finally {
        this.saving = false
      }
    },

    /* ================= RATE ================= */

    calculateAthleteRate(id) {
      let total = 0
      let present = 0

      this.trainingPlans.forEach(plan => {
        const attendance = this.getAttendance(id, plan.id)
        if (attendance) {
          total++
          if (attendance.status === 'present') present++
        }
      })

      return total ? Math.round((present / total) * 100) : 0
    },

    /* ================= UI ================= */

    getAttendanceCellClass(a, p) {
      const key = this.getKey(a, p)
      const attendance = this.getAttendance(a, p)
      const changed = this.localChanges.has(key)

      return {
        present: attendance?.status === 'present',
        absent: attendance?.status === 'absent',
        changed
      }
    },

    formatDay(date) {
      const d = new Date(date)
      const day = String(d.getDate()).padStart(2, '0')
      const month = String(d.getMonth() + 1).padStart(2, '0')
      return `${day}.${month}`
    },

    formatShortWeekday(date) {
      return ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'][new Date(date).getDay()]
    },

    getDayClass(date) {
      const d = new Date(date)
      const today = new Date()

      const isToday =
        d.getDate() === today.getDate() &&
        d.getMonth() === today.getMonth() &&
        d.getFullYear() === today.getFullYear()

      const isWeekend = d.getDay() === 0 || d.getDay() === 6

      return {
        weekend: isWeekend,
        today: isToday
      }
    },

    showNotification(message, type = 'info') {
      this.notification = { show: true, message, type }
      setTimeout(() => this.notification.show = false, 3000)
    },
    handleResize() {
      this.isMobile = window.innerWidth <= 768
    },
  }
}
</script>
<style scoped>
.date-col.today {
  background: #dee3f3;
  border-bottom: 2px solid #a2b4ed;
}

.day-selector button.today {
  border-color: #4CAF50;
}

.attendance-cell.present {
  background: #e8f5e9;
}

.attendance-cell.absent {
  background: #ffebee;
}

.attendance-page {
  padding: 24px;
}

.content-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

/* ================= HEADER ================= */

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 22px;
  font-weight: 600;
  margin: 0;
}

/* ================= FILTERS ================= */

.filters {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.filters label {
  display: flex;
  flex-direction: column;
  font-size: 14px;
  gap: 6px;
}

.filters select {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #ddd;
  font-size: 14px;
  min-width: 140px;
}

/* ================= INFO ================= */

.group-info {
  margin-bottom: 16px;
}

.group-meta {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #666;
}

/* ================= LOADING ================= */

.loading-state {
  text-align: center;
  padding: 40px 0;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 4px solid #e5e5e5;
  border-top: 4px solid #4CAF50;
  border-radius: 50%;
  margin: 0 auto 12px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ================= TABLE ================= */

.table-container {
  overflow-x: auto;

}

.attendance-table {
  border-collapse: collapse;
  width: 100%;
  min-width: 900px;
  font-size: 14px;
}

.attendance-table th,
.attendance-table td {
  border: 1px solid #eee;
  text-align: center;
  padding: 8px;
}

.attendance-table th {
  background: #f9fafb;
  font-weight: 600;
}

.sticky-col {
  position: sticky;
  left: 0;
  background: #fff;
  z-index: 2;
}

.name-col {
  left: 40px;
  min-width: 180px;
  text-align: left;
  background: #fafafa;
}

.rate-col {
  left: 220px;
  min-width: 120px;
  background: #fafafa;
}

.date-col {
  min-width: 60px;

}

.weekend {
  background: #fafafa;
}

.date-header {
  display: flex;
  flex-direction: column;
  font-size: 12px;
}

.day-number {
  font-weight: 600;
}

.weekday {
  color: #888;
}

/* ================= CELLS ================= */

.attendance-cell {
  cursor: pointer;
  transition: 0.2s;
}

.attendance-cell:hover {
  background: #f1fdf4;
}

.cell-content {
  font-size: 16px;
}

/* ================= RATE BAR ================= */

.attendance-rate {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #eee;
}

.rate-bar {
  width: 60px;
  height: 6px;
  background: #eee;
  border-radius: 6px;
  overflow: hidden;
}

.rate-fill {
  height: 100%;
  background: #f44336;
  transition: width 0.3s;
}

.rate-fill.high {
  background: #4CAF50;
}

.rate-text {
  font-size: 12px;
}

/* ================= MOBILE ================= */

.mobile-attendance {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.day-selector {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.day-selector button {
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid #ddd;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
  white-space: nowrap;
}

.day-selector button.active {
  background: #4CAF50;
  color: white;
  border-color: #4CAF50;
}

.athlete-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.athlete-card {
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 12px;
  background: #e5e5e6;
}

.athlete-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.mobile-rate {
  font-size: 13px;
  color: #555;
}

.mobile-actions {
  display: flex;
  gap: 10px;
}

.mobile-actions button {
  flex: 1;
  padding: 8px;
  border-radius: 8px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  font-size: 14px;
}

.present-btn.active {
  background: #4CAF50;
  color: white;
  border-color: #4CAF50;
}

.absent-btn.active {
  background: #f44336;
  color: white;
  border-color: #f44336;
}

/* ================= SAVE PANEL ================= */

.save-panel {
  position: sticky;
  bottom: 0;
  margin-top: 20px;
  padding: 14px;
  background: #fff;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.save-panel.mobile {
  flex-direction: column;
  gap: 10px;
}

.save-btn {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ================= EMPTY STATES ================= */

.no-group-message,
.no-training-message,
.no-athletes-message {
  text-align: center;
  padding: 30px 0;
  color: #666;
}

.create-plan-btn {
  margin-top: 10px;
  padding: 8px 14px;
  border-radius: 8px;
  border: none;
  background: #4CAF50;
  color: white;
  cursor: pointer;
}

/* ================= NOTIFICATION ================= */

.notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 12px 18px;
  border-radius: 10px;
  color: white;
  font-size: 14px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.notification.success {
  background: #4CAF50;
}

.notification.error {
  background: #f44336;
}

.notification.info {
  background: #2196F3;
}

/* ================= RESPONSIVE ================= */

@media (max-width: 768px) {

  .attendance-page {
    padding: 12px;
  }

  .content-card {
    padding: 16px;
  }

  .filters {
    flex-direction: column;
  }

}
</style>