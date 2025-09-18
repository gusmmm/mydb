<template>
  <div class="internamentos-view">
    <div class="header-section">
      <h2>Hospitalizações</h2>
      <p>Gestão de internamentos de doentes</p>
      
      <div class="actions">
        <Button 
          label="Novo Internamento" 
          icon="pi pi-plus" 
          @click="showAddDialog = true"
          severity="primary"
        />
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="internamentoStore.loading" class="loading">
      <i class="pi pi-spinner pi-spin"></i>
      Loading...
    </div>

    <!-- Error state -->
    <Message 
      v-if="internamentoStore.error" 
      severity="error" 
      :closable="true"
      @close="internamentoStore.clearError"
    >
      {{ internamentoStore.error }}
    </Message>

    <!-- Data Table -->
    <DataTable 
      v-if="!internamentoStore.loading && !internamentoStore.error"
      :value="internamentoStore.internamentos" 
      editMode="cell" 
      @cell-edit-complete="onCellEditComplete"
      class="editable-table wide-table"
      dataKey="id"
      paginator
      :rows="10"
      :rowsPerPageOptions="[5, 10, 20, 50]"
      sortField="numero_internamento"
      :sortOrder="1"
  scrollable
  scrollHeight="600px"
    >
      <template #empty>
        <div style="text-align: center; padding: 2rem;">
          <i class="pi pi-heart" style="font-size: 3rem; color: var(--text-color-secondary);"></i>
          <p>Nenhum internamento encontrado</p>
        </div>
      </template>

      <!-- ID Column -->
      <Column field="id" header="ID" :sortable="true" style="min-width: 80px;">
        <template #body="{ data }">
          {{ data.id }}
        </template>
      </Column>

      <!-- Número do Internamento -->
      <Column field="numero_internamento" header="Nº Internamento" :sortable="true" style="min-width: 140px;">
        <template #body="{ data }">
          <strong>{{ data.numero_internamento }}</strong>
        </template>
        <template #editor="{ data, field }">
          <InputText v-model.number="data[field]" type="number" />
        </template>
      </Column>

      <!-- Doente ID -->
      <Column field="doente_id" header="Doente ID" :sortable="true" style="min-width: 100px;">
        <template #body="{ data }">
          {{ data.doente_id }}
        </template>
        <template #editor="{ data, field }">
          <InputText v-model.number="data[field]" type="number" />
        </template>
      </Column>

      <!-- Data de Entrada -->
      <Column field="data_entrada" header="Data Entrada" :sortable="true" style="min-width: 120px;">
        <template #body="{ data }">
          {{ formatDate(data.data_entrada) }}
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

      <!-- Data de Alta -->
      <Column field="data_alta" header="Data Alta" :sortable="true" style="min-width: 120px;">
        <template #body="{ data }">
          {{ data.data_alta ? formatDate(data.data_alta) : '-' }}
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

      <!-- Data da Queimadura -->
      <Column field="data_queimadura" header="Data Queimadura" :sortable="true" style="min-width: 140px;">
        <template #body="{ data }">
          {{ data.data_queimadura ? formatDate(data.data_queimadura) : '-' }}
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

      <!-- Origem Entrada -->
      <Column field="origem_entrada" header="Origem Entrada" :sortable="true" style="min-width: 130px;">
        <template #body="{ data }">
          {{ displayNumber(data.origem_entrada) }}
        </template>
        <template #editor="{ data, field }">
          <InputText v-model.number="data[field]" type="number" />
        </template>
      </Column>

      <!-- Destino Alta -->
      <Column field="destino_alta" header="Destino Alta" :sortable="true" style="min-width: 120px;">
        <template #body="{ data }">
          {{ displayNumber(data.destino_alta) }}
        </template>
        <template #editor="{ data, field }">
          <InputText v-model.number="data[field]" type="number" />
        </template>
      </Column>

      <!-- ASCQ Total -->
      <Column field="ASCQ_total" header="ASCQ Total" :sortable="true" style="min-width: 110px;">
        <template #body="{ data }">
          <Badge 
            :value="data.ASCQ_total" 
            :severity="getASCQSeverity(data.ASCQ_total)"
          />
        </template>
        <template #editor="{ data, field }">
          <InputText v-model.number="data[field]" type="number" />
        </template>
      </Column>

      <!-- Lesão Inalatória -->
      <Column field="lesao_inalatoria" header="Lesão Inalatória" :sortable="true" style="min-width: 140px;">
        <template #body="{ data }">
          <Tag 
            :value="data.lesao_inalatoria" 
            :severity="data.lesao_inalatoria === 'SIM' ? 'danger' : 'success'"
          />
        </template>
        <template #editor="{ data, field }">
          <select v-model="data[field]" class="p-inputtext p-component">
            <option value="SIM">SIM</option>
            <option value="NAO">NÃO</option>
            <option value="SUSPEITA">SUSPEITA</option>
          </select>
        </template>
      </Column>

      <!-- Mecanismo Queimadura -->
      <Column field="mecanismo_queimadura" header="Mecanismo Queimadura" :sortable="true" style="min-width: 160px;">
        <template #body="{ data }">
          {{ displayNumber(data.mecanismo_queimadura) }}
        </template>
        <template #editor="{ data, field }">
          <InputText v-model.number="data[field]" type="number" />
        </template>
      </Column>

      <!-- Agente Queimadura -->
      <Column field="agente_queimadura" header="Agente Queimadura" :sortable="true" style="min-width: 150px;">
        <template #body="{ data }">
          {{ displayNumber(data.agente_queimadura) }}
        </template>
        <template #editor="{ data, field }">
          <InputText v-model.number="data[field]" type="number" />
        </template>
      </Column>

      <!-- Tipo Acidente -->
      <Column field="tipo_acidente" header="Tipo Acidente" :sortable="true" style="min-width: 130px;">
        <template #body="{ data }">
          {{ displayNumber(data.tipo_acidente) }}
        </template>
        <template #editor="{ data, field }">
          <InputText v-model.number="data[field]" type="number" />
        </template>
      </Column>

      <!-- Incêndio Florestal -->
      <Column field="incendio_florestal" header="Incêndio Florestal" :sortable="true" style="min-width: 150px;">
        <template #body="{ data }">
          <Tag 
            :value="data.incendio_florestal ? 'SIM' : 'NÃO'" 
            :severity="data.incendio_florestal ? 'warning' : 'info'"
          />
        </template>
        <template #editor="{ data, field }">
          <Checkbox v-model="data[field]" :binary="true" />
        </template>
      </Column>

      <!-- Contexto Violento -->
      <Column field="contexto_violento" header="Contexto Violento" :sortable="true" style="min-width: 160px;">
        <template #body="{ data }">
          <Tag 
            v-if="data.contexto_violento"
            :value="data.contexto_violento" 
            :severity="data.contexto_violento === 'SIM' ? 'danger' : 'success'"
          />
          <span v-else>-</span>
        </template>
        <template #editor="{ data, field }">
          <select v-model="data[field]" class="p-inputtext p-component">
            <option :value="null">Não especificado</option>
            <option value="SIM">SIM</option>
            <option value="NAO">NÃO</option>
            <option value="SUSPEITA">SUSPEITA</option>
          </select>
        </template>
      </Column>

      <!-- Tentativa de Suicídio -->
      <Column field="suicidio_tentativa" header="Tentativa Suicídio" :sortable="true" style="min-width: 150px;">
        <template #body="{ data }">
          <Tag 
            :value="data.suicidio_tentativa ? 'SIM' : 'NÃO'" 
            :severity="data.suicidio_tentativa ? 'danger' : 'info'"
          />
        </template>
        <template #editor="{ data, field }">
          <Checkbox v-model="data[field]" :binary="true" />
        </template>
      </Column>

      <!-- Fogueira Queda -->
      <Column field="fogueira_queda" header="Fogueira Queda" :sortable="true" style="min-width: 130px;">
        <template #body="{ data }">
          <Tag 
            :value="data.fogueira_queda ? 'SIM' : 'NÃO'" 
            :severity="data.fogueira_queda ? 'warning' : 'info'"
          />
        </template>
        <template #editor="{ data, field }">
          <Checkbox v-model="data[field]" :binary="true" />
        </template>
      </Column>

      <!-- Lareira Queda -->
      <Column field="lareira_queda" header="Lareira Queda" :sortable="true" style="min-width: 130px;">
        <template #body="{ data }">
          <Tag 
            :value="data.lareira_queda ? 'SIM' : 'NÃO'" 
            :severity="data.lareira_queda ? 'warning' : 'info'"
          />
        </template>
        <template #editor="{ data, field }">
          <Checkbox v-model="data[field]" :binary="true" />
        </template>
      </Column>

      <!-- Escarotomias Entrada -->
      <Column field="escarotomias_entrada" header="Escarotomias Entrada" :sortable="true" style="min-width: 160px;">
        <template #body="{ data }">
          <Tag 
            :value="data.escarotomias_entrada ? 'SIM' : 'NÃO'" 
            :severity="data.escarotomias_entrada ? 'warning' : 'info'"
          />
        </template>
        <template #editor="{ data, field }">
          <Checkbox v-model="data[field]" :binary="true" />
        </template>
      </Column>

      <!-- Intubação OT -->
      <Column field="intubacao_OT" header="Intubação OT" :sortable="true" style="min-width: 140px;">
        <template #body="{ data }">
          <Tag 
            v-if="data.intubacao_OT"
            :value="data.intubacao_OT" 
            :severity="data.intubacao_OT === 'SIM' ? 'warning' : 'success'"
          />
          <span v-else>-</span>
        </template>
        <template #editor="{ data, field }">
          <select v-model="data[field]" class="p-inputtext p-component">
            <option :value="null">Não especificado</option>
            <option value="SIM">SIM</option>
            <option value="NAO">NÃO</option>
            <option value="OUTRO">OUTRO</option>
          </select>
        </template>
      </Column>

      <!-- VMI Dias -->
      <Column field="VMI_dias" header="VMI Dias" :sortable="true" style="min-width: 100px;">
        <template #body="{ data }">
          {{ displayNumber(data.VMI_dias) }}
        </template>
        <template #editor="{ data, field }">
          <InputText v-model.number="data[field]" type="number" />
        </template>
      </Column>

      <!-- VNI -->
      <Column field="VNI" header="VNI" :sortable="true" style="min-width: 80px;">
        <template #body="{ data }">
          <Tag 
            :value="data.VNI ? 'SIM' : 'NÃO'" 
            :severity="data.VNI ? 'warning' : 'info'"
          />
        </template>
        <template #editor="{ data, field }">
          <Checkbox v-model="data[field]" :binary="true" />
        </template>
      </Column>

      <!-- Created At -->
      <Column field="created_at" header="Criado Em" :sortable="true" style="min-width: 150px;">
        <template #body="{ data }">
          {{ data.created_at ? formatDateTime(data.created_at) : '-' }}
        </template>
      </Column>

      <!-- Last Modified -->
      <Column field="last_modified" header="Última Modificação" :sortable="true" style="min-width: 170px;">
        <template #body="{ data }">
          {{ data.last_modified ? formatDateTime(data.last_modified) : '-' }}
        </template>
      </Column>

      <!-- Actions Column -->
      <Column header="Ações" :exportable="false" style="min-width: 120px;">
        <template #body="{ data }">
          <div class="action-buttons">
            <Button 
              icon="pi pi-pencil" 
              @click="handleEdit(data)"
              size="small"
              text
              severity="info"
              v-tooltip.top="'Editar'"
            />
            <Button 
              icon="pi pi-trash" 
              @click="handleDelete(data)"
              size="small"
              text
              severity="danger"
              v-tooltip.top="'Eliminar'"
            />
          </div>
        </template>
      </Column>
    </DataTable>

    <!-- Add Dialog -->
    <Dialog 
      v-model:visible="showAddDialog" 
      header="Adicionar Novo Internamento" 
      modal 
      style="width: 500px"
    >
      <div class="form-grid">
        <div class="form-field">
          <label for="numero_internamento">Número do Internamento *</label>
          <InputText 
            id="numero_internamento"
            v-model.number="newInternamento.numero_internamento" 
            type="number"
            placeholder="Ex: 12345"
            class="w-full"
          />
        </div>
        
        <div class="form-field">
          <label for="doente_id">ID do Doente *</label>
          <InputText 
            id="doente_id"
            v-model.number="newInternamento.doente_id" 
            type="number"
            placeholder="ID do doente"
            class="w-full"
          />
        </div>
        
        <div class="form-field">
          <label for="data_entrada">Data de Entrada *</label>
          <InputText 
            id="data_entrada"
            v-model="newInternamento.data_entrada" 
            type="date"
            class="w-full"
          />
        </div>
        
        <div class="form-field">
          <label for="ASCQ_total">ASCQ Total</label>
          <InputText 
            id="ASCQ_total"
            v-model.number="newInternamento.ASCQ_total" 
            type="number"
            placeholder="0-100"
            class="w-full"
          />
        </div>
        
        <div class="form-field">
          <label for="lesao_inalatoria">Lesão Inalatória *</label>
          <select 
            id="lesao_inalatoria"
            v-model="newInternamento.lesao_inalatoria"
            class="p-inputtext p-component w-full"
          >
            <option value="SIM">SIM</option>
            <option value="NAO">NÃO</option>
          </select>
        </div>
      </div>

      <template #footer>
        <Button 
          label="Cancelar" 
          icon="pi pi-times" 
          @click="showAddDialog = false; resetForm()"
          severity="secondary"
          outlined
        />
        <Button 
          label="Adicionar" 
          icon="pi pi-check" 
          @click="handleAdd"
          :loading="internamentoStore.loading"
          :disabled="!newInternamento.numero_internamento || !newInternamento.doente_id || !newInternamento.data_entrada || !newInternamento.lesao_inalatoria"
        />
      </template>
    </Dialog>

    <!-- Edit Dialog -->
    <Dialog 
      v-model:visible="showEditDialog" 
      header="Editar Internamento" 
      modal 
      style="width: 500px"
    >
      <div class="form-grid">
        <div class="form-field">
          <label for="edit_numero_internamento">Número do Internamento *</label>
          <InputText 
            id="edit_numero_internamento"
            v-model.number="editData.numero_internamento" 
            type="number"
            placeholder="Ex: 12345"
            class="w-full"
          />
        </div>
        
        <div class="form-field">
          <label for="edit_doente_id">ID do Doente *</label>
          <InputText 
            id="edit_doente_id"
            v-model.number="editData.doente_id" 
            type="number"
            placeholder="ID do doente"
            class="w-full"
          />
        </div>
        
        <div class="form-field">
          <label for="edit_data_entrada">Data de Entrada *</label>
          <InputText 
            id="edit_data_entrada"
            v-model="editData.data_entrada" 
            type="date"
            class="w-full"
          />
        </div>
        
        <div class="form-field">
          <label for="edit_ASCQ_total">ASCQ Total</label>
          <InputText 
            id="edit_ASCQ_total"
            v-model.number="editData.ASCQ_total" 
            type="number"
            placeholder="0-100"
            class="w-full"
          />
        </div>
        
        <div class="form-field">
          <label for="edit_lesao_inalatoria">Lesão Inalatória *</label>
          <select 
            id="edit_lesao_inalatoria"
            v-model="editData.lesao_inalatoria"
            class="p-inputtext p-component w-full"
          >
            <option value="SIM">SIM</option>
            <option value="NAO">NÃO</option>
          </select>
        </div>
      </div>

      <template #footer>
        <Button 
          label="Cancelar" 
          icon="pi pi-times" 
          @click="showEditDialog = false"
          severity="secondary"
          outlined
        />
        <Button 
          label="Actualizar" 
          icon="pi pi-check" 
          @click="handleUpdate"
          :loading="internamentoStore.loading"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useInternamentoStore } from '@/stores/internamento'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import type { Internamento, InternamentoCreate } from '@/services/api'

