<script setup lang="ts">
import { onMounted } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import { useRouter } from 'vue-router'

const dashboardStore = useDashboardStore()
const router = useRouter()

onMounted(() => {
  dashboardStore.fetchAllData()
})

const navigateToLookupTables = () => {
  router.push('/lookup-tables')
}

const navigateToAgentesInfecciosos = () => {
  router.push('/agentes-infecciosos')
}
</script>

<template>
  <div class="home">
    <!-- Welcome Header -->
    <div class="welcome-header">
      <div class="hero-content">
        <h1>Welcome to MyDB</h1>
        <p class="hero-subtitle">Hospital Database Management System</p>
        <div class="hero-status">
          <div v-if="dashboardStore.isDatabaseActive" class="status-indicator active">
            <i class="pi pi-check-circle"></i>
            <span>Database Active</span>
          </div>
          <div v-else class="status-indicator inactive">
            <i class="pi pi-exclamation-circle"></i>
            <span>Database Empty</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="dashboardStore.isLoading" class="loading-section">
      <div class="loading-spinner">
        <i class="pi pi-spin pi-spinner"></i>
        <p>Loading database statistics...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="dashboardStore.error" class="error-section">
      <div class="error-message">
        <i class="pi pi-exclamation-triangle"></i>
        <h3>Unable to load database statistics</h3>
        <p>{{ dashboardStore.error }}</p>
        <Button 
          label="Retry" 
          @click="dashboardStore.fetchAllData()"
          severity="secondary"
        />
      </div>
    </div>

    <!-- Main Dashboard Content -->
    <div v-else class="dashboard-content">
      
      <!-- Two-column layout for desktop -->
      <div class="dashboard-grid">
        
        <!-- Left Column -->
        <div class="left-column">
          
          <!-- Database Statistics Overview -->
          <div class="stats-section">
            <h2>Database Overview</h2>
            <div class="stats-grid">
              <!-- Core Data Statistics -->
              <div class="stat-card primary">
                <div class="stat-icon">
                  <i class="pi pi-users"></i>
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ dashboardStore.statistics.doentes }}</div>
                  <div class="stat-label">Patients</div>
                  <div class="stat-sublabel">Registered patients</div>
                </div>
              </div>

              <div class="stat-card secondary">
                <div class="stat-icon">
                  <i class="pi pi-calendar"></i>
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ dashboardStore.statistics.internamentos }}</div>
                  <div class="stat-label">Hospitalizations</div>
                  <div class="stat-sublabel">Hospital admissions</div>
                </div>
              </div>

              <div class="stat-card accent">
                <div class="stat-icon">
                  <i class="pi pi-database"></i>
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ dashboardStore.totalRecords }}</div>
                  <div class="stat-label">Total Records</div>
                  <div class="stat-sublabel">Core database entries</div>
                </div>
              </div>

              <div class="stat-card info">
                <div class="stat-icon">
                  <i class="pi pi-sitemap"></i>
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ dashboardStore.totalLookupTables }}</div>
                  <div class="stat-label">Lookup Entries</div>
                  <div class="stat-sublabel">Reference data records</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="actions-section">
            <h2>Quick Actions</h2>
            <div class="action-buttons">
              <Button 
                label="Manage Lookup Tables" 
                icon="pi pi-table" 
                @click="navigateToLookupTables"
                severity="primary"
                size="large"
                class="action-btn primary"
              />
              
              <Button 
                label="Infectious Agents" 
                icon="pi pi-sitemap" 
                @click="navigateToAgentesInfecciosos"
                severity="secondary"
                size="large"
                class="action-btn"
              />
            </div>
          </div>

        </div>

        <!-- Right Column -->
        <div class="right-column">
          
          <!-- Lookup Tables Summary -->
          <div class="lookup-summary">
            <h2>Lookup Tables Status</h2>
            <div class="lookup-cards">
              <div class="lookup-card available" @click="navigateToAgentesInfecciosos">
                <div class="lookup-header">
                  <div class="lookup-icon" style="background-color: #e74c3c;">
                    <i class="pi pi-sitemap"></i>
                  </div>
                  <div class="lookup-count">{{ dashboardStore.statistics.agentesInfecciosos }}</div>
                </div>
                <div class="lookup-body">
                  <h3>Infectious Agents</h3>
                  <p>Manage disease agents and pathogens</p>
                  <div class="lookup-status implemented">
                    <i class="pi pi-check-circle"></i>
                    <span>Available</span>
                  </div>
                </div>
              </div>

              <div class="lookup-card coming-soon">
                <div class="lookup-header">
                  <div class="lookup-icon" style="background-color: #f39c12;">
                    <i class="pi pi-exclamation-triangle"></i>
                  </div>
                  <div class="lookup-count">{{ dashboardStore.statistics.tiposAcidente }}</div>
                </div>
                <div class="lookup-body">
                  <h3>Accident Types</h3>
                  <p>Classification of accident types</p>
                  <div class="lookup-status coming-soon-status">
                    <i class="pi pi-clock"></i>
                    <span>Coming Soon</span>
                  </div>
                </div>
              </div>

              <div class="lookup-card coming-soon">
                <div class="lookup-header">
                  <div class="lookup-icon" style="background-color: #e67e22;">
                    <i class="pi pi-sun"></i>
                  </div>
                  <div class="lookup-count">{{ dashboardStore.statistics.agentesQueimadura }}</div>
                </div>
                <div class="lookup-body">
                  <h3>Burn Agents</h3>
                  <p>Burn-causing agents and substances</p>
                  <div class="lookup-status coming-soon-status">
                    <i class="pi pi-clock"></i>
                    <span>Coming Soon</span>
                  </div>
                </div>
              </div>

              <div class="lookup-card coming-soon">
                <div class="lookup-header">
                  <div class="lookup-icon" style="background-color: #9b59b6;">
                    <i class="pi pi-cog"></i>
                  </div>
                  <div class="lookup-count">{{ dashboardStore.statistics.mecanismosQueimadura }}</div>
                </div>
                <div class="lookup-body">
                  <h3>Burn Mechanisms</h3>
                  <p>Heat transfer mechanisms</p>
                  <div class="lookup-status coming-soon-status">
                    <i class="pi pi-clock"></i>
                    <span>Coming Soon</span>
                  </div>
                </div>
              </div>

              <div class="lookup-card coming-soon">
                <div class="lookup-header">
                  <div class="lookup-icon" style="background-color: #3498db;">
                    <i class="pi pi-map-marker"></i>
                  </div>
                  <div class="lookup-count">{{ dashboardStore.statistics.origensDestino }}</div>
                </div>
                <div class="lookup-body">
                  <h3>Origin/Destination</h3>
                  <p>Admission and discharge locations</p>
                  <div class="lookup-status coming-soon-status">
                    <i class="pi pi-clock"></i>
                    <span>Coming Soon</span>
                  </div>
                </div>
              </div>

            </div>
          </div>

        </div>
        
      </div>

    </div>
  </div>
