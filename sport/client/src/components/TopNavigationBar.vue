<template>
  <header class="topbar">
    <!-- LEFT -->
    <div class="topbar-left">
      <img src="../assets/logo.png" alt="Логотип" class="logo" />
    </div>

    <!-- CENTER NAV -->
    <nav class="topbar-nav" v-if="tabs.length">
      <ul ref="navList">
        <li v-for="tab in tabs" :key="tab.id">
          <a :class="{ active: isActiveTab(tab) }" @click="handleTabClick(tab)">
            <span class="link-text">{{ tab.label }}</span>
          </a>
        </li>
        <div class="link-background" :style="bgStyle"></div>
      </ul>
    </nav>

    <!-- RIGHT -->
    <div class="topbar-right">
      <slot name="right">
        <div v-if="user" class="user-name">
          {{ fullName }}
        </div>
        <button class="btn-exit" @click="handleLogout">Выйти</button>
      </slot>
    </div>
  </header>
</template>

<script>
import { ref, onMounted, watch, nextTick, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export default {
  name: 'TopNavigationBar',
  props: {
    title: { type: String, default: 'Панель управления' },
    user: { type: Object, default: null },
    tabs: {
      type: Array,
      default: () => [
        { id: 'main', label: 'Главная', route: { name: 'ManagerMain' } },
        { id: 'docs', label: 'Документы', route: { name: 'ManagerDocs' } }
      ]
    }
  },
  emits: ['logout'],
  setup(props, { emit }) {
    const bgStyle = ref({ left: '0px', width: '0px', top: '0px', height: '0px' })
    const navList = ref(null)
    const route = useRoute()
    const router = useRouter()

    const PADDING_X = 6
    const PADDING_Y = 6

    const isActiveTab = (tab) => route.name === tab.route.name

    const updateBg = () => {
      nextTick(() => {
        if (!navList.value) return

        const activeEl = navList.value.querySelector('a.active')
        // если активного элемента нет или он скрыт — скрываем фон
        if (!activeEl || activeEl.offsetParent === null) {
          bgStyle.value = { left: '0px', width: '0px', top: '0px', height: '0px' }
          return
        }

        const ulTop = navList.value.getBoundingClientRect().top
        const elTop = activeEl.getBoundingClientRect().top
        const offsetTop = elTop - ulTop + PADDING_Y

        bgStyle.value = {
          left: `${activeEl.offsetLeft + PADDING_X}px`,
          width: `${activeEl.offsetWidth - PADDING_X * 2}px`,
          top: `${offsetTop}px`,
          height: `${activeEl.offsetHeight - PADDING_Y * 2}px`
        }
      })
    }

    const handleTabClick = (tab) => {
      if (tab.route) router.push(tab.route)
    }

    const handleLogout = () => emit('logout')

    const onResize = () => updateBg()

    onMounted(() => {
      updateBg()
      window.addEventListener('resize', onResize)
    })

    onBeforeUnmount(() => {
      window.removeEventListener('resize', onResize)
    })

    watch(() => route.name, () => updateBg())

    return { bgStyle, navList, isActiveTab, handleTabClick, handleLogout }
  },
  computed: {
    fullName() {
      if (!this.user) return '—'
      const { first_name, last_name, middle_name, username } = this.user
      return `${last_name || ''} ${first_name || ''} ${middle_name || ''}`.trim() || username || '—'
    }
  }
}
</script>

<style scoped>
.topbar {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  padding: 1px 26px;
  background: linear-gradient(135deg, #1a1ac9, #1a1ac9);
  border-radius: 22px;
  color: white;
}

/* CENTER NAV */
.topbar-nav ul {
  position: relative;
  display: flex;
  list-style: none;
  padding: 6px;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 30px;
  overflow: hidden;
}

.topbar-nav li { z-index: 1 }

.topbar-nav a {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 26px;
  border-radius: 24px;
  font-weight: 700;
  color: #eae7ff;
  cursor: pointer;
  transition: color 0.25s ease;
}

.topbar-nav a.active { color: white }

.link-background {
  position: absolute;
  background: #1a1ac9;
  border-radius: 24px;
  z-index: 0;
  transition: all 0.35s cubic-bezier(0.7, 0, 0.38, 0.86);
}

.link-text { position: relative; z-index: 1 }

.topbar-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  line-height: 1;
}

.topbar-left { display: flex; align-items: center }

.btn-exit {
  padding: 10px 22px;
  border-radius: 22px;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  color: white;
  font-weight: 700;
  cursor: pointer;
  transition: 0.25s ease;
}

.btn-exit:hover { background: rgba(255, 255, 255, 0.25); transform: translateY(-1px) }

.logo { height: 44px; width: auto; object-fit: contain; transition: 0.3s ease }

/* Media Queries */
@media (max-width: 1024px) { .logo { height: 38px } }
@media (max-width: 768px) {
  .logo { height: 32px }
  .topbar { padding: 8px 14px; border-radius: 16px }
  .user-name { display: none }
  .btn-exit { padding: 8px 16px; font-size: 13px }
}
@media (max-width: 480px) { .logo { height: 26px } }
</style>