const internamentoStore = useInternamentoStore()
const toast = useToast()
const confirm = useConfirm()

// Dialog states
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const editingInternamento = ref<Internamento | null>(null)

// Form data
const newInternamento = ref<InternamentoCreate>({
  numero_internamento: 0,
  doente_id: 0,
  data_entrada: '',
  ASCQ_total: 0,
  lesao_inalatoria: 'NAO',
})

const editData = ref<Partial<Internamento>>({})

// Load data on mount
onMounted(() => {
  internamentoStore.fetchInternamentos()
})

// Add new internamento
const handleAdd = async () => {
  try {
    // Normalize payload
    const payload = { ...newInternamento.value }
    const dateKeys = ['data_entrada', 'data_alta', 'data_queimadura'] as const
    for (const k of dateKeys) {
      const v = payload[k]
      if (typeof v === 'string' && v.trim() === '') payload[k] = null as any
    }
    // Coerce numerics if coming from text inputs
    const numKeys = [
      'numero_internamento',
      'doente_id',
      'origem_entrada',
      'destino_alta',
      'ASCQ_total',
      'mecanismo_queimadura',
      'agente_queimadura',
      'tipo_acidente',
      'VMI_dias',
    ] as const
    for (const k of numKeys) {
      const v: any = (payload as any)[k]
      if (typeof v === 'string') {
        const n = Number(v)
        ;(payload as any)[k] = Number.isNaN(n) ? null : n
      }
    }

    await internamentoStore.createInternamento(payload)
    showAddDialog.value = false
    resetForm()
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Internamento added successfully',
      life: 3000,
    })
  } catch (error: any) {
    const detail = error?.response?.data?.detail || 'Failed to add internamento'
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail,
      life: 4000,
    })
  }
}

