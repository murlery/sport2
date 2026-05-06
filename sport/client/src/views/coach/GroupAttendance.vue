<template>
  <div class="attendance-page">
    <!-- Шапка -->
    <div class="content-card">
      <div class="page-header">
        <div class="left">
          <button class="back-btn" @click="goBack">← Назад</button>
          <h2>Отметка посещаемости</h2>
        </div>
      </div>

      <!-- Информация о группе -->
      <div class="group-info-card">
        <div class="group-info-header">
          <div>
            <h3>{{ group?.name || 'Загрузка...' }}</h3>
            <span class="level-badge" :class="`level-${group?.level}`">
              {{ levelLabel(group?.level) }}
            </span>
          </div>
          <div class="coach-info">
            <span class="label">Тренер:</span>
            <span class="value">{{ coachName }}</span>
          </div>
        </div>

        <!-- Выбор даты и тренировки -->
        <div class="date-selector">
          <div class="selector-group">
            <label>Выберите дату</label>
            <div class="date-input-wrapper">
              <input 
                type="date" 
                v-model="selectedDate" 
                @change="loadTrainingPlan"
                class="date-input"
              />
            </div>
          </div>

          <!-- Информация о тренировке -->
          <div v-if="selectedTrainingPlan" class="training-info">
            <div class="info-badge">
              <span class="badge-icon">🏋️</span>
              <div class="badge-content">
                <span class="badge-title">Тренировка за {{ formatDate(selectedDate) }}</span>
                <span class="badge-subtitle">{{ formatWeekday(selectedDate) }}, {{ selectedTrainingPlan.total_hours }} часов</span>
              </div>
            </div>
            <div class="training-types">
              <span 
                v-for="th in selectedTrainingPlan.training_hours" 
                :key="th.training_type.id"
                class="type-pill"
                :class="getTypeClass(th.training_type.id)"
              >
                {{ th.training_type.name }}: {{ th.hours }} ч
              </span>
            </div>
          </div>

          <div v-else-if="selectedDate && !loadingTrainingPlan && !selectedTrainingPlan" class="no-training-warning">
            <span class="warning-icon">⚠️</span>
            <span>На эту дату нет тренировки. Сначала создайте план тренировок.</span>
            <button class="create-plan-btn" @click="goToPlanCreation">Создать план</button>
          </div>
        </div>
      </div>

      <!-- Статистика -->
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-label">Всего спортсменов</span>
          <span class="stat-value">{{ athletes.length }}</span>
        </div>
        <div class="stat-card success">
          <span class="stat-label">Присутствуют</span>
          <span class="stat-value">{{ presentCount }}</span>
        </div>
        <div class="stat-card error">
          <span class="stat-label">Отсутствуют</span>
          <span class="stat-value">{{ absentCount }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">Отмечено</span>
          <span class="stat-value">{{ markedCount }}/{{ athletes.length }}</span>
        </div>
      </div>

      <!-- Список спортсменов -->
      <div class="athletes-section">
        <div class="section-header">
          <h3>Спортсмены группы</h3>
          <button class="refresh-btn" @click="loadAthletes" :disabled="loadingAthletes">
            <span class="refresh-icon">↻</span>
            Обновить
          </button>
        </div>

        <!-- Загрузка -->
        <div v-if="loadingAthletes" class="loading-state">
          <div class="spinner"></div>
          <p>Загрузка спортсменов...</p>
        </div>

        <!-- Нет спортсменов -->
        <div v-else-if="athletes.length === 0" class="empty-state">
          <p>В группе нет спортсменов</p>
        </div>

        <!-- Список спортсменов -->
        <div v-else class="athletes-list">
          <div 
            v-for="(athlete, index) in athletes" 
            :key="athlete.id" 
            class="athlete-card"
          >
            <div class="athlete-number">{{ index + 1 }}</div>
            
            <div class="athlete-info">
              <div class="athlete-name">
                <strong>{{ athlete.last_name }} {{ athlete.first_name }} {{ athlete.middle_name }}</strong>
                <span class="athlete-rank">{{ athlete.sport_rank }}</span>
              </div>
              <div class="athlete-meta">
                <span>{{ formatDate(athlete.birth_date) }}</span>
                <span>{{ athlete.gender === 'M' ? '♂' : '♀' }}</span>
              </div>
            </div>

            <div class="attendance-controls">
              <!-- Переключатель статуса -->
              <div class="status-toggle">
                <button 
                  class="toggle-btn present" 
                  :class="{ active: getStatus(athlete.id) === 'present' }"
                  @click="setStatus(athlete.id, 'present')"
                  :disabled="!selectedTrainingPlan"
                >
                  <span class="emoji">✅</span>
                  <span class="label">Присутствует</span>
                </button>
                <button 
                  class="toggle-btn absent" 
                  :class="{ active: getStatus(athlete.id) === 'absent' }"
                  @click="setStatus(athlete.id, 'absent')"
                  :disabled="!selectedTrainingPlan"
                >
                  <span class="emoji">❌</span>
                  <span class="label">Отсутствует</span>
                </button>
              </div>

              <!-- Поле для причины отсутствия -->
              <div v-if="getStatus(athlete.id) === 'absent'" class="reason-input-wrapper">
                <input
                  type="text"
                  v-model="statuses[athlete.id].absence_reason"
                  placeholder="Укажите причину..."
                  class="reason-input"
                  :disabled="!selectedTrainingPlan"
                />
              </div>

              <!-- Индикатор посещаемости -->
              <div class="attendance-rate" :title="`Посещаемость: ${athlete.attendance_rate || 0}%`">
                <div class="rate-bar">
                  <div 
                    class="rate-fill" 
                    :style="{ width: `${athlete.attendance_rate || 0}%` }"
                    :class="{ 'high-rate': (athlete.attendance_rate || 0) > 70 }"
                  ></div>
                </div>
                <span class="rate-text">{{ athlete.attendance_rate || 0 }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Кнопка сохранения -->
        <div class="save-section">
          <button 
            class="save-btn" 
            @click="saveAttendance"
            :disabled="saving || !selectedTrainingPlan || athletes.length === 0"
          >
            <span v-if="saving" class="spinner-small"></span>
            <span v-else>💾</span>
            {{ saving ? 'Сохранение...' : 'Сохранить посещаемость' }}
          </button>
          
          <div v-if="!selectedTrainingPlan && selectedDate" class="save-hint">
            Выберите дату с тренировкой
          </div>
        </div>
      </div>

      <!-- Уведомления -->
      <div v-if="notification.show" :class="['notification', notification.type]">
        {{ notification.message }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from '../../axios'

export default {
  name: 'AttendancePage',
  data() {
    return {
      group: null,
      athletes: [],
      trainingPlans: [],
      selectedTrainingPlan: null,
      statuses: {},
      selectedDate: new Date().toISOString().slice(0, 10),
      loadingGroup: false,
      loadingAthletes: false,
      loadingTrainingPlan: false,
      saving: false,
      notification: {
        show: false,
        message: '',
        type: 'info'
      }
    }
  },
  computed: {
    groupId() {
      return this.$route.params.id
    },
    coachName() {
      if (!this.group?.coach) return 'Не назначен'
      const coach = this.group.coach
      if (coach.user) {
        const user = coach.user
        return `${user.last_name || ''} ${user.first_name || ''} ${user.middle_name || ''}`.trim()
      }
      return 'Тренер'
    },
    presentCount() {
      return Object.values(this.statuses).filter(s => s.status === 'present').length
    },
    absentCount() {
      return Object.values(this.statuses).filter(s => s.status === 'absent').length
    },
    markedCount() {
      return Object.values(this.statuses).filter(s => !!s.status).length
    }
  },
  watch: {
    '$route.params.id': {
      immediate: true,
      handler() {
        this.loadGroup()
        this.loadAthletes()
      }
    },
    selectedDate() {
      this.loadTrainingPlan()
    }
  },
  methods: {
    async loadGroup() {
      this.loadingGroup = true
      try {
        const res = await axios.get(`/api/groups/${this.groupId}/`)
        this.group = res.data
      } catch (error) {
        this.showNotification('Не удалось загрузить данные группы', 'error')
      } finally {
        this.loadingGroup = false
      }
    },

    async loadAthletes() {
      this.loadingAthletes = true
      try {
        const res = await axios.get('/api/athletes/', { 
          params: { group: this.groupId } 
        })
        this.athletes = res.data
        this.initStatuses()
      } catch (error) {
        this.showNotification('Не удалось загрузить спортсменов', 'error')
      } finally {
        this.loadingAthletes = false
      }
    },

    async loadTrainingPlan() {
      if (!this.selectedDate || !this.groupId) return

      this.loadingTrainingPlan = true
      this.selectedTrainingPlan = null

      try {
        const date = new Date(this.selectedDate)
        const params = {
          group_id: this.groupId,
          month: date.getMonth() + 1,
          year: date.getFullYear()
        }
        
        const res = await axios.get('/api/training-plans/', { params })
        this.trainingPlans = res.data
        
        // Ищем план на выбранную дату
        this.selectedTrainingPlan = this.trainingPlans.find(
          plan => plan.date === this.selectedDate
        )

        if (this.selectedTrainingPlan) {
          await this.loadAttendanceForDate()
        } else {
          // Если плана нет, сбрасываем статусы
          this.initStatuses()
        }
      } catch (error) {
        console.error('Ошибка загрузки плана:', error)
        this.showNotification('Ошибка при загрузке плана тренировок', 'error')
      } finally {
        this.loadingTrainingPlan = false
      }
    },

    async loadAttendanceForDate() {
      if (!this.selectedTrainingPlan) return

      try {
        const res = await axios.get('/api/attendance/', {
          params: { training_plan: this.selectedTrainingPlan.id }
        })

        const attendanceRecords = res.data
        this.initStatuses(attendanceRecords)
      } catch (error) {
        console.error('Ошибка загрузки посещаемости:', error)
      }
    },

    initStatuses(existingRecords = []) {
      const newStatuses = {}
      
      this.athletes.forEach(athlete => {
        const existing = existingRecords.find(r => r.athlete.id === athlete.id)
        newStatuses[athlete.id] = {
          status: existing?.status || 'present',
          absence_reason: existing?.absence_reason || '',
          attendance_id: existing?.id
        }
      })
      
      this.statuses = newStatuses
    },

    getStatus(athleteId) {
      return this.statuses[athleteId]?.status || 'present'
    },

    setStatus(athleteId, status) {
      if (!this.selectedTrainingPlan) return
      
      if (!this.statuses[athleteId]) {
        this.statuses[athleteId] = { status, absence_reason: '' }
      } else {
        this.statuses[athleteId].status = status
        if (status === 'present') {
          this.statuses[athleteId].absence_reason = ''
        }
      }
    },

    async saveAttendance() {
      if (!this.selectedTrainingPlan) {
        this.showNotification('Нет тренировки на выбранную дату', 'error')
        return
      }

      this.saving = true
      let success = 0
      let errors = 0

      try {
        for (const athlete of this.athletes) {
          const status = this.statuses[athlete.id]
          if (!status) continue

          const attendanceData = {
            athlete_id: athlete.id,
            training_plan_id: this.selectedTrainingPlan.id,
            status: status.status,
            absence_reason: status.absence_reason || ''
          }

          try {
            if (status.attendance_id) {
              // Обновляем существующую запись
              await axios.put(`/api/attendance/${status.attendance_id}/`, attendanceData)
            } else {
              // Создаем новую запись
              const response = await axios.post('/api/attendance/', attendanceData)
              status.attendance_id = response.data.id
            }
            success++
          } catch (error) {
            console.error('Ошибка сохранения для спортсмена', athlete.id, error)
            errors++
          }
        }

        if (errors === 0) {
          this.showNotification('Посещаемость успешно сохранена', 'success')
          // Обновляем данные о посещаемости спортсменов
          await this.loadAthletes()
        } else {
          this.showNotification(`Сохранено: ${success}, ошибок: ${errors}`, 'warning')
        }
      } catch (error) {
        this.showNotification('Ошибка при сохранении посещаемости', 'error')
      } finally {
        this.saving = false
      }
    },

    goBack() {
      this.$router.push({ name: 'GroupDetails', params: { id: this.groupId } })
    },

    goToPlanCreation() {
      this.$router.push({ 
        name: 'TrainingPlan', 
        query: { 
          group: this.groupId,
          month: new Date(this.selectedDate).getMonth() + 1,
          year: new Date(this.selectedDate).getFullYear()
        }
      })
    },

    showNotification(message, type = 'info') {
      this.notification = { show: true, message, type }
      setTimeout(() => {
        this.notification.show = false
      }, 3000)
    },

    levelLabel(level) {
      const map = {
        'beginner': 'Начальная подготовка',
        'training': 'Учебно-тренировочный',
        'improvement': 'Совершенствование',
        'high': 'Высшее мастерство'
      }
      return map[level] || 'Не указано'
    },

    formatDate(dateString) {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleDateString('ru-RU')
    },

    formatWeekday(dateString) {
      const date = new Date(dateString)
      const weekdays = ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
      return weekdays[date.getDay()]
    },

    getTypeClass(typeId) {
      const colors = ['type-1', 'type-2', 'type-3', 'type-4', 'type-5']
      return colors[typeId % colors.length]
    }
  }
}
</script>

<style scoped>
.attendance-page {
  padding: 20px;
  min-height: 100vh;
  background: #f5f7fa;
}

.content-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
}

.page-header {
  margin-bottom: 24px;
}

.page-header .left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  background: none;
  border: none;
  color: #3498db;
  font-size: 16px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 30px;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #f0f7ff;
}

/* Карточка группы */
.group-info-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 24px;
  color: white;
  margin-bottom: 24px;
}

