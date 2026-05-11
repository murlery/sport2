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
        <button :class="{ 'active-tab': activeTab === 'training' }" @click="activeTab = 'training'">
          По тренировкам
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
              <button class="export-btn" @click="exportMonthlyStats" :disabled="!monthlyStats.length">
                Экспорт в xlsx
              </button>
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
          <div class="block-header">
            <h3>
              Квартальная статистика
              ({{ quarterLabel }})
            </h3>

            <div class="inline-actions">
              <select v-model="statsQuarter">
                <option v-for="q in quarters" :key="q.value" :value="q.value">
                  {{ q.label }}
                </option>
              </select>

              <select v-model="statsYear">
                <option v-for="y in years" :key="y" :value="String(y)">
                  {{ y }}
                </option>
              </select>
              <button class="export-btn" @click="exportQuarterlyStats" :disabled="!quarterlyStats.length">
                Экспорт в xlsx
              </button>
            </div>
          </div>
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
        <!-- Статистика по тренировкам -->
        <div v-show="activeTab === 'training'" class="stats-block training-stats">
          <div class="block-header">
            <h3>Статистика по тренировкам</h3>

            <div class="inline-actions filters">
              <select v-model="trainingFilters.department">
                <option value="">Все отделения</option>
                <option v-for="d in departments" :key="d.id" :value="d.id">
                  {{ d.name }}
                </option>
              </select>

              <select v-model="trainingFilters.coach">
                <option value="">Все тренеры</option>
                <option v-for="c in filteredCoaches" :key="c.id" :value="c.id">
                  {{ c.user.last_name }} {{ c.user.first_name }}
                </option>
              </select>

              <select v-model="trainingFilters.group">
                <option value="">Все группы</option>
                <option v-for="g in filteredGroups" :key="g.id" :value="g.id">
                  {{ g.name }}
                </option>
              </select>

              <select v-model="statsMonth">
                <option v-for="m in months" :key="m.value" :value="m.value">
                  {{ m.label }}
                </option>
              </select>

              <select v-model="statsYear">
                <option v-for="y in years" :key="y" :value="String(y)">
                  {{ y }}
                </option>
              </select>
              <button class="export-btn" @click="exportAttendanceStats">
                Экспорт в xlsx
              </button>
            </div>
          </div>

          <div class="training-layout">

            <!-- Нет тренировочного плана -->
            <div class="training-card">
              <div class="card-header-with-button">
                <h4>Нет тренировочного плана</h4>
                <button v-if="coachesWithoutPlans.length" class="notify-all-btn" @click="notifyAllCoaches"
                  :disabled="notifyingAll">
                  <span v-if="notifyingAll">⏳ Отправка уведомлений...</span>
                  <span v-else>📧 Уведомить всех ({{ coachesWithoutPlans.length }})</span>
                </button>
              </div>

              <div v-if="coachesWithoutPlans.length">
                <div v-for="coach in coachesWithoutPlans" :key="coach.id" class="warning-item">
                  <div class="warning-item-content">
                    <span class="coach-name">{{ coach.user.last_name }} {{ coach.user.first_name }}</span>
                    <span class="coach-department">{{ coach.department?.name || 'Без отделения' }}</span>
                  </div>
                </div>
              </div>

              <div v-else class="empty">
                Все тренеры сформировали планы
              </div>
            </div>
            <!-- Посещаемость -->
            <div class="training-card attendance-card">
              <h4>Посещаемость</h4>

              <div class="attendance-summary">
                <div class="attendance-circle">
                  {{ averageAttendance }}%
                </div>
              </div>

              <div class="table-container">
                <table class="data-table hoverable">
                  <thead>
                    <tr>
                      <th>Спортсмен</th>
                      <th>Группа</th>
                      <th>Посещаемость</th>
                    </tr>
                  </thead>

                  <tbody>
                    <tr v-for="row in attendanceStats" :key="row.id">
                      <td>{{ row.athlete }}</td>
                      <td>{{ row.group }}</td>
                      <td>{{ row.percent }}%</td>
                    </tr>

                    <tr v-if="!attendanceStats.length">
                      <td colspan="3" class="empty">
                        Нет данных
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import axios from '../../axios'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

