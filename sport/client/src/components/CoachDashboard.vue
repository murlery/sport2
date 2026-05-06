<template>
    <div class="coach-dashboard">
        <!-- Навигация -->
        <TopNavigationBar v-if="currentUser" :title="'Панель тренера'" :user="currentUser" :tabs="tabs"
            :activeTab="activeTab" @tab-change="onTabChange" @logout="logout" />

        <!-- Контент вкладок через дочерние роуты -->
        <router-view />
    </div>
</template>

<script>
import axios from '../axios'
import TopNavigationBar from './TopNavigationBar.vue'

export default {
    name: 'CoachDashboard',
    components: { TopNavigationBar },
    data() {
        return {
            currentUser: null,
            activeTab: '',
            tabs: [
                { id: 'main', label: 'Главная', route: { name: 'CoachMain' } },
                { id: 'attendance', label: 'Посещаемость', route: { name: 'CoachAttendance' } },
                { id: 'plan', label: 'Тренировочный план', route: { name: 'training-plan-generate' } },
                { id: 'reports', label: 'Отчет по соревнованиям', route: { name: 'CoachReports' } },
            ],
        }
    },
    async mounted() {
        await this.loadCurrentUser()
        // Устанавливаем вкладку по текущему маршруту
        this.setActiveTabByRoute(this.$route.name)
    },
    watch: {
        // Следим за сменой маршрута, чтобы обновлять активную вкладку
        '$route.name'(newName) {
            this.setActiveTabByRoute(newName)
        }
    },
    methods: {
        async loadCurrentUser() {
            try {
                const cached = localStorage.getItem('user')
                if (cached) this.currentUser = JSON.parse(cached)
                const res = await axios.get('/api/auth/me/')
                this.currentUser = res.data
                localStorage.setItem('user', JSON.stringify(res.data))
            } catch (err) {
                console.error('Ошибка загрузки пользователя:', err)
            }
        },
        setActiveTabByRoute(routeName) {
            const found = this.tabs.find(tab => tab.route.name === routeName)
            this.activeTab = found ? found.id : 'main'
        },
        onTabChange(tab) {
            this.activeTab = tab.id
            if (tab.route) this.$router.push(tab.route)
        },
        logout() {
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            this.$router.push('/login')
        }
    }
}
</script>


<style scoped>
.coach-dashboard {
    min-height: 100vh;
    padding: 20px;
}

/* Контент */
.dashboard-content {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

/* Карточки */
.card {
    background: white;
    border-radius: 10px;
    padding: 25px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.card h2 {
    margin-top: 0;
    color: #2c3e50;
    margin-bottom: 20px;
}

/* Быстрые действия */
.quick-actions {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
}

.action-btn {
    padding: 15px;
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    text-align: center;
    transition: transform 0.3s;
}

.action-btn:hover {
    transform: translateY(-3px);
}

/* Уведомления */
.notification {
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 15px 25px;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    z-index: 1000;
    animation: slideIn 0.3s ease;
}

.notification.info {
    background: #3498db;
}

.notification.success {
    background: #2ecc71;
}

.notification.error {
    background: #e74c3c;
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

/* Адаптивность */
@media (max-width: 768px) {
    .quick-actions {
        grid-template-columns: 1fr;
    }
}
</style>
