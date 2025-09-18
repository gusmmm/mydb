<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAgenteInfecciosoStore } from '@/stores/agenteInfeccioso'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import type { AgenteInfeccioso, AgenteInfecciosoCreate } from '@/services/api'

const agenteStore = useAgenteInfecciosoStore()
const toast = useToast()
const confirm = useConfirm()

// Dialog states
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const editingAgente = ref<AgenteInfeccioso | null>(null)

// Form data
const newAgente = ref<AgenteInfecciosoCreate>({
  nome: '',
  tipo_agente: '',
  codigo_snomedct: null,
  subtipo_agent: null,
})

const editData = ref<Partial<AgenteInfeccioso>>({})

// Load data on mount
onMounted(() => {
  agenteStore.fetchAgentes()
})

// Add new agent
const handleAdd = async () => {
  try {
    await agenteStore.createAgente(newAgente.value)
    showAddDialog.value = false
    resetForm()
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Infectious agent added successfully',
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to add infectious agent',
      life: 3000
    })
  }
}

// Edit agent
const handleEdit = (agente: AgenteInfeccioso) => {
  editingAgente.value = agente
  editData.value = { ...agente }
  showEditDialog.value = true
}

const handleUpdate = async () => {
  if (!editingAgente.value) return
  
  try {
    await agenteStore.updateAgente(editingAgente.value.id, editData.value)
    showEditDialog.value = false
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Infectious agent updated successfully',
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to update infectious agent',
      life: 3000
    })
  }
}

// Delete agent
const handleDelete = (agente: AgenteInfeccioso) => {
  confirm.require({
    message: `Are you sure you want to delete "${agente.nome}"?`,
    header: 'Confirm Deletion',
    icon: 'pi pi-exclamation-triangle',
    rejectProps: {
      label: 'Cancel',
      severity: 'secondary',
      outlined: true
    },
    acceptProps: {
      label: 'Delete',
      severity: 'danger'
    },
    accept: async () => {
      try {
        await agenteStore.deleteAgente(agente.id)
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Infectious agent deleted successfully',
          life: 3000
        })
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete infectious agent',
          life: 3000
        })
      }
    }
  })
}

// Cell editing
const onCellEditComplete = async (event: any) => {
  const { data, newValue, field } = event
  
  if (newValue !== data[field]) {
    try {
      const updates = { [field]: newValue }
      await agenteStore.updateAgente(data.id, updates)
      data[field] = newValue
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: `${field} updated successfully`,
        life: 2000
      })
    } catch (error) {
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: `Failed to update ${field}`,
        life: 3000
      })
      // Revert the change
      event.preventDefault()
    }
  }
}

const resetForm = () => {
  newAgente.value = {
    nome: '',
    tipo_agente: '',
    codigo_snomedct: null,
    subtipo_agent: null,
  }
}
</script>

