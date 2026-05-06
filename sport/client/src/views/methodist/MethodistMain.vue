<template>
  <div class="reports-page">
    <!-- Шапка с приветствием (можно оставить пустой или добавить позже) -->
    <header class="page-header"></header>

    <!-- Компактные карточки-сводки в стиле "stat-pills" -->
    <div class="stats-pills" style="margin-bottom: 24px;">
      <div class="stat-pill pending" @click="setStatusFilter('submitted')"
        :class="{ active: statusFilter === 'submitted' }">
        <span class="stat-value">{{ pendingCount }}</span>
        <span class="stat-label">На проверке</span>
      </div>
      <div class="stat-pill returned" @click="setStatusFilter('returned')"
        :class="{ active: statusFilter === 'returned' }">
        <span class="stat-value">{{ returnedCount }}</span>
        <span class="stat-label">Доработка</span>
      </div>
      <div class="stat-pill approved" @click="setStatusFilter('approved')"
        :class="{ active: statusFilter === 'approved' }">
        <span class="stat-value">{{ approvedCount }}</span>
        <span class="stat-label">Утверждено</span>
      </div>
      <div class="stat-pill total" @click="setStatusFilter('all')" :class="{ active: statusFilter === 'all' }">
        <span class="stat-value">{{ totalReports }}</span>
        <span class="stat-label">Все отчеты</span>
      </div>
    </div>

    <!-- Основной макет в две колонки, как в "Мои отчеты" -->
    <div class="reports-layout">
      <!-- Левая колонка: список отчетов -->
      <div class="reports-sidebar">
        <div class="sidebar-header">
          <h3>Отчеты тренеров</h3>
          <button class="icon-btn refresh" @click="loadData" :disabled="loading" title="Обновить">
            🔄
          </button>
        </div>

        <!-- ФИЛЬТРЫ -->
        <div class="reports-filters">
          <!-- Поиск по всем полям -->
          <div class="search-box" style="margin-bottom: 12px;">
            <input type="text" v-model="searchQuery" placeholder="Поиск по названию, тренеру, месту..." />
          </div>

          <!-- Фильтр по статусу (компактные табы) -->
          <div class="filter-tabs" style="margin-bottom: 12px;">
            <button class="filter-tab" :class="{ active: statusFilter === 'all' }" @click="statusFilter = 'all'">
              Все
            </button>
            <button class="filter-tab" :class="{ active: statusFilter === 'submitted' }"
              @click="statusFilter = 'submitted'">
              На проверке
            </button>
            <button class="filter-tab" :class="{ active: statusFilter === 'returned' }"
              @click="statusFilter = 'returned'">
              Доработка
            </button>
            <button class="filter-tab" :class="{ active: statusFilter === 'approved' }"
              @click="statusFilter = 'approved'">
              Утвержденные
            </button>
          </div>

          <!-- Фильтры по отделению, тренеру и месяцу -->
          <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px;">
            <!-- Фильтр по отделению -->
            <select v-model="departmentFilter" class="filter-select">
              <option value="">Все отделения</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept.name">
                {{ dept.name }}
              </option>
            </select>

            <!-- Фильтр по тренеру -->
            <select v-model="coachFilter" class="filter-select">
              <option value="">Все тренеры</option>
              <option v-for="coach in uniqueCoaches" :key="coach.id" :value="coach.id">
                {{ coach.name }}
              </option>
            </select>

            <!-- Фильтр по месяцу -->
            <select v-model="monthFilter" class="filter-select">
              <option value="">Все месяцы</option>
              <option v-for="(monthName, monthIndex) in months" :key="monthIndex" :value="monthIndex">
                {{ monthName }}
              </option>
            </select>

            <!-- Кнопка сброса фильтров -->
            <button v-if="hasActiveFilters" class="link-icon small" @click="resetFilters" style="margin-left: auto;">
              ✕ Сбросить фильтры
            </button>
          </div>

          <!-- Информация о количестве отфильтрованных отчетов -->
          <div class="filter-info" v-if="filteredReports.length !== competitions.length">
            Показано {{ filteredReports.length }} из {{ competitions.length }} отчетов
          </div>
        </div>

        <!-- Контейнер с отчетами -->
        <div class="reports-list" style="max-height: 60vh;">
          <div v-if="loading" class="loading-reports">
            <div class="spinner"></div>
            <p>Загрузка отчетов...</p>
          </div>

          <div v-else-if="filteredReports.length === 0" class="empty-reports">
            <p>Отчеты не найдены</p>
            <p class="hint" v-if="hasActiveFilters">Попробуйте изменить параметры фильтрации</p>
          </div>

          <div v-else>
            <!-- Группировка отчетов по статусу (если фильтр не выбран) -->
            <template v-if="statusFilter === 'all'">
              <!-- Секция: На проверке -->
              <div v-if="groupedReports.submitted.length" class="filter-tabs"
                style="margin: 12px 0 4px; background: transparent; padding: 0;">
                <span class="filter-tab" style="flex: none; background: #dbeafe; color: #1e40af;">
                  На проверке ({{ groupedReports.submitted.length }})
                </span>
              </div>
              <div v-for="report in groupedReports.submitted" :key="report.id" class="report-card submitted"
                :class="{ active: selectedReport?.id === report.id }" @click="selectReport(report)">
                <div class="report-card-header">
                  <div class="report-title">
                    <h4>{{ report.name }}</h4>
                    <span class="report-date">{{ formatDate(report.date) }} • {{ report.location }}</span>
                  </div>
                  <span class="status-badge submitted">На проверке</span>
                </div>
                <div class="report-card-body">
                  <div class="report-meta">
                    <span class="meta-item">{{ report.location }}</span>
                    <span class="meta-item">{{ report.level }}</span>
                    <span class="meta-item">Тренер: {{ coachName(report.coach) }}</span>
                    <span v-if="report.coach?.department" class="meta-item">{{ report.coach.department.name }}</span>
                  </div>
                  <div v-if="report.review_comment" class="review-comment">
                    <span class="comment-text">{{ report.review_comment }}</span>
                  </div>
                </div>
                <div v-if="report.protocol" class="report-card-footer">
                  <button class="link-icon" @click.stop="downloadProtocol(report)">
                    📎 Протокол
                  </button>
                </div>
              </div>

              <!-- Секция: На доработке -->
              <div v-if="groupedReports.returned.length" class="filter-tabs"
                style="margin: 16px 0 4px; background: transparent; padding: 0;">
                <span class="filter-tab" style="flex: none; background: #fee2e2; color: #991b1b;">
                  На доработке ({{ groupedReports.returned.length }})
                </span>
              </div>
              <div v-for="report in groupedReports.returned" :key="report.id" class="report-card returned"
                :class="{ active: selectedReport?.id === report.id }" @click="selectReport(report)">
                <div class="report-card-header">
                  <div class="report-title">
                    <h4>{{ report.name }}</h4>
                    <span class="report-date">{{ formatDate(report.date) }} • {{ report.location }}</span>
                  </div>
                  <span class="status-badge returned">Доработка</span>
                </div>
                <div class="report-card-body">
                  <div class="report-meta">
                    <span class="meta-item">{{ report.location }}</span>
                    <span class="meta-item">{{ report.level }}</span>
                    <span class="meta-item">Тренер: {{ coachName(report.coach) }}</span>
                    <span v-if="report.coach?.department" class="meta-item">{{ report.coach.department.name }}</span>
                  </div>
                  <div v-if="report.review_comment" class="review-comment">
                    <span class="comment-text">{{ report.review_comment }}</span>
                  </div>
                </div>
                <div v-if="report.protocol" class="report-card-footer">
                  <button class="link-icon" @click.stop="downloadProtocol(report)">
                    Протокол
                  </button>
                </div>
              </div>

              <!-- Секция: Утвержденные -->
              <div v-if="groupedReports.approved.length" class="filter-tabs"
                style="margin: 16px 0 4px; background: transparent; padding: 0;">
                <span class="filter-tab" style="flex: none; background: #d1fae5; color: #065f46;">
                  Утвержденные ({{ groupedReports.approved.length }})
                </span>
              </div>
              <div v-for="report in groupedReports.approved" :key="report.id" class="report-card approved"
                :class="{ active: selectedReport?.id === report.id }" @click="selectReport(report)">
                <div class="report-card-header">
                  <div class="report-title">
                    <h4>{{ report.name }}</h4>
                    <span class="report-date">{{ formatDate(report.date) }} • {{ report.location }}</span>
                  </div>
                  <span class="status-badge approved">Утверждено</span>
                </div>
                <div class="report-card-body">
                  <div class="report-meta">
                    <span class="meta-item">{{ report.location }}</span>
                    <span class="meta-item">{{ report.level }}</span>
                    <span class="meta-item">Тренер: {{ coachName(report.coach) }}</span>
                    <span v-if="report.coach?.department" class="meta-item">{{ report.coach.department.name }}</span>
                  </div>
                  <div v-if="report.review_comment" class="review-comment">
                    <span class="comment-text">{{ report.review_comment }}</span>
                  </div>
                </div>
                <div v-if="report.protocol" class="report-card-footer">
                  <button class="link-icon" @click.stop="downloadProtocol(report)">
                    Протокол
                  </button>
                </div>
              </div>
            </template>

            <!-- Если выбран конкретный статус, показываем без группировки -->
            <template v-else>
              <div v-for="report in filteredReports" :key="report.id"
                :class="['report-card', report.status, { active: selectedReport?.id === report.id }]"
                @click="selectReport(report)">
                <div class="report-card-header">
                  <div class="report-title">
                    <h4>{{ report.name }}</h4>
                    <span class="report-date">{{ formatDate(report.date) }} • {{ report.location }}</span>
                  </div>
                  <span class="status-badge" :class="report.status">
                    {{ statusLabel(report.status) }}
                  </span>
                </div>
                <div class="report-card-body">
                  <div class="report-meta">
                    <span class="meta-item">{{ report.location }}</span>
                    <span class="meta-item">{{ report.level }}</span>
                    <span class="meta-item">Тренер: {{ coachName(report.coach) }}</span>
                    <span v-if="report.coach?.department" class="meta-item">{{ report.coach.department.name }}</span>
                  </div>
                  <div v-if="report.review_comment" class="review-comment">
                    <span class="comment-text">{{ report.review_comment }}</span>
                  </div>
                </div>
                <div v-if="report.protocol" class="report-card-footer">
                  <button class="link-icon" @click.stop="downloadProtocol(report)">
                    Протокол
                  </button>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- Правая колонка: детали отчета -->
      <div v-if="selectedReport" class="report-details-panel">
        <div class="details-header">
          <h3>Детали отчета</h3>
          <div class="details-actions">
            <!-- Кнопка скачивания протокола в правой панели -->
            <button v-if="selectedReport.protocol" class="action outline small"
              @click="downloadProtocol(selectedReport)">
              Скачать протокол
            </button>
            <span class="status-badge" :class="selectedReport.status">
              {{ statusLabel(selectedReport.status) }}
            </span>
          </div>
        </div>

        <div class="details-content">
          <div class="details-section">
            <h4>Информация о соревновании</h4>
            <div class="details-grid">
              <div class="detail-item">
                <span class="detail-label">Название</span>
                <span class="detail-value">{{ selectedReport.name }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Дата проведения</span>
                <span class="detail-value">{{ formatDate(selectedReport.date) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Место проведения</span>
                <span class="detail-value">{{ selectedReport.location }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Уровень</span>
                <span class="detail-value">{{ selectedReport.level }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Тренер</span>
                <span class="detail-value">{{ coachName(selectedReport.coach) }}</span>
              </div>
              <div class="detail-item" v-if="selectedReport.coach?.department">
                <span class="detail-label">Отделение</span>
                <span class="detail-value">{{ selectedReport.coach.department.name }}</span>
              </div>
            </div>
          </div>

          <div class="details-section">
            <h4>Участники соревнования</h4>
            <div class="participants-table-container">
              <table class="participants-table">
                <thead>
                  <tr>
                    <th>№</th>
                    <th>Спортсмен</th>
                    <th>Вес</th>
                    <th>Результат</th>
                    <th>Разряд</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(res, idx) in selectedReport.results || []" :key="res.id">
                    <td>{{ idx + 1 }}</td>
                    <td><strong>{{ athleteName(res.athlete) }}</strong></td>
                    <td>{{ res.weight_category || '—' }}</td>
                    <td>
                      <span v-if="res.is_participant" class="result-badge participant">Участник</span>
                      <span v-else-if="res.place" class="result-badge place">
                        {{ getPlaceEmoji(res.place) }} {{ res.place }} место
                      </span>
                      <span v-else>—</span>
                    </td>
                    <td>
                      <span class="rank-badge">
                        {{ res.athlete?.last_rank || '—' }}
                      </span>
                    </td>
                  </tr>
                  <tr v-if="!(selectedReport.results || []).length">
                    <td colspan="5" class="empty">Нет участников</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Блок комментария -->
          <div class="details-section">
            <h4>Комментарий методиста</h4>
            <div class="form-field">
              <textarea v-model="reviewComment" rows="4"
                placeholder="Если есть замечания, оставьте комментарий..."></textarea>
            </div>
          </div>

          <!-- Кнопки действий -->
          <div class="form-actions" style="margin-top: 24px;">
            <div class="actions-right" style="width: 100%; justify-content: flex-end;">
              <button class="action outline" @click="returnReport(selectedReport)" :disabled="loading">
                Отправить на доработку
              </button>
              <button class="action primary large" @click="approveReport(selectedReport)" :disabled="loading">
                Утвердить отчет
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Пустое состояние -->
      <div v-else class="report-details-panel empty">
        <div class="empty-details">
          <h3>Выберите отчет</h3>
          <p>Нажмите на отчет из списка, чтобы просмотреть детали</p>
        </div>
      </div>
    </div>

    <!-- Модальное окно просмотра протокола (оставлено для обратной совместимости) -->
    <div v-if="showProtocolModal" class="modal-overlay" @click.self="showProtocolModal = false">
      <div class="modal-content protocol-modal">
        <div class="modal-header">
          <h3>Просмотр протокола</h3>
          <button class="icon-btn close" @click="showProtocolModal = false">✕</button>
        </div>
        <div class="modal-body">
          <iframe v-if="protocolUrl" :src="protocolUrl" class="protocol-viewer" frameborder="0"></iframe>
          <div v-else class="protocol-placeholder">
            <p>Не удалось загрузить протокол</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Уведомления -->
    <div v-if="notification.show" :class="['notification', notification.type]">
      <span class="notification-icon">
        {{ notification.type === 'success' ? '✅' : notification.type === 'error' ? '❌' : 'ℹ️' }}
      </span>
      <span class="notification-message">{{ notification.message }}</span>
    </div>
  </div>
</template>

<script>
import axios from '../../axios'

export default {
  name: 'MethodistMain',

  data() {
    return {
      loading: false,
      currentUser: null,
      competitions: [],
      selectedReport: null,
      reviewComment: '',
      showProtocolModal: false,
      protocolUrl: null,
      notification: { show: false, message: '', type: 'info' },

      // Фильтры
      searchQuery: '',
      statusFilter: 'all', // all, submitted, returned, approved
      departmentFilter: '',
      coachFilter: '',
      monthFilter: '',

      // Справочники
      months: [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
      ]
    }
  },

  computed: {
    // Все отчеты по статусам (без фильтров)
    pendingReports() {
      return this.competitions.filter(c => c.status === 'submitted')
    },
    approvedReports() {
      return this.competitions.filter(c => c.status === 'approved')
    },
    returnedReports() {
      return this.competitions.filter(c => c.status === 'returned')
    },

    // Счетчики
    pendingCount() {
      return this.pendingReports.length
    },
    returnedCount() {
      return this.returnedReports.length
    },
    approvedCount() {
      return this.approvedReports.length
    },
    totalReports() {
      return this.competitions.length
    },

    // Уникальные значения для фильтров
    departments() {
      const map = new Map()

      this.competitions.forEach(comp => {
        const dept = comp.coach?.department
        if (dept && !map.has(dept.id)) {
          map.set(dept.id, dept)
        }
      })

      return Array.from(map.values()).sort((a, b) =>
        a.name.localeCompare(b.name)
      )
    },

    uniqueCoaches() {
      const coachesMap = new Map()
      this.competitions.forEach(comp => {
        if (comp.coach?.id && !coachesMap.has(comp.coach.id)) {
          coachesMap.set(comp.coach.id, {
            id: comp.coach.id,
            name: this.coachName(comp.coach)
          })
        }
      })
      return Array.from(coachesMap.values()).sort((a, b) => a.name.localeCompare(b.name))
    },

    // Отфильтрованные отчеты
    filteredReports() {
      return this.competitions.filter(report => {
        // Фильтр по статусу
        if (this.statusFilter !== 'all' && report.status !== this.statusFilter) {
          return false
        }

        // Фильтр по отделению
        if (this.departmentFilter && report.coach?.department?.name !== this.departmentFilter) {
          return false
        }

        // Фильтр по тренеру
        if (this.coachFilter && report.coach?.id !== parseInt(this.coachFilter)) {
          return false
        }

        // Фильтр по месяцу
        if (this.monthFilter !== '') {
          const reportMonth = new Date(report.date).getMonth()
          if (reportMonth !== parseInt(this.monthFilter)) {
            return false
          }
        }

        // Поиск по тексту
        if (this.searchQuery) {
          const query = this.searchQuery.toLowerCase()
          const searchableFields = [
            report.name,
            report.location,
            report.level,
            this.coachName(report.coach),
            report.coach?.department?.name,
            report.review_comment
          ].filter(Boolean).map(f => f.toLowerCase())

          const matches = searchableFields.some(field => field.includes(query))
          if (!matches) return false
        }

        return true
      })
    },

    // Отчеты, сгруппированные по статусу (для отображения)
    groupedReports() {
      return {
        submitted: this.filteredReports.filter(r => r.status === 'submitted'),
        returned: this.filteredReports.filter(r => r.status === 'returned'),
        approved: this.filteredReports.filter(r => r.status === 'approved'),
        draft: this.filteredReports.filter(r => r.status === 'draft')
      }
    },

    // Есть ли активные фильтры
    hasActiveFilters() {
      return this.searchQuery ||
        this.statusFilter !== 'all' ||
        this.departmentFilter ||
        this.coachFilter ||
        this.monthFilter !== ''
    }
  },

  watch: {
    // Сбрасываем выбранный отчет при изменении фильтров
    filteredReports(newVal) {
      if (this.selectedReport && !newVal.find(r => r.id === this.selectedReport.id)) {
        this.selectedReport = newVal[0] || null
        if (this.selectedReport) {
          this.reviewComment = this.selectedReport.review_comment || ''
        }
      }
    }
  },

  async mounted() {
    const raw = localStorage.getItem('user')
    if (raw) this.currentUser = JSON.parse(raw)
    await this.loadData()
  },

  methods: {
    async loadData() {
      this.loading = true
      try {
        const res = await axios.get('/api/competitions/')
        this.competitions = res.data
        if (this.competitions.length && !this.selectedReport) {
          this.selectedReport = this.competitions[0]
          this.reviewComment = this.selectedReport.review_comment || ''
        }
      } catch (err) {
        console.error(err)
        this.showNotification('Ошибка загрузки отчетов', 'error')
      } finally {
        this.loading = false
      }
    },

    selectReport(report) {
      this.selectedReport = report
      this.reviewComment = report.review_comment || ''
    },

    setStatusFilter(status) {
      this.statusFilter = status
    },

    resetFilters() {
      this.searchQuery = ''
      this.statusFilter = 'all'
      this.departmentFilter = ''
      this.coachFilter = ''
      this.monthFilter = ''
    },

    async approveReport(report) {
      await this.updateStatus(report, 'approved')
    },

    async returnReport(report) {
      if (!this.reviewComment.trim()) {
        this.showNotification('Добавьте комментарий для доработки', 'error')
        return
      }
      await this.updateStatus(report, 'returned')
    },

    async updateStatus(report, status) {
      try {
        await axios.patch(`/api/competitions/${report.id}/`, {
          status,
          review_comment: this.reviewComment
        })
        this.showNotification('Статус обновлен', 'success')
        await this.loadData()
      } catch (err) {
        console.error(err)
        this.showNotification('Не удалось обновить статус', 'error')
      }
    },

    async downloadProtocol(report) {
      if (!report.protocol) {
        this.showNotification('Протокол не прикреплен', 'error')
        return
      }

      try {
        // Новый endpoint для скачивания через API
        const downloadUrl = `/api/competitions/${report.id}/download-protocol/`

        const response = await axios.get(downloadUrl, { responseType: 'blob' })

        // Имя файла берём из заголовка или из пути
        let filename = report.protocol.split('/').pop()
        const contentDisposition = response.headers['content-disposition']
        if (contentDisposition) {
          const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
          if (match && match[1]) {
            filename = match[1].replace(/['"]/g, '')
          }
        }

        const url = window.URL.createObjectURL(response.data)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)

        this.showNotification('Протокол успешно скачан', 'success')
      } catch (error) {
        console.error('Ошибка скачивания протокола:', error)
        if (error.response && error.response.status === 404) {
          this.showNotification('Протокол не найден на сервере', 'error')
        } else {
          this.showNotification('Не удалось скачать протокол', 'error')
        }
      }
    },

    // Метод для просмотра протокола (оставлен для обратной совместимости)
    async viewProtocol(report) {
      if (!report.protocol) {
        this.showNotification('Протокол не прикреплен', 'error')
        return
      }
      this.protocolUrl = report.protocol
      this.showProtocolModal = true
    },

    coachName(coach) {
      if (!coach) return '—'
      const u = coach.user || coach
      return `${u.last_name || ''} ${u.first_name || ''}`.trim() || '-'
    },

    athleteName(athlete) {
      if (!athlete) return ''
      const u = athlete.user || athlete
      return `${u.last_name || ''} ${u.first_name || ''} ${u.middle_name || ''}`.trim()
    },

    formatDate(date) {
      if (!date) return '-'
      return new Date(date).toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      })
    },

    statusLabel(status) {
      const map = {
        draft: 'Черновик',
        submitted: 'На проверке',
        approved: 'Утверждено',
        returned: 'Доработка'
      }
      return map[status] || status
    },

    getPlaceEmoji(place) {
      const emoji = { 1: '🥇', 2: '🥈', 3: '🥉' }
      return emoji[place] || '🏅'
    },

    showNotification(message, type = 'info') {
      this.notification = { show: true, message, type }
      setTimeout(() => (this.notification.show = false), 3000)
    }
  }
}
</script>

<style scoped>
/* ================= ОСНОВНЫЕ СТИЛИ ================= */
.reports-page {
  min-height: 100vh;

  padding: 24px;
}

/* ================= СТАТИСТИКА (PILLS) ================= */
.stats-pills {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.stat-pill {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 16px;
  background: #f8fafc;
  border-radius: 40px;
  min-width: 80px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.stat-pill:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-pill.active {
  border-color: #3498db;
  background: #ebf5ff;
}

.stat-pill .stat-value {
  font-size: 20px;
  font-weight: 700;
  line-height: 1.2;
}

.stat-pill .stat-label {
  font-size: 11px;
  color: #6b7280;
}

.stat-pill.pending .stat-value {
  color: #3b82f6;
}

.stat-pill.returned .stat-value {
  color: #ef4444;
}

.stat-pill.approved .stat-value {
  color: #10b981;
}

.stat-pill.total .stat-value {
  color: #1f2937;
}

/* ================= МАКЕТ ДВУХ КОЛОНОК ================= */
.reports-layout {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 24px;
  align-items: start;
}

/* ================= ЛЕВАЯ КОЛОНКА ================= */
.reports-sidebar {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.icon-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  border-radius: 50%;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:hover {
  background: #f3f4f6;
}

.icon-btn.refresh {
  color: #3498db;
}

.icon-btn.refresh:disabled {
  opacity: 0.5;
  animation: spin 1s linear infinite;
}

.icon-btn.close {
  font-size: 16px;
  color: #6b7280;
}

.icon-btn.close:hover {
  background: #fee2e2;
  color: #ef4444;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

/* ================= ФИЛЬТРЫ ================= */
.reports-filters {
  margin-bottom: 20px;
}

.filter-tabs {
  display: flex;
  gap: 4px;
  background: #f3f4f6;
  padding: 4px;
  border-radius: 40px;
}

.filter-tab {
  flex: 1;
  padding: 8px 12px;
  border: none;
  background: transparent;
  border-radius: 30px;
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tab.active {
  background: white;
  color: #1f2937;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.filter-select {
  padding: 8px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 30px;
  font-size: 13px;
  color: #1f2937;
  background: white;
  cursor: pointer;
  outline: none;
  min-width: 140px;
  transition: all 0.2s;
}

.filter-select:hover {
  border-color: #3498db;
}

.filter-select:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.filter-info {
  font-size: 12px;
  color: #6b7280;
  margin-top: 8px;
  padding: 4px 12px;
  background: #f3f4f6;
  border-radius: 20px;
  display: inline-block;
}

/* Поиск */
.search-box {
  position: relative;
  width: 100%;
  box-sizing: border-box;
}

.search-box input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 1px solid #e5e7eb;
  border-radius: 40px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
  background: white;
  box-sizing: border-box; /* Важно! */
}

.search-box input:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.search-box::before {
 
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
  color: #9ca3af;
  pointer-events: none;
  z-index: 1;
}

/* Список отчетов */
.reports-list {
  max-height: 60vh;
  overflow-y: auto;
  padding-right: 8px;
}

/* Карточка отчета */
.report-card {
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
}

.report-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
}

.report-card.active {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.report-card.submitted {
  border-left: 4px solid #3b82f6;
}

.report-card.returned {
  border-left: 4px solid #ef4444;
}

.report-card.approved {
  border-left: 4px solid #10b981;
}

.report-card.draft {
  border-left: 4px solid #f59e0b;
}

.report-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.report-title h4 {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.report-date {
  font-size: 12px;
  color: #6b7280;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 40px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.status-badge.submitted {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.returned {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.approved {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.draft {
  background: #fef3c7;
  color: #92400e;
}

.report-card-body {
  margin-bottom: 12px;
}

.report-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #4b5563;
}

.review-comment {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #fff3cd;
  border-radius: 8px;
  font-size: 13px;
  color: #856404;
}

.report-card-footer {
  display: flex;
  justify-content: flex-end;
}

.link-icon {
  background: none;
  border: none;
  color: #3498db;
  font-size: 13px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 20px;
  transition: all 0.2s;
}

.link-icon:hover {
  background: #f0f9ff;
  text-decoration: underline;
}

.link-icon.small {
  font-size: 11px;
  padding: 2px 6px;
}

/* Загрузка */
.loading-reports {
  text-align: center;
  padding: 40px 0;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top-color: #3498db;
  border-radius: 50%;
  margin: 0 auto 12px;
  animation: spin 1s linear infinite;
}

/* Пустое состояние */
.empty-reports {
  text-align: center;
  padding: 40px 0;
  color: #9ca3af;
}

.empty-reports p {
  margin: 0 0 8px;
}

.empty-reports .hint {
  font-size: 12px;
  opacity: 0.7;
}

/* ================= ПРАВАЯ КОЛОНКА ================= */
.report-details-panel {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  min-height: 600px;
}

.report-details-panel.empty {
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-details {
  text-align: center;
  color: #9ca3af;
}

.empty-details h3 {
  margin: 0 0 8px;
  color: #4b5563;
}

.empty-details p {
  margin: 0;
  font-size: 14px;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.details-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.details-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.details-section {
  margin-bottom: 24px;
}

.details-section h4 {
  margin: 0 0 16px;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item.full-width {
  grid-column: span 2;
}

.detail-label {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 15px;
  color: #1f2937;
}

/* Таблица участников */
.participants-table-container {
  overflow-x: auto;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.participants-table {
  width: 100%;
  border-collapse: collapse;
}

.participants-table th {
  text-align: left;
  padding: 12px 8px;
  background: #f8fafc;
  font-size: 13px;
  font-weight: 600;
  color: #4b5563;
  border-bottom: 2px solid #e5e7eb;
}

.participants-table td {
  padding: 10px 8px;
  border-bottom: 1px solid #e5e7eb;
  color: #1f2937;
}

.participants-table tr:last-child td {
  border-bottom: none;
}

.result-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.result-badge.participant {
  background: #f3f4f6;
  color: #4b5563;
}

.result-badge.place {
  background: #fef3c7;
  color: #92400e;
}

.rank-badge {
  background: #e0f2fe;
  color: #0369a1;
  padding: 4px 8px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 12px;
  display: inline-block;
}

/* Текстовое поле */
.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field textarea {
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
  font-family: inherit;
  resize: vertical;
}

.form-field textarea:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

/* ================= КНОПКИ ================= */
.action {
  padding: 10px 20px;
  border: none;
  border-radius: 40px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.action.primary {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.action.primary.large {
  padding: 14px 32px;
  font-size: 16px;
}

.action.outline {
  background: white;
  border: 1px solid #d1d5db;
  color: #4b5563;
}

.action:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.action.small {
  padding: 6px 12px;
  font-size: 12px;
}

.form-actions {
  display: flex;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.actions-right {
  display: flex;
  gap: 12px;
}

/* ================= МОДАЛЬНОЕ ОКНО ================= */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

.modal-content {
  background: white;
  border-radius: 20px;
  padding: 24px;
  max-width: 90%;
  max-height: 90vh;
  overflow: auto;
  animation: slideUp 0.3s;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }

  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.protocol-modal {
  width: 800px;
  max-width: 90vw;
}

.protocol-viewer {
  width: 100%;
  height: 70vh;
  border: none;
}

.protocol-placeholder {
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  border-radius: 12px;
  color: #9ca3af;
}

/* ================= УВЕДОМЛЕНИЯ ================= */
.notification {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 16px 24px;
  border-radius: 60px;
  color: white;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.3s;
  z-index: 1000;
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

.notification.success {
  background: linear-gradient(135deg, #10b981, #059669);
}

.notification.error {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.notification.info {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.notification-icon {
  font-size: 18px;
}

/* ================= АДАПТАЦИЯ ================= */
@media (max-width: 1200px) {
  .reports-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .reports-page {
    padding: 12px;
  }

  .stats-pills {
    width: 100%;
    justify-content: space-between;
  }

  .stat-pill {
    min-width: 60px;
    padding: 6px 12px;
  }

  .filter-select {
    min-width: 120px;
  }

  .details-grid {
    grid-template-columns: 1fr;
  }

  .detail-item.full-width {
    grid-column: span 1;
  }

  .form-actions .actions-right {
    flex-direction: column;
    width: 100%;
  }

  .action {
    width: 100%;
  }

  .notification {
    left: 16px;
    right: 16px;
    bottom: 16px;
  }
}
</style>