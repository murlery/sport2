<template>
  <div class="reports-page">
    <!-- Шапка с приветствием -->
    <header class="page-header">
    </header>

    <div class="tabs-container">
      <div class="tabs">
        <button class="tab" :class="{ active: activeTab === 'reports' }" @click="activeTab = 'reports'">
          <span class="tab-label">Мои отчеты</span>
          <span v-if="totalReports" class="tab-badge">{{ totalReports }}</span>
        </button>
        <button class="tab" :class="{ active: activeTab === 'create' }" @click="activeTab = 'create'; clearSelection()">
          <span class="tab-label">Создать отчет</span>
        </button>
        <div class="stats-pills">
          <div class="stat-pill draft">
            <span class="stat-value">{{ draftCount }}</span>
            <span class="stat-label">Черновики</span>
          </div>
          <div class="stat-pill submitted">
            <span class="stat-value">{{ submittedCount }}</span>
            <span class="stat-label">На проверке</span>
          </div>
          <div class="stat-pill returned"> <!-- Изменено с approved на returned -->
            <span class="stat-value">{{ returnedCount }}</span>
            <span class="stat-label">На доработке</span> <!-- Изменено с Утверждено на На доработке -->
          </div>
        </div>
      </div>
    </div>

    <!-- Вкладка: Мои отчеты -->
    <div v-if="activeTab === 'reports'" class="tab-content">
      <div class="reports-layout">
        <!-- Список отчетов (левая колонка) -->
        <div class="reports-sidebar">
          <div class="sidebar-header">
            <h3>Все отчеты</h3>
            <button class="icon-btn refresh" @click="loadCompetitions" :disabled="loadingReports" title="Обновить">
              🔄
            </button>
          </div>

          <div class="reports-filters">
            <div class="filter-tabs">
              <button class="filter-tab" :class="{ active: reportsFilter === 'all' }" @click="reportsFilter = 'all'">
                Все
              </button>
              <button class="filter-tab" :class="{ active: reportsFilter === 'draft' }"
                @click="reportsFilter = 'draft'">
                Черновики
              </button>
              <button class="filter-tab" :class="{ active: reportsFilter === 'submitted' }"
                @click="reportsFilter = 'submitted'">
                На проверке
              </button>
              <button class="filter-tab" :class="{ active: reportsFilter === 'returned' }"
                @click="reportsFilter = 'returned'">
                На доработке
              </button>
            </div>

            <div class="search-box">
              <input type="text" v-model="reportsSearch" placeholder="Поиск по названию..." />
            </div>
          </div>

          <div v-if="loadingReports" class="loading-reports">
            <div class="spinner"></div>
            <p>Загрузка отчетов...</p>
          </div>

          <div v-else-if="filteredReports.length === 0" class="empty-reports">
            <p>Отчеты не найдены</p>
            <button class="action primary small" @click="activeTab = 'create'">
              Создать первый отчет
            </button>
          </div>

          <div v-else class="reports-list">
            <div v-for="report in filteredReports" :key="report.id" class="report-card" :class="{
              active: selectedReport?.id === report.id,
              [report.status]: true
            }" @click="selectReport(report)">
              <div class="report-card-header">
                <div class="report-title">
                  <h4>{{ report.name }}</h4>
                  <span class="report-date">{{ formatDate(report.date) }}</span>
                </div>
                <span class="status-badge" :class="report.status">
                  {{ statusLabel(report.status) }}
                </span>
              </div>

              <div class="report-card-body">
                <div class="report-meta">
                  <span class="meta-item">
                    {{ report.location }}
                  </span>
                  <span class="meta-item">
                    {{ report.level }}
                  </span>
                  <span class="meta-item">
                    {{ report.results?.length || 0 }} участников
                  </span>
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
          </div>
        </div>

        <!-- Детали отчета (правая колонка) -->
        <div class="report-details-panel" v-if="selectedReport">
          <div class="details-header">
            <h3>Детали отчета</h3>
            <div class="details-actions">
              <button v-if="selectedReport.status === 'draft' || selectedReport.status === 'returned'"
                class="action primary small" @click="editReport(selectedReport)">
                Редактировать
              </button>
              <button v-if="selectedReport.protocol" class="action outline small"
                @click="downloadProtocol(selectedReport)">
                Скачать протокол
              </button>
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
                  <span class="detail-label">Статус</span>
                  <span class="detail-value">
                    <span class="status-badge" :class="selectedReport.status">
                      {{ statusLabel(selectedReport.status) }}
                    </span>
                  </span>
                </div>
                <div v-if="selectedReport.review_comment" class="detail-item full-width">
                  <span class="detail-label">Комментарий методиста</span>
                  <div class="comment-bubble">
                    {{ selectedReport.review_comment }}
                  </div>
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
                      <th>Весовая категория</th>
                      <th>Результат</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(result, idx) in selectedReport.results" :key="result.id">
                      <td>{{ idx + 1 }}</td>
                      <td>
                        <strong>{{ athleteName(result.athlete) }}</strong>
                      </td>
                      <td>{{ result.weight_category || '—' }}</td>
                      <td>
                        <span v-if="result.is_participant" class="result-badge participant">
                          Участник
                        </span>
                        <span v-else-if="result.place" class="result-badge place">
                          {{ getPlaceEmoji(result.place) }} {{ result.place }} место
                        </span>
                        <span v-else>—</span>
                      </td>
                    </tr>
                    <tr v-if="!selectedReport.results?.length">
                      <td colspan="5" class="empty">Нет участников</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Пустое состояние деталей -->
        <div v-else class="report-details-panel empty">
          <div class="empty-details">
            <h3>Выберите отчет</h3>
            <p>Нажмите на отчет из списка, чтобы просмотреть детали</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Вкладка: Создание отчета -->
    <div v-if="activeTab === 'create'" class="tab-content">
      <div class="create-report-layout">
        <div class="create-report-header">
          <h2>{{ isEditing ? 'Редактирование отчета' : 'Создание нового отчета' }}</h2>
          <p class="hint">Заполните информацию о соревновании и добавьте участников</p>
        </div>

        <div class="create-report-grid">
          <!-- Левая колонка - информация о соревновании -->
          <div class="form-section competition-section">
            <div class="section-header">
              <h3>Информация о соревновании</h3>
            </div>

            <div class="form-grid">
              <div class="form-field required">
                <label>Название соревнования</label>
                <input type="text" v-model="competitionForm.name" placeholder="Например, Первенство города"
                  :class="{ error: validationErrors.name }" />
                <span v-if="validationErrors.name" class="field-error">
                  {{ validationErrors.name }}
                </span>
              </div>

              <div class="form-field required">
                <label>Дата проведения</label>
                <input type="date" v-model="competitionForm.date" :class="{ error: validationErrors.date }" />
                <span v-if="validationErrors.date" class="field-error">
                  {{ validationErrors.date }}
                </span>
              </div>

              <div class="form-field required">
                <label>Место проведения</label>
                <input type="text" v-model="competitionForm.location" placeholder="Город, спортивный комплекс"
                  :class="{ error: validationErrors.location }" />
                <span v-if="validationErrors.location" class="field-error">
                  {{ validationErrors.location }}
                </span>
              </div>

              <div class="form-field required">
                <label>Уровень соревнований</label>
                <select v-model="competitionForm.level" :class="{ error: validationErrors.level }">
                  <option value="">Выберите уровень</option>
                  <option v-for="lvl in levels" :key="lvl" :value="lvl">
                    {{ lvl }}
                  </option>
                </select>
                <span v-if="validationErrors.level" class="field-error">
                  {{ validationErrors.level }}
                </span>
              </div>

              <div class="form-field file-field">
                <label>Протокол соревнований</label>

                <div v-if="isEditing && existingProtocol" class="current-file">
                  <a href="#" @click.prevent="downloadExistingProtocol" class="file-link">
                    <span class="file-name">📄 {{ existingProtocol }}</span>
                  </a>
                  <button class="link-icon small" @click="removeExistingProtocol">Удалить</button>
                </div>

                <!-- Загрузка нового протокола -->
                <div class="file-upload" @click="$refs.protocolInput.click()">
                  <input ref="protocolInput" type="file" accept=".pdf,.doc,.docx" @change="onProtocolChange" hidden />
                  <div class="file-upload-area">
                    <span class="upload-icon">📎</span>
                    <span v-if="protocolName" class="file-name">{{ protocolName }}</span>
                    <span v-else class="upload-text">Выберите файл или перетащите его сюда</span>
                    <span class="file-hint">PDF, DOC, DOCX до 10 МБ</span>
                  </div>
                </div>
                <button v-if="protocolFile" class="link-icon small" @click="protocolFile = null">
                  Удалить новый файл
                </button>
              </div>
            </div>
          </div>

          <!-- Правая колонка - добавление участников -->
          <div class="form-section participants-section">
            <div class="section-header">
              <h3>Участники</h3>
              <span class="participants-count">{{ participants.length }} / 50</span>
            </div>

            <!-- Форма добавления участника -->
            <div class="add-participant-form">
              <h4>{{ editingParticipant ? 'Редактирование участника' : 'Добавить участника' }}</h4>

              <div class="form-row">
                <div class="form-field required">
                  <label>ФИО спортсмена</label>
                  <input type="text" v-model="athleteSearch" @input="filterAthletes"
                    placeholder="Начните вводить ФИО" />

                  <ul v-if="filteredAthletes.length && athleteSearch" class="autocomplete-list">
                    <li v-for="ath in filteredAthletes" :key="ath.id" @click="selectAthlete(ath)">
                      {{ athleteName(ath) }}
                    </li>
                  </ul>
                </div>

                <div class="form-field">
                  <label>Весовая категория</label>
                  <input type="text" v-model="participantForm.weight_category" placeholder="например, до 70 кг" />
                </div>
              </div>

              <div class="form-row">
                <div class="form-field">
                  <label>Занятое место</label>
                  <select v-model="participantForm.place">
                    <option value="">Участник без места</option>
                    <option value="1">🥇 1 место</option>
                    <option value="2">🥈 2 место</option>
                    <option value="3">🥉 3 место</option>
                  </select>
                </div>
              </div>

              <div class="form-row">
                <div class="form-field actions">
                  <button class="action outline" @click="cancelEditParticipant" v-if="editingParticipant">
                    Отмена
                  </button>
                  <button class="action primary" @click="addParticipant" :disabled="!participantForm.athlete_id">
                    {{ editingParticipant ? 'Обновить' : 'Добавить' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Список добавленных участников -->
            <div class="participants-list">
              <div v-for="(p, idx) in participants" :key="p.tempId" class="participant-item"
                @click="editParticipant(p)">
                <div class="participant-number">{{ idx + 1 }}</div>
                <div class="participant-info">
                  <div class="participant-name">{{ p.athlete_name }}</div>
                  <div class="participant-details">
                    <span v-if="p.weight_category" class="detail-tag">
                      {{ p.weight_category }}
                    </span>
                    <span v-if="p.is_participant" class="detail-tag participant">
                      Участник
                    </span>
                    <span v-else-if="p.place" class="detail-tag place">
                      {{ p.place }} место
                    </span>
                    <span v-if="p.rank" class="detail-tag">
                      {{ p.rank }}
                    </span>
                  </div>
                </div>
                <button class="icon-btn remove" @click.stop="removeParticipant(p.tempId)" title="Удалить">
                  ✕
                </button>
              </div>

              <div v-if="participants.length === 0" class="empty-participants">
                <p>Участники не добавлены</p>
                <p class="hint">Используйте форму выше, чтобы добавить участников</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Действия с отчетом -->
        <div class="form-actions">
          <div class="actions-left">
            <button class="action outline" @click="cancelEdit" v-if="isEditing">
              Отменить
            </button>
          </div>

          <div class="actions-right">
            <button class="action outline" @click="saveReport" :disabled="saving || !canSaveDraft">
              {{ saving ? 'Сохранение...' : ' Сохранить черновик' }}
            </button>

            <button class="action primary large" @click="submitReport" :disabled="saving || !canSubmit">
              {{ saving ? 'Отправка...' : ' Отправить методисту' }}
            </button>
          </div>
        </div>

        <!-- Индикатор прогресса -->
        <div class="progress-indicator" v-if="participants.length > 0">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: `${Math.min(100, (participants.length / 5) * 100)}%` }"></div>
          </div>
          <span class="progress-text">
            Минимум участников: {{ participants.length }}/5
          </span>
        </div>
      </div>
    </div>

    <!-- Модальное окно просмотра протокола -->
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
  name: 'CoachReports',
  data() {
    const today = new Date().toISOString().slice(0, 10)
    return {
      // Табы и фильтры
      activeTab: 'reports',
      reportsFilter: 'all',
      reportsSearch: '',

      // Пользователь и данные
      currentUser: null,
      coachInfo: null,
      groups: [],
      athletes: [],
      competitions: [],
      selectedReport: null,

      // Состояния загрузки
      loadingAthletes: false,
      loadingReports: false,
      saving: false,

      // Формы
      selectedGroup: '',
      protocolFile: null,
      existingProtocol: null, // Для хранения имени существующего протокола
      isEditing: false,
      editingParticipant: null, // Для редактирования участника

      competitionForm: {
        name: '',
        date: today,
        location: '',
        level: ''
      },

      participantForm: {
        athlete_id: '',
        weight_category: '',
        place: '',
        is_participant: false,
        rank: ''
      },

      participants: [],

      // Валидация
      validationErrors: {},

      // Модальное окно
      showProtocolModal: false,
      protocolUrl: null,
      athleteSearch: '',
      filteredAthletes: [],

      // Уведомления
      notification: { show: false, message: '', type: 'info' }
    }
  },

  computed: {
    debugCoachId() {
      return this.coachInfo?.id || 'не загружен'
    },
    levels() {
      return ['Локальный', 'Городской', 'Региональный', 'Федеральный', 'Всероссийский']
    },

    coachName() {
      if (!this.coachInfo?.user) return '-'
      const u = this.coachInfo.user
      return `${u.last_name || ''} ${u.first_name || ''}`.trim() || '-'
    },

    draftCount() {
      return this.competitions.filter(c => c.status === 'draft').length
    },

    submittedCount() {
      return this.competitions.filter(c => c.status === 'submitted').length
    },

    approvedCount() {
      return this.competitions.filter(c => c.status === 'approved').length
    },
    returnedCount() {
      return this.competitions.filter(c => c.status === 'returned').length
    },

    totalReports() {
      return this.competitions.length
    },

    protocolName() {
      return this.protocolFile?.name || ''
    },

    filteredReports() {
      let filtered = this.competitions

      // Фильтр по статусу
      if (this.reportsFilter !== 'all') {
        filtered = filtered.filter(r => r.status === this.reportsFilter)
      }

      // Поиск по названию
      if (this.reportsSearch) {
        const search = this.reportsSearch.toLowerCase()
        filtered = filtered.filter(r =>
          r.name.toLowerCase().includes(search) ||
          r.location.toLowerCase().includes(search)
        )
      }

      return filtered
    },

    canSaveDraft() {
      return this.competitionForm.name &&
        this.competitionForm.date &&
        this.competitionForm.location &&
        this.competitionForm.level
    },

    canSubmit() {
      return this.canSaveDraft && this.participants.length > 0
    }
  },

  async mounted() {
    await this.loadCurrentUser()
    await this.loadCoachInfo()
    await this.loadGroups()
    await this.loadAthletes()
    await this.loadCompetitions()
  },

  methods: {
    // ================= ЗАГРУЗКА ДАННЫХ =================

    async loadCurrentUser() {
      const raw = localStorage.getItem('user')
      if (raw) this.currentUser = JSON.parse(raw)
      try {
        const res = await axios.get('/api/auth/me/')
        this.currentUser = res.data
        localStorage.setItem('user', JSON.stringify(res.data))
      } catch (error) {
        console.warn('Не удалось обновить пользователя', error)
      }
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
      if (!this.coachInfo?.id) {
        this.groups = []
        return
      }
      try {
        const res = await axios.get('/api/groups/', { params: { coach: this.coachInfo.id } })
        this.groups = res.data
        if (!this.selectedGroup && this.groups.length) {
          this.selectedGroup = String(this.groups[0].id)
        }
      } catch (error) {
        console.error('Ошибка загрузки групп', error)
      }
    },

    async loadAthletes() {
      if (!this.coachInfo?.id) {
        this.athletes = []
        return
      }
      if (!this.selectedGroup) {
        this.athletes = []
        return
      }
      this.loadingAthletes = true
      try {
        const res = await axios.get('/api/athletes/', {
          params: { coach: this.coachInfo.id }
        })
        this.athletes = res.data
      } catch (error) {
        console.error('Ошибка загрузки спортсменов', error)
        this.showNotification('Не удалось загрузить спортсменов', 'error')
      } finally {
        this.loadingAthletes = false
      }
    },

    async loadCompetitions() {
      this.loadingReports = true
      try {
        if (!this.coachInfo?.id) {
          this.competitions = []
          this.loadingReports = false
          return
        }

        const params = { coach_id: this.coachInfo.id }
        const res = await axios.get('/api/competitions/', { params })

        let filteredComps = res.data.filter(comp => {
          const compCoachId = comp.coach?.id || comp.coach_id || comp.coach
          return compCoachId == this.coachInfo.id
        })

        this.competitions = filteredComps.sort((a, b) =>
          new Date(b.date) - new Date(a.date)
        )

        console.log('Загружено отчетов для тренера:', this.competitions.length)
      } catch (error) {
        console.error('Ошибка загрузки отчетов', error)
        this.showNotification('Не удалось загрузить отчеты', 'error')
      } finally {
        this.loadingReports = false
      }
    },

    filterAthletes() {
      const search = this.athleteSearch.toLowerCase()
      this.filteredAthletes = this.athletes.filter(a =>
        this.athleteName(a).toLowerCase().includes(search)
      ).slice(0, 5)
    },

    selectAthlete(ath) {
      this.participantForm.athlete_id = String(ath.id)
      this.participantForm.rank = ath.rank || ''
      this.athleteSearch = this.athleteName(ath)
      this.filteredAthletes = []
    },

    // ================= РАБОТА С ОТЧЕТАМИ =================

    selectReport(report) {
      this.selectedReport = report
    },

    editReport(report) {
      this.hydrateFromReport(report)
      this.isEditing = true
      this.activeTab = 'create'
    },

    clearSelection() {
      this.selectedReport = null
      this.resetForms()
      this.isEditing = false
    },

    cancelEdit() {
      this.resetForms()
      this.isEditing = false
      this.activeTab = 'reports'
    },

    hydrateFromReport(comp) {
      this.competitionForm = {
        name: comp.name || '',
        date: comp.date || new Date().toISOString().slice(0, 10),
        location: comp.location || '',
        level: comp.level || ''
      }

      // Сохраняем информацию о существующем протоколе
      if (comp.protocol) {
        const protocolUrl = comp.protocol.split('/').pop()
        this.existingProtocol = protocolUrl
      } else {
        this.existingProtocol = null
      }

      this.participants = (comp.results || []).map(r => ({
        id: r.id,
        tempId: `temp-${r.id}`,
        athlete_id: String(r.athlete?.id || r.athlete),
        athlete_name: this.athleteName(r.athlete),
        weight_category: r.weight_category || '',
        place: r.place ? String(r.place) : '',
        is_participant: !!r.is_participant,
        rank: r.athlete?.rank || ''
      }))

      const groupId = comp.results?.[0]?.athlete?.group?.id
      if (groupId) {
        this.selectedGroup = String(groupId)
        this.loadAthletes()
      }

      this.editingReportId = comp.id
    },

    // ================= ПРОТОКОЛЫ =================

    onProtocolChange(event) {
      const file = event.target.files[0]
      if (file && file.size > 10 * 1024 * 1024) {
        this.showNotification('Файл слишком большой (макс. 10 МБ)', 'error')
        return
      }
      this.protocolFile = file || null
    },

    removeExistingProtocol() {
      this.existingProtocol = null
      // Помечаем, что старый протокол нужно удалить
      this.protocolFile = null
    },

    async downloadProtocol(report) {
      if (!report.protocol) {
        this.showNotification('Протокол не прикреплен', 'error')
        return
      }

      try {
        console.log('Downloading protocol from:', report.protocol)

        const response = await axios.get(report.protocol, {
          responseType: 'blob'
        })

        let filename = 'protocol'

        const contentDisposition = response.headers['content-disposition']
        if (contentDisposition) {
          const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
          if (match && match[1]) {
            filename = match[1].replace(/['"]/g, '')
          }
        } else {
          const urlParts = report.protocol.split('/')
          filename = urlParts[urlParts.length - 1]
        }

        const fileType = response.headers['content-type']

        const url = window.URL.createObjectURL(new Blob([response.data], { type: fileType }))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)

        this.showNotification('Файл успешно скачан', 'success')
      } catch (error) {
        console.error('Ошибка скачивания протокола:', error)
        this.showNotification('Не удалось скачать протокол', 'error')
      }
    },

    async viewProtocol(report) {
      if (!report.protocol) return

      try {
        this.protocolUrl = report.protocol
        this.showProtocolModal = true
      } catch (error) {
        console.error('Ошибка просмотра протокола:', error)
        this.showNotification('Не удалось открыть протокол', 'error')
      }
    },
    removeExistingProtocol() {
      this.existingProtocol = null
      // Помечаем, что старый протокол нужно удалить
      this.protocolFile = null
    },

    // Добавьте этот новый метод
    async downloadExistingProtocol() {
      if (!this.editingReportId) return

      try {
        // Получаем текущий отчет, чтобы получить URL протокола
        const report = this.competitions.find(c => c.id === this.editingReportId)
        if (report && report.protocol) {
          await this.downloadProtocol(report)
        } else {
          this.showNotification('Протокол не найден', 'error')
        }
      } catch (error) {
        console.error('Ошибка скачивания протокола:', error)
        this.showNotification('Не удалось скачать протокол', 'error')
      }
    },

    // ================= УПРАВЛЕНИЕ УЧАСТНИКАМИ =================

    editParticipant(participant) {
      this.editingParticipant = participant
      this.participantForm = {
        athlete_id: participant.athlete_id,
        weight_category: participant.weight_category,
        place: participant.place,
        is_participant: participant.is_participant,
        rank: participant.rank
      }
      // Заполняем поиск
      const athlete = this.athletes.find(a => String(a.id) === String(participant.athlete_id))
      if (athlete) {
        this.athleteSearch = this.athleteName(athlete)
      }
    },

    cancelEditParticipant() {
      this.editingParticipant = null
      this.clearParticipantForm()
    },

    clearParticipantForm() {
      this.participantForm = {
        athlete_id: '',
        weight_category: '',
        place: '',
        is_participant: false,
        rank: ''
      }
      this.athleteSearch = ''
      this.filteredAthletes = []
    },

    addParticipant() {
      if (!this.participantForm.athlete_id) {
        this.showNotification('Выберите спортсмена', 'error')
        return
      }

      if (this.participants.length >= 50) {
        this.showNotification('Достигнуто максимальное количество участников (50)', 'error')
        return
      }

      const athlete = this.athletes.find(a => String(a.id) === String(this.participantForm.athlete_id))

      if (this.editingParticipant) {
        // Обновляем существующего участника
        const index = this.participants.findIndex(p => p.tempId === this.editingParticipant.tempId)
        if (index !== -1) {
          this.participants[index] = {
            ...this.editingParticipant,
            athlete_id: this.participantForm.athlete_id,
            athlete_name: athlete ? this.athleteName(athlete) : 'Спортсмен',
            weight_category: this.participantForm.weight_category,
            place: this.participantForm.place,
            is_participant: this.participantForm.is_participant,
            rank: this.participantForm.rank
          }
        }
        this.showNotification('Участник обновлен', 'success')
      } else {
        // Добавляем нового участника
        const tempId = `temp-${Date.now()}-${Math.random()}`
        this.participants.push({
          tempId,
          athlete_id: this.participantForm.athlete_id,
          athlete_name: athlete ? this.athleteName(athlete) : 'Спортсмен',
          weight_category: this.participantForm.weight_category,
          place: this.participantForm.place,
          is_participant: this.participantForm.is_participant,
          rank: this.participantForm.rank
        })
        this.showNotification('Участник добавлен', 'success')
      }

      // Сброс формы
      this.editingParticipant = null
      this.clearParticipantForm()
    },

    removeParticipant(id) {
      this.participants = this.participants.filter(p => p.tempId !== id)
      this.showNotification('Участник удален', 'info')
    },

    // ================= СОХРАНЕНИЕ ОТЧЕТА =================

    validateForm() {
      const errors = {}

      if (!this.competitionForm.name) errors.name = 'Укажите название соревнования'
      if (!this.competitionForm.date) errors.date = 'Укажите дату проведения'
      if (!this.competitionForm.location) errors.location = 'Укажите место проведения'
      if (!this.competitionForm.level) errors.level = 'Выберите уровень соревнований'

      this.validationErrors = errors
      return Object.keys(errors).length === 0
    },

    async saveReportInternal(status = 'draft') {
      if (!this.validateForm()) {
        this.showNotification('Заполните все обязательные поля', 'error')
        return null
      }

      this.saving = true

      try {
        const isEditing = this.isEditing && this.editingReportId
        let competitionId = this.editingReportId

        // ===== СОХРАНЕНИЕ СОРЕВНОВАНИЯ =====
        const formData = new FormData()
        formData.append('name', this.competitionForm.name)
        formData.append('date', this.competitionForm.date)
        formData.append('location', this.competitionForm.location)
        formData.append('level', this.competitionForm.level)
        formData.append('status', status)

        if (this.coachInfo?.id) {
          formData.append('coach_id', Number(this.coachInfo.id))
        }

        // Если есть новый файл протокола - отправляем его
        if (this.protocolFile) {
          formData.append('protocol', this.protocolFile)
        } else if (isEditing && !this.existingProtocol) {
          // Если удалили старый протокол и не загрузили новый
          formData.append('protocol', '')
        }

        if (isEditing) {
          await axios.patch(`/api/competitions/${competitionId}/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
        } else {
          const res = await axios.post('/api/competitions/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
          competitionId = Number(res.data.id)
        }

        // ===== РАБОТА С УЧАСТНИКАМИ =====

        if (isEditing) {
          // Получаем ВСЕ результаты и фильтруем по competitionId
          const existingRes = await axios.get('/api/competition-results/')
          const existingResults = existingRes.data.filter(r =>
            Number(r.competition) === Number(competitionId)
          )

          console.log(`Results for competition ${competitionId}:`, existingResults)

          // ID результатов, которые есть в форме
          const formResultIds = new Set(
            this.participants
              .filter(p => p.id)
              .map(p => p.id)
          )

          // Удаляем результаты, которых нет в форме
          const toDelete = existingResults.filter(r => !formResultIds.has(r.id))
          console.log('Results to delete:', toDelete.map(r => r.id))

          await Promise.all(
            toDelete.map(r =>
              axios.delete(`/api/competition-results/${r.id}/`)
            )
          )
        }

        // Создаем или обновляем результаты
        for (const p of this.participants) {
          const payload = {
            competition: Number(competitionId),
            athlete_id: Number(p.athlete_id),
            coach_id: Number(this.coachInfo?.id),
            place: p.is_participant ? null : (p.place ? Number(p.place) : null),
            is_participant: p.is_participant,
            weight_category: p.weight_category || ''
          }

          if (isEditing && p.id) {
            // Обновляем существующий результат
            console.log(`Updating result ${p.id} for athlete ${p.athlete_id}`, payload)
            await axios.patch(`/api/competition-results/${p.id}/`, payload)
          } else {
            // Создаем новый результат
            console.log(`Creating new result for athlete ${p.athlete_id}`, payload)
            await axios.post('/api/competition-results/', payload)
          }
        }

        this.showNotification(
          status === 'submitted'
            ? 'Отчет отправлен методисту'
            : 'Черновик сохранен',
          'success'
        )

        await this.loadCompetitions()
        this.resetForms()
        this.isEditing = false
        this.activeTab = 'reports'

        return competitionId

      } catch (error) {
        console.error('Ошибка сохранения отчета', error)
        this.showNotification('Не удалось сохранить отчет', 'error')
        return null
      } finally {
        this.saving = false
      }
    },

    async saveReport() {
      await this.saveReportInternal('draft')
    },

    async submitReport() {
      await this.saveReportInternal('submitted')
    },

    // ================= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =================

    athleteName(athlete) {
      if (!athlete) return ''
      const obj = athlete.user || athlete
      return `${obj.last_name || ''} ${obj.first_name || ''} ${obj.middle_name || ''}`.trim()
    },

    formatDate(dateString) {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      })
    },

    statusLabel(status) {
      const map = {
        draft: 'Черновик',
        submitted: 'Отправлен',
        approved: 'Утвержден',
        returned: 'На доработку'
      }
      return map[status] || status
    },

    getPlaceEmoji(place) {
      const emoji = {
        1: '🥇',
        2: '🥈',
        3: '🥉'
      }
      return emoji[place] || '🏅'
    },

    resetForms() {
      this.competitionForm = {
        name: '',
        date: new Date().toISOString().slice(0, 10),
        location: '',
        level: ''
      }
      this.clearParticipantForm()
      this.participants = []
      this.protocolFile = null
      this.existingProtocol = null
      this.validationErrors = {}
      this.editingReportId = null
      this.editingParticipant = null
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
/* ================= ОСНОВНЫЕ СТИЛИ ================= */

.reports-page {
  min-height: 100vh;

  padding: 24px;
}

/* ================= ШАПКА ================= */


.stats-pills {
  display: flex;
  gap: 12px;
}


.stat-pill {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 16px;
  background: #f8fafc;
  border-radius: 40px;
  min-width: 80px;
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

.stat-pill.draft .stat-value {
  color: #f59e0b;
}

.stat-pill.submitted .stat-value {
  color: #3b82f6;
}

.stat-pill.approved .stat-value {
  color: #10b981;
}

/* ================= ТАБЫ ================= */

.tabs-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.tabs {
  display: flex;
  gap: 8px;
  background: white;
  padding: 6px;
  border-radius: 60px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  flex: 1;
}

.tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  background: transparent;
  border-radius: 40px;
  font-size: 15px;
  font-weight: 600;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.autocomplete-list {
  list-style: none;
  margin: 0;
  padding: 0;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  max-height: 150px;
  overflow-y: auto;
  background: white;
}

.autocomplete-list li {
  padding: 8px 12px;
  cursor: pointer;
}

.autocomplete-list li:hover {
  background: #f3f4f6;
}

@media (max-width: 768px) {
  .tabs-container {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .tabs {
    width: 100%;
  }

  .stats-pills {
    justify-content: space-around;
    width: 100%;
  }
}


.tab:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.tab.active {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}



.tab-badge {
  padding: 2px 8px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 30px;
  font-size: 12px;
}

/* ================= ВКЛАДКА МОИ ОТЧЕТЫ ================= */

.tab-content {
  margin-top: 24px;
}

.reports-layout {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 24px;
  align-items: start;
}

/* Левая колонка - список отчетов */
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

.reports-filters {
  margin-bottom: 20px;
}

.filter-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 12px;
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
  box-sizing: border-box;
  /* Важно! */
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
  max-height: 600px;
  overflow-y: auto;
  padding-right: 8px;
}

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

.report-card.draft {
  border-left: 4px solid #f59e0b;
}

.report-card.submitted {
  border-left: 4px solid #3b82f6;
}

.report-card.approved {
  border-left: 4px solid #10b981;
}

.report-card.returned {
  border-left: 4px solid #ef4444;
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
}

.status-badge.draft {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.submitted {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.approved {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.returned {
  background: #fee2e2;
  color: #991b1b;
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

/* Правая колонка - детали отчета */
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

.comment-bubble {
  padding: 12px;
  background: #fef3c7;
  border-radius: 12px;
  font-size: 14px;
  color: #92400e;
}

/* Таблица участников */
.participants-table-container {
  overflow-x: auto;
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

/* ================= ВКЛАДКА СОЗДАНИЕ ОТЧЕТА ================= */

.create-report-layout {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.create-report-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.create-report-header h2 {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
}

.create-report-header .hint {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.create-report-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.form-section {
  background: #f8fafc;
  border-radius: 16px;
  padding: 20px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  flex: 1;
}



.participants-count {
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
  background: white;
  padding: 4px 12px;
  border-radius: 30px;
}

/* Формы */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field.required label::after {
  content: '*';
  color: #ef4444;
  margin-left: 4px;
}

.form-field label {
  font-size: 13px;
  font-weight: 600;
  color: #4b5563;
}

.form-field input,
.form-field select {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
}

.form-field input:focus,
.form-field select:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-field input.error,
.form-field select.error {
  border-color: #ef4444;
}

.field-error {
  font-size: 12px;
  color: #ef4444;
}

/* Загрузка файла */
.file-field {
  grid-column: span 2;
}

.file-upload {
  cursor: pointer;
}

.file-upload-area {
  padding: 24px;
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  text-align: center;
  transition: all 0.2s;
}

.file-upload-area:hover {
  border-color: #3498db;
  background: #f0f9ff;
}

.upload-icon {
  display: block;
  font-size: 24px;
  margin-bottom: 8px;
}

.upload-text {
  display: block;
  font-size: 14px;
  color: #4b5563;
  margin-bottom: 4px;
}

.file-name {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #3498db;
  margin-bottom: 4px;
}

.file-hint {
  display: block;
  font-size: 11px;
  color: #9ca3af;
}

/* Форма добавления участника */
.participants-filters {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.participants-filters select {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
}

.add-participant-form {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.add-participant-form h4 {
  margin: 0 0 16px;
  font-size: 15px;
  font-weight: 600;
  color: #374151;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
}

.form-row:last-child {
  margin-bottom: 0;
}

.checkbox {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
}

/* Список участников */
.participants-list {
  max-height: 300px;
  overflow-y: auto;
}

.participant-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  margin-bottom: 8px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
}

.participant-item:hover {
  border-color: #3498db;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.participant-number {
  width: 28px;
  height: 28px;
  background: #f3f4f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: #4b5563;
}

.participant-info {
  flex: 1;
}

.participant-name {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.participant-details {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.detail-tag {
  padding: 2px 8px;
  background: #f3f4f6;
  border-radius: 20px;
  font-size: 11px;
  color: #4b5563;
}

.detail-tag.participant {
  background: #f3f4f6;
  color: #6b7280;
}

.detail-tag.place {
  background: #fef3c7;
  color: #92400e;
}

.icon-btn.remove {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: #9ca3af;
  cursor: pointer;
  transition: all 0.2s;
}

.icon-btn.remove:hover {
  background: #fee2e2;
  color: #ef4444;
}

.empty-participants {
  text-align: center;
  padding: 32px;
  background: white;
  border-radius: 12px;
  color: #9ca3af;
}

.empty-participants p {
  margin: 0 0 4px;
}

.empty-participants .hint {
  font-size: 12px;
  opacity: 0.7;
}

/* Действия с формой */
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.actions-left,
.actions-right {
  display: flex;
  gap: 12px;
}

/* Индикатор прогресса */
.progress-indicator {
  margin-top: 16px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}

.progress-bar {
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2980b9);
  border-radius: 3px;
  transition: width 0.3s;
}

.progress-text {
  font-size: 12px;
  color: #6b7280;
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

.action.small {
  padding: 6px 12px;
  font-size: 12px;
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

.icon-btn.back {
  font-size: 20px;
}

.icon-btn.refresh {
  color: #3498db;
}

.icon-btn.refresh:disabled {
  opacity: 0.5;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
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

/* ================= ЗАГРУЗКА ================= */

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

  .create-report-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .reports-page {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-right {
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
  }

  .stats-pills {
    width: 100%;
    justify-content: space-between;
  }

  .tabs {
    width: 100%;
  }

  .tab {
    flex: 1;
    justify-content: center;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .file-field {
    grid-column: span 1;
  }

  .form-actions {
    flex-direction: column;
    gap: 12px;
  }

  .actions-left,
  .actions-right {
    width: 100%;
  }

  .actions-right {
    flex-direction: column;
  }

  .notification {
    left: 16px;
    right: 16px;
    bottom: 16px;
  }
}

.file-link {
  text-decoration: none;
  color: inherit;
  display: inline-block;
  cursor: pointer;
}

.file-link:hover {
  text-decoration: underline;
  color: #3498db;
}

.current-file {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 6px;
}
</style>