// Edit internamento
const handleEdit = (internamento: Internamento) => {
  editingInternamento.value = internamento
  editData.value = { ...internamento }
  showEditDialog.value = true
}

const handleUpdate = async () => {
  if (!editingInternamento.value) return

  try {
    const payload: any = { ...editData.value }
    const dateKeys = ['data_entrada', 'data_alta', 'data_queimadura']
    for (const k of dateKeys) {
      const v = payload[k]
      if (typeof v === 'string' && v.trim() === '') payload[k] = null
    }
    const numKeys = [
      'numero_internamento',
      'doente_id',
      'origem_entrada',
      'destino_alta',
      'ASCQ_total',
      'mecanismo_queimadura',
      'agente_queimadura',
      'tipo_acidente',
      'VMI_dias',
    ]
    for (const k of numKeys) {
      const v = payload[k]
      if (typeof v === 'string') {
        const n = Number(v)
        payload[k] = Number.isNaN(n) ? null : n
      }
    }

    await internamentoStore.updateInternamento(editingInternamento.value.id, payload)
    showEditDialog.value = false
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Internamento updated successfully',
      life: 3000,
    })
  } catch (error: any) {
    const detail = error?.response?.data?.detail || 'Failed to update internamento'
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail,
      life: 4000,
    })
  }
}

