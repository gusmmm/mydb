<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useDoenteStore } from '@/stores/doente'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import type { Doente, DoenteCreate } from '@/services/api'

const doenteStore = useDoenteStore()
const toast = useToast()
const confirm = useConfirm()

// Dialog states
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const editingDoente = ref<Doente | null>(null)

// Form data
const newDoente = ref<DoenteCreate>({
  nome: '',
  numero_processo: 0,
  data_nascimento: null,
  sexo: 'M',
  morada: '',
})

const editData = ref<Partial<Doente>>({})

// Load data on mount
onMounted(() => {
  doenteStore.fetchDoentes()
})

// Add new patient
const handleAdd = async () => {
  try {
    await doenteStore.createDoente(newDoente.value)
    showAddDialog.value = false
    resetForm()
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Patient added successfully',
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to add patient',
      life: 3000
    })
  }
}

// Edit patient
const handleEdit = (doente: Doente) => {
  editingDoente.value = doente
  editData.value = { ...doente }
  showEditDialog.value = true
}

const handleUpdate = async () => {
  if (!editingDoente.value) return
  
  try {
    await doenteStore.updateDoente(editingDoente.value.id, editData.value)
    showEditDialog.value = false
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Patient updated successfully',
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to update patient',
      life: 3000
    })
  }
}

// Delete patient
const handleDelete = (doente: Doente) => {
  confirm.require({
    message: `Are you sure you want to delete patient "${doente.nome}"?`,
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
        await doenteStore.deleteDoente(doente.id)
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Patient deleted successfully',
          life: 3000
        })
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete patient',
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
      await doenteStore.updateDoente(data.id, updates)
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

// Format date for display
const formatDate = (dateString: string | null) => {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleDateString('pt-PT')
  } catch {
    return dateString
  }
}

// Format date for input
const formatDateForInput = (dateString: string | null) => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    return date.toISOString().split('T')[0]
  } catch {
    return ''
  }
}

const resetForm = () => {
  newDoente.value = {
    nome: '',
    numero_processo: 0,
    data_nascimento: null,
    sexo: 'M',
    morada: '',
  }
}
</script>

