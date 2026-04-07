<template>
  <div class="admin">
    <!-- Tabs -->
    <div class="tabs">
      <button class="tab" :class="{ active: tab === 'hardware' }" @click="tab = 'hardware'">
        Hardware
        <span class="tab-count">{{ hardware.length }}</span>
      </button>
      <button class="tab" :class="{ active: tab === 'users' }" @click="tab = 'users'">
        Users
        <span class="tab-count">{{ users.length }}</span>
      </button>
      <button class="tab" :class="{ active: tab === 'audit' }" @click="tab = 'audit'">
        ⚡ AI Audit
        <span v-if="auditIssues.length" class="tab-count tab-count-red">{{ auditIssues.length }}</span>
      </button>
    </div>

    <!-- ─── Hardware Tab ───────────────────────────────────── -->
    <div v-if="tab === 'hardware'">
      <div class="section-actions">
        <button class="btn btn-primary btn-sm" @click="openAddHardware">+ Add Item</button>
      </div>

      <div class="card" style="padding:0;overflow:hidden">
        <table class="table">
          <thead>
            <tr>
              <th>#</th>
              <th>Name</th>
              <th>Brand</th>
              <th>Purchase Date</th>
              <th>Status</th>
              <th>Notes</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="hardware.length === 0">
              <td colspan="7" style="text-align:center;padding:32px;color:var(--text-dim)">No items.</td>
            </tr>
            <tr v-for="item in hardware" :key="item.id">
              <td class="text-mono text-dim">{{ item.id }}</td>
              <td style="font-weight:500">{{ item.name }}</td>
              <td class="text-dim">{{ item.brand }}</td>
              <td class="text-mono text-dim">{{ item.purchaseDate ?? '—' }}</td>
              <td>
                <select
                  :value="item.status"
                  class="status-select"
                  :class="statusSelectClass(item.status)"
                  @change="quickStatusChange(item, $event.target.value)"
                >
                  <option>Available</option>
                  <option>In Use</option>
                  <option>Repair</option>
                  <option>Unknown</option>
                </select>
              </td>
              <td class="text-dim" style="font-size:12px;max-width:180px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
                {{ item.notes ?? '—' }}
              </td>
              <td>
                <div class="action-btns">
                  <button class="btn btn-ghost btn-sm" @click="openEdit(item)">Edit</button>
                  <button class="btn btn-danger btn-sm" @click="confirmDelete(item)">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ─── Users Tab ──────────────────────────────────────── -->
    <div v-if="tab === 'users'">
      <div class="section-actions">
        <button class="btn btn-primary btn-sm" @click="showAddUser = true">+ Create User</button>
      </div>

      <div class="card" style="padding:0;overflow:hidden">
        <table class="table">
          <thead>
            <tr>
              <th>#</th>
              <th>Username</th>
              <th>Role</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td class="text-mono text-dim">{{ u.id }}</td>
              <td style="font-weight:500">{{ u.username }}</td>
              <td>
                <span class="badge" :class="u.role === 'admin' ? 'badge-inuse' : 'badge-unknown'">
                  {{ u.role }}
                </span>
              </td>
              <td>
                <button
                  class="btn btn-danger btn-sm"
                  @click="deleteUser(u)"
                  :disabled="u.username === authStore.user?.username"
                >Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ─── AI Audit Tab ───────────────────────────────────── -->
    <div v-if="tab === 'audit'" class="audit-tab">
      <div class="section-actions">
        <button class="btn btn-primary btn-sm" @click="runAudit" :disabled="auditLoading">
          <span v-if="auditLoading" class="spin"></span>
          <span v-else>Run Audit</span>
        </button>
      </div>

      <div v-if="!auditRun" class="audit-empty">
        <div style="font-size:32px">⚡</div>
        <p>Run an AI-powered inventory audit to flag issues in the hardware data.</p>
      </div>

      <div v-else-if="auditIssues.length === 0" class="audit-empty">
        <div style="font-size:32px">✅</div>
        <p>No issues found. Inventory looks clean!</p>
      </div>

      <div v-else class="audit-list">
        <div
          v-for="(issue, i) in auditIssues"
          :key="i"
          class="audit-card"
          :class="`severity-${issue.severity}`"
        >
          <div class="audit-card-header">
            <span class="severity-badge">{{ issue.severity }}</span>
            <span class="audit-title">{{ issue.issue }}</span>
            <span v-if="issue.item_id" class="text-mono text-dim" style="font-size:11px">ID {{ issue.item_id }}</span>
          </div>
          <p class="audit-detail">{{ issue.detail }}</p>
        </div>
      </div>
    </div>

    <!-- ─── Add/Edit Hardware Modal ────────────────────────── -->
    <div v-if="showHardwareModal" class="modal-overlay" @click.self="showHardwareModal = false">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ editingItem ? 'Edit Item' : 'Add Item' }}</h2>
          <button class="modal-close" @click="showHardwareModal = false">×</button>
        </div>

        <div class="form-group">
          <label>Name *</label>
          <input v-model="form.name" class="input" placeholder="e.g. MacBook Pro 14" required />
        </div>
        <div class="form-group">
          <label>Brand</label>
          <input v-model="form.brand" class="input" placeholder="e.g. Apple" />
        </div>
        <div class="form-group">
          <label>Purchase Date</label>
          <input v-model="form.purchaseDate" class="input" type="date" />
        </div>
        <div class="form-group">
          <label>Status</label>
          <select v-model="form.status" class="input">
            <option>Available</option>
            <option>In Use</option>
            <option>Repair</option>
          </select>
        </div>
        <div class="form-group">
          <label>Notes</label>
          <input v-model="form.notes" class="input" placeholder="Optional notes…" />
        </div>

        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showHardwareModal = false">Cancel</button>
          <button class="btn btn-primary" @click="saveHardware" :disabled="formLoading">
            <span v-if="formLoading" class="spin"></span>
            <span v-else>{{ editingItem ? 'Save' : 'Add' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ─── Add User Modal ─────────────────────────────────── -->
    <div v-if="showAddUser" class="modal-overlay" @click.self="showAddUser = false">
      <div class="modal">
        <div class="modal-header">
          <h2>Create User</h2>
          <button class="modal-close" @click="showAddUser = false">×</button>
        </div>

        <div class="form-group">
          <label>Email *</label>
          <input v-model="userForm.username" class="input" placeholder="e.g. user@booksy.com" type="email" />
        </div>
        <div class="form-group">
          <label>Password *</label>
          <input v-model="userForm.password" type="password" class="input" placeholder="Min 6 chars" />
        </div>
        <div class="form-group">
          <label>Role</label>
          <select v-model="userForm.role" class="input">
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
        </div>

        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showAddUser = false">Cancel</button>
          <button class="btn btn-primary" @click="createUser" :disabled="formLoading">
            <span v-if="formLoading" class="spin"></span>
            <span v-else>Create</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ─── Confirm Delete Modal ───────────────────────────── -->
    <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
      <div class="modal" style="max-width:360px">
        <div class="modal-header">
          <h2>Delete Item</h2>
          <button class="modal-close" @click="deleteTarget = null">×</button>
        </div>
        <p style="color:var(--text-dim);font-size:13px">
          Delete <strong style="color:var(--text)">{{ deleteTarget?.name }}</strong>?
          This cannot be undone.
        </p>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="deleteTarget = null">Cancel</button>
          <button class="btn btn-danger" @click="doDelete" :disabled="formLoading">
            <span v-if="formLoading" class="spin"></span>
            <span v-else>Delete</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api.js'
import { useAuthStore } from '../stores/auth.js'
import { useToastStore } from '../stores/toast.js'

const authStore = useAuthStore()
const toast     = useToastStore()

const tab      = ref('hardware')
const hardware = ref([])
const users    = ref([])

// audit
const auditLoading = ref(false)
const auditRun     = ref(false)
const auditIssues  = ref([])

// modals
const showHardwareModal = ref(false)
const showAddUser       = ref(false)
const editingItem       = ref(null)
const deleteTarget      = ref(null)
const formLoading       = ref(false)

const form = ref({ name:'', brand:'', purchaseDate:'', status:'Available', notes:'' })
const userForm = ref({ username:'', password:'', role:'user' })

async function fetchHardware() {
  const { data } = await api.get('/api/hardware')
  hardware.value = data
}

async function fetchUsers() {
  const { data } = await api.get('/api/users')
  users.value = data
}

onMounted(() => { fetchHardware(); fetchUsers() })

// ── Hardware ───────────────────────────────────────────────

function openAddHardware() {
  editingItem.value = null
  form.value = { name:'', brand:'', purchaseDate:'', status:'Available', notes:'' }
  showHardwareModal.value = true
}

function openEdit(item) {
  editingItem.value = item
  form.value = { ...item }
  showHardwareModal.value = true
}

async function saveHardware() {
  if (!form.value.name) return toast.error('Name is required')
  formLoading.value = true
  try {
    if (editingItem.value) {
      await api.put(`/api/hardware/${editingItem.value.id}`, form.value)
      toast.success('Item updated')
    } else {
      await api.post('/api/hardware', form.value)
      toast.success('Item added')
    }
    showHardwareModal.value = false
    await fetchHardware()
  } catch (e) {
    toast.error(e?.response?.data?.detail || 'Error saving item')
  } finally {
    formLoading.value = false
  }
}

async function quickStatusChange(item, newStatus) {
  try {
    await api.put(`/api/hardware/${item.id}`, { ...item, status: newStatus })
    toast.success(`Status updated to ${newStatus}`)
    await fetchHardware()
  } catch {
    toast.error('Failed to update status')
  }
}

function confirmDelete(item) { deleteTarget.value = item }

async function doDelete() {
  formLoading.value = true
  try {
    await api.delete(`/api/hardware/${deleteTarget.value.id}`)
    toast.success('Item deleted')
    deleteTarget.value = null
    await fetchHardware()
  } catch {
    toast.error('Failed to delete')
  } finally {
    formLoading.value = false
  }
}

// ── Users ──────────────────────────────────────────────────

async function createUser() {
  if (!userForm.value.username || !userForm.value.password) return toast.error('Fill all fields')
  formLoading.value = true
  try {
    await api.post('/api/auth/register', { email: userForm.value.username, password: userForm.value.password, role: userForm.value.role })
    toast.success(`User ${userForm.value.username} created`)
    showAddUser.value = false
    userForm.value = { username:'', password:'', role:'user' }
    await fetchUsers()
  } catch (e) {
    toast.error(e?.response?.data?.detail || 'Failed to create user')
  } finally {
    formLoading.value = false
  }
}

async function deleteUser(u) {
  try {
    await api.delete(`/api/users/${u.id}`)
    toast.success(`User ${u.username} deleted`)
    await fetchUsers()
  } catch {
    toast.error('Failed to delete user')
  }
}

// ── AI Audit ───────────────────────────────────────────────

async function runAudit() {
  auditLoading.value = true
  auditRun.value = false
  try {
    const { data } = await api.get('/api/ai/audit')
    auditIssues.value = data.issues
    auditRun.value = true
    if (data.issues.length) toast.info(`Audit found ${data.issues.length} issue(s)`)
    else toast.success('Audit complete — no issues!')
  } catch {
    toast.error('Audit failed')
  } finally {
    auditLoading.value = false
  }
}

// ── Helpers ────────────────────────────────────────────────

function statusSelectClass(status) {
  return {
    Available: 'status-available',
    'In Use':  'status-inuse',
    Repair:    'status-repair',
    Unknown:   'status-unknown',
  }[status] ?? 'status-unknown'
}
</script>

<style scoped>
.admin {
  padding: 24px 28px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 1200px;
}

/* ── Tabs ─────────────────────────────────────────────────── */
.tabs {
  display: flex;
  border-bottom: 1px solid var(--border);
}
.tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-dim);
  cursor: pointer;
  font-family: var(--sans);
  font-size: 13px;
  font-weight: 500;
  transition: all var(--transition);
  margin-bottom: -1px;
}
.tab:hover { color: var(--text); background: var(--bg-2); }
.tab.active { color: var(--accent); border-bottom-color: var(--accent); }
.tab-count {
  background: var(--bg-3);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 0 6px;
  font-size: 10px;
  color: var(--text-dim);
}
.tab-count-red { background: var(--red-bg); color: var(--red); border-color: var(--red-border); }