</template>

<style scoped>
.home {
  width: 100vw;
  max-width: 100vw;
  padding: 2rem 4rem;
  margin: 0;
  min-height: calc(100vh - 120px);
  background: #f5f7fa;
  box-sizing: border-box;
}

/* Welcome Header */
.welcome-header {
  text-align: center;
  margin-bottom: 4rem;
  padding: 3rem 0;
  background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
  border-radius: 16px;
  color: white;
  box-shadow: 0 8px 32px rgba(74, 85, 104, 0.2);
}

.hero-content h1 {
  font-size: 3rem;
  margin: 0 0 0.5rem 0;
  font-weight: 700;
}

.hero-subtitle {
  font-size: 1.3rem;
  margin: 0 0 1.5rem 0;
  opacity: 0.9;
}

.hero-status {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 25px;
  font-weight: 500;
}

.status-indicator.active {
  background: rgba(39, 174, 96, 0.3);
}

.status-indicator.inactive {
  background: rgba(231, 76, 60, 0.3);
}

/* Loading and Error States */
.loading-section, .error-section {
  text-align: center;
  padding: 4rem 2rem;
}

.loading-spinner i {
  font-size: 3rem;
  color: #3498db;
  margin-bottom: 1rem;
}

.loading-spinner p {
  font-size: 1.2rem;
  color: #666;
}

