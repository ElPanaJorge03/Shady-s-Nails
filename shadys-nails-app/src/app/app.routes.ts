import { Routes } from '@angular/router';
import { ServicesComponent } from './features/services/services.component';
import { LoginComponent } from './auth/login/login';
import { RegisterComponent } from './auth/register/register';
import { BookingComponent } from './features/booking/booking';
import { authGuard } from './core/guards/auth.guard';
import { workerGuard } from './core/guards/worker.guard';

export const routes: Routes = [
    {
        path: '',
        loadComponent: () => import('./features/landing/landing.component').then(m => m.LandingComponent),
        pathMatch: 'full'
    },
    {
        path: 'login',
        component: LoginComponent
    },
    {
        path: 'register',
        component: RegisterComponent
    },
    {
        path: 'forgot-password',
        loadComponent: () => import('./auth/forgot-password/forgot-password').then(m => m.ForgotPasswordComponent)
    },
    {
        path: 'services',
        component: ServicesComponent
    },
    {
        path: 'booking',
        component: BookingComponent
    },
    {
        path: 'my-appointments',
        loadComponent: () => import('./features/my-appointments/my-appointments').then(m => m.MyAppointmentsComponent),
        canActivate: [authGuard]
    },
    {
        path: 'dashboard',
        loadComponent: () => import('./features/worker-dashboard/worker-dashboard').then(m => m.WorkerDashboardComponent),
        canActivate: [authGuard, workerGuard]
    },
    {
        path: 'settings',
        loadComponent: () => import('./features/profile-settings/profile-settings').then(m => m.ProfileSettingsComponent),
        canActivate: [authGuard]
    },
    {
        path: '**',
        redirectTo: '',
        pathMatch: 'full'
    }
];