.section-actions { display: flex; justify-content: flex-end; margin-bottom: 8px; }
.action-btns { display: flex; gap: 6px; }

/* ── Status select inline ─────────────────────────────────── */
.status-select {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 3px 8px;
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  cursor: pointer;
  outline: none;
  color: var(--text);
}
.status-select:focus { border-color: var(--border-strong); }
.status-available { color: var(--green); border-color: var(--green-border); }
.status-inuse     { color: var(--text); border-color: var(--border-strong); }
.status-repair    { color: var(--red);  border-color: var(--red-border); }
.status-unknown   { color: var(--text-dim); }

/* ── Audit ────────────────────────────────────────────────── */
.audit-tab { display: flex; flex-direction: column; gap: 12px; }
.audit-empty {
  text-align: center;
  padding: 48px;
  color: var(--text-dim);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}
.audit-list { display: flex; flex-direction: column; gap: 8px; }
.audit-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 16px;
  border-left-width: 3px;
}
.severity-critical { border-left-color: var(--red); }
.severity-warning  { border-left-color: var(--border-strong); }
.severity-info     { border-left-color: var(--border); }

.audit-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.audit-title { font-weight: 600; flex: 1; }
.severity-badge {
  font-family: var(--mono);
  font-size: 10px;
  text-transform: uppercase;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 2px;
  border: 1px solid;
}
.severity-critical .severity-badge { background: var(--red-bg);  color: var(--red);      border-color: var(--red-border); }
.severity-warning  .severity-badge { background: var(--bg-3);   color: var(--text);     border-color: var(--border-strong); }
.severity-info     .severity-badge { background: var(--bg-2);   color: var(--text-dim); border-color: var(--border); }
.audit-detail { font-size: 13px; color: var(--text-dim); }
</style>
