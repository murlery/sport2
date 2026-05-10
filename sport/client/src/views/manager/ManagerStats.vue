<template>
    <div class="methodist-page">
        <section class="card stats-card">

            <!-- HEADER -->
            <div class="card-header">
                <div>
                    <p class="eyebrow">Статистика</p>
                    <h2>Годовая статистика руководителя</h2>
                </div>

                <div class="inline-actions">

                    <!-- ФИЛЬТР ОТДЕЛЕНИЯ -->
                    <select v-model="filters.department">
                        <option value="">Все отделения</option>
                        <option v-for="d in departments" :key="d.id" :value="d.name">
                            {{ d.name }}
                        </option>
                    </select>

                    <!-- ФИЛЬТР УРОВНЯ -->
                    <select v-model="filters.level">
                        <option value="">Все уровни</option>
                        <option v-for="l in levels" :key="l" :value="l">
                            {{ l }}
                        </option>
                    </select>

                    <!-- ГОД -->
                    <select v-model="statsYear">
                        <option v-for="y in years" :key="y" :value="String(y)">
                            {{ y }}
                        </option>
                    </select>

                    <button class="export-btn" @click="exportYearlyStats">
                        Экспорт в xlsx
                    </button>
                </div>
            </div>

            <!-- 🏆 ТОП ОТДЕЛЕНИЯ -->
            <div class="stats-block monthly">
                <div class="block-header">
                    <h3>Топ-отделения за год</h3>
                </div>

                <div class="table-container">
                    <table class="data-table hoverable">
                        <thead>
                            <tr>
                                <th>Место</th>
                                <th>Отделение</th>
                                <th>Соревнований</th>
                                <th>Участников</th>
                                <th>Призовых мест</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr v-for="(row, index) in topDepartments" :key="row.department">
                                <td><strong>#{{ index + 1 }}</strong></td>
                                <td>{{ row.department }}</td>
                                <td>{{ row.events }}</td>
                                <td>{{ row.participants }}</td>
                                <td>{{ row.prizePlaces }}</td>
                            </tr>

                            <tr v-if="!topDepartments.length">
                                <td colspan="5" class="empty">Нет данных</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- 📊 ГОДОВАЯ СТАТИСТИКА -->
            <div class="stats-block quarterly">
                <div class="block-header">
                    <h3>Годовая статистика ({{ statsYear }})</h3>
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
                            <tr v-for="row in yearlyStats" :key="row.key">
                                <td>{{ row.department }}</td>
                                <td>{{ row.level }}</td>
                                <td>{{ row.events }}</td>
                                <td>{{ row.participants }}</td>
                                <td>{{ row.prizePlaces }}</td>
                            </tr>

                            <tr v-if="!yearlyStats.length">
                                <td colspan="5" class="empty">Нет данных за год</td>
                            </tr>
                        </tbody>

                        <tfoot v-if="yearlyStats.length">
                            <tr class="summary-row">
                                <td colspan="2"><strong>Итого</strong></td>
                                <td>{{ totalEvents }}</td>
                                <td>{{ totalParticipants }}</td>
                                <td>{{ totalPrizes }}</td>
                            </tr>
                        </tfoot>
                    </table>
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
    name: 'ManagerYearStats',

    data() {
        const now = new Date()

        return {
            statsYear: String(now.getFullYear()),
            competitions: [],

            departments: [],

            filters: {
                department: '',
                level: ''
            },

            levels: [
                'Локальный',
                'Городской',
                'Региональный',
                'Федеральный',
                'Всероссийский'
            ]
        }
    },

    async mounted() {
        await this.loadData()
    },

    computed: {

        years() {
            const y = new Date().getFullYear()
            return [y - 1, y, y + 1]
        },

        approvedReports() {
            return this.competitions.filter(c => c.status === 'approved')
        },

        // =========================
        // ФИЛЬТРОВАННАЯ БАЗА
        // =========================
        filteredReports() {

            return this.approvedReports.filter(c => {

                const yearOk =
                    new Date(c.date).getFullYear() === Number(this.statsYear)

                const deptOk =
                    !this.filters.department ||
                    c.coach?.department?.name === this.filters.department

                const levelOk =
                    !this.filters.level ||
                    c.level === this.filters.level

                return yearOk && deptOk && levelOk
            })
        },

        // =========================
        // ГОДОВАЯ СТАТИСТИКА
        // =========================
        yearlyStats() {

            const grouped = {}

            this.filteredReports.forEach(c => {

                const dept = c.coach?.department?.name || '—'
                const key = `${dept}|${c.level}`

                const results = c.results || []

                const participants = results.length

                const prizePlaces = results.filter(
                    r => !r.is_participant && r.place
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

                grouped[key].events++
                grouped[key].participants += participants
                grouped[key].prizePlaces += prizePlaces
            })

            return Object.values(grouped)
        },

        // =========================
        // ТОП ОТДЕЛЕНИЯ
        // =========================
        topDepartments() {

            const map = {}

            this.yearlyStats.forEach(r => {

                if (!map[r.department]) {
                    map[r.department] = {
                        department: r.department,
                        events: 0,
                        participants: 0,
                        prizePlaces: 0
                    }
                }

                map[r.department].events += r.events
                map[r.department].participants += r.participants
                map[r.department].prizePlaces += r.prizePlaces
            })

            return Object.values(map)
                .sort((a, b) => b.prizePlaces - a.prizePlaces)
                .slice(0, 5)
        },

        totalEvents() {
            return this.yearlyStats.reduce((a, b) => a + b.events, 0)
        },

        totalParticipants() {
            return this.yearlyStats.reduce((a, b) => a + b.participants, 0)
        },

        totalPrizes() {
            return this.yearlyStats.reduce((a, b) => a + b.prizePlaces, 0)
        }
    },

    methods: {

        async loadData() {
            try {
                const res = await axios.get('/api/competitions/')
                const dep = await axios.get('/api/departments/')

                this.competitions = res.data
                this.departments = dep.data

            } catch (e) {
                console.error(e)
            }
        },

        exportYearlyStats() {

            const rows = [
                ['ГОДОВАЯ СТАТИСТИКА'],
                [`Год: ${this.statsYear}`],
                [],
                ['Отделение', 'Уровень', 'Соревнований', 'Участников', 'Призовых мест']
            ]

            this.yearlyStats.forEach(r => {
                rows.push([
                    r.department,
                    r.level,
                    r.events,
                    r.participants,
                    r.prizePlaces
                ])
            })

            rows.push([])

            rows.push([
                'ИТОГО',
                '',
                this.totalEvents,
                this.totalParticipants,
                this.totalPrizes
            ])

            const ws = XLSX.utils.aoa_to_sheet(rows)
            const wb = XLSX.utils.book_new()

            XLSX.utils.book_append_sheet(wb, ws, 'Годовая статистика')

            const file = XLSX.write(wb, {
                bookType: 'xlsx',
                type: 'array'
            })

            saveAs(
                new Blob([file], {
                    type: 'application/octet-stream'
                }),
                `Годовая_статистика_${this.statsYear}.xlsx`
            )
        }
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
</style>
