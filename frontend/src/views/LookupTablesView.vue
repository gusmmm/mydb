<script setup lang="ts">
import { onMounted } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import { useRouter } from 'vue-router'

const dashboardStore = useDashboardStore()
const router = useRouter()

onMounted(() => {
  dashboardStore.fetchStatistics()
})

const lookupTables = [
  {
    id: 'agentes-infecciosos',
    name: 'Agentes Infecciosos',
    description: 'Manage infectious disease agents and pathogens',
    icon: 'pi-sitemap',
    route: '/agentes-infecciosos',
    count: () => dashboardStore.statistics.agentesInfecciosos,
    implemented: true,
    color: '#e74c3c'
  },
  {
    id: 'tipos-acidente',
    name: 'Tipos de Acidente',
    description: 'Classification of accident types',
    icon: 'pi-exclamation-triangle',
    route: '/tipos-acidente',
    count: () => dashboardStore.statistics.tiposAcidente,
    implemented: false,
    color: '#f39c12'
  },
  {
    id: 'agentes-queimadura',
    name: 'Agentes de Queimadura',
    description: 'Burn-causing agents and substances',
    icon: 'pi-sun',
    route: '/agentes-queimadura',
    count: () => dashboardStore.statistics.agentesQueimadura,
    implemented: false,
    color: '#e67e22'
  },
  {
    id: 'mecanismos-queimadura',
    name: 'Mecanismos de Queimadura',
    description: 'Heat transfer mechanisms in burns',
    icon: 'pi-cog',
    route: '/mecanismos-queimadura',
    count: () => dashboardStore.statistics.mecanismosQueimadura,
    implemented: false,
    color: '#9b59b6'
  },
  {
    id: 'origens-destino',
    name: 'Origens e Destinos',
    description: 'Patient admission and discharge locations',
    icon: 'pi-map-marker',
    route: '/origens-destino',
    count: () => dashboardStore.statistics.origensDestino,
    implemented: false,
    color: '#3498db'
  }
]

const navigateToTable = (table: any) => {
  if (table.implemented) {
    router.push(table.route)
  }
}
</script>

<template>
  <div class="lookup-tables">
    <div class="header">
      <h2>Lookup Tables Management</h2>
      <p>Manage reference data and classification systems</p>
    </div>

    <div class="tables-grid">
      <div 
        v-for="table in lookupTables" 
        :key="table.id"
        class="table-card"
        :class="{ 
          'implemented': table.implemented,
          'not-implemented': !table.implemented 
        }"
        @click="navigateToTable(table)"
      >
        <div class="card-header">
          <div 
            class="table-icon" 
            :style="{ backgroundColor: table.color }"
          >
            <i :class="`pi ${table.icon}`"></i>
          </div>
          <div class="table-count" v-if="!dashboardStore.isLoading">
            {{ table.count() }}
          </div>
          <div class="table-count" v-else>
            <i class="pi pi-spin pi-spinner"></i>
          </div>
        </div>
        
        <div class="card-body">
          <h3>{{ table.name }}</h3>
          <p>{{ table.description }}</p>
        </div>
        
        <div class="card-footer">
          <div v-if="table.implemented" class="status-badge implemented">
            <i class="pi pi-check"></i>
            Available
          </div>
          <div v-else class="status-badge coming-soon">
            <i class="pi pi-clock"></i>
            Coming Soon
          </div>
        </div>
      </div>
    </div>

    <div class="back-button">
      <Button 
        label="Back to Dashboard" 
        icon="pi pi-arrow-left" 
        @click="$router.push('/')"
        severity="secondary"
        text
      />
    </div>
  </div>
</template>

<style scoped>
.lookup-tables {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  text-align: center;
  margin-bottom: 3rem;
}

.header h2 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 2.5rem;
}

.header p {
  color: #666;
  font-size: 1.2rem;
}

.tables-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.table-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 2px solid transparent;
  position: relative;
}

.table-card.implemented {
  cursor: pointer;
}

.table-card.implemented:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: #3498db;
}

.table-card.not-implemented {
  opacity: 0.7;
  cursor: not-allowed;
}

.table-card.not-implemented:hover {
  opacity: 0.8;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.table-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.table-count {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
}

.card-body h3 {
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-size: 1.3rem;
}

.card-body p {
  color: #666;
  margin: 0;
  line-height: 1.5;
}

.card-footer {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 500;
  font-size: 0.9rem;
}

.status-badge.implemented {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.status-badge.coming-soon {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.back-button {
  text-align: center;
  margin-top: 2rem;
}
</style>