export default {
  name: 'MethodistStats',

  data() {
    const today = new Date()

    return {
      notifyingCoachId: null,  // Для отслеживания отправки одному тренеру
    notifyingAll: false ,
      statsMonth: String(today.getMonth() + 1),
      statsYear: String(today.getFullYear()),
      statsQuarter: String(
        Math.floor(today.getMonth() / 3) + 1
      ),

      competitions: [],
      trainingPlans: [],
      attendance: [],
      departments: [],
      coaches: [],
      groups: [],

      activeTab: 'month',

      trainingFilters: {
        department: '',
        coach: '',
        group: ''
      },
       
    }
  },

  // =========================
  // WATCH
  // =========================
  watch: {

    // При смене отделения
    'trainingFilters.department'() {

      // сброс тренера
      this.trainingFilters.coach = ''

      // сброс группы
      this.trainingFilters.group = ''
    },

    // При смене тренера
    'trainingFilters.coach'() {

      // сброс группы
      this.trainingFilters.group = ''
    }
  },

  computed: {

    // =========================
    // Фильтрация тренеров
    // =========================
    filteredCoaches() {

      // если отделение не выбрано
      if (!this.trainingFilters.department) {
        return this.coaches
      }

      // только тренеры выбранного отделения
      return this.coaches.filter(
        coach =>
          coach.department?.id ==
          this.trainingFilters.department
      )
    },

    // =========================
    // Фильтрация групп
    // =========================
    filteredGroups() {

      let groups = this.groups

      // фильтр по отделению
      if (this.trainingFilters.department) {

        groups = groups.filter(
          group =>
            group.department?.id ==
            this.trainingFilters.department
        )
      }

      // фильтр по тренеру
      if (this.trainingFilters.coach) {

        groups = groups.filter(
          group =>
            group.coach?.id ==
            this.trainingFilters.coach
        )
      }

      return groups
    },

    // =========================
    // Планы тренировок
    // =========================
    filteredTrainingPlans() {

      return this.trainingPlans.filter(plan => {

        const d = new Date(plan.date)

        const monthOk =
          d.getMonth() === Number(this.statsMonth) - 1

        const yearOk =
          d.getFullYear() === Number(this.statsYear)

        const departmentOk =
          !this.trainingFilters.department ||
          plan.group?.department?.id ==
          this.trainingFilters.department

        const coachOk =
          !this.trainingFilters.coach ||
          plan.group?.coach?.id ==
          this.trainingFilters.coach

        const groupOk =
          !this.trainingFilters.group ||
          plan.group?.id ==
          this.trainingFilters.group

        return (
          monthOk &&
          yearOk &&
          departmentOk &&
          coachOk &&
          groupOk
        )
      })
    },

    // =========================
    // Тренеры без планов
    // =========================
    coachesWithoutPlans() {

      return this.filteredCoaches.filter(coach => {

        const hasPlan =
          this.filteredTrainingPlans.some(
            p => p.group?.coach?.id === coach.id
          )

        return !hasPlan
      })
    },

    // =========================
    // Посещаемость
    // =========================
    attendanceStats() {

      const stats = {}

      this.attendance.forEach(a => {

        const plan = a.training_plan

        if (!plan) return

        const d = new Date(plan.date)

        // месяц / год
        if (
          d.getMonth() !== Number(this.statsMonth) - 1 ||
          d.getFullYear() !== Number(this.statsYear)
        ) {
          return
        }

        // отделение
        if (
          this.trainingFilters.department &&
          plan.group?.department?.id !=
          this.trainingFilters.department
        ) {
          return
        }

        // тренер
        if (
          this.trainingFilters.coach &&
          plan.group?.coach?.id !=
          this.trainingFilters.coach
        ) {
          return
        }

        // группа
        if (
          this.trainingFilters.group &&
          plan.group?.id !=
          this.trainingFilters.group
        ) {
          return
        }

        const athlete = a.athlete

        if (!athlete) return

        const athleteId = athlete.id

        if (!stats[athleteId]) {

          stats[athleteId] = {
            id: athleteId,

            athlete:
              `${athlete.last_name} ${athlete.first_name}`,

            group:
              athlete.group?.name || '—',

            total: 0,
            present: 0
          }
        }

        stats[athleteId].total += 1

        if (a.status === 'present') {
          stats[athleteId].present += 1
        }
      })

      return Object.values(stats).map(s => ({
        ...s,

        percent: s.total
          ? Math.round(
            (s.present / s.total) * 100
          )
          : 0
      }))
    },

    // =========================
    // Средняя посещаемость
    // =========================
    averageAttendance() {

      if (!this.attendanceStats.length) {
        return 0
      }

      const total =
        this.attendanceStats.reduce(
          (sum, row) => sum + row.percent,
          0
        )

      return Math.round(
        total / this.attendanceStats.length
      )
    },

    // =========================
    // Группировка месячной статистики
    // =========================
    groupedMonthlyStats() {

      const groups = {}

      this.monthlyStats.forEach(row => {

        if (!groups[row.department]) {
          groups[row.department] = []
        }

        groups[row.department].push(row)
      })

      return Object.entries(groups).map(
        ([department, rows]) => ({
          department,
          rows
        })
      )
    },

    // =========================
    // Месяцы
    // =========================
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
    quarters() {

      return [
        { value: '1', label: '1 квартал' },
        { value: '2', label: '2 квартал' },
        { value: '3', label: '3 квартал' },
        { value: '4', label: '4 квартал' }
      ]
    },

    // =========================
    // Года
    // =========================
    years() {

      const current =
        new Date().getFullYear()

      return [
        current - 1,
        current,
        current + 1
      ]
    },

    // =========================
    // Название месяца
    // =========================
    monthLabel() {

      const date = new Date(
        Number(this.statsYear),
        Number(this.statsMonth) - 1,
        1
      )

      return date.toLocaleDateString(
        'ru-RU',
        {
          month: 'long',
          year: 'numeric'
        }
      )
    },

    // =========================
    // Название квартала
    // =========================
    quarterLabel() {

      return `${this.statsQuarter}-й квартал ${this.statsYear}`
    },

    // =========================
    // Утвержденные отчеты
    // =========================
    approvedReports() {

      return this.competitions.filter(
        c => c.status === 'approved'
      )
    },

    // =========================
    // Месячная статистика
    // =========================
    monthlyStats() {

      const m =
        Number(this.statsMonth) - 1

      const y =
        Number(this.statsYear)

      return this.approvedReports
        .filter(c => {

          const d = new Date(c.date)

          return (
            d.getMonth() === m &&
            d.getFullYear() === y
          )
        })
        .map(c => {

          const participants =
            (c.results || []).length

          const prizePlaces =
            (c.results || []).filter(
              r =>
                !r.is_participant &&
                r.place
            ).length

          return {
            id: c.id,
            name: c.name,
            date: c.date,
            location: c.location,
            level: c.level,

            department:
              c.coach?.department?.name || '—',

            coach: c.coach?.user
              ? `${c.coach.user.last_name} ${c.coach.user.first_name}`
              : '—',

            participants,
            prizePlaces
          }
        })
    },

    // =========================
    // Квартальная статистика
    // =========================
    quarterlyStats() {

      const y =
        Number(this.statsYear)

      // выбранный квартал
      const q =
        Number(this.statsQuarter) - 1

      const approved =
        this.approvedReports.filter(c => {

          const d = new Date(c.date)

          return (
            d.getFullYear() === y &&
            Math.floor(
              d.getMonth() / 3
            ) === q
          )
        })

      const grouped = {}

      approved.forEach(c => {

        const dept =
          c.coach?.department?.name || '—'

        const key =
          `${dept}|${c.level}`

        const results =
          c.results || []

        const participants =
          results.length

        const prize =
          results.filter(
            r =>
              !r.is_participant &&
              r.place
          ).length

        if (!grouped[key]) {

          grouped[key] = {
            department: dept,
            level: c.level,
            events: 0,
            participants: 0,
            prizePlaces: 0,
            key
          }
        }

        grouped[key].events += 1
        grouped[key].participants += participants
        grouped[key].prizePlaces += prize
      })

      return Object.values(grouped)
    },
  },

  async mounted() {
    await this.loadData()
  },

  methods: {
    async notifyAllCoaches() {
    if (!this.coachesWithoutPlans.length) {
      this.showNotification('Нет тренеров для уведомления', 'info');
      return;
    }
    
    // Подтверждение перед отправкой
    const confirm = window.confirm(
      `Вы собираетесь отправить напоминание ${this.coachesWithoutPlans.length} тренерам.\n\n` +
      `Тренеры без плана:\n${this.coachesWithoutPlans.map(c => `- ${c.user.last_name} ${c.user.first_name}`).join('\n')}\n\n` +
      `Продолжить?`
    );
    
    if (!confirm) return;
    
    this.notifyingAll = true;
    
    try {
      const response = await axios.post('/api/coach-notifications/notify-all-training-plan/', {
        month: this.statsMonth,
        year: this.statsYear,
        department_id: this.trainingFilters.department || null,
        coach_ids: this.coachesWithoutPlans.map(c => c.id)  // Отправляем только тем, у кого нет плана
      });
      
      const { sent, total, failed_coaches, message } = response.data;
      
      if (sent === total) {
        this.showNotification(`✅ Успешно отправлено ${sent} из ${total} уведомлений`, 'success');
      } else {
        this.showNotification(
          `⚠️ Отправлено ${sent} из ${total}.\nНе удалось: ${failed_coaches.join(', ')}`,
          'error'
        );
      }
      
    } catch (error) {
      console.error('Ошибка массовой отправки:', error);
      const errorMsg = error.response?.data?.error || 'Не удалось отправить уведомления';
      this.showNotification(errorMsg, 'error');
      
    } finally {
      this.notifyingAll = false;
    }
  },
  
  showNotification(message, type = 'info') {
    // Создаем и показываем уведомление
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
      <span class="notification-icon">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
      <span class="notification-message">${message}</span>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease-out';
      setTimeout(() => notification.remove(), 300);
    }, 4000);
  },

    // =========================
    // Загрузка данных
    // =========================
    async loadData() {

      try {

        const [
          competitionsRes,
          plansRes,
          attendanceRes,
          departmentsRes,
          coachesRes,
          groupsRes
        ] = await Promise.all([

          axios.get('/api/competitions/'),
          axios.get('/api/training-plans/'),
          axios.get('/api/attendance/'),
          axios.get('/api/departments/'),
          axios.get('/api/coaches/'),
          axios.get('/api/groups/')
        ])

        this.competitions =
          competitionsRes.data

        this.trainingPlans =
          plansRes.data

        this.attendance =
          attendanceRes.data

        this.departments =
          departmentsRes.data

        this.coaches =
          coachesRes.data

        this.groups =
          groupsRes.data

      } catch (err) {

        console.error(err)
      }
    },

    // =========================
    // Формат даты
    // =========================
    formatDate(date) {

      return date
        ? new Date(date)
          .toLocaleDateString('ru-RU')
        : '-'
    },
    exportMonthlyStats() {

      if (!this.monthlyStats.length) return

      const monthName =
        this.months.find(
          m => m.value == this.statsMonth
        )?.label || ''

      const rows = [

        // Заголовок
        ['МЕСЯЧНАЯ СТАТИСТИКА'],
        [`Период: ${monthName} ${this.statsYear}`],
        [],

        // Шапка таблицы
        [
          'Отделение',
          'Соревнование',
          'Дата',
          'Место',
          'Уровень',
          'Участников',
          'Призовых мест',
          'Тренер'
        ]
      ]

      // Данные
      this.monthlyStats.forEach(row => {

        rows.push([
          row.department,
          row.name,
          this.formatDate(row.date),
          row.location,
          row.level,
          row.participants,
          row.prizePlaces,
          row.coach
        ])
      })

      // Итоги
      rows.push([])

      rows.push([
        'ИТОГО',
        '',
        '',
        '',
        '',
        this.monthlyStats.reduce(
          (a, b) => a + b.participants,
          0
        ),
        this.monthlyStats.reduce(
          (a, b) => a + b.prizePlaces,
          0
        ),
        ''
      ])

      const ws =
        XLSX.utils.aoa_to_sheet(rows)

      const wb =
        XLSX.utils.book_new()

      XLSX.utils.book_append_sheet(
        wb,
        ws,
        'Месячная статистика'
      )

      const file =
        XLSX.write(wb, {
          bookType: 'xlsx',
          type: 'array'
        })

      saveAs(
        new Blob([file], {
          type:
            'application/octet-stream'
        }),
        `Месячная_статистика_${monthName}_${this.statsYear}.xlsx`
      )
    },

    // =========================
    // Экспорт квартальной статистики
    // =========================
    exportQuarterlyStats() {

      if (!this.quarterlyStats.length) return

      const rows = [

        // Заголовок
        ['КВАРТАЛЬНАЯ СТАТИСТИКА'],
        [
          `Период: ${this.statsQuarter}-й квартал ${this.statsYear}`
        ],
        [],

        // Шапка
        [
          'Отделение',
          'Уровень',
          'Соревнований',
          'Участников',
          'Призовых мест'
        ]
      ]

      // Данные
      this.quarterlyStats.forEach(row => {

        rows.push([
          row.department,
          row.level,
          row.events,
          row.participants,
          row.prizePlaces
        ])
      })

      // Итоги
      rows.push([])

      rows.push([
        'ИТОГО',
        '',
        this.quarterlyStats.reduce(
          (a, b) => a + b.events,
          0
        ),
        this.quarterlyStats.reduce(
          (a, b) => a + b.participants,
          0
        ),
        this.quarterlyStats.reduce(
          (a, b) => a + b.prizePlaces,
          0
        )
      ])

      const ws =
        XLSX.utils.aoa_to_sheet(rows)

      const wb =
        XLSX.utils.book_new()

      XLSX.utils.book_append_sheet(
        wb,
        ws,
        'Квартальная статистика'
      )

      const file =
        XLSX.write(wb, {
          bookType: 'xlsx',
          type: 'array'
        })

      saveAs(
        new Blob([file], {
          type:
            'application/octet-stream'
        }),
        `Квартальная_статистика_${this.statsQuarter}_квартал_${this.statsYear}.xlsx`
      )
    },
    exportAttendanceStats() {
      if (!this.attendanceStats.length) return

      const workbook = XLSX.utils.book_new()

      // группировка по отделениям
      const groupedByDepartment = {}

      this.attendance.forEach(a => {
        const plan = a.training_plan
        if (!plan) return

        const dept = plan.group?.department?.name || 'Без отделения'

        // фильтры
        const d = new Date(plan.date)

        if (
          d.getMonth() !== Number(this.statsMonth) - 1 ||
          d.getFullYear() !== Number(this.statsYear)
        ) return

        if (
          this.trainingFilters.department &&
          plan.group?.department?.id != this.trainingFilters.department
        ) return

        if (
          this.trainingFilters.coach &&
          plan.group?.coach?.id != this.trainingFilters.coach
        ) return

        if (
          this.trainingFilters.group &&
          plan.group?.id != this.trainingFilters.group
        ) return

        const athlete = a.athlete
        if (!athlete) return

        if (!groupedByDepartment[dept]) {
          groupedByDepartment[dept] = {}
        }

        const id = athlete.id

        if (!groupedByDepartment[dept][id]) {
          groupedByDepartment[dept][id] = {
            athlete: `${athlete.last_name} ${athlete.first_name}`,
            group: athlete.group?.name || '—',
            coach: plan.group?.coach?.user
              ? `${plan.group.coach.user.last_name} ${plan.group.coach.user.first_name}`
              : '—',
            total: 0,
            present: 0
          }
        }

        groupedByDepartment[dept][id].total++

        if (a.status === 'present') {
          groupedByDepartment[dept][id].present++
        }
      })

      // создание листов
      Object.entries(groupedByDepartment).forEach(([dept, data]) => {
        const rows = [
          [`Отделение: ${dept}`],
          [],
          ['Спортсмен', 'Группа', 'Тренер', 'Посещения', 'Посещаемость %']
        ]

        Object.values(data).forEach(r => {
          const percent = r.total
            ? Math.round((r.present / r.total) * 100)
            : 0

          rows.push([
            r.athlete,
            r.group,
            r.coach,
            r.total,
            percent
          ])
        })

        const ws = XLSX.utils.aoa_to_sheet(rows)
        XLSX.utils.book_append_sheet(workbook, ws, dept.slice(0, 30))
      })

      const file = XLSX.write(workbook, {
        bookType: 'xlsx',
        type: 'array'
      })

      saveAs(
        new Blob([file], { type: 'application/octet-stream' }),
        `Посещаемость_${this.statsYear}_${this.statsMonth}.xlsx`
      )
    },
  }
}
</script>

