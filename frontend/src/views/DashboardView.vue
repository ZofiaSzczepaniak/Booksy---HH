<template>
  <div class="dashboard">

    <!-- ─── MY RENTALS ───────────────────────────────────────── -->
    <div v-if="section === 'my-rentals'">
      <div v-if="loading" class="loading-state">
        <span class="spin"></span> Loading your rentals…
      </div>
      <div v-else-if="myRentals.length === 0" class="empty-state">
        <div class="empty-icon">📦</div>
        <p>You have no rented items.</p>
        <router-link to="/" class="btn btn-ghost btn-sm">Browse inventory</router-link>
      </div>
      <div v-else class="table-wrap card" style="padding:0;overflow:hidden;">
        <table class="table">
          <thead>
            <tr>
              <th>#</th>
              <th>Name</th>
              <th>Brand</th>
              <th>Purchase Date</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in myRentals" :key="item.id">
              <td class="text-mono text-dim">{{ item.id }}</td>
              <td>
                <div style="font-weight:500">{{ item.name }}</div>
                <div v-if="item.notes" class="text-dim" style="font-size:11px;margin-top:2px">
                  ⚠ {{ item.notes }}
                </div>
              </td>
              <td class="text-dim">{{ item.brand }}</td>
              <td class="text-mono text-dim">{{ item.purchaseDate ?? '—' }}</td>
              <td><span class="badge badge-inuse">In Use</span></td>
              <td>
                <button
                  class="btn btn-ghost btn-sm"
                  @click="returnItem(item)"
                  :disabled="actionLoading === item.id"
                >
                  <span v-if="actionLoading === item.id" class="spin"></span>
                  <span v-else>Return</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ─── INVENTORY ────────────────────────────────────────── -->
    <template v-if="section === 'inventory'">

      <!-- AI Search (centered, above table) -->
      <div class="search-center">
        <div class="search-wrap">
          <input
            v-model="searchQuery"
            class="input search-input"
            placeholder='Try "laptop for video editing" or "phone for testing"…'
            @keyup.enter="aiSearch"
          />
          <button class="btn btn-ghost btn-sm" @click="aiSearch" :disabled="aiSearching">
            <span v-if="aiSearching" class="spin"></span>
            <span v-else>⚡ AI Search</span>
          </button>
          <button v-if="aiResults !== null" class="btn btn-ghost btn-sm" @click="clearAiSearch">
            Clear
          </button>
        </div>
      </div>

      <!-- Filter bar -->
      <div class="filter-bar">
        <div class="filter-group">
          <label>Status</label>
          <select v-model="filterStatus" class="input filter-select">
            <option value="">All</option>
            <option>Available</option>
            <option>In Use</option>
            <option>Repair</option>
            <option>Unknown</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Brand</label>
          <select v-model="filterBrand" class="input filter-select">
            <option value="">All</option>
            <option v-for="b in brands" :key="b">{{ b }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Name</label>
          <input v-model="filterName" class="input filter-select" placeholder="Filter by name…" />
        </div>
        <button v-if="anyFilter" class="btn btn-ghost btn-sm" @click="clearFilters" style="margin-top:18px">
          Reset
        </button>
      </div>

      <!-- AI result banner -->
      <div v-if="aiResults !== null" class="ai-banner">
        <div class="ai-banner-main">
          <span class="ai-badge">⚡ AI</span>
          <span>
            Found <strong>{{ aiResults.length }}</strong>
            result{{ aiResults.length !== 1 ? 's' : '' }}
            for "<em>{{ lastQuery }}</em>"
          </span>
          <span v-if="aiIntent?.use_case" class="ai-intent-pill">
            {{ aiIntent.use_case }}
          </span>
          <span
            v-if="aiEnriched"
            class="ai-enriched-pill"
            title="Results enriched with live web data"
          >
            🌐 web-enriched
          </span>
        </div>
        <div v-if="aiIntent?.keywords?.length" class="ai-keywords">
          <span>Looking for:</span>
          <span v-for="kw in aiIntent.keywords" :key="kw" class="ai-keyword">{{ kw }}</span>
        </div>
      </div>

      <!-- Table -->
      <div class="table-wrap card" style="padding:0;overflow:hidden;">
        <div v-if="loading" class="loading-state">
          <span class="spin"></span> Loading inventory…
        </div>

        <table v-else class="table">
          <thead>
            <tr>
              <th @click="sort('id')"># {{ sortIcon('id') }}</th>
              <th @click="sort('name')">Name {{ sortIcon('name') }}</th>
              <th @click="sort('brand')">Brand {{ sortIcon('brand') }}</th>
              <th @click="sort('purchaseDate')">Purchase Date {{ sortIcon('purchaseDate') }}</th>
              <th @click="sort('status')">Status {{ sortIcon('status') }}</th>
              <th v-if="aiResults !== null" class="col-reason">Match reason</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filtered.length === 0">
              <td :colspan="aiResults !== null ? 7 : 6"
                  style="text-align:center;padding:32px;color:var(--text-dim)">
                No items match your filters.
              </td>
            </tr>
            <tr v-for="item in filtered" :key="item.id">
              <td class="text-mono text-dim">{{ item.id }}</td>
              <td>
                <div style="font-weight:500">{{ item.name }}</div>
                <div v-if="item.notes" class="text-dim" style="font-size:11px;margin-top:2px">
                  ⚠ {{ item.notes }}
                </div>
              </td>
              <td class="text-dim">{{ item.brand }}</td>
              <td class="text-mono text-dim">{{ item.purchaseDate ?? '—' }}</td>
              <td>
                <span class="badge" :class="statusClass(item.status)">{{ item.status }}</span>
              </td>

              <!-- AI match reason + score — only during AI search -->
              <td v-if="aiResults !== null" class="col-reason">
                <div v-if="item._reason" class="reason-wrap">
                  <span class="reason-text">{{ item._reason }}</span>
                  <span
                    v-if="item._score"
                    class="score-pill"
                    :class="scorePillClass(item._score)"
                  >
                    {{ Math.round(item._score * 100) }}%
                  </span>
                </div>
                <span v-else class="text-dim" style="font-size:11px">—</span>
              </td>

              <td>
                <div class="action-btns">
                  <button
                    v-if="item.status === 'Available'"
                    class="btn btn-primary btn-sm"
                    @click="rent(item)"
                    :disabled="actionLoading === item.id"
                  >
                    <span v-if="actionLoading === item.id" class="spin"></span>
                    <span v-else>Rent</span>
                  </button>
                  <button
                    v-else-if="item.status === 'In Use'"
                    class="btn btn-ghost btn-sm"
                    @click="returnItem(item)"
                    :disabled="actionLoading === item.id"
                  >
                    <span v-if="actionLoading === item.id" class="spin"></span>
                    <span v-else>Return</span>
                  </button>
                  <span v-else class="text-dim" style="font-size:11px">—</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </template><!-- end inventory tab -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api.js'
import { useAuthStore } from '../stores/auth.js'
import { useToastStore } from '../stores/toast.js'
import { useRoute } from 'vue-router'

const auth  = useAuthStore()
const toast = useToastStore()
const route = useRoute()

const section       = computed(() => route.query.section === 'my-rentals' ? 'my-rentals' : 'inventory')
const items         = ref([])
const myRentals     = ref([])
const loading       = ref(true)
const actionLoading = ref(null)

// sort
const sortKey = ref('id')
const sortDir = ref(1)

// filters
const filterStatus = ref('')
const filterBrand  = ref('')
const filterName   = ref('')

// ai search
const searchQuery  = ref('')
const aiSearching  = ref(false)
const aiResults    = ref(null)   // null = not searched yet
const lastQuery    = ref('')
const aiIntent     = ref(null)   // { category, use_case, keywords }
const aiEnriched   = ref(false)  // true if backend used Serper web search

// ── Data fetching ──────────────────────────────────────────

async function fetchItems() {
  loading.value = true
  try {
    const [inv, rentals] = await Promise.all([
      api.get('/api/hardware'),
      api.get('/api/hardware/my-rentals'),
    ])
    items.value     = inv.data
    myRentals.value = rentals.data
  } catch {
    toast.error('Failed to load inventory')
  } finally {
    loading.value = false
  }
}

onMounted(fetchItems)

// ── Computed ───────────────────────────────────────────────

const brands = computed(() => {
  const b = new Set(items.value.map(i => i.brand).filter(Boolean))
  return [...b].sort()
})

const anyFilter = computed(() =>
  filterStatus.value || filterBrand.value || filterName.value
)

const sourceList = computed(() =>
  aiResults.value !== null ? aiResults.value : items.value
)

const filtered = computed(() => {
  let list = sourceList.value

  if (filterStatus.value) list = list.filter(i => i.status === filterStatus.value)
  if (filterBrand.value)  list = list.filter(i => i.brand  === filterBrand.value)
  if (filterName.value)   list = list.filter(i =>
    i.name?.toLowerCase().includes(filterName.value.toLowerCase())
  )

  // During AI search — sort by score descending (best match first)
  if (aiResults.value !== null) {
    return [...list].sort((a, b) => (b._score ?? 0) - (a._score ?? 0))
  }

  return [...list].sort((a, b) => {
    const va = a[sortKey.value] ?? ''
    const vb = b[sortKey.value] ?? ''
    return va < vb ? -sortDir.value : va > vb ? sortDir.value : 0
  })
})

function sort(key) {
  if (aiResults.value !== null) return // manual sort disabled during AI search
  if (sortKey.value === key) sortDir.value *= -1
  else { sortKey.value = key; sortDir.value = 1 }
}

function sortIcon(key) {
  if (aiResults.value !== null || sortKey.value !== key) return ''
  return sortDir.value === 1 ? ' ↑' : ' ↓'
}

function clearFilters() {
  filterStatus.value = ''
  filterBrand.value  = ''
  filterName.value   = ''
}

// ── Status / score helpers ─────────────────────────────────

function statusClass(status) {
  return {
    Available: 'badge-available',
    'In Use':  'badge-inuse',
    Repair:    'badge-repair',
    Unknown:   'badge-unknown',
  }[status] ?? 'badge-unknown'
}

function scorePillClass(score) {
  if (score >= 0.8) return 'score-high'
  if (score >= 0.5) return 'score-mid'
  return 'score-low'
}

// ── AI Search ──────────────────────────────────────────────

async function aiSearch() {
  const q = searchQuery.value.trim()
  if (!q) return

  aiSearching.value = true
  lastQuery.value   = q
  aiIntent.value    = null
  aiEnriched.value  = false

  try {
    const { data } = await api.post('/api/ai/search', { query: q })

    aiResults.value  = data.results  ?? []
    aiIntent.value   = data.intent   ?? null
    aiEnriched.value = data.enriched ?? false

    if (aiResults.value.length === 0) {
      toast.info('No matching items found — try a different description')
    }
  } catch (e) {
    toast.error(e?.response?.data?.detail || 'AI search failed')
    aiResults.value = null
  } finally {
    aiSearching.value = false
  }
}

function clearAiSearch() {
  aiResults.value   = null
  aiIntent.value    = null
  aiEnriched.value  = false
  searchQuery.value = ''
}

// ── Rent / Return ──────────────────────────────────────────

async function rent(item) {
  actionLoading.value = item.id
  try {
    await api.post(`/api/hardware/${item.id}/rent`, {
      user_id:  auth.user.id,
      username: auth.user.username,
    })
    toast.success(`Rented "${item.name}"`)
    await fetchItems()
  } catch (e) {
    toast.error(e?.response?.data?.detail || 'Rent failed')
  } finally {
    actionLoading.value = null
  }
}

async function returnItem(item) {
  actionLoading.value = item.id
  try {
    await api.post(`/api/hardware/${item.id}/return`)
    toast.success(`Returned "${item.name}"`)
    await fetchItems()
  } catch (e) {
    toast.error(e?.response?.data?.detail || 'Return failed')
  } finally {
    actionLoading.value = null
  }
}
</script>

<style scoped>
.dashboard {
  padding: 24px 28px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 1200px;
}

/* ── Empty / Loading ──────────────────────────────────────── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 56px 32px;
  color: var(--text-dim);
  text-align: center;
}
.empty-icon { font-size: 32px; }
.loading-state {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 32px;
  color: var(--text-dim);
}

/* ── AI Search centered ───────────────────────────────────── */
.search-center {
  display: flex;
  justify-content: center;
  padding: 8px 0;
}
.search-wrap  { display: flex; align-items: center; gap: 6px; }
.search-input { width: 420px; }

/* ── Filter bar ───────────────────────────────────────────── */
.filter-bar {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  flex-wrap: wrap;
  padding: 12px;
  background: var(--bg-2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}
.filter-group { display: flex; flex-direction: column; gap: 4px; }
.filter-group label {
  font-family: var(--sans);
  font-size: 12px;
  font-weight: 500;
  color: var(--text-dim);
}
.filter-select { width: 150px; }

/* ── AI Banner ────────────────────────────────────────────── */
.ai-banner {
  background: var(--bg-2);
  border: 1px solid var(--border);
  border-left: 3px solid var(--border-strong);
  border-radius: var(--radius);
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.ai-banner-main {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  font-size: 13px;
}
.ai-badge {
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 700;
  background: var(--accent);
  color: #fff;
  padding: 2px 7px;
  border-radius: 2px;
  letter-spacing: .04em;
  flex-shrink: 0;
}
.ai-intent-pill {
  background: var(--bg-3);
  border: 1px solid var(--border);
  color: var(--text-dim);
  font-family: var(--mono);
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 20px;
}
.ai-enriched-pill {
  background: var(--bg-3);
  border: 1px solid var(--border);
  color: var(--text-dim);
  font-family: var(--mono);
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 20px;
}
.ai-keywords {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  font-size: 11px;
  color: var(--text-dim);
}
.ai-keyword {
  background: var(--bg-3);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 1px 8px;
  font-family: var(--mono);
  font-size: 10px;
}

/* ── Table ────────────────────────────────────────────────── */
.table-wrap { overflow-x: auto; }
.col-reason { min-width: 200px; max-width: 280px; }

.reason-wrap {
  display: flex;
  align-items: flex-start;
  gap: 6px;
}
.reason-text {
  font-size: 12px;
  color: var(--text-dim);
  line-height: 1.4;
  flex: 1;
}
.score-pill {
  flex-shrink: 0;
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 2px;
  border: 1px solid var(--border);
  margin-top: 1px;
}
.score-high { background: var(--green-bg);  color: var(--green);    border-color: var(--green-border); }
.score-mid  { background: var(--bg-3);      color: var(--text-dim); }
.score-low  { background: var(--red-bg);    color: var(--red);      border-color: var(--red-border); }

.action-btns { display: flex; gap: 6px; }
</style>