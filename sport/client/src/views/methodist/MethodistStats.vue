<template>
  <div class="methodist-page">
    <section class="card stats-card">
      <div class="card-header">
        <div>
          <p class="eyebrow">Статистика</p>
          <h2>Месячная и квартальная</h2>
        </div>
      </div>

      <!-- Таб переключения -->
      <div class="tabs">
        <button :class="{ 'active-tab': activeTab === 'month' }" @click="activeTab = 'month'">
          Месячная
        </button>
        <button :class="{ 'active-tab': activeTab === 'quarter' }" @click="activeTab = 'quarter'">
          Квартальная
        </button>
      </div>

      <!-- Контент табов -->
      <div class="tabs-content">
        <!-- Месячная статистика -->
        <div v-show="activeTab === 'month'" class="stats-block monthly">
          <div class="block-header">
            <h3>Месячная статистика ({{ monthLabel }})</h3>
            <div class="inline-actions">
              <select v-model="statsMonth">
                <option v-for="m in months" :key="m.value" :value="m.value">{{ m.label }}</option>
              </select>
              <select v-model="statsYear">
                <option v-for="y in years" :key="y" :value="String(y)">{{ y }}</option>
              </select>
            </div>
          </div>

          <div class="table-container">
            <table class="data-table hoverable">
              <thead>
                <tr>
                  <th>Отделение</th>
                  <th>Соревнование</th>
                  <th>Дата / место</th>
                  <th>Уровень</th>
                  <th>Участников</th>
                  <th>Призовые места</th>
                  <th>Тренер</th>
                </tr>
              </thead>
              <tbody>
                <!-- Группировка по отделению -->
                <template v-for="group in groupedMonthlyStats">
                  <tr v-for="(row, index) in group.rows" :key="row.id">
                    <!-- Ключ теперь на реальном элементе -->
                    <td v-if="index === 0" :rowspan="group.rows.length">{{ group.department }}</td>
                    <td>{{ row.name }}</td>
                    <td>{{ formatDate(row.date) }} • {{ row.location }}</td>
                    <td>{{ row.level }}</td>
                    <td>{{ row.participants }}</td>
                    <td>{{ row.prizePlaces }}</td>
                    <td>{{ row.coach }}</td>
                  </tr>
                </template>

                <tr v-if="!monthlyStats.length">
                  <td colspan="7" class="empty">Нет данных за месяц</td>
                </tr>
              </tbody>
              <tfoot v-if="monthlyStats.length">
                <tr class="summary-row">
                  <td colspan="4"><strong>Итого</strong></td>
                  <td>{{monthlyStats.reduce((a, b) => a + b.participants, 0)}}</td>
                  <td>{{monthlyStats.reduce((a, b) => a + b.prizePlaces, 0)}}</td>
                  <td></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>

        <!-- Квартальная статистика -->
        <div v-show="activeTab === 'quarter'" class="stats-block quarterly">
          <h3>Квартальная статистика ({{ quarterLabel }})</h3>
          <div class="table-container">
            <table class="data-table hoverable">
              <thead>
                <tr>
                  <th>Отделение</th>
                  <th>Уровень</th>
                  <th>Соревнований</th>
                  <th>Участников</th>
                  <th>Призовых мест</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in quarterlyStats" :key="row.key">
                  <td>{{ row.department }}</td>
                  <td>{{ row.level }}</td>
                  <td>{{ row.events }}</td>
                  <td>{{ row.participants }}</td>
                  <td>{{ row.prizePlaces }}</td>
                </tr>
                <tr v-if="!quarterlyStats.length">
                  <td colspan="5" class="empty">Нет данных за квартал</td>
                </tr>
              </tbody>
              <tfoot v-if="quarterlyStats.length">
                <tr class="summary-row">
                  <td colspan="2"><strong>Итого</strong></td>
                  <td>{{quarterlyStats.reduce((a, b) => a + b.events, 0)}}</td>
                  <td>{{quarterlyStats.reduce((a, b) => a + b.participants, 0)}}</td>
                  <td>{{quarterlyStats.reduce((a, b) => a + b.prizePlaces, 0)}}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import axios from '../../axios'

