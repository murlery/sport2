<template>
    <section class="card docs">
        <div class="card-header">
            <div>
                <h2>Формирование документов</h2>
            </div>
        </div>

        <div class="form-grid">
            <label class="field">
                <span>Тип документа</span>
                <select v-model="docForm.doc_type">
                    <option v-for="t in docTypes" :key="t" :value="t">{{ t }}</option>
                </select>
            </label>
        </div>

        <!-- Динамическая форма в зависимости от типа документа -->
<div v-if="docForm.doc_type === 'Справка (освобождение)'" class="dynamic-form">
    <div class="form-row">
        <label class="field">
            <span>ФИО спортсмена</span>

            <div class="autocomplete-wrapper">
                <input
                    v-model="athleteSearch"
                    @input="onAthleteInput"
                    @focus="filterAthletes"
                    @blur="handleAthleteBlur"
                    placeholder="Начните вводить ФИО спортсмена"
                    class="autocomplete-input"
                />

                <ul
                    v-if="filteredAthletes.length && showAthleteDropdown"
                    class="autocomplete-list"
                >
                    <li
                        v-for="ath in filteredAthletes"
                        :key="ath.id"
                        @mousedown="selectAthlete(ath)"
                    >
                        <div class="athlete-name">
                            {{ getAthleteFullName(ath) }}
                        </div>

                        <div class="athlete-details">
                            {{ ath.group?.name || 'Без группы' }}
                        </div>
                    </li>
                </ul>
            </div>
        </label>

        <!-- ВРУЧНУЮ -->
        <label class="field">
            <span>Группа / Класс</span>

            <input
                v-model="docForm.group"
                placeholder="Введите группу / класс"
            />
        </label>
    </div>

    <div class="form-row">
        <label class="field">
            <span>Дата начала освобождения</span>
            <input type="date" v-model="docForm.start_date" />
        </label>

        <label class="field">
            <span>Дата окончания освобождения</span>
            <input type="date" v-model="docForm.end_date" />
        </label>
    </div>

    <div class="form-row">
        <label class="field full-width">
            <span>Название соревнования / мероприятия</span>

            <input
                v-model="docForm.event_name"
                placeholder="Введите название соревнования / мероприятия"
            />
        </label>
    </div>

    <div class="form-row">
        <label class="field">
            <span>Учебное заведение (в дательном падеже)</span>

            <input
                v-model="docForm.institution_name"
                placeholder="Введите учебное заведение"
            />
        </label>

        <label class="field">
            <span>Директор (ФИО)</span>

            <input
                v-model="docForm.director_name"
                placeholder="Введите ФИО директора"
            />
        </label>
    </div>

    <div class="form-row">
        <label class="field">
            <span>ФИО тренера (ответственный)</span>

            <div class="autocomplete-wrapper">
                <input
                    v-model="coachSearch"
                    @input="onCoachInput"
                    @focus="filterCoaches"
                    @blur="handleCoachBlur"
                    placeholder="Начните вводить ФИО тренера"
                    class="autocomplete-input"
                />

                <ul
                    v-if="filteredCoaches.length && showCoachDropdown"
                    class="autocomplete-list"
                >
                    <li
                        v-for="coach in filteredCoaches"
                        :key="coach.id"
                        @mousedown="selectCoach(coach)"
                    >
                        <div class="athlete-name">
                            {{ getCoachFullName(coach) }}
                        </div>

                        <div class="athlete-details">
                            {{ coach.position || 'Тренер' }}
                        </div>
                    </li>
                </ul>
            </div>
        </label>
    </div>
