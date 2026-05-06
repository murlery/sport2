import { createRouter, createWebHistory } from 'vue-router'
import Login from '../components/Login.vue'
import ManagerDashboard from '../components/ManagerDashboard.vue'
import CoachDashboard from '../components/CoachDashboard.vue'
import MethodistDashboard from '../components/MethodistDashboard.vue'
import Reports from '../views/coach/Reports.vue'
import GroupDetails from '../views/coach/GroupDetails.vue'
import GroupAttendance from '../views/coach/GroupAttendance.vue'
import CoachAttendancePage from '../views/coach/CoachAttendancePage.vue'
import AddAthlete from '../views/coach/AddAthlete.vue'
import TrainingPlan from '../views/coach/TrainingPlanGenerate.vue'
import CoachGroups from '../views/coach/CoachGroups.vue'

import ManagerMain from '../views/manager/ManagerMain.vue'
import ManagerDocs from '../views/manager/ManagerDocs.vue'

import MethodistMain from '../views/methodist/MethodistMain.vue'
import MethodistStats from '../views/methodist/MethodistStats.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login },

  // Manager routes
  {
    path: '/manager',
    name: 'ManagerDashboard',
    component: ManagerDashboard,
    children: [
      { path: '', name: 'ManagerMain', component: ManagerMain },
      { path: 'docs', name: 'ManagerDocs', component: ManagerDocs }
    ]
  },

  // Coach routes
  {
    path: '/coach',
    name: 'CoachDashboard',
    component: CoachDashboard,
    children: [
      { path: '', name: 'CoachMain', component: CoachGroups }, // Главная вкладка
      { path: 'attendance', name: 'CoachAttendance', component: CoachAttendancePage },
      { path: 'plan', name: 'training-plan-generate', component: TrainingPlan },
      { path: 'reports', name: 'CoachReports', component: Reports }
    ]
  },
  { path: '/coach/groups/:id', name: 'CoachGroupDetails', component: GroupDetails },
  { path: '/coach/groups/:id/attendance', name: 'CoachGroupAttendance', component: GroupAttendance },
  { path: '/coach/athletes/new', name: 'CoachAddAthlete', component: AddAthlete },

  // Methodist
  {
    path: '/methodist',
    component: MethodistDashboard,
    children: [
      { path: '', name: 'MethodistMain', component: MethodistMain },
      { path: 'stats', name: 'MethodistStats', component: MethodistStats }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