.group-info-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.group-info-header h3 {
  font-size: 24px;
  margin: 0 0 8px 0;
}

.level-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 30px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.2);
}

.coach-info {
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 16px;
  border-radius: 30px;
}

.coach-info .label {
  opacity: 0.8;
  margin-right: 8px;
}

.coach-info .value {
  font-weight: 600;
}

/* Выбор даты */
.date-selector {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px;
}

.selector-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 300px;
}

.selector-group label {
  font-size: 14px;
  opacity: 0.9;
}

.date-input-wrapper {
  background: white;
  border-radius: 30px;
  padding: 2px;
}

.date-input {
  width: 100%;
  padding: 12px 16px;
  border: none;
  border-radius: 30px;
  font-size: 16px;
  outline: none;
}

/* Информация о тренировке */
.training-info {
  margin-top: 16px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 16px;
}

.info-badge {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.badge-icon {
  font-size: 24px;
}

.badge-title {
  font-weight: 600;
  display: block;
  margin-bottom: 4px;
}

.badge-subtitle {
  font-size: 14px;
  opacity: 0.8;
}

.training-types {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.type-pill {
  padding: 4px 12px;
  border-radius: 30px;
  font-size: 12px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.2);
}

/* Предупреждение о отсутствии тренировки */
.no-training-warning {
  margin-top: 16px;
  background: rgba(255, 200, 0, 0.2);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.warning-icon {
  font-size: 20px;
}

.create-plan-btn {
  background: white;
  color: #764ba2;
  border: none;
  padding: 8px 16px;
  border-radius: 30px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.create-plan-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

/* Статистика */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #f8fafc;
  padding: 16px;
  border-radius: 12px;
  text-align: center;
  border: 1px solid #eef2f6;
}

.stat-card.success {
  background: #e8f5e9;
  color: #2e7d32;
}

.stat-card.error {
  background: #ffebee;
  color: #c62828;
}

.stat-label {
  display: block;
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 8px;
}

.stat-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
}

/* Секция спортсменов */
.athletes-section {
  background: #f8fafc;
  border-radius: 16px;
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  color: #2c3e50;
}

.refresh-btn {
  background: none;
  border: 1px solid #e2e8f0;
  padding: 8px 16px;
  border-radius: 30px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: #edf2f7;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-icon {
  font-size: 16px;
}

/* Состояния загрузки */
.loading-state {
  text-align: center;
  padding: 40px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #3498db;
  border-radius: 50%;
  margin: 0 auto 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  display: inline-block;
  margin-right: 8px;
  animation: spin 0.8s linear infinite;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #95a5a6;
}

/* Список спортсменов */
.athletes-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.athlete-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #eef2f6;
  display: grid;
  grid-template-columns: auto 1fr 2fr;
  gap: 16px;
  align-items: start;
  transition: all 0.2s;
}