</div>

        <!-- Форма для приказа на автобус -->
        <div v-else-if="docForm.doc_type === 'Приказ (автобус)'" class="dynamic-form">
            <div class="form-row">
                <label class="field">
                    <span>Отделение</span>
                    <div class="autocomplete-wrapper">
                        <input v-model="busDepartmentSearch" @input="filterDepartments" @focus="filterDepartments"
                            @blur="handleDepartmentBlur" placeholder="Введите отделение"
                            class="autocomplete-input" />
                        <ul v-if="filteredDepartments.length && showDepartmentDropdown" class="autocomplete-list">
                            <li v-for="dept in filteredDepartments" :key="dept.id" @mousedown="selectDepartment(dept)">
                                <div class="athlete-name">{{ dept.name }}</div>
                                <div class="athlete-details">{{ dept.description || 'Отделение' }}</div>
                            </li>
                        </ul>
                    </div>
                </label>
                <label class="field">
                    <span>Название группы</span>
                    <div class="autocomplete-wrapper">
                        <input v-model="busGroupSearch" @input="filterGroupsForBus" @focus="filterGroupsForBus"
                            @blur="handleBusGroupBlur" placeholder="Введите название группы"
                            class="autocomplete-input" />
                        <ul v-if="filteredBusGroups.length && showBusGroupDropdown" class="autocomplete-list">
                            <li v-for="group in filteredBusGroups" :key="group.id" @mousedown="selectBusGroup(group)">
                                <div class="athlete-name">{{ group.name }}</div>
                                <div class="athlete-details">{{ group.coach_name || 'Тренер: не указан' }}</div>
                            </li>
                        </ul>
                    </div>
                </label>
            </div>

            <div class="form-row">
                <label class="field">
                    <span>Тренер/сопровождающий</span>
                    <div class="autocomplete-wrapper">
                        <input v-model="busCoachSearch" @input="filterBusCoaches" @focus="filterBusCoaches"
                            @blur="handleBusCoachBlur" placeholder="Начните вводить ФИО тренера"
                            class="autocomplete-input" />
                        <ul v-if="filteredBusCoaches.length && showBusCoachDropdown" class="autocomplete-list">
                            <li v-for="coach in filteredBusCoaches" :key="coach.id" @mousedown="selectBusCoach(coach)">
                                <div class="athlete-name">{{ getCoachFullName(coach) }}</div>
                                <div class="athlete-details">{{ coach.position || 'Тренер' }}</div>
                            </li>
                        </ul>
                    </div>
                </label>
                <label class="field">
                    <span>Количество спортсменов</span>
                    <input type="number" v-model="docForm.bus_athletes_count" placeholder="Например: 12" />
                </label>
            </div>

            <div class="form-row">
                <label class="field">
                    <span>Дата отправления</span>
                    <input type="date" v-model="docForm.bus_departure_date" />
                </label>
                <label class="field">
                    <span>Дата возвращения</span>
                    <input type="date" v-model="docForm.bus_return_date" />
                </label>
            </div>

            <div class="form-row">
                <label class="field full-width">
                    <span>Пункт назначения</span>
                    <input v-model="docForm.bus_destination" placeholder="Введите пункт назначения" />
                </label>
            </div>

            <div class="form-row">
                <label class="field full-width">
                    <span>Название мероприятия</span>
                    <input v-model="docForm.bus_event_name"
                        placeholder="Введите название мероприятия" />
                </label>
            </div>
        </div>

        <div class="actions end">
            <button class="btn ghost" @click="resetDocForm">Очистить</button>
            <button class="btn primary" :disabled="loadingDoc" @click="generateDoc">
                {{ loadingDoc ? 'Генерируем...' : 'Сгенерировать и скачать' }}
            </button>
        </div>

        <!-- Сообщение об ошибке -->
        <div v-if="error" class="error-message">
            {{ error }}
        </div>
    </section>
</template>

<script>
import axios from '../../axios'
import {
    Document,
    Packer,
    Paragraph,
    TextRun,
    AlignmentType,
    Table,
    TableRow,
    TableCell,
    WidthType,
    BorderStyle
} from 'docx'