.error-message {
  max-width: 500px;
  margin: 0 auto;
}

.error-message i {
  font-size: 3rem;
  color: #e74c3c;
  margin-bottom: 1rem;
}

.error-message h3 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.error-message p {
  color: #666;
  margin-bottom: 1.5rem;
}

/* Dashboard Content */
.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Two-column layout for desktop */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 4rem;
  min-height: 600px;
  align-items: start;
  width: 100%;
  max-width: 100%;
}

.left-column,
.right-column {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.stats-section h2,
.lookup-summary h2,
.actions-section h2 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
}

/* Stats Grid - Adjusted for left column */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1.5rem;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  color: white;
}

.stat-card.primary .stat-icon {
  background: #4a5568;
}

.stat-card.secondary .stat-icon {
  background: #718096;
}

.stat-card.accent .stat-icon {
  background: #2d3748;
}

.stat-card.info .stat-icon {
  background: #4a5568;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: bold;
  color: #2c3e50;
  line-height: 1;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 1.1rem;
  color: #2c3e50;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.stat-sublabel {
  font-size: 0.9rem;
  color: #666;
}

/* Lookup Tables Summary */
.lookup-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.lookup-stat {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.lookup-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.lookup-details {
  flex: 1;
}

.lookup-number {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
  line-height: 1;
}

.lookup-name {
  font-size: 0.9rem;
  color: #2c3e50;
  font-weight: 500;
  margin: 0.25rem 0;
}

.lookup-status {
  font-size: 0.8rem;
  font-weight: 500;
}

.lookup-status.implemented {
  color: #27ae60;
}

.lookup-status.coming-soon {
  color: #f39c12;
}

/* Lookup Tables Cards */
.lookup-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
  margin-top: 1.5rem;
}

.lookup-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 2px solid transparent;
  transition: all 0.3s ease;
  cursor: pointer;
}

.lookup-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.lookup-card.available {
  border-color: #4a5568;
  background: white;
}

.lookup-card.available:hover {
  border-color: #2d3748;
  background: #f7fafc;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.lookup-card.coming-soon {
  border-color: #a0aec0;
  opacity: 0.8;
  background: #f7fafc;
}

.lookup-card.coming-soon:hover {
  border-color: #718096;
  opacity: 0.9;
}

.lookup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.lookup-count {
  background: #4a5568;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 16px;
  font-weight: 600;
  font-size: 1.1rem;
}

.lookup-body h3 {
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
}

.lookup-body p {
  color: #666;
  margin: 0 0 1rem 0;
  line-height: 1.4;
}

.lookup-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.implemented-status {
  color: #27ae60;
}

.coming-soon-status {
  color: #f39c12;
}

/* Actions Section */
.actions-section {
  text-align: center;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.action-btn {
  min-width: 200px;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
}

/* Responsive Design */
@media (max-width: 1400px) {
  .home {
    padding: 2rem 3rem;
  }
  
  .dashboard-grid {
    gap: 3rem;
  }
}

@media (max-width: 1200px) {
  .home {
    padding: 2rem;
  }
  
  .dashboard-grid {
    grid-template-columns: 1fr;
    gap: 3rem;
  }
  
  .lookup-cards {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .lookup-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .home {
    padding: 1rem;
  }
  
  .hero-content h1 {
    font-size: 2.2rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .lookup-cards {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .hero-content h1 {
    font-size: 1.8rem;
  }
  
  .hero-subtitle {
    font-size: 1.1rem;
  }
  
  .stats-section h2,
  .lookup-summary h2,
  .actions-section h2 {
    font-size: 1.5rem;
  }
}
</style>