.athlete-card:hover {
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.athlete-number {
  width: 32px;
  height: 32px;
  background: #f1f7fc;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #3498db;
}

.athlete-info {
  min-width: 200px;
}

.athlete-name {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 4px;
}

.athlete-rank {
  background: #f1f7fc;
  padding: 2px 8px;
  border-radius: 30px;
  font-size: 11px;
  color: #3498db;
}

.athlete-meta {
  font-size: 13px;
  color: #7f8c8d;
  display: flex;
  gap: 12px;
}

/* Контролы посещаемости */
.attendance-controls {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-toggle {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.toggle-btn {
  flex: 1;
  min-width: 120px;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 30px;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
  font-size: 14px;
}

.toggle-btn.present:hover {
  background: #e8f5e9;
  border-color: #4caf50;
}

.toggle-btn.present.active {
  background: #4caf50;
  border-color: #4caf50;
  color: white;
}

.toggle-btn.absent:hover {
  background: #ffebee;
  border-color: #f44336;
}

.toggle-btn.absent.active {
  background: #f44336;
  border-color: #f44336;
  color: white;
}

.toggle-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.emoji {
  font-size: 16px;
}

.reason-input-wrapper {
  width: 100%;
}

.reason-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 30px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
}

.reason-input:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.reason-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

/* Индикатор посещаемости */
.attendance-rate {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.rate-bar {
  flex: 1;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.rate-fill {
  height: 100%;
  background: #f44336;
  border-radius: 3px;
  transition: width 0.3s;
}

.rate-fill.high-rate {
  background: #4caf50;
}

.rate-text {
  font-size: 12px;
  font-weight: 600;
  color: #7f8c8d;
  min-width: 40px;
}

/* Кнопка сохранения */
.save-section {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #eef2f6;
}

.save-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px 32px;
  border-radius: 40px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.save-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.save-hint {
  margin-top: 8px;
  color: #f39c12;
  font-size: 14px;
}

/* Уведомления */
.notification {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 16px 24px;
  border-radius: 12px;
  color: white;
  font-weight: 500;
  animation: slideIn 0.3s;
  z-index: 1000;
}

.notification.success {
  background: #4caf50;
}

.notification.error {
  background: #f44336;
}

.notification.warning {
  background: #f39c12;
}

.notification.info {
  background: #3498db;
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

/* Адаптивность для мобильных */
@media (max-width: 768px) {
  .attendance-page {
    padding: 10px;
  }

  .content-card {
    padding: 16px;
  }

  .athlete-card {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .athlete-number {
    display: none;
  }

  .status-toggle {
    flex-direction: column;
  }

  .toggle-btn {
    width: 100%;
  }

  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }

  .group-info-header {
    flex-direction: column;
  }

  .notification {
    left: 16px;
    right: 16px;
    bottom: 16px;
    text-align: center;
  }
}
</style>