export default {
    name: 'ManagerDocs',
    data() {
        return {
            docForm: {
                doc_type: 'Справка (освобождение)',
                content: '',
                student_name: '',
                student_id: null,
                group: '',
                start_date: '',
                end_date: '',
                event_name: '',
                institution_name: '',
                director_name: '',
                coach_name: '',
                coach_id: null,
                bus_departure_date: '',
                bus_return_date: '',
                bus_destination: '',
                bus_department: '',
                bus_group_name: '',
                bus_coach_name: '',
                bus_coach_id: null,
                bus_athletes_count: '',
                bus_event_name: ''
            },
            docTypes: ['Приказ (автобус)', 'Справка (освобождение)'],
            loadingDoc: false,
            recentDocs: [],
            error: null,

            // Данные для автодополнения
            athletes: [],
            coaches: [],
            groupsList: [],
            departments: [],

            athleteSearch: '',
            coachSearch: '',
            groupSearch: '',
            busCoachSearch: '',
            busDepartmentSearch: '',
            busGroupSearch: '',

            filteredAthletes: [],
            filteredCoaches: [],
            filteredGroupsExemption: [],
            filteredBusCoaches: [],
            filteredDepartments: [],
            filteredBusGroups: [],

            showAthleteDropdown: false,
            showCoachDropdown: false,
            showGroupExemptionDropdown: false,
            showBusCoachDropdown: false,
            showDepartmentDropdown: false,
            showBusGroupDropdown: false,

            loadingAthletes: false,
            loadingCoaches: false,
            loadingGroups: false,
            loadingDepartments: false
        }
    },

    async mounted() {
        await this.loadRecentDocs()
        await this.loadAthletes()
        await this.loadCoaches()
        await this.loadGroupsList()
        await this.loadDepartments()
    },

    methods: {
        async loadRecentDocs() {
            try {
                const response = await axios.get('/api/admin-docs/')
                this.recentDocs = response.data.slice(0, 5)
            } catch (error) {
                console.error('Ошибка загрузки документов:', error)
            }
        },

        async loadAthletes() {
            this.loadingAthletes = true
            try {
                const response = await axios.get('/api/athletes/', {
                    params: { limit: 100 }
                })
                this.athletes = response.data
                console.log('Загружено спортсменов:', this.athletes.length)
            } catch (error) {
                console.error('Ошибка загрузки спортсменов:', error)
                this.athletes = []
            } finally {
                this.loadingAthletes = false
            }
        },

        async loadCoaches() {
            this.loadingCoaches = true
            try {
                const response = await axios.get('/api/coaches/', {
                    params: { limit: 100 }
                })
                this.coaches = response.data
                console.log('Загружено тренеров:', this.coaches.length)
            } catch (error) {
                console.error('Ошибка загрузки тренеров:', error)
                this.coaches = []
            } finally {
                this.loadingCoaches = false
            }
        },

        async loadGroupsList() {
            this.loadingGroups = true
            try {
                const response = await axios.get('/api/groups/', {
                    params: { limit: 100 }
                })
                this.groupsList = response.data
                console.log('Загружено групп:', this.groupsList.length)
            } catch (error) {
                console.error('Ошибка загрузки групп:', error)
                this.groupsList = []
            } finally {
                this.loadingGroups = false
            }
        },

        async loadDepartments() {
            this.loadingDepartments = true
            try {
                const response = await axios.get('/api/departments/', {
                    params: { limit: 100 }
                })
                this.departments = response.data
                console.log('Загружено отделений:', this.departments.length)
            } catch (error) {
                console.error('Ошибка загрузки отделений:', error)
                this.departments = []
            } finally {
                this.loadingDepartments = false
            }
        },

        filterAthletes() {
            const search = this.athleteSearch.toLowerCase().trim()
            if (!search) {
                this.filteredAthletes = []
                this.showAthleteDropdown = false
                return
            }
            this.filteredAthletes = this.athletes.filter(ath => {
                const fullName = this.getAthleteFullName(ath).toLowerCase()
                return fullName.includes(search)
            }).slice(0, 10)
            this.showAthleteDropdown = this.filteredAthletes.length > 0
        },

        filterCoaches() {
            const search = this.coachSearch.toLowerCase().trim()
            if (!search) {
                this.filteredCoaches = []
                this.showCoachDropdown = false
                return
            }
            this.filteredCoaches = this.coaches.filter(coach => {
                const fullName = this.getCoachFullName(coach).toLowerCase()
                return fullName.includes(search)
            }).slice(0, 10)
            this.showCoachDropdown = this.filteredCoaches.length > 0
        },

        filterGroupsForExemption() {
            const search = this.groupSearch.toLowerCase().trim()
            if (!search) {
                this.filteredGroupsExemption = []
                this.showGroupExemptionDropdown = false
                return
            }
            this.filteredGroupsExemption = this.groupsList.filter(group => {
                const name = group.name?.toLowerCase() || ''
                return name.includes(search)
            }).slice(0, 10)
            this.showGroupExemptionDropdown = this.filteredGroupsExemption.length > 0
        },

        filterDepartments() {
            const search = this.busDepartmentSearch.toLowerCase().trim()
            if (!search) {
                this.filteredDepartments = []
                this.showDepartmentDropdown = false
                return
            }
            this.filteredDepartments = this.departments.filter(dept => {
                const name = dept.name?.toLowerCase() || ''
                return name.includes(search)
            }).slice(0, 10)
            this.showDepartmentDropdown = this.filteredDepartments.length > 0
        },

        filterGroupsForBus() {
            const search = this.busGroupSearch.toLowerCase().trim()
            if (!search) {
                this.filteredBusGroups = []
                this.showBusGroupDropdown = false
                return
            }
            this.filteredBusGroups = this.groupsList.filter(group => {
                const name = group.name?.toLowerCase() || ''
                return name.includes(search)
            }).slice(0, 10)
            this.showBusGroupDropdown = this.filteredBusGroups.length > 0
        },

        filterBusCoaches() {
            const search = this.busCoachSearch.toLowerCase().trim()
            if (!search) {
                this.filteredBusCoaches = []
                this.showBusCoachDropdown = false
                return
            }
            this.filteredBusCoaches = this.coaches.filter(coach => {
                const fullName = this.getCoachFullName(coach).toLowerCase()
                return fullName.includes(search)
            }).slice(0, 10)
            this.showBusCoachDropdown = this.filteredBusCoaches.length > 0
        },

        selectAthlete(athlete) {
            this.athleteSearch = this.getAthleteFullName(athlete)
            this.docForm.student_name = this.getAthleteFullName(athlete)
            this.docForm.student_id = athlete.id
            if (athlete.group && athlete.group.name) {
                
            }
            this.showAthleteDropdown = false
        },

        selectCoach(coach) {
            this.coachSearch = this.getCoachFullName(coach)
            this.docForm.coach_name = this.getCoachFullName(coach)
            this.docForm.coach_id = coach.id
            this.showCoachDropdown = false
        },

        selectGroupForExemption(group) {
            this.groupSearch = group.name
            this.docForm.group = group.name
            this.showGroupExemptionDropdown = false
        },

        selectDepartment(dept) {
            this.busDepartmentSearch = dept.name
            this.docForm.bus_department = dept.name
            this.showDepartmentDropdown = false
        },

        selectBusGroup(group) {
            this.busGroupSearch = group.name
            this.docForm.bus_group_name = group.name
            this.showBusGroupDropdown = false
        },

        selectBusCoach(coach) {
            this.busCoachSearch = this.getCoachFullName(coach)
            this.docForm.bus_coach_name = this.getCoachFullName(coach)
            this.docForm.bus_coach_id = coach.id
            this.showBusCoachDropdown = false
        },

        handleAthleteBlur() {
            setTimeout(() => { this.showAthleteDropdown = false }, 200)
        },

        handleCoachBlur() {
            setTimeout(() => { this.showCoachDropdown = false }, 200)
        },

        handleGroupBlur() {
            setTimeout(() => { this.showGroupExemptionDropdown = false }, 200)
        },

        handleDepartmentBlur() {
            setTimeout(() => { this.showDepartmentDropdown = false }, 200)
        },

        handleBusGroupBlur() {
            setTimeout(() => { this.showBusGroupDropdown = false }, 200)
        },

        handleBusCoachBlur() {
            setTimeout(() => { this.showBusCoachDropdown = false }, 200)
        },

        getAthleteFullName(athlete) {
            if (!athlete) return ''
            const user = athlete.user || athlete
            const lastName = user.last_name || ''
            const firstName = user.first_name || ''
            const middleName = user.middle_name || ''
            return `${lastName} ${firstName} ${middleName}`.trim()
        },

        getCoachFullName(coach) {
            if (!coach) return ''
            const user = coach.user || coach
            const lastName = user.last_name || ''
            const firstName = user.first_name || ''
            const middleName = user.middle_name || ''
            return `${lastName} ${firstName} ${middleName}`.trim()
        },

        async generateDoc() {
            this.error = null

            console.log('Тип документа:', this.docForm.doc_type)
            console.log('Данные формы:', this.docForm)

            // Валидация в зависимости от типа документа
            if (this.docForm.doc_type === 'Справка (освобождение)') {
                if (!this.docForm.student_name || !this.docForm.group || !this.docForm.start_date ||
                    !this.docForm.end_date || !this.docForm.event_name || !this.docForm.institution_name ||
                    !this.docForm.director_name || !this.docForm.coach_name) {
                    this.error = 'Заполните все поля формы освобождения'
                    console.log('Не заполнены поля справки')
                    return
                }
            }
            else if (this.docForm.doc_type === 'Приказ (автобус)') {
                // Проверяем каждое поле отдельно для наглядности
                if (!this.docForm.bus_departure_date) {
                    this.error = 'Заполните дату отправления'
                    return
                }
                if (!this.docForm.bus_return_date) {
                    this.error = 'Заполните дату возвращения'
                    return
                }
                if (!this.docForm.bus_destination) {
                    this.error = 'Заполните пункт назначения'
                    return
                }
                if (!this.docForm.bus_department) {
                    this.error = 'Заполните отделение'
                    return
                }
                if (!this.docForm.bus_group_name) {
                    this.error = 'Заполните название группы'
                    return
                }
                if (!this.docForm.bus_coach_name) {
                    this.error = 'Заполните ФИО тренера'
                    return
                }
                if (!this.docForm.bus_athletes_count) {
                    this.error = 'Заполните количество спортсменов'
                    return
                }
                if (!this.docForm.bus_event_name) {
                    this.error = 'Заполните название мероприятия'
                    return
                }
            }
            else {
                if (!this.docForm.content) {
                    this.error = 'Заполните содержание документа'
                    return
                }
            }

            this.loadingDoc = true

            try {
                if (this.docForm.doc_type === 'Справка (освобождение)') {
                    await this.generateExemptionDocx()
                }
                else if (this.docForm.doc_type === 'Приказ (автобус)') {
                    await this.generateBusOrderDocx()
                }
                else {
                    await this.generateTxtDoc()
                }

                await this.loadRecentDocs()
                this.resetDocForm()
            } catch (error) {
                console.error('Ошибка генерации документа:', error)
                this.error = 'Ошибка при генерации документа: ' + (error.message || 'Неизвестная ошибка')
            } finally {
                this.loadingDoc = false
            }
        },

        async generateBusOrderDocx() {
            const today = new Date()
            const orderNumber = `№${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}${String(today.getDate()).padStart(2, '0')}`
            const currentDate = `${today.getDate().toString().padStart(2, '0')}.${(today.getMonth() + 1).toString().padStart(2, '0')}.${today.getFullYear()}`

            const departureDate = new Date(this.docForm.bus_departure_date)
            const returnDate = new Date(this.docForm.bus_return_date)

            const formatFullDate = (date) => {
                const months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                    'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
                return `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()} года`
            }

            const doc = new Document({
                styles: {
                    default: {
                        document: {
                            run: { font: "Times New Roman", size: 28 },
                            paragraph: {
                                spacing: { line: 240, after: 0, before: 0 }
                            }
                        }
                    }
                },
                sections: [{
                    properties: {
                        page: {
                            margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
                        }
                    },
                    children: [
                        new Paragraph({ alignment: AlignmentType.CENTER, indent: { left: 0, firstLine: 0 }, children: [new TextRun({ text: "Муниципальное бюджетное учреждение", size: 28 })] }),
                        new Paragraph({ alignment: AlignmentType.CENTER, indent: { left: 0, firstLine: 0 }, children: [new TextRun({ text: "дополнительного образования Шелеховского района", size: 28 })] }),
                        new Paragraph({ alignment: AlignmentType.CENTER, indent: { left: 0, firstLine: 0 }, children: [new TextRun({ text: "Спортивная школа «Юность»", bold: true, size: 28 })] }),
                        new Paragraph({ children: [] }),
                        new Paragraph({ alignment: AlignmentType.CENTER, indent: { left: 0, firstLine: 0 }, children: [new TextRun({ text: "ПРИКАЗ", bold: true, size: 32 })] }),
                        new Paragraph({ children: [] }),
                        new Paragraph({ alignment: AlignmentType.RIGHT, indent: { left: 0, firstLine: 0 }, children: [new TextRun({ text: `${currentDate} г.`, size: 28 }), new TextRun({ text: ` ${orderNumber}`, bold: true, size: 28 })] }),
                        new Paragraph({ children: [] }),
                        new Paragraph({ alignment: AlignmentType.CENTER, indent: { left: 0, firstLine: 0 }, children: [new TextRun({ text: "О выделении автотранспорта", bold: true, size: 28 })] }),
                        new Paragraph({ children: [] }),
                        new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 720 }, children: [new TextRun({ text: `В связи с проведением ${this.docForm.bus_event_name}, а также для обеспечения безопасной перевозки несовершеннолетних спортсменов,`, size: 28 })] }),
                        new Paragraph({ children: [] }),
                        new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 720 }, children: [new TextRun({ text: `ПРИКАЗЫВАЮ:`, size: 28 })] }),
                        new Paragraph({ children: [] }),
                        new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 720 }, children: [new TextRun({ text: `1. Выделить автотранспорт (школьный автобус) для перевозки делегации ${this.docForm.bus_department} в составе:`, size: 28 })] }),
                        new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: { left: 1440, firstLine: 0 }, children: [new TextRun({ text: `- группы ${this.docForm.bus_group_name} (${this.docForm.bus_athletes_count} спортсменов);`, size: 28 })] }),
                        new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: { left: 1440, firstLine: 0 }, children: [new TextRun({ text: `- тренера-преподавателя ${this.docForm.bus_coach_name}.`, size: 28 })] }),
                        new Paragraph({ children: [] }),
                        new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 720 }, children: [new TextRun({ text: `2. Установить маршрут следования: г. Шелехов - ${this.docForm.bus_destination}.`, size: 28 })] }),
                        new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 720 }, children: [new TextRun({ text: `3. Установить сроки поездки: с ${formatFullDate(departureDate)} по ${formatFullDate(returnDate)}.`, size: 28 })] }),
                        new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 720 }, children: [new TextRun({ text: `4. Назначить ответственным за жизнь и здоровье детей в пути следования тренера-преподавателя ${this.docForm.bus_coach_name}.`, size: 28 })] }),
                        new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 720 }, children: [new TextRun({ text: `5. Контроль за исполнением настоящего приказа оставляю за собой.`, size: 28 })] }),
                        new Paragraph({ children: [] }),
                        new Paragraph({ children: [] }),
                        new Paragraph({ children: [] }),
                        new Paragraph({ children: [] }),
                        new Paragraph({ alignment: AlignmentType.RIGHT, indent: { left: 0, firstLine: 0 }, children: [new TextRun({ text: "Директор", size: 28 }), new TextRun({ text: " ", size: 28 }), new TextRun({ text: "Ю.Д. Домнич", bold: true, size: 28 })] }),
                        new Paragraph({ children: [] }),
                        new Paragraph({ alignment: AlignmentType.RIGHT, indent: { left: 0, firstLine: 0 }, children: [new TextRun({ text: "С приказом ознакомлены:", size: 28 })] }),
                        new Paragraph({ children: [] }),
                        new Paragraph({ children: [] }),
                        new Paragraph({ alignment: AlignmentType.LEFT, indent: { left: 0, firstLine: 0 }, children: [new TextRun({ text: `_________________ ${this.docForm.bus_coach_name}`, size: 28 })] })
                    ]
                }]
            })

            const blob = await Packer.toBlob(doc)
            const fileName = `Приказ_автобус_${this.getCurrentDate()}.docx`

            const formData = new FormData()
            formData.append('doc_type', this.docForm.doc_type)
            formData.append('file_path', new File([blob], fileName, { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' }))

            await axios.post('/api/admin-docs/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })

            this.downloadBlob(blob, fileName)
        },

        async generateExemptionDocx() {
    // Форматируем дату
    const today = new Date()
    const letterDate = `${today.getDate().toString().padStart(2, '0')}.${(today.getMonth() + 1).toString().padStart(2, '0')}.${today.getFullYear()}г.`

    const dateRange = this.formatDateRange(this.docForm.start_date, this.docForm.end_date)

    // Фиксированная ширина страницы A4 в DXA (1 DXA = 1/1440 дюйма)
    // Ширина A4 = 8.27 дюйма = примерно 11906 DXA при полях 2.54 см
    const pageWidth = 11906 // ширина A4 без учета полей
    const leftMargin = 1440 // левое поле 2.54 см
    const rightMargin = 1440 // правое поле 2.54 см
    const availableWidth = pageWidth - leftMargin - rightMargin // доступная ширина для таблицы
    
    // Задаем фиксированную ширину колонок в DXA
    const leftColWidth = 4500   // левая колонка (фикс)
    const middleColWidth = 800  // средняя колонка (фикс, маленький отступ)
    const rightColWidth = availableWidth - leftColWidth - middleColWidth // правая колонка (оставшееся место)

    const doc = new Document({
        styles: {
            default: {
                document: {
                    run: { font: "Times New Roman", size: 28 },
                    paragraph: {
                        spacing: { line: 240, after: 0, before: 0 }
                    }
                }
            }
        },
        sections: [{
            properties: {
                page: {
                    margin: {
                        top: 1440,
                        right: 1440,
                        bottom: 1440,
                        left: 1440
                    }
                }
            },
            children: [
                // Таблица для верхней шапки с фиксированной шириной
                new Table({
                    width: { size: availableWidth, type: WidthType.DXA }, // фиксированная общая ширина
                    borders: {
                        top: { style: BorderStyle.NONE },
                        bottom: { style: BorderStyle.NONE },
                        left: { style: BorderStyle.NONE },
                        right: { style: BorderStyle.NONE },
                        insideHorizontal: { style: BorderStyle.NONE },
                        insideVertical: { style: BorderStyle.NONE }
                    },
                    rows: [
                        new TableRow({
                            children: [
                                // Левая колонка (фиксированная ширина)
                                new TableCell({
                                    width: { size: leftColWidth, type: WidthType.DXA },
                                    borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } },
                                    verticalAlign: "center",
                                    children: [
                                        new Paragraph({
                                            alignment: AlignmentType.CENTER,
                                            indent: { left: 0, firstLine: 0 },
                                            children: [new TextRun({ text: "Отдел по молодежной политике и спорту", bold: true, size: 28 })]
                                        }),
                                        new Paragraph({
                                            alignment: AlignmentType.CENTER,
                                            indent: { left: 0, firstLine: 0 },
                                            children: [new TextRun({ text: "Администрация Шелеховского муниципального района", size: 28 })]
                                        }),
                                        new Paragraph({ children: [] }),
                                        new Paragraph({
                                            alignment: AlignmentType.CENTER,
                                            indent: { left: 0, firstLine: 0 },
                                            children: [new TextRun({ text: "Спортивная школа «Юность»", bold: true, size: 28 })]
                                        }),
                                        new Paragraph({
                                            alignment: AlignmentType.CENTER,
                                            indent: { left: 0, firstLine: 0 },
                                            children: [new TextRun({ text: "666035, г.Шелехов Иркутской области", size: 28 })]
                                        }),
                                        new Paragraph({
                                            alignment: AlignmentType.CENTER,
                                            indent: { left: 0, firstLine: 0 },
                                            children: [new TextRun({ text: "1 м-он, д 44", size: 28 })]
                                        }),
                                        new Paragraph({
                                            alignment: AlignmentType.CENTER,
                                            indent: { left: 0, firstLine: 0 },
                                            children: [new TextRun({ text: "Телефон: 4-66-37", size: 28 })]
                                        }),
                                        new Paragraph({
                                            alignment: AlignmentType.CENTER,
                                            indent: { left: 0, firstLine: 0 },
                                            children: [new TextRun({ text: "E-mail: yunost-shel20@mail.ru", size: 28 })]
                                        }),
                                        new Paragraph({
                                            alignment: AlignmentType.CENTER,
                                            indent: { left: 0, firstLine: 0 },
                                            children: [
                                                new TextRun({ text: `${letterDate} б/н`, size: 28 }),
                                                new TextRun({ text: "На № ______ от ______", break: 1, size: 28 })
                                            ]
                                        }),
                                    ]
                                }),
                                
                                // Средняя колонка (фиксированная ширина - отступ)
                                new TableCell({
                                    width: { size: middleColWidth, type: WidthType.DXA },
                                    borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } },
                                    children: [new Paragraph({ children: [] })]
                                }),
                                
                                // Правая колонка (автоматическая ширина, но с фиксацией через общую ширину)
                                new TableCell({
                                    width: { size: rightColWidth, type: WidthType.DXA },
                                    borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } },
                                    verticalAlign: "center",
                                    children: [
                                        new Paragraph({
                                            indent: { left: 0, firstLine: 0 },
                                            alignment: AlignmentType.CENTER,
                                            children: [new TextRun({ text: this.docForm.institution_name, size: 28 })]
                                        }),
                                        new Paragraph({ children: [] }),
                                        new Paragraph({
                                            indent: { left: 0, firstLine: 0 },
                                            alignment: AlignmentType.CENTER,
                                            children: [new TextRun({ text: `Директору ${this.docForm.director_name}`, size: 28 })]
                                        })
                                    ]
                                })
                            ]
                        })
                    ]
                }),
                
                // Остальная часть документа...
                new Paragraph({ children: [] }),
                new Paragraph({ children: [] }),
                
                // Обращение (по центру)
                new Paragraph({
                    alignment: AlignmentType.CENTER,
                    indent: { left: 0, firstLine: 0 },
                    children: [
                        new TextRun({ text: `Уважаемый ${this.getDirectorFirstName(this.docForm.director_name)} ${this.getDirectorLastName(this.docForm.director_name)}!`, size: 28 })
                    ]
                }),
                
                new Paragraph({ children: [] }),
                new Paragraph({ children: [] }),
                
                // Основной текст
                new Paragraph({
                    alignment: AlignmentType.JUSTIFIED,
                    indent: { firstLine: 720 },
                    children: [
                        new TextRun({ 
                            text: `Муниципальное бюджетное учреждение дополнительного образования Шелеховского района спортивная школа «Юность» просит Вас освободить от занятий с ${dateRange}, студентку группы ${this.docForm.group} ${this.docForm.student_name}, для участия в ${this.docForm.event_name}.`,
                            size: 28
                        })
                    ]
                }),
                
                new Paragraph({ children: [] }),
                new Paragraph({ children: [] }),
                
                // Ответственность
                new Paragraph({
                    alignment: AlignmentType.JUSTIFIED,
                    indent: { firstLine: 720 },
                    children: [
                        new TextRun({ 
                            text: `Ответственность за жизнь и здоровье ${this.docForm.student_name} несет тренер - преподаватель ${this.docForm.coach_name}.`,
                            size: 28
                        })
                    ]
                }),
                
                new Paragraph({ children: [] }),
                new Paragraph({ children: [] }),
                new Paragraph({ children: [] }),
                new Paragraph({ children: [] }),
                
                // Подпись
                new Paragraph({
                    alignment: AlignmentType.RIGHT,
                    indent: { left: 0, firstLine: 0 },
                    children: [
                        new TextRun({ text: "Директор", size: 28 }),
                        new TextRun({ text: " ", size: 28 }),
                        new TextRun({ text: "Ю.Д. Домнич", bold: true, size: 28 })
                    ]
                })
            ]
        }]
    })
    
    const blob = await Packer.toBlob(doc)
    const fileName = `Освобождение_${this.docForm.student_name}_${this.getCurrentDate()}.docx`
    
    const formData = new FormData()
    formData.append('doc_type', this.docForm.doc_type)
    formData.append('file_path', new File([blob], fileName, { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' }))
    
    await axios.post('/api/admin-docs/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    this.downloadBlob(blob, fileName)
},
        onAthleteInput() {
    this.docForm.student_name = this.athleteSearch
    this.filterAthletes()
},

onCoachInput() {
    this.docForm.coach_name = this.coachSearch
    this.filterCoaches()
},

        async generateTxtDoc() {
            const content = this.composeDocText()
            const fileName = `${this.docForm.doc_type}_${this.getCurrentDate()}.txt`
            const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })

            const formData = new FormData()
            formData.append('doc_type', this.docForm.doc_type)
            formData.append('file_path', new File([blob], fileName, { type: 'text/plain' }))

            await axios.post('/api/admin-docs/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })

            this.downloadBlob(blob, fileName)
        },

        formatDateRange(start, end) {
            const startDate = new Date(start)
            const endDate = new Date(end)
            const startDay = startDate.getDate()
            const startMonth = startDate.toLocaleString('ru-RU', { month: 'long' })
            const endDay = endDate.getDate()
            const endMonth = endDate.toLocaleString('ru-RU', { month: 'long' })
            const year = endDate.getFullYear()

            if (startDate.getMonth() === endDate.getMonth()) {
                return `${startDay} по ${endDay} ${endMonth} ${year} года`
            } else {
                return `${startDay} ${startMonth} по ${endDay} ${endMonth} ${year} года`
            }
        },

        getDirectorFirstName(fullName) {
            const parts = fullName.trim().split(' ')
            return parts[0] || ''
        },

        getDirectorLastName(fullName) {
            const parts = fullName.trim().split(' ')
            return parts.slice(1).join(' ') || ''
        },

        composeDocText() {
            const date = new Date().toLocaleDateString('ru-RU', {
                day: 'numeric',
                month: 'long',
                year: 'numeric'
            })
            return [
                `ТИП ДОКУМЕНТА: ${this.docForm.doc_type}`,
                `ДАТА СОЗДАНИЯ: ${date}`,
                '',
                this.docForm.content,
                '',
                `---`,
                `Документ сгенерирован автоматически системой SportSchool`,
            ].join('\n')
        },

        getCurrentDate() {
            const d = new Date()
            const year = d.getFullYear()
            const month = String(d.getMonth() + 1).padStart(2, '0')
            const day = String(d.getDate()).padStart(2, '0')
            return `${year}-${month}-${day}`
        },

        formatDate(dateString) {
            if (!dateString) return '—'
            const d = new Date(dateString)
            return d.toLocaleDateString('ru-RU')
        },

        downloadBlob(blob, filename) {
            const url = window.URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = filename
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
            window.URL.revokeObjectURL(url)
        },

        async downloadDoc(doc) {
            if (!doc.file_path) {
                this.error = 'Файл не найден'
                return
            }
            try {
                const response = await axios.get(doc.file_path, {
                    responseType: 'blob'
                })
                const fileName = doc.file_path.split('/').pop()
                this.downloadBlob(response.data, fileName)
            } catch (error) {
                console.error('Ошибка скачивания:', error)
                this.error = 'Не удалось скачать документ'
            }
        },

        resetDocForm() {
            this.docForm = {
                doc_type: this.docForm.doc_type, // сохраняем текущий тип документа
                content: '',
                student_name: '',
                student_id: null,
                group: '',
                start_date: '',
                end_date: '',
                event_name: '',
                institution_name: '',
                director_name: '',
                coach_name: '',
                coach_id: null,
                bus_departure_date: '',
                bus_return_date: '',
                bus_destination: '',
                bus_department: '',
                bus_group_name: '',
                bus_coach_name: '',
                bus_coach_id: null,
                bus_athletes_count: '',
                bus_event_name: ''
            }

            // Очищаем все поисковые поля
            this.athleteSearch = ''
            this.coachSearch = ''
            this.groupSearch = ''
            this.busCoachSearch = ''
            this.busDepartmentSearch = ''
            this.busGroupSearch = ''

            // Очищаем все отфильтрованные списки
            this.filteredAthletes = []
            this.filteredCoaches = []
            this.filteredGroupsExemption = []
            this.filteredBusCoaches = []
            this.filteredDepartments = []
            this.filteredBusGroups = []

            // Закрываем все выпадающие списки
            this.showAthleteDropdown = false
            this.showCoachDropdown = false
            this.showGroupExemptionDropdown = false
            this.showBusCoachDropdown = false
            this.showDepartmentDropdown = false
            this.showBusGroupDropdown = false

            this.error = null
        },
    }
}
</script>

