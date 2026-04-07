<template>
  <div class="app-shell" v-if="auth.isLoggedIn">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <span class="logo-mark">Logo</span>
      </div>

      <nav class="sidebar-nav">
        <router-link :to="{ path: '/' }" class="nav-item" :class="{ 'nav-active': isHardwareList }">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
          Hardware List
        </router-link>
        <router-link :to="{ path: '/', query: { section: 'my-rentals' } }" class="nav-item" :class="{ 'nav-active': isMyRentals }">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 7H4a2 2 0 00-2 2v6a2 2 0 002 2h16a2 2 0 002-2V9a2 2 0 00-2-2z"/><path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16"/></svg>
          My Rentals
        </router-link>
        <router-link v-if="auth.isAdmin" to="/admin" class="nav-item" active-class="nav-active">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
          Admin Panel
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <span class="user-avatar">{{ auth.user?.username?.[0]?.toUpperCase() }}</span>
          <div class="user-meta">
            <div class="user-name">{{ auth.user?.username }}</div>
            <div class="user-role">{{ auth.user?.role }}</div>
          </div>
        </div>
        <button class="nav-item logout-item" @click="logout">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9"/></svg>
          Logout
        </button>
      </div>
    </aside>

    <main class="main-content">
      <router-view />
    </main>
  </div>

  <!-- Public pages (login) -->
  <router-view v-else />

  <!-- Toasts -->
  <div class="toast-wrap">
    <div
      v-for="t in toastStore.toasts"
      :key="t.id"
      class="toast"
      :class="`toast-${t.type}`"
    >{{ t.message }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from './stores/auth.js'
import { useToastStore } from './stores/toast.js'
import { useRouter, useRoute } from 'vue-router'

const auth = useAuthStore()
const toastStore = useToastStore()
const router = useRouter()
const route  = useRoute()

const isMyRentals   = computed(() => route.path === '/' && route.query.section === 'my-rentals')
const isHardwareList = computed(() => route.path === '/' && route.query.section !== 'my-rentals')

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-shell {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* ── Sidebar ────────────────────────────────────── */
.sidebar {
  width: 200px;
  min-width: 200px;
  background: var(--bg-2);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 20px 0;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px 20px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 12px;
}
.logo-mark {
  width: 44px; height: 44px;
  background: transparent;
  color: var(--accent);
  border: 2px solid var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--mono);
  font-weight: 700;
  font-size: 12px;
  border-radius: var(--radius);
  flex-shrink: 0;
}
.logo-text {
  font-family: var(--mono);
  font-size: 11px;
  line-height: 1.3;
  color: var(--text);
  font-weight: 700;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1px;
  padding: 0 8px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: var(--radius);
  color: var(--text-dim);
  text-decoration: none;
  font-family: var(--sans);
  font-size: 13px;
  font-weight: 500;
  transition: all var(--transition);
}
.nav-item:hover { color: var(--text); background: var(--bg-3); }
.nav-active { color: var(--accent) !important; background: var(--bg-3) !important; font-weight: 700; }

.sidebar-footer {
  padding: 12px 8px 0;
  border-top: 1px solid var(--border);
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  min-width: 0;
}
.user-avatar {
  width: 26px; height: 26px;
  background: var(--bg-3);
  border: 1px solid var(--border);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 700;
  color: var(--text);
  flex-shrink: 0;
}
.user-meta { min-width: 0; }
.user-name { font-size: 12px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-role { font-size: 11px; color: var(--text-dim); font-family: var(--mono); text-transform: uppercase; }
.logout-item {
  border: none;
  background: none;
  width: 100%;
  cursor: pointer;
  color: var(--text-dim) !important;
}
.logout-item:hover { color: var(--red) !important; background: var(--red-bg); }

/* ── Main ───────────────────────────────────────── */
.main-content {
  flex: 1;
  overflow-y: auto;
  background: var(--bg);
}
</style>
