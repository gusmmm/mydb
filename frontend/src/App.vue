<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import TabMenu from 'primevue/tabmenu'
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const items = [
  { label: 'Home', icon: 'pi pi-home', to: '/', command: () => router.push('/') },
  { label: 'Lookup Tables', icon: 'pi pi-table', to: '/lookup-tables', command: () => router.push('/lookup-tables') },
  { label: 'Agentes Infecciosos', icon: 'pi pi-sitemap', to: '/agentes-infecciosos', command: () => router.push('/agentes-infecciosos') },
  { label: 'Patients', icon: 'pi pi-users', to: '/doentes', command: () => router.push('/doentes') },
  { label: 'Hospitalizations', icon: 'pi pi-heart', to: '/internamentos', command: () => router.push('/internamentos') },
]

const activeIndex = ref(0)

// Update active index based on current route
watch(() => route.path, (newPath) => {
  if (newPath === '/') {
    activeIndex.value = 0
  } else if (newPath === '/lookup-tables') {
    activeIndex.value = 1
  } else if (newPath === '/agentes-infecciosos') {
    activeIndex.value = 2
  } else if (newPath === '/doentes') {
    activeIndex.value = 3
  } else if (newPath === '/internamentos') {
    activeIndex.value = 4
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
  padding: 0;
  max-width: 100vw;
  width: 100vw;
  overflow-x: hidden;
}
</style>