<template>
  <div class="agentes-view">
    <div class="header-section">
      <h2>Infectious Agents</h2>
      <p>Manage the infectious agents lookup table</p>
      
      <div class="actions">
        <Button 
          label="Add New Agent" 
          icon="pi pi-plus" 
          @click="showAddDialog = true"
          severity="primary"
        />
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="agenteStore.loading" class="loading">
      <i class="pi pi-spinner pi-spin"></i>
      Loading...
    </div>

    <!-- Error state -->
    <Message 
      v-if="agenteStore.error" 
      severity="error" 
      :closable="true"
      @close="agenteStore.clearError"
    >
      {{ agenteStore.error }}
    </Message>

    <!-- Data Table -->
    <DataTable 
      v-if="!agenteStore.loading && !agenteStore.error"
      :value="agenteStore.agentes" 
      editMode="cell" 
      @cell-edit-complete="onCellEditComplete"
      class="editable-table wide-table"
      paginator
      :rows="10"
      :rowsPerPageOptions="[5, 10, 20, 50]"
      sortField="nome"
      :sortOrder="1"
      scrollable
      scrollHeight="600px"
    >
      <Column field="id" header="ID" sortable style="width: 80px; min-width: 80px" />
      
      <Column field="nome" header="Agent Name" sortable style="width: 300px; min-width: 250px">
        <template #editor="{ data, field }">
          <InputText v-model="data[field]" autofocus />
        </template>
      </Column>
      
      <Column field="tipo_agente" header="Agent Type" sortable style="width: 150px; min-width: 120px">
        <template #editor="{ data, field }">
          <InputText v-model="data[field]" />
        </template>
      </Column>
      
      <Column field="subtipo_agent" header="Agent Subtype" sortable style="width: 200px; min-width: 150px">
        <template #body="{ data }">
          <span v-if="data.subtipo_agent">{{ data.subtipo_agent }}</span>
          <span v-else class="empty-cell">-</span>
        </template>
        <template #editor="{ data, field }">
          <InputText v-model="data[field]" />
        </template>
      </Column>
      
      <Column field="codigo_snomedct" header="SNOMED CT Code" sortable style="width: 180px; min-width: 150px">
        <template #body="{ data }">
          <span v-if="data.codigo_snomedct">{{ data.codigo_snomedct }}</span>
          <span v-else class="empty-cell">-</span>
        </template>
        <template #editor="{ data, field }">
          <InputText v-model="data[field]" />
        </template>
      </Column>
      
      <Column header="Actions" style="width: 120px; min-width: 120px">
        <template #body="{ data }">
          <div class="action-buttons">
            <Button 
              icon="pi pi-pencil" 
              @click="handleEdit(data)"
              severity="info"
              text
              size="small"
              v-tooltip="'Edit'"
            />
            <Button 
              icon="pi pi-trash" 
              @click="handleDelete(data)"
              severity="danger"
              text
              size="small"
              v-tooltip="'Delete'"
            />
          </div>
        </template>
      </Column>
    </DataTable>

    <!-- Add Dialog -->
    <Dialog 
      v-model:visible="showAddDialog" 
      modal 
      header="Add New Infectious Agent"
      style="width: 500px"
    >
      <div class="form-grid">
        <div class="field">
          <label for="nome">Name *</label>
          <InputText id="nome" v-model="newAgente.nome" required />
        </div>
        
        <div class="field">
          <label for="tipo_agente">Type *</label>
          <InputText id="tipo_agente" v-model="newAgente.tipo_agente" required />
        </div>
        
        <div class="field">
          <label for="subtipo_agent">Subtype</label>
          <InputText id="subtipo_agent" v-model="newAgente.subtipo_agent" />
        </div>
        
        <div class="field">
          <label for="codigo_snomedct">SNOMED CT Code</label>
          <InputText id="codigo_snomedct" v-model="newAgente.codigo_snomedct" />
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" @click="showAddDialog = false" severity="secondary" />
        <Button 
          label="Add" 
          @click="handleAdd" 
          :disabled="!newAgente.nome || !newAgente.tipo_agente"
        />
      </template>
    </Dialog>

    <!-- Edit Dialog -->
    <Dialog 
      v-model:visible="showEditDialog" 
      modal 
      header="Edit Infectious Agent"
      style="width: 500px"
    >
      <div class="form-grid">
        <div class="field">
          <label for="edit_nome">Name *</label>
          <InputText id="edit_nome" v-model="editData.nome" required />
        </div>
        
        <div class="field">
          <label for="edit_tipo_agente">Type *</label>
          <InputText id="edit_tipo_agente" v-model="editData.tipo_agente" required />
        </div>
        
        <div class="field">
          <label for="edit_subtipo_agent">Subtype</label>
          <InputText id="edit_subtipo_agent" v-model="editData.subtipo_agent" />
        </div>
        
        <div class="field">
          <label for="edit_codigo_snomedct">SNOMED CT Code</label>
          <InputText id="edit_codigo_snomedct" v-model="editData.codigo_snomedct" />
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" @click="showEditDialog = false" severity="secondary" />
        <Button label="Update" @click="handleUpdate" />
      </template>
    </Dialog>

    <!-- Toast and Confirm Dialog -->
    <Toast />
    <ConfirmDialog />
  </div>
</template>

<style scoped>
.agentes-view {
  padding: 2rem 4rem;
  max-width: 100%;
  width: 100%;
  background: #f5f7fa;
  min-height: calc(100vh - 120px);
}

.header-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 2rem;
}

.header-section h2 {
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 700;
}

.header-section p {
  color: #666;
  margin: 0 0 1.5rem 0;
  font-size: 1.1rem;
}

.actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.loading {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 1.1rem;
  color: #666;
  padding: 2rem;
  justify-content: center;
}

.loading i {
  font-size: 1.5rem;
}

.form-grid {
  display: grid;
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
}

.field label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

.empty-cell {
  color: #999;
  font-style: italic;
}

/* Wide table styling */
.wide-table {
  min-width: 100%;
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

:deep(.wide-table .p-datatable-table) {
  min-width: 1000px;
  width: 100%;
  border-collapse: collapse;
}

/* Ensure alternating row colors for better readability */
:deep(.wide-table .p-datatable-tbody > tr:nth-child(even)) {
  background-color: #f8f9fa !important;
}

:deep(.wide-table .p-datatable-tbody > tr:nth-child(even) > td) {
  background-color: #f8f9fa !important;
}

:deep(.wide-table .p-datatable-tbody > tr:nth-child(odd)) {
  background-color: #ffffff !important;
}

:deep(.wide-table .p-datatable-tbody > tr:nth-child(odd) > td) {
  background-color: #ffffff !important;
}

:deep(.wide-table .p-datatable-thead > tr > th) {
  white-space: nowrap;
  padding: 1rem 0.75rem;
  font-weight: 600;
  background-color: #e9ecef !important;
  color: #212529 !important;
  border-bottom: 2px solid #dee2e6;
}

:deep(.wide-table .p-datatable-tbody > tr > td) {
  padding: 0.75rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
  background-color: #ffffff !important;
  color: #212529 !important;
}

:deep(.editable-table .p-datatable-tbody > tr > td.p-cell-editing) {
  padding: 0.5rem;
  background-color: #fff3cd !important;
  border: 2px solid #ffc107 !important;
}

:deep(.editable-table .p-datatable-tbody > tr:hover) {
  background-color: #e3f2fd !important;
}

:deep(.editable-table .p-datatable-tbody > tr:hover > td) {
  background-color: #e3f2fd !important;
  color: #1565c0 !important;
}

/* Responsive adjustments */
@media (max-width: 1200px) {
  .agentes-view {
    padding: 2rem;
  }
}

@media (max-width: 768px) {
  .agentes-view {
    padding: 1rem;
  }
  
  .header-section {
    padding: 1.5rem;
  }
  
  .header-section h2 {
    font-size: 1.5rem;
  }
}
</style>