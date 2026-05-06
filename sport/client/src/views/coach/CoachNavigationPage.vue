<template>
  <div class="coach-nav-page">
    <div class="card">
      <p class="eyebrow">Coach navigation</p>
      <h1 class="title">{{ title }}</h1>
      <p v-if="description" class="description">{{ description }}</p>
      <div v-if="contextText" class="context">
        <span class="label">Context</span>
        <span class="value">{{ contextText }}</span>
      </div>
      <button class="back-btn" @click="goBack">Back to dashboard</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CoachNavigationPage',
  props: {
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      default: ''
    }
  },
  computed: {
    contextText() {
      const { id } = this.$route.params
      const { group } = this.$route.query
      return id || group || ''
    }
  },
  methods: {
    goBack() {
      this.$router.push({ name: 'CoachDashboard' })
    }
  }
}
</script>

<style scoped>
.coach-nav-page {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.card {
  width: min(640px, 100%);
  background: #ffffff;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

.eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #7f8c8d;
  font-size: 12px;
  font-weight: 700;
}

.title {
  margin: 8px 0 12px;
  color: #2c3e50;
  font-size: 28px;
}

.description {
  margin: 0 0 20px;
  color: #555;
  line-height: 1.6;
}

.context {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 24px;
  padding: 12px 14px;
  background: #f8f9fb;
  border: 1px dashed #dce0e6;
  border-radius: 8px;
}

.label {
  font-weight: 700;
  color: #2c3e50;
}

.value {
  color: #34495e;
  font-weight: 500;
}

.back-btn {
  padding: 12px 18px;
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(52, 152, 219, 0.25);
}
</style>