<style scoped>
.training-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 16px;
  margin-top: 16px;
}

.training-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.training-card h4 {
  margin-bottom: 14px;
  color: #1f2937;
}

.warning-item {
  padding: 10px;
  border-radius: 8px;
  background: #fef2f2;
  color: #b91c1c;
  margin-bottom: 8px;
  font-weight: 500;
}

.attendance-card {
  min-height: 400px;
}

.attendance-summary {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.attendance-circle {
  width: 130px;
  height: 130px;
  border-radius: 50%;
  border: 12px solid #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  background: #eff6ff;
}

.filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

@media (max-width: 1024px) {
  .training-layout {
    grid-template-columns: 1fr;
  }
}


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

.inline-actions {
  display: flex;
  flex-direction: row;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
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

.export-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 10px;
  background: #27ae60;
  color: white;

  font-weight: 600;
  cursor: pointer;
  transition: .2s;
}

.export-btn:hover {
  opacity: .9;
}

.export-btn:disabled {
  opacity: .5;
  cursor: not-allowed;
}

.card-header-with-button {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header-with-button h4 {
  margin: 0;
}

.notify-all-btn {
  background: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.notify-all-btn:hover:not(:disabled) {
  background: #218838;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.notify-all-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.7;
}

.warning-item {
  margin-bottom: 8px;
}

.warning-item-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #fff3cd;
  border-radius: 8px;
}

.coach-name {
  font-weight: 500;
  color: #856404;
}

.coach-department {
  font-size: 12px;
  color: #856404;
  opacity: 0.8;
}

.notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 9999;
  animation: slideIn 0.3s ease-out;
}

.notification.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.notification.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.notification.info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
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
</style>
