<template>
  <div class="add-athlete-page">
    <header class="page-header">
      <div class="left">
        <button class="back-btn" @click="goBack">← Назад</button>
        <p class="eyebrow">Новый спортсмен</p>
        <h1>Добавление спортсмена</h1>
        <div class="controls">
          <label class="field">
            <span>Группа</span>
            <select v-model="form.group_id">
              <option value="">Выберите группу</option>
              <option v-for="group in groups" :key="group.id" :value="String(group.id)">
                {{ group.name }}
              </option>
            </select>
          </label>
          <button class="action ghost" :disabled="loadingGroups" @click="loadGroups">
            Обновить группы
          </button>
        </div>
      </div>
      <div class="right">
        <div class="stat">
          <p class="label">Доступно групп</p>
          <p class="value">{{ groups.length }}</p>
        </div>
        <div class="stat">
          <p class="label">Дата рождения</p>
          <p class="value">{{ form.birth_date || '—' }}</p>
        </div>
      </div>
    </header>

    <section class="card">
      <div class="card-header">
        <p class="eyebrow">Данные</p>
        <h2>Основная информация</h2>
      </div>

      <div class="form-grid">
        <label class="field">
          <span>Фамилия*</span>
          <input type="text" v-model="form.last_name" placeholder="Введите фамилию" />
        </label>
        <label class="field">
          <span>Имя*</span>
          <input type="text" v-model="form.first_name" placeholder="Введите имя" />
        </label>
        <label class="field">
          <span>Отчество</span>
          <input type="text" v-model="form.middle_name" placeholder="Введите отчество" />
        </label>
        <label class="field">
          <span>Дата рождения</span>
          <input type="date" v-model="form.birth_date" />
        </label>
        <label class="field">
          <span>Пол</span>
          <select v-model="form.gender">
            <option value="">Не выбран</option>
            <option value="M">Мужской</option>
            <option value="F">Женский</option>
          </select>
        </label>
        <label class="field">
          <span>Спортивный разряд*</span>
          <select v-model="form.sport_rank">
            <option value="">Выберите разряд</option>
            <option value="MSMK">МСМК</option>
            <option value="MS">МС</option>
            <option value="KMS">КМС</option>
            <option value="I">I</option>
            <option value="II">II</option>
            <option value="III">III</option>
            <option value="1 юн.">1 юн.</option>
            <option value="2 юн.">2 юн.</option>
            <option value="3 юн.">3 юн.</option>
          </select>
        </label>
      </div>

      <div class="actions">
        <button class="action ghost" @click="resetForm">Очистить</button>
        <button class="action primary" :disabled="saving" @click="saveAthlete">
          {{ saving ? 'Сохраняем...' : 'Создать' }}
        </button>
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
  name: 'AddAthlete',

  data() {
    return {
      currentUser: null,
      coachInfo: null,
      groups: [],
      loadingGroups: false,
      saving: false,
      form: {
        first_name: '',
        last_name: '',
        middle_name: '',
        birth_date: '',
        sport_rank: '',
        gender: '',
        group_id: ''
      },
      notification: {
        show: false,
        message: '',
        type: 'info'
      }
    }
  },

  async mounted() {
    await this.loadCurrentUser()
    await this.loadCoachInfo()
    await this.loadGroups()
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

    applyInitialGroup() {
      const queryGroup = this.$route.query.group
      if (queryGroup) this.form.group_id = String(queryGroup)
    },

    resetForm() {
      this.form = {
        first_name: '',
        last_name: '',
        middle_name: '',
        birth_date: '',
        sport_rank: '',
        gender: '',
        group_id: this.form.group_id // оставляем выбранную группу
      }
    },

    async saveAthlete() {
      if (!this.form.first_name || !this.form.last_name || !this.form.sport_rank) {
        this.showNotification('Заполните имя, фамилию и разряд', 'error')
        return
      }
      if (!this.form.group_id) {
        this.showNotification('Выберите группу', 'error')
        return
      }
      this.saving = true
      try {
        const payload = { ...this.form }
        await axios.post('/api/athletes/', payload)
        this.showNotification('Спортсмен создан', 'success')
        this.$router.push({ name: 'CoachDashboard' })
      } catch (error) {
        console.error('Ошибка создания спортсмена', error)
        this.showNotification('Не удалось создать спортсмена', 'error')
      } finally {
        this.saving = false
      }
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
.add-athlete-page {
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
  min-width: 220px;
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

.right {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
  min-width: 220px;
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
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
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

  .right {
    width: 100%;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  }
}
</style>