<template>
  <div class="doentes-view">
    <div class="header-section">
      <h2>Patients</h2>
      <p>Manage the patients database</p>
      
      <div class="actions">
        <Button 
          label="Add New Patient" 
          icon="pi pi-plus" 
          @click="showAddDialog = true"
          severity="primary"
        />
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="doenteStore.loading" class="loading">
      <i class="pi pi-spinner pi-spin"></i>
      Loading...
    </div>

    <!-- Error state -->
    <Message 
      v-if="doenteStore.error" 
      severity="error" 
      :closable="true"
      @close="doenteStore.clearError"
    >
      {{ doenteStore.error }}
    </Message>

    <!-- Data Table -->
    <DataTable 
      v-if="!doenteStore.loading && !doenteStore.error"
      :value="doenteStore.doentes" 
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
      
      <Column field="nome" header="Name" sortable style="width: 250px; min-width: 200px">
        <template #editor="{ data, field }">
          <InputText v-model="data[field]" autofocus />
        </template>
      </Column>
      
      <Column field="numero_processo" header="Process Number" sortable style="width: 150px; min-width: 120px">
        <template #editor="{ data, field }">
          <InputText v-model.number="data[field]" type="number" />
        </template>
      </Column>
      
      <Column field="sexo" header="Gender" sortable style="width: 100px; min-width: 80px">
        <template #body="{ data }">
          <span :class="`gender-badge gender-${data.sexo.toLowerCase()}`">
            {{ data.sexo === 'M' ? 'Male' : 'Female' }}
          </span>
        </template>
        <template #editor="{ data, field }">
          <select v-model="data[field]" class="p-inputtext p-component">
            <option value="M">Male</option>
            <option value="F">Female</option>
          </select>
        </template>
      </Column>
      
      <Column field="data_nascimento" header="Birth Date" sortable style="width: 130px; min-width: 120px">
        <template #body="{ data }">
          <span>{{ formatDate(data.data_nascimento) }}</span>
        </template>
        <template #editor="{ data, field }">
          <InputText 
            v-model="data[field]" 
            type="date"
            :value="formatDateForInput(data[field])"
            @input="data[field] = $event.target.value"
          />
        </template>
      </Column>
      
      <Column field="morada" header="Address" sortable style="width: 300px; min-width: 200px">
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

    <!-- Add Patient Dialog -->
    <Dialog 
      v-model:visible="showAddDialog" 
      header="Add New Patient" 
      modal 
      style="width: 500px"
    >
      <div class="form-grid">
        <div class="form-field">
          <label for="nome">Name *</label>
          <InputText 
            id="nome"
            v-model="newDoente.nome" 
            placeholder="Patient name"
            class="w-full"
          />
        </div>
        
        <div class="form-field">
          <label for="numero_processo">Process Number *</label>
          <InputText 
            id="numero_processo"
            v-model.number="newDoente.numero_processo" 
            type="number"
            placeholder="Unique process number"
            class="w-full"
          />
        </div>
        
        <div class="form-field">
          <label for="sexo">Gender *</label>
          <select 
            id="sexo"
            v-model="newDoente.sexo" 
            class="p-inputtext p-component w-full"
          >
            <option value="M">Male</option>
            <option value="F">Female</option>
          </select>
        </div>
        
        <div class="form-field">
          <label for="data_nascimento">Birth Date</label>
          <InputText 
            id="data_nascimento"
            v-model="newDoente.data_nascimento" 
            type="date"
            class="w-full"
          />
        </div>
        
        <div class="form-field">
          <label for="morada">Address *</label>
          <InputText 
            id="morada"
            v-model="newDoente.morada" 
            placeholder="Patient address"
            class="w-full"
          />
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          @click="showAddDialog = false"
          severity="secondary"
          outlined
        />
        <Button 
          label="Add Patient" 
          icon="pi pi-check" 
          @click="handleAdd"
          :disabled="!newDoente.nome || !newDoente.numero_processo || !newDoente.morada"
        />
      </template>
    </Dialog>

    <!-- Edit Patient Dialog -->
    <Dialog 
      v-model:visible="showEditDialog" 
      header="Edit Patient" 
      modal 
      style="width: 500px"
    >
      <div v-if="editData" class="form-grid">
        <div class="form-field">
          <label for="edit_nome">Name *</label>
          <InputText 
            id="edit_nome"
            v-model="editData.nome" 
            placeholder="Patient name"
            class="w-full"
          />
        </div>
        
        <div class="form-field">
          <label for="edit_numero_processo">Process Number *</label>
          <InputText 
            id="edit_numero_processo"
            v-model.number="editData.numero_processo" 
            type="number"
            placeholder="Unique process number"
            class="w-full"
          />
        </div>
        
        <div class="form-field">
          <label for="edit_sexo">Gender *</label>
          <select 
            id="edit_sexo"
            v-model="editData.sexo" 
            class="p-inputtext p-component w-full"
          >
            <option value="M">Male</option>
            <option value="F">Female</option>
          </select>
        </div>
        
        <div class="form-field">
          <label for="edit_data_nascimento">Birth Date</label>
          <InputText 
            id="edit_data_nascimento"
            v-model="editData.data_nascimento" 
            type="date"
            :value="formatDateForInput(editData.data_nascimento)"
            @input="editData.data_nascimento = $event.target.value"
            class="w-full"
          />
        </div>
        
        <div class="form-field">
          <label for="edit_morada">Address *</label>
          <InputText 
            id="edit_morada"
            v-model="editData.morada" 
            placeholder="Patient address"
            class="w-full"
          />
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          @click="showEditDialog = false"
          severity="secondary"
          outlined
        />
        <Button 
          label="Update Patient" 
          icon="pi pi-check" 
          @click="handleUpdate"
          :disabled="!editData.nome || !editData.numero_processo || !editData.morada"
        />
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.doentes-view {
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

.editable-table {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

/* Wide table styling to match AgentesInfecciosView */
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

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

.empty-cell {
  color: #999;
  font-style: italic;
}

.gender-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
  text-align: center;
}

.gender-m {
  background-color: #e3f2fd;
  color: #1976d2;
}

.gender-f {
  background-color: #fce4ec;
  color: #c2185b;
}

.form-grid {
  display: grid;
  gap: 1rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
  font-size: 0.9rem;
}

.w-full {
  width: 100%;
}

/* Responsive adjustments */
@media (max-width: 1200px) {
  .doentes-view {
    padding: 2rem;
  }
}

@media (max-width: 768px) {
  .doentes-view {
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