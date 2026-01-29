import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { AppointmentsService, Appointment } from '../../core/services/appointments.service';
import { ApiService, Service } from '../../core/services/api.service';
import { AuthService } from '../../core/services/auth.service';
import { ToastService } from '../../core/services/toast.service';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner';
import { environment } from '../../../environments/environment';

// Interfaces
interface DailyStats {
  date: string;
  total_appointments: number;
  confirmed_appointments: number;
  pending_appointments: number;
  completed_appointments: number;
  cancelled_appointments: number;
  estimated_revenue: number;
  actual_revenue: number;
  global_pending_appointments: number;
}

interface RevenueStats {
  period: string;
  total_revenue: number;
  completed_revenue: number;
  pending_revenue: number;
  total_appointments: number;
}

interface ServicePopularity {
  service_id: number;
  service_name: string;
  total_bookings: number;
  total_revenue: number;
}

interface ScheduleItem {
  day_of_week: number;
  is_working: boolean;
  start_time: string;
  end_time: string;
  break_start?: string;
  break_end?: string;
}

interface BlockedDateResponse {
  id: number;
  worker_id: number;
  date: string;
  reason?: string;
}

@Component({
  selector: 'app-worker-dashboard',
  standalone: true,
  imports: [CommonModule, LoadingSpinnerComponent, FormsModule, ReactiveFormsModule, RouterModule],
  templateUrl: './worker-dashboard.html',
  styleUrls: ['./worker-dashboard.scss', './worker-dashboard-fixes.scss']
})
export class WorkerDashboardComponent implements OnInit {
  // Estado general
  loading = true;
  activeTab: 'overview' | 'appointments' | 'services' | 'stats' | 'schedules' = 'overview';

  // Citas
  appointments: Appointment[] = [];
  todayAppointments: Appointment[] = [];
  upcomingAppointments: Appointment[] = [];

  // Estadísticas
  dailyStats: DailyStats | null = null;
  weekStats: RevenueStats | null = null;
  monthStats: RevenueStats | null = null;
  popularServices: ServicePopularity[] = [];

  // Servicios
  services: Service[] = [];
  editingService: Service | null = null;
  serviceForm: FormGroup;
  showServiceForm = false;

  // Horarios
  schedules: ScheduleItem[] = [];
  blockedDates: BlockedDateResponse[] = [];
  loadingSchedules = false;
  newBlockDate: string = '';
  newBlockReason: string = '';

  // Usuario actual
  currentUser: any = null;

  // Días de la semana para mostrar
  weekDays = [
    { id: 0, name: 'Lunes' },
    { id: 1, name: 'Martes' },
    { id: 2, name: 'Miércoles' },
    { id: 3, name: 'Jueves' },
    { id: 4, name: 'Viernes' },
    { id: 5, name: 'Sábado' },
    { id: 6, name: 'Domingo' }
  ];

