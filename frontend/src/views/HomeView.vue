<script setup lang="ts">
import { onMounted } from 'vue'
import { useAgenteInfecciosoStore } from '@/stores/agenteInfeccioso'

const agenteStore = useAgenteInfecciosoStore()

onMounted(() => {
  agenteStore.fetchAgentes()
})
</script>

<template>
  <div class="home">
    <div class="welcome-section">
      <h2>Welcome to MyDB</h2>
      <p>Hospital Database Management System</p>
      
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">{{ agenteStore.totalAgentes }}</div>
          <div class="stat-label">Infectious Agents</div>
        </div>
        
        <div class="stat-card">
          <div class="stat-number">{{ Object.keys(agenteStore.agentesPorTipo).length }}</div>
          <div class="stat-label">Agent Types</div>
        </div>
      </div>

      <div class="quick-actions">
        <h3>Quick Actions</h3>
        <div class="action-buttons">
          <Button 
            label="Manage Infectious Agents" 
            icon="pi pi-database" 
            @click="$router.push('/agentes-infecciosos')"
            severity="primary"
            size="large"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.welcome-section h2 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.welcome-section p {
  color: #666;
  margin-bottom: 2rem;
  font-size: 1.1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: #27ae60;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: #666;
  font-weight: 500;
}

.quick-actions h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}
</style>
