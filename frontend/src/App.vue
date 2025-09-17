<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import TabMenu from 'primevue/tabmenu'
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const items = [
  { label: 'Home', icon: 'pi pi-home', to: '/', command: () => router.push('/') },
  { label: 'Agentes Infecciosos', icon: 'pi pi-database', to: '/agentes-infecciosos', command: () => router.push('/agentes-infecciosos') },
]

const activeIndex = ref(0)

// Update active index based on current route
watch(() => route.path, (newPath) => {
  if (newPath === '/') {
    activeIndex.value = 0
  } else if (newPath === '/agentes-infecciosos') {
    activeIndex.value = 1
  }
}, { immediate: true })
</script>

<template>
  <div class="layout">
    <header class="header">
      <h1>MyDB - Hospital Database Management</h1>
      <TabMenu :model="items" v-model:activeIndex="activeIndex" />
    </header>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #f8f9fa;
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.header h1 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1.8rem;
}

.main-content {
  flex: 1;
  padding: 1rem 2rem;
  max-width: 100%;
  width: 100%;
  overflow-x: auto;
}
</style>
