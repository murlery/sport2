<template>
  <div class="training-plan-page">
    <div class="content-card">
      <div class="page-header">
        <h2>Тренировочный план</h2>
      </div>

      <!-- Вкладки -->
      <div class="tabs">
        <button :class="{ active: activeTab === 'table' }" @click="activeTab = 'table'; loadAllPlans()">Просмотр
          тренировочного плана</button>
        <button :class="{ active: activeTab === 'form' }" @click="activeTab = 'form'">Составление плана</button>
      </div>

      <!-- Сетка карточек -->
      <div v-if="activeTab === 'table'" class="tab-content">
        <!-- Фильтры -->
        <div class="filters">
          <label>Группа
            <select v-model="tableFilters.group_id" @change="applyFilters">
              <!-- Убрали "Все группы", добавили "Выберите группу" -->
              <option value="">Выберите группу</option>
              <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
            </select>
          </label>
          <label>Месяц
            <select v-model="tableFilters.month" @change="applyFilters" :disabled="!tableFilters.group_id">
              <option value="">Все месяцы</option>
              <option v-for="m in months" :key="m.value" :value="m.value">{{ m.label }}</option>
            </select>
          </label>
          <label>Год
            <select v-model="tableFilters.year" @change="applyFilters" :disabled="!tableFilters.group_id">
              <option value="">Все годы</option>
              <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
            </select>
          </label>
          <label class="search-label">
            <span>Поиск</span>
            <div class="search-wrapper">
              <input type="text" v-model="searchQuery" @input="applyFilters" placeholder="Поиск по тренировкам..."
                :disabled="!tableFilters.group_id" class="search-input" />
              <span v-if="searchQuery" class="search-clear" @click="clearSearch">✕</span>
            </div>
          </label>
          <!-- Кнопка экспорта в стиле Excel -->
          <button class="excel-btn" @click="exportToExcel"
            :disabled="!tableFilters.group_id || filteredPlans.length === 0">

            <span>Экспорт в xlsx</span>
          </button>
        </div>

        <!-- Результаты поиска -->
        <div v-if="tableFilters.group_id && searchQuery" class="search-results-info">
          Найдено тренировок: {{ filteredPlans.length }}
          <button class="clear-search-btn" @click="clearSearch">Сбросить поиск</button>
        </div>


        <!-- Сообщение, если группа не выбрана -->
        <div v-if="!tableFilters.group_id" class="no-group-message">
          <p>Выберите группу для просмотра тренировочного плана</p>
        </div>

        <!-- Сообщение, если нет данных -->
        <div v-else-if="filteredPlans.length === 0" class="no-data">
          Нет тренировок за выбранный период
        </div>

        <!-- Сетка карточек -->
        <div v-else class="cards-grid">
          <div v-for="plan in filteredPlans" :key="plan.id" class="date-card" @click="openEditModal(plan)">
            <h3>
              {{ formatDate(plan.date) }}<br>
              {{ formatWeekday(plan.date) }}
            </h3>
            <p class="total-hours">Всего часов: {{ plan.total_hours }}</p>
            <div class="types">
              <div v-for="th in plan.training_hours" :key="th.training_type.id"
                :class="['type-item', getTypeCellClass(th.training_type.id)]">
                {{ th.training_type.name }}: {{ th.hours }} ч
              </div>
            </div>
          </div>
        </div>
        <!-- МОДАЛЬНОЕ ОКНО -->
        <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
          <div class="edit-modal">

            <div class="modal-header">
              <h2>
                Редактирование тренировки
              </h2>

              <button class="close-btn" @click="closeEditModal">
                ✕
              </button>
            </div>

            <div v-if="editingPlan">

              <div class="modal-info">
                <p>
                  <strong>Дата:</strong>
                  {{ formatDate(editingPlan.date) }}
                </p>

                <p>
                  <strong>Группа:</strong>
                  {{ editingPlan.group?.name }}
                </p>
              </div>

              <div class="edit-types">

                <div v-for="(row, index) in editingPlan.training_hours" :key="index" class="edit-row">

                  <select v-model="row.training_type.id">
                    <option v-for="t in trainingTypes" :key="t.id" :value="t.id">
                      {{ t.name }}
                    </option>
                  </select>

                  <input type="number" min="0" step="0.5" v-model.number="row.hours" />

                  <button class="remove-btn" @click="removeEditType(index)">
                    ✕
                  </button>

                </div>

              </div>

              <button class="ghost add-btn" @click="addEditType">
                + Добавить раздел подготовки
              </button>

              <div class="modal-actions">

                <button class="primary" @click="savePlanChanges">
                  Сохранить
                </button>

                <button class="secondary" @click="closeEditModal">
                  Отмена
                </button>

              </div>

            </div>

          </div>
        </div>
      </div>

      <!-- Форма -->
      <div v-if="activeTab === 'form'" class="tab-content">
        <div class="card">
          <h2>Параметры</h2>
          <div class="form-grid">
            <label>Группа
              <select v-model="form.group_id">
                <option value="">Выберите группу</option>
                <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
              </select>
            </label>
            <label>Год
              <select v-model="form.year">
                <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
              </select>
            </label>
            <label>Месяц
              <select v-model="form.month">
                <option v-for="m in months" :key="m.value" :value="m.value">{{ m.label }}</option>
              </select>
            </label>
            <label>Часов в день
              <input type="number" step="0.5" min="0.5" v-model.number="form.total_hours" />
            </label>
          </div>
        </div>

        <div class="card">
          <h2>Дни недели</h2>
          <div class="weekdays">
            <label v-for="d in weekdays" :key="d.value">
              <input type="checkbox" :value="d.value" v-model="form.weekdays" />
              {{ d.label }}
            </label>
          </div>
        </div>

        <div class="card">
          <h2>Виды тренировок</h2>
          <table class="types-table">
            <thead>
              <tr>
                <th>Тип</th>
                <th>Часы</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in form.training_types" :key="index">
                <td>
                  <select v-model="row.id">
                    <option value="">Выберите тип</option>
                    <option v-for="t in trainingTypes" :key="t.id" :value="t.id">{{ t.name }}</option>
                  </select>
                </td>
                <td><input type="number" min="0.5" step="0.5" v-model.number="row.hours" /></td>
                <td><button class="remove-btn" @click="removeType(index)">✕</button></td>
              </tr>
            </tbody>
          </table>
          <button class="ghost" @click="addType">+ Добавить тип</button>
        </div>

        <div class="actions">
          <button class="primary" :disabled="!canSubmit || loading" @click="generatePlan">
            {{ loading ? 'Создание...' : 'Сгенерировать план' }}
          </button>
        </div>

        <div v-if="notification" class="notification">{{ notification }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '../../axios'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

export default {
  data() {
    const today = new Date()
    return {
      activeTab: 'table',
      groups: [],
      trainingTypes: [],
      allPlans: [],
      filteredPlans: [],
      searchQuery: '', // Новое поле для поиска
      notification: '',
      loading: false,
      currentCoach: {
        last_name: '',
        first_name: '',
        middle_name: ''
      },
      showEditModal: false,
      editingPlan: null,

      form: {
        group_id: '',
        year: today.getFullYear(),
        month: today.getMonth() + 1,
        weekdays: [],
        total_hours: 2,
        training_types: [],
      },

      tableFilters: {
        group_id: '',
        month: today.getMonth() + 1,
        year: today.getFullYear()
      },

      months: [
        { value: 1, label: 'Январь' }, { value: 2, label: 'Февраль' }, { value: 3, label: 'Март' }, { value: 4, label: 'Апрель' },
        { value: 5, label: 'Май' }, { value: 6, label: 'Июнь' }, { value: 7, label: 'Июль' }, { value: 8, label: 'Август' },
        { value: 9, label: 'Сентябрь' }, { value: 10, label: 'Октябрь' }, { value: 11, label: 'Ноябрь' }, { value: 12, label: 'Декабрь' }
      ]
    }
  },
  computed: {
    weekdays() { return [{ value: 0, label: 'Пн' }, { value: 1, label: 'Вт' }, { value: 2, label: 'Ср' }, { value: 3, label: 'Чт' }, { value: 4, label: 'Пт' }, { value: 5, label: 'Сб' }, { value: 6, label: 'Вс' }] },
    years() { const y = new Date().getFullYear(); return [y - 1, y, y + 1] },
    canSubmit() { return this.form.group_id && this.form.weekdays.length && this.form.training_types.length },

    trainingTypesInFilteredPlans() {
      const map = {}
      this.filteredPlans.forEach(p => {
        p.training_hours.forEach(th => {
          map[th.training_type.id] = th.training_type
        })
      })
      return Object.values(map)
    }
  },
  async mounted() {
    await Promise.all([this.loadGroups(), this.loadTrainingTypes()])
    this.addType()
    await this.loadAllPlans()

    try {
      const response = await axios.get('/api/me/')
      this.currentCoach = response.data
    } catch (e) {
      console.log('Данные тренера не загружены, используем значения по умолчанию')
    }
    const tab = this.$route.query.tab
    const group = this.$route.query.group

    if (tab) {
      this.activeTab = tab
    }

    if (group) {
      const groupId = Number(group)

      // выбрать группу в форме генерации
      this.form.group_id = groupId

      // выбрать группу в таблице
      this.tableFilters.group_id = groupId

      // применить фильтры
      this.applyFilters()
    }
  },
  methods: {
    async loadGroups() {
      this.groups = (await axios.get('/api/groups/')).data
    },

    async loadTrainingTypes() {
      this.trainingTypes = (await axios.get('/api/training-types/')).data
    },

    addType() {
      this.form.training_types.push({ id: '', hours: 0 })
    },

    removeType(i) {
      this.form.training_types.splice(i, 1)
    },
    // =========================
// Открыть модальное окно
// =========================
openEditModal(plan) {

  this.editingPlan = JSON.parse(
    JSON.stringify(plan)
  )

  this.showEditModal = true
},

// =========================
// Закрыть модальное окно
// =========================
closeEditModal() {
  this.showEditModal = false
  this.editingPlan = null
},

// =========================
// Добавить раздел
// =========================
addEditType() {

  this.editingPlan.training_hours.push({
    training_type: {
      id: '',
      name: ''
    },
    hours: 0
  })
},

// =========================
// Удалить раздел
// =========================
removeEditType(index) {

  this.editingPlan.training_hours.splice(index, 1)
},

// =========================
// Сохранение
// =========================
async savePlanChanges() {

  try {

    const payload = {
      total_hours: this.editingPlan.training_hours.reduce(
        (sum, t) => sum + Number(t.hours || 0),
        0
      ),

      training_hours: this.editingPlan.training_hours.map(t => ({
        training_type_id: t.training_type.id,
        hours: t.hours
      }))
    }

    await axios.patch(
      `/api/training-plans/${this.editingPlan.id}/`,
      payload
    )

    await this.loadAllPlans()

    this.closeEditModal()

    this.notification = 'Тренировка обновлена'

  } catch (e) {

    console.error(e)

    this.notification =
      'Ошибка сохранения тренировки'
  }
},

    async generatePlan() {
      this.loading = true
      this.notification = ''
      try {
        await axios.post('/api/training-plans/generate/', this.form)
        this.notification = 'План создан'
        await this.loadAllPlans()
      } catch (e) {
        this.notification = e.response?.data?.error || 'Ошибка'
      } finally {
        this.loading = false
      }
    },

    async loadAllPlans() {
      this.loading = true
      try {
        const data = (await axios.get('/api/training-plans/')).data
        this.allPlans = data.sort((a, b) => new Date(a.date) - new Date(b.date))
        console.log('Все планы загружены:', this.allPlans.length)

        this.applyFilters()
      } catch (e) {
        console.error('Ошибка загрузки планов:', e)
      } finally {
        this.loading = false
      }
    },

    // Метод для поиска по плану
    searchInPlan(plan, query) {
      if (!query) return true

      const searchLower = query.toLowerCase().trim()

      // Поиск по дате
      const dateStr = this.formatDate(plan.date) + ' ' + this.formatWeekday(plan.date)
      if (dateStr.toLowerCase().includes(searchLower)) return true

      // Поиск по общему количеству часов
      if (plan.total_hours.toString().includes(searchLower)) return true

      // Поиск по типам тренировок
      for (const th of plan.training_hours) {
        // Поиск по названию типа тренировки
        if (th.training_type.name.toLowerCase().includes(searchLower)) return true

        // Поиск по количеству часов типа тренировки
        if (th.hours.toString().includes(searchLower)) return true
      }

      return false
    },

    clearSearch() {
      this.searchQuery = ''
      this.applyFilters()
    },

    applyFilters() {
      console.log('Применяем фильтры:', JSON.parse(JSON.stringify(this.tableFilters)))
      console.log('Поисковый запрос:', this.searchQuery)

      // Если группа не выбрана, показываем пустой массив
      if (!this.tableFilters.group_id) {
        this.filteredPlans = []
        return
      }

      // Сначала применяем фильтры по группе, месяцу и году
      let filtered = this.allPlans.filter(plan => {
        const planGroupId = plan.group ? plan.group.id : null
        if (planGroupId !== Number(this.tableFilters.group_id)) {
          return false
        }

        const planDate = new Date(plan.date)
        const planYear = planDate.getFullYear()
        const planMonth = planDate.getMonth() + 1

        if (this.tableFilters.year && planYear !== Number(this.tableFilters.year)) {
          return false
        }

        if (this.tableFilters.month && planMonth !== Number(this.tableFilters.month)) {
          return false
        }

        return true
      })

      // Затем применяем поиск, если есть запрос
      if (this.searchQuery) {
        filtered = filtered.filter(plan => this.searchInPlan(plan, this.searchQuery))
      }

      this.filteredPlans = filtered
      console.log('Отфильтровано планов:', this.filteredPlans.length)
    },

    formatDate(d) {
      const dateObj = new Date(d)
      return `${dateObj.getDate().toString().padStart(2, '0')}.${(dateObj.getMonth() + 1).toString().padStart(2, '0')}`
    },

    formatWeekday(d) {
      const dateObj = new Date(d)
      const dayNames = ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
      return dayNames[dateObj.getDay()]
    },

    getTypeCellClass(typeId) {
      const colors = ['training-type-1', 'training-type-2', 'training-type-3', 'training-type-4', 'training-type-5']
      const idx = this.trainingTypesInFilteredPlans.findIndex(t => t.id === typeId)
      return colors[idx % colors.length]
    },

    exportToExcel() {
      if (!this.filteredPlans.length) return

      const coachName = [this.currentCoach.last_name, this.currentCoach.first_name, this.currentCoach.middle_name]
        .filter(Boolean)
        .join(' ') || 'Неизвестный тренер'

      const groupName = this.groups.find(g => g.id === this.tableFilters.group_id)?.name || 'Не выбрана'
      const monthName = this.tableFilters.month ?
        this.months.find(m => m.value === this.tableFilters.month)?.label : 'Все месяцы'
      const year = this.tableFilters.year || 'Все годы'

      const metadataRows = [
        ['Тренер', coachName],
        ['Группа', groupName],
        ['Месяц', monthName],
        ['Год', year],
        this.searchQuery ? ['Поиск', this.searchQuery] : [],
        [],
      ]

      const dates = this.filteredPlans.map(p => p.date)

      const header = ['Показатель / Дата', ...dates.map(d => this.formatDate(d))]

      const totalHoursRow = ['Всего часов', ...this.filteredPlans.map(p => p.total_hours)]

      const trainingRows = this.trainingTypesInFilteredPlans.map(tt => {
        return [
          tt.name,
          ...dates.map(date => {
            const plan = this.filteredPlans.find(p => p.date === date)
            const th = plan?.training_hours.find(x => x.training_type.id === tt.id)
            return th ? th.hours : 0
          })
        ]
      })

      const worksheetData = [...metadataRows, header, totalHoursRow, ...trainingRows]

      const wb = XLSX.utils.book_new()
      const ws = XLSX.utils.aoa_to_sheet(worksheetData)
      XLSX.utils.book_append_sheet(wb, ws, 'Тренировочный план')

      const fileName = `Тренировочный_план_${groupName}_${monthName}_${year}${this.searchQuery ? '_поиск' : ''}.xlsx`
      const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
      saveAs(new Blob([wbout], { type: 'application/octet-stream' }), fileName)
    }
  }
}
</script>




<style scoped>
/* Новый стиль для сообщения о выборе группы */
.no-group-message {
  text-align: center;
  padding: 60px 40px;
  background: #f8f9fa;
  border-radius: 12px;
  color: #7f8c8d;
  font-size: 18px;

}

.no-group-message p {
  margin: 0;
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 16px;
}

/* Стили для заблокированных полей */
select:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
  opacity: 0.6;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.training-plan-page {
  padding: 30px;
  min-height: 100vh;
}

/* Главная карточка */
.content-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

/* Заголовок */
.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
}

