<template>
    <div class="reports-page">
        <!-- Шапка -->
        <header class="page-header">
            <h1></h1>
        </header>

        <!-- ТАБЫ -->
        <div class="tabs-container">
            <div class="tabs">
                <button class="tab" :class="{ active: activeTab === 'athletes' }" @click="activeTab = 'athletes'">
                    <span class="tab-label">Спортсмены</span>
                    <span v-if="athletes.length" class="tab-badge">{{ athletes.length }}</span>
                </button>
                <button class="tab" :class="{ active: activeTab === 'employees' }" @click="activeTab = 'employees'">
                    <span class="tab-label">Сотрудники</span>
                    <span v-if="employees.length" class="tab-badge">{{ employees.length }}</span>
                </button>
                <button class="tab" :class="{ active: activeTab === 'ranks' }"
                    @click="activeTab = 'ranks'; loadOrders()">
                    <span class="tab-label">Разряды</span>
                    <span v-if="orders.length" class="tab-badge">{{ orders.length }}</span>
                </button>
            </div>
        </div>

        <!-- ================= СПОРТСМЕНЫ ================= -->
        <div v-if="activeTab === 'athletes'" class="tab-content">
            <div class="reports-layout" style="grid-template-columns: 1fr;">
                <div class="reports-sidebar" style="max-width: 100%;">
                    <div class="sidebar-header">
                        <h3>Спортсмены</h3>
                        <button class="icon-btn refresh" @click="loadAthletes" title="Обновить">
                            <i class="bi bi-arrow-clockwise"></i>
                        </button>
                    </div>

                    <!-- ФИЛЬТРЫ для спортсменов -->
                    <div class="reports-filters">
                        <div class="search-box" style="margin-bottom: 12px;">
                            <input type="text" v-model="athleteFilters.search" placeholder="Поиск по ФИО..." />
                        </div>

                        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px;">
                            <select v-model="athleteFilters.department" class="filter-select"
                                @change="onDepartmentChange">
                                <option value="">Все отделения</option>
                                <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                                    {{ dept.name }}
                                </option>
                            </select>

                            <select v-model="athleteFilters.coach" class="filter-select" @change="onCoachChange">
                                <option value="">Все тренеры</option>
                                <option v-for="coach in filteredCoaches" :key="coach.id" :value="coach.id">
                                    {{ coachName(coach) }}
                                </option>
                            </select>

                            <select v-model="athleteFilters.group" class="filter-select">
                                <option value="">Все группы</option>
                                <option v-for="group in filteredGroups" :key="group.id" :value="group.id">
                                    {{ group.name }}
                                </option>
                            </select>

                            <select v-model="athleteFilters.rank" class="filter-select">
                                <option value="">Все разряды</option>
                                <option v-for="rank in uniqueRanks" :key="rank" :value="rank">
                                    {{ rank }}
                                </option>
                            </select>

                            <button v-if="hasAthleteFilters" class="link-icon small" @click="resetAthleteFilters">
                                ✕ Сбросить
                            </button>
                        </div>

                        <div class="filter-info" v-if="filteredAthletes.length !== athletes.length">
                            Показано {{ filteredAthletes.length }} из {{ athletes.length }} спортсменов
                        </div>
                    </div>

                    <div style="margin-bottom: 20px;">
                        <button class="action primary" @click="openAthleteModal()">
                            <i class="bi bi-person-add"> </i> Добавить спортсмена
                        </button>
                    </div>

                    <div class="table-container">
                        <table class="participants-table">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>ФИО</th>
                                    <th>Дата рождения</th>
                                    <th>Возраст</th>
                                    <th>Разряд</th>
                                    <th>Отделение</th>
                                    <th>Тренер</th>
                                    <th>Группа</th>
                                    <th></th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(a, i) in filteredAthletes" :key="a.id">
                                    <td>{{ i + 1 }}</td>
                                    <td><strong>{{ athleteName(a) }}</strong></td>
                                    <td>{{ formatDate(a.birth_date) }}</td>
                                    <td>{{ calculateAge(a.birth_date) }}</td>
                                    <td><span class="rank-badge">{{ a.last_rank || '—' }}</span></td>
                                    <td>{{ a.group?.department?.name || '—' }}</td>
                                    <td>{{ coachName(a.group?.coach) || '—' }}</td>
                                    <td>{{ a.group?.name || '—' }}</td>
                                    <td>
                                        <button class="icon-btn" @click="openAthleteModal(a)" title="Редактировать">
                                            <i class="bi bi-pencil-square"></i>
                                        </button>
                                    </td>
                                </tr>
                                <tr v-if="!filteredAthletes.length">
                                    <td colspan="9" class="empty">Спортсмены не найдены</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- ================= СОТРУДНИКИ ================= -->
        <div v-if="activeTab === 'employees'" class="tab-content">
            <div class="reports-layout" style="grid-template-columns: 1fr;">
                <div class="reports-sidebar" style="max-width: 100%;">
                    <div class="sidebar-header">
                        <h3>Сотрудники</h3>
                        <button class="icon-btn refresh" @click="loadEmployees" title="Обновить">
                            <i class="bi bi-arrow-clockwise"></i>
                        </button>
                    </div>

                    <div class="reports-filters">
                        <div class="search-box" style="margin-bottom: 12px;">
                            <input type="text" v-model="employeeFilters.search"
                                placeholder="Поиск по ФИО или email..." />
                        </div>

                        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px;">
                            <select v-model="employeeFilters.role" class="filter-select">
                                <option value="">Все роли</option>
                                <option value="coach">Тренеры</option>
                                <option value="methodist">Методисты</option>
                                <option value="manager">Руководители</option>
                            </select>

                            <select v-model="employeeFilters.department" class="filter-select">
                                <option value="">Все отделения</option>
                                <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                                    {{ dept.name }}
                                </option>
                            </select>

                            <button v-if="hasEmployeeFilters" class="link-icon small" @click="resetEmployeeFilters">
                                ✕ Сбросить
                            </button>
                        </div>
                    </div>

                    <div class="table-container">
                        <table class="participants-table">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>ФИО</th>
                                    <th>Email</th>
                                    <th>Роль</th>
                                    <th>Отделение</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(e, i) in filteredEmployees" :key="e.id">
                                    <td>{{ i + 1 }}</td>
                                    <td><strong>{{ userFullName(e) }}</strong></td>
                                    <td>{{ e.email }}</td>
                                    <td><span class="status-badge" :class="e.role">{{ roleLabel(e.role) }}</span></td>
                                    <td>{{ e.department?.name || '—' }}</td>
                                </tr>
                                <tr v-if="!filteredEmployees.length">
                                    <td colspan="5" class="empty">Сотрудники не найдены</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- ================= РАЗРЯДЫ ================= -->
        <div v-if="activeTab === 'ranks'" class="tab-content">
            <div class="reports-layout" style="grid-template-columns: 1fr 1.2fr;">
                <!-- Левая колонка: список приказов -->
                <div class="reports-sidebar">
                    <div class="sidebar-header">
                        <h3>Приказы о присвоении разрядов</h3>
                        <button class="icon-btn refresh" @click="loadOrders" title="Обновить">
                            <i class="bi bi-arrow-clockwise"></i>
                        </button>
                    </div>

                    <div class="reports-filters">
                        <div class="search-box" style="margin-bottom: 12px;">
                            <input type="text" v-model="orderFilters.search" placeholder="Поиск по номеру..." />
                        </div>

                        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px;">
                            <select v-model="orderFilters.year" class="filter-select">
                                <option value="">Все годы</option>
                                <option v-for="year in orderYears" :key="year" :value="year">{{ year }}</option>
                            </select>

                            <button v-if="hasOrderFilters" class="link-icon small" @click="resetOrderFilters">
                                ✕ Сбросить
                            </button>
                        </div>
                    </div>

                    <div style="margin-bottom: 20px;">
                        <button class="action primary" @click="openOrderModal">
                            <i class="bi bi-file-earmark-plus"></i> Добавить приказ
                        </button>
                    </div>

                    <div class="reports-list" style="max-height: 50vh;">
                        <div v-for="o in filteredOrders" :key="o.id" class="report-card"
                            :class="{ active: selectedOrder?.id === o.id }" @click="selectOrder(o)">
                            <div class="report-card-header">
                                <div class="report-title">
                                    <h4>Приказ №{{ o.order_number }}</h4>
                                    <span class="report-date">{{ formatDate(o.order_date) }}</span>
                                </div>
                                <div style="display: flex; gap: 8px; align-items: center;">
                                    <!-- Кнопка просмотра документа -->
                                    <button v-if="o.document" class="link-icon" @click.stop="viewDocument(o)">
                                        <i class="bi bi-eye-fill"> </i> Просмотр
                                    </button>
                                    <!-- Кнопка скачивания документа -->
                                    <button v-if="o.document" class="link-icon" @click.stop="downloadDocument(o)">
                                        <i class="bi bi-download"> </i> Скачать
                                    </button>
                                    <span class="status-badge">{{ o.athletes?.length || 0 }} спортсменов</span>
                                </div>
                            </div>
                        </div>

                        <div v-if="!filteredOrders.length" class="empty-reports">
                            <p>Приказы не найдены</p>
                        </div>
                    </div>
                </div>

                <!-- Правая колонка: детали приказа -->
                <div v-if="selectedOrder" class="report-details-panel">
                    <div class="details-header">
                        <h3>Приказ №{{ selectedOrder.order_number }}</h3>
                        <div class="details-actions">
                            <!-- Кнопки просмотра и скачивания в деталях -->
                            <button v-if="selectedOrder.document" class="action outline small"
                                @click="viewDocument(selectedOrder)">
                                <i class="bi bi-eye-fill"></i>Просмотреть документ
                            </button>
                            <button v-if="selectedOrder.document" class="action outline small"
                                @click="downloadDocument(selectedOrder)">
                                <i class="bi bi-download"></i> Скачать документ
                            </button>
                            <span class="status-badge">{{ formatDate(selectedOrder.order_date) }}</span>
                        </div>
                    </div>

                    <div class="details-content">
                        <div class="details-section">
                            <h4>Список спортсменов в приказе</h4>

                            <button class="action primary small" @click="openAssignModal" style="margin-bottom: 16px;">
                                <i class="bi bi-person-add"> </i> Добавить спортсмена
                            </button>

                            <div class="participants-table-container">
                                <table class="participants-table">
                                    <thead>
                                        <tr>
                                            <th>#</th>
                                            <th>Спортсмен</th>
                                            <th>Присвоенный разряд</th>
                                            <th>Дата присвоения</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="(a, idx) in selectedOrder.athletes" :key="a.id">
                                            <td>{{ idx + 1 }}</td>
                                            <td><strong>{{ athleteName(a.athlete) }}</strong></td>
                                            <td><span class="rank-badge">{{ a.assigned_rank }}</span></td>
                                            <td>{{ formatDate(a.assignment_date) }}</td>
                                        </tr>
                                        <tr v-if="!selectedOrder.athletes?.length">
                                            <td colspan="4" class="empty">Нет спортсменов в приказе</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>

                <div v-else class="report-details-panel empty">
                    <div class="empty-details">
                        <h3>Выберите приказ</h3>
                        <p>Нажмите на приказ из списка, чтобы просмотреть детали</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- ================= МОДАЛКА СПОРТСМЕНА ================= -->
        <div v-if="showAthleteModal" class="modal-overlay" @click.self="showAthleteModal = false">
            <div class="modal-content" style="width: 500px;">
                <div class="modal-header">
                    <h3>{{ editingAthlete ? 'Редактирование спортсмена' : 'Добавление спортсмена' }}</h3>
                    <button class="icon-btn close" @click="showAthleteModal = false">✕</button>
                </div>

                <div class="modal-body">
                    <div class="form-field">
                        <label>Отделение</label>
                        <select v-model="athleteForm.department_id" @change="onModalDepartmentChange"
                            class="filter-select">
                            <option value="">Выберите отделение</option>
                            <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                                {{ dept.name }}
                            </option>
                        </select>
                    </div>

                    <div class="form-field">
                        <label>Тренер</label>
                        <select v-model="athleteForm.coach_id" @change="onModalCoachChange" class="filter-select"
                            :disabled="!athleteForm.department_id">
                            <option value="">Выберите тренера</option>
                            <option v-for="coach in modalCoaches" :key="coach.id" :value="coach.id">
                                {{ coachName(coach) }}
                            </option>
                        </select>
                    </div>

                    <div class="form-field">
                        <label>Группа</label>
                        <select v-model="athleteForm.group_id" class="filter-select" :disabled="!athleteForm.coach_id">
                            <option value="">Выберите группу</option>
                            <option v-for="group in modalGroups" :key="group.id" :value="group.id">
                                {{ group.name }}
                            </option>
                        </select>
                    </div>

                    <div class="form-field">
                        <label>Фамилия</label>
                        <input type="text" v-model="athleteForm.last_name" placeholder="Фамилия" />
                    </div>

                    <div class="form-field">
                        <label>Имя</label>
                        <input type="text" v-model="athleteForm.first_name" placeholder="Имя" />
                    </div>

                    <div class="form-field">
                        <label>Отчество</label>
                        <input type="text" v-model="athleteForm.middle_name" placeholder="Отчество" />
                    </div>

                    <div class="form-field">
                        <label>Дата рождения</label>
                        <input type="date" v-model="athleteForm.birth_date" />
                    </div>

                    <div class="form-field">
                        <label>Разряд</label>
                        <input type="text" v-model="athleteForm.last_rank" placeholder="Разряд" />
                    </div>
                </div>

                <div class="modal-footer">
                    <button class="action outline" @click="showAthleteModal = false">Отмена</button>
                    <button class="action primary" @click="saveAthlete">Сохранить</button>
                </div>
            </div>
        </div>

        <!-- ================= МОДАЛКА ПРИКАЗА (с загрузкой файла) ================= -->
        <div v-if="showOrderModal" class="modal-overlay" @click.self="showOrderModal = false">
            <div class="modal-content" style="width: 500px;">
                <div class="modal-header">
                    <h3>Новый приказ</h3>
                    <button class="icon-btn close" @click="showOrderModal = false">✕</button>
                </div>

                <div class="modal-body">
                    <div class="form-field">
                        <label>Номер приказа</label>
                        <input type="text" v-model="orderForm.order_number" placeholder="Например: 123-п" />
                    </div>

                    <div class="form-field">
                        <label>Дата приказа</label>
                        <input type="date" v-model="orderForm.order_date" />
                    </div>

                    <!-- Поле для загрузки документа -->
                    <div class="form-field file-field">
                        <label>Документ приказа (PDF, DOC, DOCX)</label>
                        <div class="file-upload" @click="$refs.orderDocumentInput.click()">
                            <input ref="orderDocumentInput" type="file" accept=".pdf,.doc,.docx"
                                @change="onOrderDocumentChange" hidden />
                            <div class="file-upload-area">
                                <span class="upload-icon"><i class="bi bi-download"></i></span>
                                <span v-if="orderDocumentName" class="file-name">{{ orderDocumentName }}</span>
                                <span v-else class="upload-text">Выберите файл или перетащите его сюда</span>
                                <span class="file-hint">PDF, DOC, DOCX до 10 МБ</span>
                            </div>
                        </div>
                        <button v-if="orderDocumentFile" class="link-icon small" @click="removeOrderDocument">
                            Удалить файл
                        </button>
                    </div>
                </div>

                <div class="modal-footer">
                    <button class="action outline" @click="showOrderModal = false">Отмена</button>
                    <button class="action primary" @click="saveOrder" :disabled="saving">
                        {{ saving ? 'Сохранение...' : 'Сохранить' }}
                    </button>
                </div>
            </div>
        </div>

        <!-- ================= МОДАЛКА ПРОСМОТРА ДОКУМЕНТА ================= -->
        <div v-if="showDocumentModal" class="modal-overlay" @click.self="showDocumentModal = false">
            <div class="modal-content protocol-modal">
                <div class="modal-header">
                    <h3>Просмотр документа</h3>
                    <button class="icon-btn close" @click="showDocumentModal = false">✕</button>
                </div>
                <div class="modal-body">
                    <iframe v-if="documentUrl" :src="documentUrl" class="protocol-viewer" frameborder="0"></iframe>
                    <div v-else class="protocol-placeholder">
                        <p>Не удалось загрузить документ</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- ================= МОДАЛКА ДОБАВЛЕНИЯ В ПРИКАЗ ================= -->
        <div v-if="showAssignModal" class="modal-overlay" @click.self="showAssignModal = false">
            <div class="modal-content" style="width: 400px;">
                <div class="modal-header">
                    <h3>Добавить спортсмена в приказ</h3>
                    <button class="icon-btn close" @click="showAssignModal = false">✕</button>
                </div>

                <div class="modal-body">
                    <div class="form-field">
                        <label>Спортсмен</label>
                        <select v-model="assignForm.athlete_id" class="filter-select">
                            <option value="">Выберите спортсмена</option>
                            <option v-for="a in athletes" :key="a.id" :value="a.id">
                                {{ athleteName(a) }} ({{ a.last_rank || 'без разряда' }})
                            </option>
                        </select>
                    </div>

                    <div class="form-field">
                        <label>Присваиваемый разряд</label>
                        <input type="text" v-model="assignForm.assigned_rank" placeholder="Например: 1 разряд" />
                    </div>

                    <div class="form-field">
                        <label>Дата присвоения</label>
                        <input type="date" v-model="assignForm.assignment_date" />
                    </div>
                </div>

                <div class="modal-footer">
                    <button class="action outline" @click="showAssignModal = false">Отмена</button>
                    <button class="action primary" @click="assignAthlete" :disabled="assignSaving">
                        {{ assignSaving ? 'Добавление...' : 'Добавить' }}
                    </button>
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
    data() {
        return {
            activeTab: 'athletes',

            // Данные
            athletes: [],
            employees: [],
            groups: [],
            coaches: [],
            departments: [],
            orders: [],
            selectedOrder: null,

            // Фильтры для спортсменов
            athleteFilters: {
                search: '',
                department: '',
                coach: '',
                group: '',
                rank: ''
            },

            // Фильтры для сотрудников
            employeeFilters: {
                search: '',
                role: '',
                department: ''
            },

            // Фильтры для приказов
            orderFilters: {
                search: '',
                year: ''
            },

            // Модалки
            showAthleteModal: false,
            editingAthlete: null,
            athleteForm: {
                department_id: '',
                coach_id: '',
                group_id: '',
                last_name: '',
                first_name: '',
                middle_name: '',
                birth_date: '',
                last_rank: ''
            },

            // Для приказов
            showOrderModal: false,
            orderForm: {
                order_number: '',
                order_date: new Date().toISOString().slice(0, 10)
            },
            orderDocumentFile: null,
            saving: false,

            // Для просмотра документа
            showDocumentModal: false,
            documentUrl: null,

            showAssignModal: false,
            assignSaving: false,
            assignForm: {
                athlete_id: '',
                assigned_rank: '',
                assignment_date: new Date().toISOString().slice(0, 10)
            },

            // Для каскадных списков в модалке
            modalCoaches: [],
            modalGroups: [],

            // Уведомления
            notification: { show: false, message: '', type: 'info' }
        }
    },

    computed: {
        // Имя загруженного документа
        orderDocumentName() {
            return this.orderDocumentFile?.name || ''
        },

        // Фильтрованные спортсмены
        filteredAthletes() {
            return this.athletes.filter(athlete => {
                if (this.athleteFilters.search) {
                    const name = this.athleteName(athlete).toLowerCase()
                    if (!name.includes(this.athleteFilters.search.toLowerCase())) return false
                }

                if (this.athleteFilters.department) {
                    if (athlete.group?.department?.id != this.athleteFilters.department) return false
                }

                if (this.athleteFilters.coach) {
                    if (athlete.group?.coach?.id != this.athleteFilters.coach) return false
                }

                if (this.athleteFilters.group) {
                    if (athlete.group?.id != this.athleteFilters.group) return false
                }

                if (this.athleteFilters.rank) {
                    if (athlete.last_rank !== this.athleteFilters.rank) return false
                }

                return true
            })
        },

        uniqueRanks() {
            const ranks = new Set()
            this.athletes.forEach(a => {
                if (a.last_rank) ranks.add(a.last_rank)
            })
            return Array.from(ranks).sort()
        },

        filteredEmployees() {
            return this.employees.filter(emp => {
                if (this.employeeFilters.search) {
                    const fullName = this.userFullName(emp).toLowerCase()
                    const email = (emp.email || '').toLowerCase()
                    const search = this.employeeFilters.search.toLowerCase()
                    if (!fullName.includes(search) && !email.includes(search)) return false
                }

                if (this.employeeFilters.role && emp.role !== this.employeeFilters.role) return false

                if (this.employeeFilters.department && emp.department?.id != this.employeeFilters.department) return false

                return true
            })
        },

        filteredOrders() {
            return this.orders.filter(order => {
                if (this.orderFilters.search) {
                    if (!order.order_number.toLowerCase().includes(this.orderFilters.search.toLowerCase())) return false
                }

                if (this.orderFilters.year) {
                    const year = new Date(order.order_date).getFullYear()
                    if (year != this.orderFilters.year) return false
                }

                return true
            })
        },

        orderYears() {
            const years = new Set()
            this.orders.forEach(o => {
                years.add(new Date(o.order_date).getFullYear())
            })
            return Array.from(years).sort((a, b) => b - a)
        },

        filteredCoaches() {
            if (!this.athleteFilters.department) return this.coaches
            return this.coaches.filter(c => c.department?.id == this.athleteFilters.department)
        },

        filteredGroups() {
            if (!this.athleteFilters.coach) return this.groups
            return this.groups.filter(g => g.coach?.id == this.athleteFilters.coach)
        },

        hasAthleteFilters() {
            return this.athleteFilters.search ||
                this.athleteFilters.department ||
                this.athleteFilters.coach ||
                this.athleteFilters.group ||
                this.athleteFilters.rank
        },

        hasEmployeeFilters() {
            return this.employeeFilters.search || this.employeeFilters.role || this.employeeFilters.department
        },

        hasOrderFilters() {
            return this.orderFilters.search || this.orderFilters.year
        }
    },

    async mounted() {
        await this.loadAthletes()
        await this.loadEmployees()
        await this.loadGroups()
        await this.loadCoaches()
        await this.loadDepartments()
        await this.loadOrders()
    },

    methods: {
        // ================= ЗАГРУЗКА =================
        async loadAthletes() {
            try {
                const res = await axios.get('/api/athletes/')
                this.athletes = res.data
            } catch (err) {
                this.showNotification('Ошибка загрузки спортсменов', 'error')
            }
        },

        async loadEmployees() {
            try {
                const res = await axios.get('/api/users/')
                this.employees = res.data
            } catch (err) {
                this.showNotification('Ошибка загрузки сотрудников', 'error')
            }
        },

        async loadGroups() {
            try {
                const res = await axios.get('/api/groups/')
                this.groups = res.data
            } catch (err) {
                console.error(err)
            }
        },

        async loadCoaches() {
            try {
                const res = await axios.get('/api/coaches/')
                this.coaches = res.data
            } catch (err) {
                console.error(err)
            }
        },

        async loadDepartments() {
            try {
                const res = await axios.get('/api/departments/')
                this.departments = res.data
            } catch (err) {
                console.error(err)
            }
        },

        async loadOrders() {
            try {
                const res = await axios.get('/api/rankassignmentorders/')
                this.orders = res.data
            } catch (err) {
                this.showNotification('Ошибка загрузки приказов', 'error')
            }
        },

        // ================= ФИЛЬТРЫ =================
        onDepartmentChange() {
            this.athleteFilters.coach = ''
            this.athleteFilters.group = ''
        },

        onCoachChange() {
            this.athleteFilters.group = ''
        },

        resetAthleteFilters() {
            this.athleteFilters = {
                search: '',
                department: '',
                coach: '',
                group: '',
                rank: ''
            }
        },

        resetEmployeeFilters() {
            this.employeeFilters = {
                search: '',
                role: '',
                department: ''
            }
        },

        resetOrderFilters() {
            this.orderFilters = {
                search: '',
                year: ''
            }
        },

        // ================= СПОРТСМЕНЫ =================
        openAthleteModal(athlete = null) {
            this.editingAthlete = athlete

            if (athlete) {
                this.athleteForm = {
                    department_id: athlete.group?.department?.id || '',
                    coach_id: athlete.group?.coach?.id || '',
                    group_id: athlete.group?.id || '',
                    last_name: athlete.last_name || '',
                    first_name: athlete.first_name || '',
                    middle_name: athlete.middle_name || '',
                    birth_date: athlete.birth_date || '',
                    last_rank: athlete.last_rank || ''
                }

                if (this.athleteForm.department_id) {
                    this.modalCoaches = this.coaches.filter(c => c.department?.id == this.athleteForm.department_id)
                }

                if (this.athleteForm.coach_id) {
                    this.modalGroups = this.groups.filter(g => g.coach?.id == this.athleteForm.coach_id)
                }
            } else {
                this.athleteForm = {
                    department_id: '',
                    coach_id: '',
                    group_id: '',
                    last_name: '',
                    first_name: '',
                    middle_name: '',
                    birth_date: '',
                    last_rank: ''
                }
                this.modalCoaches = []
                this.modalGroups = []
            }

            this.showAthleteModal = true
        },

        onModalDepartmentChange() {
            this.athleteForm.coach_id = ''
            this.athleteForm.group_id = ''
            if (this.athleteForm.department_id) {
                this.modalCoaches = this.coaches.filter(c => c.department?.id == this.athleteForm.department_id)
            } else {
                this.modalCoaches = []
            }
            this.modalGroups = []
        },

        onModalCoachChange() {
            this.athleteForm.group_id = ''
            if (this.athleteForm.coach_id) {
                this.modalGroups = this.groups.filter(g => g.coach?.id == this.athleteForm.coach_id)
            } else {
                this.modalGroups = []
            }
        },

        async saveAthlete() {
            try {
                const athleteData = {
                    last_name: this.athleteForm.last_name,
                    first_name: this.athleteForm.first_name,
                    middle_name: this.athleteForm.middle_name,
                    birth_date: this.athleteForm.birth_date,
                    last_rank: this.athleteForm.last_rank,
                    group_id: this.athleteForm.group_id || null
                }

                if (this.editingAthlete) {
                    await axios.put(`/api/athletes/${this.editingAthlete.id}/`, athleteData)
                    this.showNotification('Спортсмен обновлен', 'success')
                } else {
                    await axios.post('/api/athletes/', athleteData)
                    this.showNotification('Спортсмен добавлен', 'success')
                }

                this.showAthleteModal = false
                await this.loadAthletes()
            } catch (err) {
                this.showNotification('Ошибка сохранения', 'error')
            }
        },

        // ================= ПРИКАЗЫ =================
        openOrderModal() {
            this.orderForm = {
                order_number: '',
                order_date: new Date().toISOString().slice(0, 10)
            }
            this.orderDocumentFile = null
            this.showOrderModal = true
        },

        onOrderDocumentChange(event) {
            const file = event.target.files[0]
            if (file && file.size > 10 * 1024 * 1024) {
                this.showNotification('Файл слишком большой (макс. 10 МБ)', 'error')
                return
            }
            this.orderDocumentFile = file || null
        },

        removeOrderDocument() {
            this.orderDocumentFile = null
            if (this.$refs.orderDocumentInput) {
                this.$refs.orderDocumentInput.value = ''
            }
        },

        async saveOrder() {
            if (!this.orderForm.order_number || !this.orderForm.order_date) {
                this.showNotification('Заполните номер и дату приказа', 'error')
                return
            }

            this.saving = true

            try {
                const formData = new FormData()
                formData.append('order_number', this.orderForm.order_number)
                formData.append('order_date', this.orderForm.order_date)

                if (this.orderDocumentFile) {
                    formData.append('document', this.orderDocumentFile)
                }

                const response = await axios.post('/api/rankassignmentorders/', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                })

                this.showOrderModal = false
                this.showNotification('Приказ создан', 'success')
                await this.loadOrders()

                // Автоматически выбираем созданный приказ
                if (response.data.id) {
                    this.selectedOrder = response.data
                }
            } catch (err) {
                console.error('Ошибка создания приказа:', err)
                this.showNotification('Ошибка создания приказа', 'error')
            } finally {
                this.saving = false
            }
        },

        selectOrder(order) {
            this.selectedOrder = order
        },

        // ================= РАБОТА С ДОКУМЕНТАМИ =================
        async viewDocument(order) {
            if (!order.document) {
                this.showNotification('Документ не прикреплен', 'error')
                return
            }

            try {
                // Открываем документ в новой вкладке для просмотра
                window.open(order.document, '_blank')
            } catch (error) {
                console.error('Ошибка просмотра документа:', error)
                this.showNotification('Не удалось открыть документ', 'error')
            }
        },

        async downloadDocument(order) {
            if (!order.document) {
                this.showNotification('Документ не прикреплен', 'error')
                return
            }

            try {
                const downloadUrl = `/api/rankassignmentorders/${order.id}/download/`

                const response = await axios.get(downloadUrl, { responseType: 'blob' })

                // Получаем имя файла из заголовка Content-Disposition
                let filename = order.document.split('/').pop() // имя файла с расширением по умолчанию
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
                link.setAttribute('download', filename) // сохраняем с правильным расширением
                document.body.appendChild(link)
                link.click()
                link.remove()
                window.URL.revokeObjectURL(url)

                this.showNotification('Документ успешно скачан', 'success')
            } catch (error) {
                console.error('Ошибка скачивания документа:', error)
                if (error.response && error.response.status === 404) {
                    this.showNotification('Документ не найден на сервере', 'error')
                } else {
                    this.showNotification('Не удалось скачать документ', 'error')
                }
            }
        },
        // ================= НАЗНАЧЕНИЕ =================
        openAssignModal() {
            this.assignForm = {
                athlete_id: '',
                assigned_rank: '',
                assignment_date: new Date().toISOString().slice(0, 10)
            }
            this.showAssignModal = true
        },

        async assignAthlete() {
    if (!this.assignForm.athlete_id || !this.assignForm.assigned_rank) {
        this.showNotification('Заполните все поля', 'error')
        return
    }

    this.assignSaving = true

    try {
        // Поле должно называться rank_order
        const payload = {
            athlete_id: this.assignForm.athlete_id,
            rank_order: this.selectedOrder.id,
            assigned_rank: this.assignForm.assigned_rank,
            assignment_date: this.assignForm.assignment_date
        }

        const response = await axios.post('/api/athlete-rank-assignments/', payload)
        this.showAssignModal = false
        this.showNotification('Спортсмен добавлен в приказ', 'success')

        // ===========================
        // Обновляем last_rank у спортсмена локально
        // ===========================
        const updatedAthlete = this.athletes.find(a => a.id === this.assignForm.athlete_id)
        if (updatedAthlete) {
            updatedAthlete.last_rank = response.data.assigned_rank
        }

        // Перезагружаем приказы, чтобы отобразить нового спортсмена в приказе
        await this.loadOrders()

        // Обновляем выбранный приказ
        const updated = this.orders.find(o => o.id === this.selectedOrder.id)
        if (updated) {
            this.selectedOrder = updated
        }

    } catch (err) {
        console.error('Ошибка добавления:', err)
        console.error('Error response:', err.response?.data)

        if (err.response?.data) {
            const errorMsg = typeof err.response.data === 'object'
                ? JSON.stringify(err.response.data)
                : err.response.data
            this.showNotification(`Ошибка: ${errorMsg}`, 'error')
        } else {
            this.showNotification('Ошибка добавления спортсмена', 'error')
        }
    } finally {
        this.assignSaving = false
    }
},

        // ================= УТИЛИТЫ =================
        athleteName(a) {
            if (!a) return '—'
            return `${a.last_name || ''} ${a.first_name || ''} ${a.middle_name || ''}`.trim() || '—'
        },

        coachName(c) {
            if (!c || !c.user) return '—'
            return `${c.user.last_name || ''} ${c.user.first_name || ''}`.trim() || '—'
        },

        userFullName(u) {
            if (!u) return '—'
            return `${u.last_name || ''} ${u.first_name || ''}`.trim() || '—'
        },

        formatDate(d) {
            if (!d) return '—'
            return new Date(d).toLocaleDateString('ru-RU')
        },

        calculateAge(d) {
            if (!d) return '—'
            const today = new Date()
            const birth = new Date(d)
            let age = today.getFullYear() - birth.getFullYear()
            const monthDiff = today.getMonth() - birth.getMonth()
            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
                age--
            }
            return age
        },

        roleLabel(role) {
            const map = {
                coach: 'Тренер',
                manager: 'Руководитель',
                methodist: 'Методист'
            }
            return map[role] || role
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
    
}