<style scoped>
.card {
    background: #fff;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    margin: 20px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

h2 {
    margin: 4px 0 0;
    font-size: 18px;
    color: #1f2937;
}

.form-grid {
    margin-bottom: 16px;
}

.field {
    display: flex;
    flex-direction: column;
    font-size: 14px;
    margin-bottom: 16px;
}

.field.full {
    width: 100%;
}

.field span {
    margin-bottom: 6px;
    font-weight: 600;
    color: #4b5563;
}

.field select,
.field input,
.field textarea {
    padding: 10px 12px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-size: 14px;
    outline: none;
    transition: all 0.2s;
    font-family: inherit;
}

.field select:focus,
.field input:focus,
.field textarea:focus {
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.dynamic-form {
    background: #f9fafb;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 16px;
    border: 1px solid #e5e7eb;
}

.form-row {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
}

.form-row .field {
    flex: 1;
    min-width: 180px;
}

.full-width {
    width: 100%;
}

.autocomplete-wrapper {
    position: relative;
    width: 100%;
}

.autocomplete-input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-size: 14px;
    outline: none;
    transition: all 0.2s;
}

.autocomplete-input:focus {
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.autocomplete-list {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    max-height: 250px;
    overflow-y: auto;
    z-index: 1000;
    list-style: none;
    padding: 0;
    margin: 4px 0 0;
}

.autocomplete-list li {
    padding: 10px 12px;
    cursor: pointer;
    transition: background 0.2s;
    border-bottom: 1px solid #f3f4f6;
}

.autocomplete-list li:last-child {
    border-bottom: none;
}

.autocomplete-list li:hover {
    background: #f3f4f6;
}

.athlete-name {
    font-weight: 600;
    color: #1f2937;
    font-size: 14px;
}

.athlete-details {
    font-size: 12px;
    color: #6b7280;
    margin-top: 2px;
}

.actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 20px;
}

.btn {
    padding: 10px 20px;
    border: none;
    border-radius: 40px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.btn.ghost {
    background: white;
    border: 1px solid #d1d5db;
    color: #4b5563;
}

.btn.primary {
    background: linear-gradient(135deg, #3498db, #2980b9);
    color: white;
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
}

.error-message {
    margin-top: 16px;
    padding: 12px;
    background: #fee2e2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    color: #991b1b;
    font-size: 14px;
}
/* Добавьте эти стили в ваш существующий <style scoped> */

/* Общие стили для всех полей ввода */
.field {
    display: flex;
    flex-direction: column;
    font-size: 14px;
    margin-bottom: 16px;
    min-width: 0; /* Важно для правильного сжатия */
    flex: 1 1 200px; /* Базовый размер 200px, может сжиматься и расширяться */
}

.field.full-width {
    width: 100%;
    flex: 1 1 100%;
}

/* Стили для строк формы */
.form-row {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 8px;
}

/* Убираем минимальную ширину у вложенных полей */
.form-row .field {
    min-width: 180px;
    flex: 1 1 180px;
}

/* Стили для автодополнения */
.autocomplete-wrapper {
    position: relative;
    width: 100%;
    min-width: 0;
}

/* Принудительный перенос длинных слов */
.field input,
.field select,
.field textarea,
.autocomplete-input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-size: 14px;
    outline: none;
    transition: all 0.2s;
    box-sizing: border-box; /* Важно для правильного расчета ширины */
    word-break: break-word; /* Перенос длинных слов */
}

/* Особые стили для полей с датами */
input[type="date"] {
    min-width: 140px;
}

/* Стили для числовых полей */
input[type="number"] {
    min-width: 100px;
}

/* Адаптивность для мобильных устройств */
@media (max-width: 768px) {
    .form-row {
        flex-direction: column;
        gap: 12px;
    }
    
    .form-row .field {
        min-width: 100%;
        flex: 1 1 100%;
    }
    
    input[type="date"],
    input[type="number"] {
        width: 100%;
    }
}

/* Стили для динамической формы */
.dynamic-form {
    background: #f9fafb;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
    border: 1px solid #e5e7eb;
    overflow-x: auto; /* Добавляем прокрутку при необходимости */
}

/* Стили для текстовых полей */
textarea {
    resize: vertical;
    min-height: 120px;
}

/* Стили для выпадающих списков */
.autocomplete-list {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    max-height: 250px;
    overflow-y: auto;
    overflow-x: hidden;
    z-index: 1000;
    list-style: none;
    padding: 0;
    margin: 4px 0 0;
}

.autocomplete-list li {
    padding: 10px 12px;
    cursor: pointer;
    transition: background 0.2s;
    border-bottom: 1px solid #f3f4f6;
    word-wrap: break-word;
    white-space: normal;
    overflow-wrap: break-word;
}

.athlete-name {
    font-weight: 600;
    color: #1f2937;
    font-size: 14px;
    word-break: break-word;
}

.athlete-details {
    font-size: 12px;
    color: #6b7280;
    margin-top: 2px;
    word-break: break-word;
}

/* Стили для меток полей */
.field span {
    margin-bottom: 6px;
    font-weight: 600;
    color: #4b5563;
    display: block;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Для длинных меток на мобильных */
@media (max-width: 480px) {
    .field span {
        white-space: normal;
        font-size: 12px;
    }
}
</style>