/* Вкладки */
.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.tabs button {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #f4f6f8;
  cursor: pointer;
  font-weight: 500;
  transition: 0.25s ease;
}

.tabs button.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.tabs button:hover {
  background: #e9eef3;
}

/* Фильтры */
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 20px;
}

/* Сетка карточек */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.date-card {
  background: #f1f7fc;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #e2e4e7;
  box-shadow: 0 20px 12px rgba(6, 6, 6, 0.05);

}

.date-card h3 {
  font-size: 16px;
  margin-bottom: 8px;
}

.total-hours {
  font-weight: 600;
  margin-bottom: 8px;

}

.types {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.type-item {
  padding: 4px 6px;
  border-radius: 6px;
  font-weight: 500;
  color: #fff;
}

/* Цвета тренировок */
.training-type-1 {
  background: #fdebd0;
  color: #784212;
}

.training-type-2 {
  background: #d5f5e3;
  color: #145a32;
}

.training-type-3 {
  background: #f5d6e0;
  color: #6c3483;
}

.training-type-4 {
  background: #f9e79f;
  color: #7d6608;
}

.training-type-5 {
  background: #d6eaf8;
  color: #154360;
}

/* Форма */
.card {
  background: #f9fafb;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 12px;
  border: 1px solid #eef1f4;
}

label {
  font-size: 14px;
  font-weight: 500;
  color: #34495e;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

select,
input[type="number"] {
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid #dcdfe3;
  background: white;
  font-size: 14px;
  transition: 0.2s ease;
}

select:focus,
input:focus {
  outline: none;
  border-color: #3498db;
}

/* Сетка формы */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

/* Дни недели */
.weekdays {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
}

/* Таблица типов */
.types-table {
  width: 50%;
  border-collapse: collapse;
  margin-bottom: 12px;
}

.types-table th,
.types-table td {
  border-bottom: 1px solid #eaecef;
  padding: 8px;
  text-align: center;
}

.types-table th {
  background: #f4f6f8;
  font-weight: 600;
}

/* Кнопки */
.primary {
  background: #3498db;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 10px 20px;
  cursor: pointer;
  font-weight: 600;
  transition: 0.25s ease;
}

.primary:hover {
  background: #2980b9;
}

.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ghost {
  background: #f1f3f6;
  border: 1px solid #e5e7eb;
  padding: 8px 14px;
  border-radius: 8px;
  cursor: pointer;
  transition: 0.2s ease;
}

.ghost:hover {
  background: #e5eaf0;
}

.remove-btn {
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  padding: 4px 8px;
  transition: 0.2s ease;
}

.remove-btn:hover {
  background: #c0392b;
}

/* Действия и уведомления */
.actions {
  text-align: right;
  margin-top: 10px;
}

.notification {
  margin-top: 16px;
  padding: 12px;
  background: #e3f2fd;
  border-radius: 8px;
  color: #1565c0;
  font-weight: 500;
}


/* Новые стили для поиска */
.search-label {
  min-width: 250px;
}

.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input {
  width: 100%;
  padding: 8px 30px 8px 12px;
  border-radius: 8px;
  border: 1px solid #dcdfe3;
  background: white;
  font-size: 14px;
  transition: 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.search-input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
  opacity: 0.6;
}

.search-clear {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #95a5a6;
  font-size: 16px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #ecf0f1;
  transition: 0.2s ease;
}

.search-clear:hover {
  background: #bdc3c7;
  color: #2c3e50;
}

.search-results-info {
  background: #e3f2fd;
  padding: 10px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #1565c0;
  font-weight: 500;
}

.clear-search-btn {
  background: none;
  border: 1px solid #90caf9;
  color: #1565c0;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  cursor: pointer;
  transition: 0.2s ease;
}

.clear-search-btn:hover {
  background: #bbdefb;
  border-color: #42a5f5;
}

.excel-btn {
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 8px 20px;
  /* Увеличил вертикальные отступы */
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  height: 40px;
  /* Сделал такую же высоту как у полей ввода */
  margin-top: 0;
  align-self: flex-end;
  /* Выравнивание по нижнему краю */
  box-shadow: 0 2px 5px rgba(39, 174, 96, 0.3);
  line-height: 1;
  /* Фиксим вертикальное выравнивание текста */
}

.excel-btn:hover:not(:disabled) {
  background: #219a52;

  box-shadow: 0 4px 10px rgba(39, 174, 96, 0.4);
}

.excel-btn:active:not(:disabled) {

  box-shadow: 0 2px 5px rgba(39, 174, 96, 0.3);
}

.excel-btn:disabled {
  background: #a5d6a7;
  cursor: not-allowed;
  opacity: 0.6;
  transform: none;
  box-shadow: none;
}
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.edit-modal {
  width: 700px;
  max-width: 95%;
  background: white;
  border-radius: 18px;
  padding: 24px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.close-btn {
  border: none;
  background: none;
  font-size: 22px;
  cursor: pointer;
}

.edit-row {
  display: grid;
  grid-template-columns: 1fr 120px 50px;
  gap: 12px;
  margin-bottom: 12px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.add-btn {
  margin-top: 10px;
}
/* =========================
   📱 МОБИЛЬНАЯ АДАПТАЦИЯ ФОРМЫ
========================= */

@media (max-width: 768px) {

  .training-plan-page {
    padding: 15px;
  }

  .content-card {
    padding: 16px;
  }

  /* Вкладки */
  .tabs {
    flex-direction: column;
  }

  .tabs button {
    width: 100%;
  }

  /* Сетка формы — 1 колонка */
  .form-grid {
    grid-template-columns: 1fr;
  }

  /* Карточки */
  .card {
    padding: 16px;
  }

  .card h2 {
    font-size: 18px;
  }

  /* Дни недели */
  .weekdays {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
  }

  .weekdays label {
    background: #f1f3f6;
    padding: 8px;
    border-radius: 8px;
    align-items: center;
    justify-content: center;
    font-size: 13px;
  }

  .weekdays input {
    margin-right: 6px;
  }

  /* Таблица типов — вертикальный вид */
  .types-table {
    width: 100%;
  }

  .types-table thead {
    display: none;
  }

  .types-table tr {
    display: flex;
    flex-direction: column;
    gap: 8px;
    background: white;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 10px;
    border: 1px solid #eaecef;
  }

  .types-table td {
    border: none;
    padding: 0;
    text-align: left;
  }

  .types-table select,
  .types-table input {
    width: 100%;
  }

  .remove-btn {
    align-self: flex-end;
  }

  /* Кнопки */
  .ghost {
    width: 100%;
  }

  .actions {
    text-align: center;
  }

  .primary {
    width: 100%;
    padding: 14px;
    font-size: 16px;
  }

  /* Уведомление */
  .notification {
    text-align: center;
    font-size: 14px;
  }

}
</style>