export default {
  name: 'MethodistStats',
  data() {
    const today = new Date()
    return {
      statsMonth: String(today.getMonth() + 1),
      statsYear: String(today.getFullYear()),
      competitions: [],
      activeTab: 'month'
    }
  },
  computed: {
    groupedMonthlyStats() {
      const groups = {}

      this.monthlyStats.forEach(row => {
        if (!groups[row.department]) {
          groups[row.department] = []
        }
        groups[row.department].push(row)
      })

      return Object.entries(groups).map(([department, rows]) => ({
        department,
        rows
      }))
    },
    months() {
      return [
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
    },
    years() {
      const current = new Date().getFullYear()
      return [current - 1, current, current + 1]
    },
    monthLabel() {
      const date = new Date(Number(this.statsYear), Number(this.statsMonth) - 1, 1)
      return date.toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' })
    },
    quarterLabel() {
      const month = Number(this.statsMonth)
      const year = Number(this.statsYear)
      const q = Math.floor((month - 1) / 3) + 1
      return `${q}-й квартал ${year}`
    },
    approvedReports() {
      return this.competitions.filter(c => c.status === 'approved')
    },
    monthlyStats() {
      const m = Number(this.statsMonth) - 1
      const y = Number(this.statsYear)
      return this.approvedReports.filter(c => {
        const d = new Date(c.date)
        return d.getMonth() === m && d.getFullYear() === y
      }).map(c => {
        console.log('RESULTS:', c.results, c) // ← ВОТ СЮДА

        const participants = (c.results || []).length
        const prizePlaces = (c.results || []).filter(r => !r.is_participant && r.place).length
        return {
          id: c.id,
          name: c.name,
          date: c.date,
          location: c.location,
          level: c.level,
          department: c.coach?.department?.name || '—',
          coach: c.coach?.user ? `${c.coach.user.last_name} ${c.coach.user.first_name}` : '—',
          participants,
          prizePlaces
        }
      })
    },
    quarterlyStats() {
      const y = Number(this.statsYear)
      const month = Number(this.statsMonth)
      const q = Math.floor((month - 1) / 3)
      const approved = this.approvedReports.filter(c => {
        const d = new Date(c.date)
        return d.getFullYear() === y && Math.floor(d.getMonth() / 3) === q
      })
      const grouped = {}
      approved.forEach(c => {
        const dept = c.coach?.department?.name || '—'
        const key = `${dept}|${c.level}`
        const results = c.results || []
        const participants = results.length
        const prize = results.filter(r => !r.is_participant && r.place).length
        if (!grouped[key]) grouped[key] = { department: dept, level: c.level, events: 0, participants: 0, prizePlaces: 0, key }
        grouped[key].events += 1
        grouped[key].participants += participants
        grouped[key].prizePlaces += prize
      })
      return Object.values(grouped)
    }
  },
  async mounted() {
    await this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const res = await axios.get('/api/competitions/')
        this.competitions = res.data
      } catch (err) { console.error(err) }
    },
    formatDate(date) { return date ? new Date(date).toLocaleDateString('ru-RU') : '-' }
  }
}
</script>

<style scoped>
.methodist-page {
  min-height: 100vh;

  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #9ca3af;
  font-size: 12px;
  font-weight: 700;
}

.tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.tabs button {
  padding: 8px 16px;
  border: none;
  background: #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.tabs button.active-tab {
  background: #3b82f6;
  color: #fff;
}

.tabs button:hover:not(.active-tab) {
  background: #d1d5db;
}

.stats-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.stats-block {
  background: #f9fafb;
  border-radius: 14px;
  padding: 14px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.stats-block h3 {
  margin: 0 0 10px;
  color: #1f2937;
  font-size: 16px;
}

.block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 8px;
  flex-wrap: wrap;
}

.inline-actions select {
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid #d1d9e0;
  background: #fff;
  cursor: pointer;
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
  padding: 10px;
  background: #eef2f7;
  color: #4b5563;
  border-bottom: 1px solid #e5e7eb;
}

.data-table td {
  padding: 10px;
  border-bottom: 1px solid #f0f2f5;
  color: #1f2937;
  transition: background 0.2s;
}

.data-table.hoverable tbody tr:hover {
  background: #f3f4f6;
}

.empty {
  text-align: center;
  color: #6b7280;
  padding: 12px 0;
}

tfoot .summary-row td {
  font-weight: 700;
  background: #f1f5f9;
}

@media (max-width:1024px) {
  .stats-layout {
    grid-template-columns: 1fr;
  }
}
</style>
