import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/authStore';

// Public Views
import HomeView from '../views/public/HomeView.vue';
import AboutView from '../views/public/AboutView.vue';
import HowItWorksView from '../views/public/HowItWorksView.vue';
import GuideView from '../views/public/GuideView.vue';
import LoginView from '../views/public/LoginView.vue';
import RegisterView from '../views/public/RegisterView.vue';

// User / Vendor Views
import DashboardView from '../views/user/DashboardView.vue';
import AnalyzeView from '../views/user/AnalyzeView.vue';
import ResultView from '../views/user/ResultView.vue';
import HistoryView from '../views/user/HistoryView.vue';
import HistoryDetailView from '../views/user/HistoryDetailView.vue';
import ProfileView from '../views/user/ProfileView.vue';

// Admin / Researcher Views
import AdminDashboardView from '../views/admin/AdminDashboardView.vue';
import DatasetView from '../views/admin/DatasetView.vue';
import DatasetUploadView from '../views/admin/DatasetUploadView.vue';
import FreshnessCategoriesView from '../views/admin/FreshnessCategoriesView.vue';
import ModelsView from '../views/admin/ModelsView.vue';
import EvaluationView from '../views/admin/EvaluationView.vue';
import EnvironmentalView from '../views/admin/EnvironmentalView.vue';
import ErrorAnalysisView from '../views/admin/ErrorAnalysisView.vue';
import ReportsView from '../views/admin/ReportsView.vue';
import UserManagementView from '../views/admin/UserManagementView.vue';
import SettingsView from '../views/admin/SettingsView.vue';

const routes = [
  { path: '/', name: 'Home', component: HomeView },
  { path: '/about', name: 'About', component: AboutView },
  { path: '/how-it-works', name: 'HowItWorks', component: HowItWorksView },
  { path: '/guide', name: 'Guide', component: GuideView },
  { path: '/login', name: 'Login', component: LoginView },
  { path: '/register', name: 'Register', component: RegisterView },

  // User Views
  { path: '/dashboard', name: 'Dashboard', component: DashboardView, meta: { requiresAuth: true } },
  { path: '/analyze', name: 'Analyze', component: AnalyzeView },
  { path: '/result/:id', name: 'Result', component: ResultView },
  { path: '/history', name: 'History', component: HistoryView, meta: { requiresAuth: true } },
  { path: '/history/:id', name: 'HistoryDetail', component: HistoryDetailView, meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: ProfileView, meta: { requiresAuth: true } },

  // Admin & Researcher Views
  { path: '/admin', name: 'AdminDashboard', component: AdminDashboardView, meta: { requiresRoles: ['admin', 'researcher'] } },
  { path: '/admin/dataset', name: 'AdminDataset', component: DatasetView, meta: { requiresRoles: ['admin', 'researcher'] } },
  { path: '/admin/dataset/new', name: 'AdminDatasetUpload', component: DatasetUploadView, meta: { requiresRoles: ['admin', 'researcher'] } },
  { path: '/admin/categories', name: 'AdminCategories', component: FreshnessCategoriesView, meta: { requiresRoles: ['admin', 'researcher'] } },
  { path: '/admin/models', name: 'AdminModels', component: ModelsView, meta: { requiresRoles: ['admin', 'researcher'] } },
  { path: '/admin/evaluation', name: 'AdminEvaluation', component: EvaluationView, meta: { requiresRoles: ['admin', 'researcher'] } },
  { path: '/admin/environmental', name: 'AdminEnvironmental', component: EnvironmentalView, meta: { requiresRoles: ['admin', 'researcher'] } },
  { path: '/admin/error-analysis', name: 'AdminErrorAnalysis', component: ErrorAnalysisView, meta: { requiresRoles: ['admin', 'researcher'] } },
  { path: '/admin/reports', name: 'AdminReports', component: ReportsView, meta: { requiresRoles: ['admin', 'researcher'] } },
  { path: '/admin/users', name: 'AdminUsers', component: UserManagementView, meta: { requiresRoles: ['admin'] } },
  { path: '/admin/settings', name: 'AdminSettings', component: SettingsView, meta: { requiresRoles: ['admin', 'researcher'] } },

  { path: '/:pathMatch(.*)*', redirect: '/' }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  }
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  if (authStore.token && !authStore.user) {
    await authStore.initialize();
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({ name: 'Login', query: { redirect: to.fullPath } });
  }

  if (to.meta.requiresRoles) {
    if (!authStore.isAuthenticated) {
      return next({ name: 'Login', query: { redirect: to.fullPath } });
    }
    const role = authStore.user?.role;
    if (!to.meta.requiresRoles.includes(role)) {
      return next({ name: 'Dashboard' });
    }
  }

  next();
});

export default router;