// Delete internamento
const handleDelete = (internamento: Internamento) => {
  confirm.require({
    message: `Are you sure you want to delete internamento #${internamento.numero_internamento}?`,
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
        await internamentoStore.deleteInternamento(internamento.id)
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Internamento deleted successfully',
          life: 3000
        })
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete internamento',
          life: 3000
        })
      }
    }
  })
}

// Cell editing
const onCellEditComplete = async (event: any) => {
  const { data, newValue, field } = event

  // Normalize payload by field type to satisfy backend validation
  const dateFields = new Set(['data_entrada', 'data_alta', 'data_queimadura'])
  const numberFields = new Set([
    'numero_internamento',
    'doente_id',
    'origem_entrada',
    'destino_alta',
    'ASCQ_total',
    'mecanismo_queimadura',
    'agente_queimadura',
    'tipo_acidente',
    'VMI_dias',
  ])

  let normalized: any = newValue
  // Empty strings for date fields should be null (schema expects null or YYYY-MM-DD)
  if (dateFields.has(field)) {
    normalized = typeof newValue === 'string' && newValue.trim() === '' ? null : newValue
  }
  // Coerce number fields to numbers (or null)
  if (numberFields.has(field)) {
    if (newValue === '' || newValue === null || Number.isNaN(newValue)) {
      normalized = null
    } else if (typeof newValue === 'string') {
      const parsed = Number(newValue)
      normalized = Number.isNaN(parsed) ? null : parsed
    }
  }

  try {
    const updates = { [field]: normalized }
    await internamentoStore.updateInternamento(data.id, updates)
    data[field] = normalized
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: `${field} updated successfully`,
      life: 2000,
    })
  } catch (error: any) {
    const detail = error?.response?.data?.detail || `Failed to update ${field}`
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail,
      life: 4000,
    })
    // Revert the change
    event.preventDefault()
  }
}

const resetForm = () => {
  newInternamento.value = {
    numero_internamento: 0,
    doente_id: 0,
    data_entrada: '',
    ASCQ_total: 0,
    lesao_inalatoria: 'NAO',
  }
}

// Utility functions
const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('pt-PT')
}

const formatDateTime = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('pt-PT')
}

const getASCQSeverity = (score: number) => {
  if (score >= 75) return 'danger'
  if (score >= 50) return 'warning'
  if (score >= 25) return 'info'
  return 'success'
}

// Provide date string suitable for <input type="date">
const formatDateForInput = (dateString: string | null | undefined) => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    return date.toISOString().split('T')[0]
  } catch {
    return ''
  }
}

// Display helper for numeric fields that may be 0/null
const displayNumber = (val: number | null | undefined) => {
  return val === null || val === undefined ? '-' : String(val)
}
</script>


<style scoped>
.internamentos-view {
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

/* Wide table styling to match DoentesView */
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
  .internamentos-view {
    padding: 2rem;
  }
}

@media (max-width: 768px) {
  .internamentos-view {
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