.page-header {
    margin-bottom: 24px;
}

.page-header h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 600;
    color: #1f2937;
}

.tabs-container {
    margin-bottom: 24px;
}

.tabs {
    display: flex;
    gap: 8px;
    background: white;
    padding: 6px;
    border-radius: 60px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
    width: fit-content;
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

.tab-content {
    margin-top: 24px;
}

.reports-layout {
    display: grid;
    gap: 24px;
    align-items: start;
}

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

.filter-select:disabled {
    background: #f3f4f6;
    cursor: not-allowed;
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

.table-container {
    overflow-x: auto;
    max-height: 60vh;
    overflow-y: auto;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
}

.participants-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}

.participants-table th {
    text-align: left;
    padding: 12px 8px;
    background: #f8fafc;
    font-size: 13px;
    font-weight: 600;
    color: #4b5563;
    border-bottom: 2px solid #e5e7eb;
    position: sticky;
    top: 0;
    z-index: 10;
}

.participants-table td {
    padding: 10px 8px;
    border-bottom: 1px solid #e5e7eb;
    color: #1f2937;
}

.participants-table tbody tr:hover {
    background: #f3f4f6;
}

.empty {
    text-align: center;
    color: #6b7280;
    padding: 20px 0;
}

.reports-list {
    max-height: 50vh;
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

.report-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 8px;
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

.empty-reports {
    text-align: center;
    padding: 40px 0;
    color: #9ca3af;
}

.report-details-panel {
    background: white;
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    min-height: 500px;
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

.status-badge {
    padding: 4px 12px;
    border-radius: 40px;
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
}

.status-badge.coach {
    background: #dbeafe;
    color: #1e40af;
}

.status-badge.methodist {
    background: #d1fae5;
    color: #065f46;
}

.status-badge.manager {
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

.icon-btn.refresh {
    color: #3498db;
}

.icon-btn.close {
    font-size: 16px;
    color: #6b7280;
}

.icon-btn.close:hover {
    background: #fee2e2;
    color: #ef4444;
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

.modal-body {
    padding: 16px 0;
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid #e5e7eb;
}

.form-field {
    margin-bottom: 16px;
}

.form-field label {
    display: block;
    margin-bottom: 6px;
    font-size: 13px;
    font-weight: 600;
    color: #4b5563;
}

.form-field input,
.form-field select {
    width: 100%;
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

.form-field input:disabled,
.form-field select:disabled {
    background: #f3f4f6;
    cursor: not-allowed;
}

/* Стили для загрузки файла */
.file-field {
    margin-top: 20px;
}

.file-upload {
    cursor: pointer;
}

.file-upload-area {
    padding: 20px;
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

/* Стили для просмотра документов */
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

@media (max-width: 1200px) {
    .reports-layout {
        grid-template-columns: 1fr !important;
    }
}

@media (max-width: 768px) {
    .reports-page {
        padding: 12px;
    }

    .tabs {
        width: 100%;
    }

    .tab {
        flex: 1;
        justify-content: center;
        padding: 8px 12px;
        font-size: 13px;
    }

    .filter-select {
        min-width: 120px;
    }

    .modal-content {
        width: 95% !important;
        margin: 20px auto;
        padding: 16px;
    }

    .notification {
        left: 16px;
        right: 16px;
        bottom: 16px;
    }
}
</style>