  constructor(
    private appointmentsService: AppointmentsService,
    private apiService: ApiService,
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef,
    private toastService: ToastService,
    private http: HttpClient,
    private fb: FormBuilder
  ) {
    this.currentUser = this.authService.getCurrentUser();

    // Inicializar formulario de servicios
    this.serviceForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(100)]],
      duration_minutes: ['', [Validators.required, Validators.min(1), Validators.max(480)]],
      price: ['', [Validators.required, Validators.min(1)]],
      state: [true]
    });
  }

  ngOnInit(): void {
    this.loadAllData();
  }

  loadAllData(): void {
    this.loading = true;
    Promise.all([
      this.loadAppointments(),
      this.loadDailyStats(),
      this.loadWeekStats(),
      this.loadMonthStats(),
      this.loadPopularServices(),
      this.loadServices(),
      this.loadSchedules(),
      this.loadBlockedDates()
    ]).finally(() => {
      this.loading = false;
      this.cdr.detectChanges();
    });
  }

  // ═══════════════════════════════════════════════════
  // HORARIOS (NUEVO)
  // ═══════════════════════════════════════════════════

  loadSchedules(): Promise<void> {
    return new Promise((resolve, reject) => {
      const token = this.authService.getToken();
      this.http.get<ScheduleItem[]>(
        `${environment.apiUrl}/schedules`,
        { headers: { Authorization: `Bearer ${token}` } }
      ).subscribe({
        next: (data) => {
          // Asegurar formato HH:MM para inputs time (cortar segundos si vienen)
          this.schedules = data.map(s => ({
            ...s,
            start_time: s.start_time.substring(0, 5),
            end_time: s.end_time.substring(0, 5)
          }));
          resolve();
        },
        error: (err) => {
          console.error('Error loading schedules:', err);
          reject(err);
        }
      });
    });
  }

  saveSchedules(): void {
    this.loadingSchedules = true;
    const token = this.authService.getToken();

    // Asegurar formato de hora HH:MM:SS (a veces viene HH:MM)
    const formattedSchedules = this.schedules.map(s => ({
      ...s,
      start_time: s.start_time.length === 5 ? s.start_time + ':00' : s.start_time,
      end_time: s.end_time.length === 5 ? s.end_time + ':00' : s.end_time
    }));

    this.http.put(
      `${environment.apiUrl}/schedules`,
      { schedules: formattedSchedules },
      { headers: { Authorization: `Bearer ${token}` } }
    ).subscribe({
      next: () => {
        this.toastService.success('Horario actualizado correctamente');
        this.loadingSchedules = false;
      },
      error: (err) => {
        console.error('Error saving schedules:', err);
        this.toastService.error('Error al guardar el horario');
        this.loadingSchedules = false;
      }
    });
  }

  getScheduleForDay(dayId: number): ScheduleItem | undefined {
    return this.schedules.find(s => s.day_of_week === dayId);
  }

  // BLOCKED DATES
  loadBlockedDates(): Promise<void> {
    return new Promise((resolve, reject) => {
      const token = this.authService.getToken();
      this.http.get<BlockedDateResponse[]>(
        `${environment.apiUrl}/schedules/blocks`,
        { headers: { Authorization: `Bearer ${token}` } }
      ).subscribe({
        next: (data) => {
          this.blockedDates = data;
          resolve();
        },
        error: (err) => {
          console.error('Error loading blocked dates:', err);
          reject(err);
        }
      });
    });
  }

  addBlockDate(): void {
    if (!this.newBlockDate) return;

    const token = this.authService.getToken();
    this.http.post(
      `${environment.apiUrl}/schedules/blocks`,
      { date: this.newBlockDate, reason: this.newBlockReason },
      { headers: { Authorization: `Bearer ${token}` } }
    ).subscribe({
      next: () => {
        this.toastService.success('Fecha bloqueada correctamente');
        this.loadBlockedDates();
        this.newBlockDate = '';
        this.newBlockReason = '';
      },
      error: (err) => {
        console.error('Error blocking date:', err);
        this.toastService.error(err.error?.detail || 'Error al bloquear fecha');
      }
    });
  }

  deleteBlockDate(dateVal: string): void {
    if (!confirm('¿Desbloquear esta fecha?')) return;

    const token = this.authService.getToken();
    this.http.delete(
      `${environment.apiUrl}/schedules/blocks/${dateVal}`,
      { headers: { Authorization: `Bearer ${token}` } }
    ).subscribe({
      next: () => {
        this.toastService.success('Fecha desbloqueada');
        this.loadBlockedDates();
      },
      error: (err) => {
        console.error('Error unblocking date:', err);
        this.toastService.error('Error al desbloquear fecha');
      }
    });
  }


  // ═══════════════════════════════════════════════════
  // CITAS (EXISTENTE)
  // ═══════════════════════════════════════════════════

  loadAppointments(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.appointmentsService.getAllAppointments().subscribe({
        next: (appointments) => {
          this.appointments = appointments;
          this.filterAppointments();
          resolve();
        },
        error: (err) => {
          console.error('Error loading appointments:', err);
          this.toastService.error('Error al cargar las citas');
          reject(err);
        }
      });
    });
  }

  filterAppointments(): void {
    const today = new Date().toISOString().split('T')[0];

    // Citas de HOY
    this.todayAppointments = this.appointments
      .filter(apt => apt.date === today && apt.status !== 'cancelled')
      .sort((a, b) => a.start_time.localeCompare(b.start_time));

    // Citas FUTURAS (incluyendo hoy, o desde hoy)
    this.upcomingAppointments = this.appointments
      .filter(apt => apt.status !== 'cancelled' && apt.status !== 'completed')
      .sort((a, b) => {
        if (a.date !== b.date) return a.date.localeCompare(b.date);
        return a.start_time.localeCompare(b.start_time);
      });
  }

  confirmAppointment(appointment: Appointment): void {
    if (!confirm('¿Confirmar esta cita?')) return;

    const token = this.authService.getToken();
    this.http.patch(
      `${environment.apiUrl}/appointments/${appointment.id}/confirm`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    ).subscribe({
      next: () => {
        appointment.status = 'confirmed';
        this.toastService.success('Cita confirmada');
        this.loadDailyStats();
      },
      error: (err) => {
        console.error('Error confirming appointment:', err);
        this.toastService.error('Error al confirmar la cita');
      }
    });
  }

  completeAppointment(appointment: Appointment): void {
    if (!confirm('¿Marcar esta cita como completada?')) return;

    const token = this.authService.getToken();
    this.http.patch(
      `${environment.apiUrl}/appointments/${appointment.id}/complete`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    ).subscribe({
      next: () => {
        appointment.status = 'completed';
        this.toastService.success('Cita completada');
        this.loadDailyStats();
      },
      error: (err) => {
        console.error('Error completing appointment:', err);
        this.toastService.error('Error al completar la cita');
      }
    });
  }

  cancelAppointment(appointment: Appointment): void {
    if (!confirm('¿Cancelar esta cita?')) return;

    this.appointmentsService.cancelAppointment(appointment.id).subscribe({
      next: () => {
        appointment.status = 'cancelled';
        this.toastService.success('Cita cancelada');
        this.loadDailyStats();
        this.filterAppointments();
      },
      error: (err) => {
        console.error('Error cancelling appointment:', err);
        this.toastService.error('Error al cancelar la cita');
      }
    });
  }

  // ═══════════════════════════════════════════════════
  // ESTADÍSTICAS
  // ═══════════════════════════════════════════════════

  loadDailyStats(): Promise<void> {
    return new Promise((resolve, reject) => {
      const token = this.authService.getToken();
      this.http.get<DailyStats>(
        `${environment.apiUrl}/stats/today`,
        { headers: { Authorization: `Bearer ${token}` } }
      ).subscribe({
        next: (stats) => {
          this.dailyStats = stats;
          resolve();
        },
        error: (err) => {
          console.error('Error loading daily stats:', err);
          reject(err);
        }
      });
    });
  }

  loadWeekStats(): Promise<void> {
    return new Promise((resolve, reject) => {
      const token = this.authService.getToken();
      this.http.get<RevenueStats>(
        `${environment.apiUrl}/stats/week`,
        { headers: { Authorization: `Bearer ${token}` } }
      ).subscribe({
        next: (stats) => {
          this.weekStats = stats;
          resolve();
        },
        error: (err) => {
          console.error('Error loading week stats:', err);
          reject(err);
        }
      });
    });
  }

  loadMonthStats(): Promise<void> {
    return new Promise((resolve, reject) => {
      const token = this.authService.getToken();
      this.http.get<RevenueStats>(
        `${environment.apiUrl}/stats/month`,
        { headers: { Authorization: `Bearer ${token}` } }
      ).subscribe({
        next: (stats) => {
          this.monthStats = stats;
          resolve();
        },
        error: (err) => {
          console.error('Error loading month stats:', err);
          reject(err);
        }
      });
    });
  }

  loadPopularServices(): Promise<void> {
    return new Promise((resolve, reject) => {
      const token = this.authService.getToken();
      this.http.get<ServicePopularity[]>(
        `${environment.apiUrl}/stats/services-popular?limit=5`,
        { headers: { Authorization: `Bearer ${token}` } }
      ).subscribe({
        next: (services) => {
          this.popularServices = services;
          resolve();
        },
        error: (err) => {
          console.error('Error loading popular services:', err);
          reject(err);
        }
      });
    });
  }

  // ═══════════════════════════════════════════════════
  // SERVICIOS
  // ═══════════════════════════════════════════════════

  loadServices(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.apiService.getServices().subscribe({
        next: (services) => {
          this.services = services;
          resolve();
        },
        error: (err) => {
          console.error('Error loading services:', err);
          this.toastService.error('Error al cargar servicios');
          reject(err);
        }
      });
    });
  }

  openServiceForm(service?: Service): void {
    this.editingService = service || null;

    if (service) {
      this.serviceForm.patchValue({
        name: service.name,
        duration_minutes: service.duration_minutes,
        price: service.price,
        state: service.state
      });
    } else {
      this.serviceForm.reset({ state: true });
    }

    this.showServiceForm = true;
  }

  closeServiceForm(): void {
    this.showServiceForm = false;
    this.editingService = null;
    this.serviceForm.reset({ state: true });
  }

  saveService(): void {
    if (this.serviceForm.invalid) {
      Object.keys(this.serviceForm.controls).forEach(key => {
        this.serviceForm.get(key)?.markAsTouched();
      });
      return;
    }

    const token = this.authService.getToken();
    const serviceData = this.serviceForm.value;

    if (this.editingService) {
      // Actualizar servicio existente
      this.http.put(
        `${environment.apiUrl}/services/${this.editingService.id}`,
        serviceData,
        { headers: { Authorization: `Bearer ${token}` } }
      ).subscribe({
        next: () => {
          this.toastService.success('Servicio actualizado correctamente');
          this.closeServiceForm();
          this.loadServices();
        },
        error: (err) => {
          console.error('Error updating service:', err);
          this.toastService.error(err.error?.detail || 'Error al actualizar el servicio');
        }
      });
    } else {
      // Crear nuevo servicio
      this.http.post(
        `${environment.apiUrl}/services/`,
        serviceData,
        { headers: { Authorization: `Bearer ${token}` } }
      ).subscribe({
        next: () => {
          this.toastService.success('Servicio creado correctamente');
          this.closeServiceForm();
          this.loadServices();
        },
        error: (err) => {
          console.error('Error creating service:', err);
          this.toastService.error(err.error?.detail || 'Error al crear el servicio');
        }
      });
    }
  }

  toggleService(service: Service): void {
    const token = this.authService.getToken();
    this.http.patch(
      `${environment.apiUrl}/services/${service.id}/toggle`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    ).subscribe({
      next: (updatedService: any) => {
        service.state = updatedService.state;
        this.toastService.success(
          service.state ? 'Servicio activado' : 'Servicio desactivado'
        );
      },
      error: (err) => {
        console.error('Error toggling service:', err);
        this.toastService.error('Error al cambiar estado del servicio');
      }
    });
  }

  deleteService(service: Service): void {
    if (!confirm(`¿Estás seguro de eliminar el servicio "${service.name}"?`)) return;

    const token = this.authService.getToken();
    this.http.delete(
      `${environment.apiUrl}/services/${service.id}`,
      { headers: { Authorization: `Bearer ${token}` } }
    ).subscribe({
      next: () => {
        this.toastService.success('Servicio eliminado correctamente');
        this.loadServices();
      },
      error: (err) => {
        console.error('Error deleting service:', err);
        this.toastService.error(err.error?.detail || 'Error al eliminar el servicio');
      }
    });
  }

  // ═══════════════════════════════════════════════════
  // UTILIDADES
  // ═══════════════════════════════════════════════════

  setActiveTab(tab: any): void {
    this.activeTab = tab;
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    date.setMinutes(date.getMinutes() + date.getTimezoneOffset());
    return date.toLocaleDateString('es-ES', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount);
  }

  getStatusClass(status: string): string {
    switch (status) {
      case 'pending': return 'status-pending';
      case 'confirmed': return 'status-confirmed';
      case 'completed': return 'status-completed';
      case 'cancelled': return 'status-cancelled';
      default: return '';
    }
  }

  getStatusText(status: string): string {
    switch (status) {
      case 'pending': return 'Pendiente';
      case 'confirmed': return 'Confirmada';
      case 'completed': return 'Completada';
      case 'cancelled': return 'Cancelada';
      default: return status;
    }
  }

  goBack(): void {
    this.router.navigate(['/services']);
  }
}
