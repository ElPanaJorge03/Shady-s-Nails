import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AppointmentsService, Appointment } from '../../core/services/appointments.service';
import { AuthService } from '../../core/services/auth.service';
import { ToastService } from '../../core/services/toast.service';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner';

@Component({
  selector: 'app-worker-dashboard',
  standalone: true,
  imports: [CommonModule, LoadingSpinnerComponent],
  templateUrl: './worker-dashboard.html',
  styleUrl: './worker-dashboard.scss'
})
export class WorkerDashboardComponent implements OnInit {
  appointments: Appointment[] = [];
  todayAppointments: Appointment[] = [];
  loading = true;
  selectedDate: string = '';

  stats = {
    total: 0,
    completed: 0,
    pending: 0,
    cancelled: 0
  };

  constructor(
    private appointmentsService: AppointmentsService,
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef,
    private toastService: ToastService
  ) {
    console.log('🏗️ Dashboard Constructor - Iniciando...');
    // Fecha de hoy en formato YYYY-MM-DD
    const today = new Date();
    this.selectedDate = this.formatDateForInput(today);
  }

  ngOnInit(): void {
    console.log('🚀 Dashboard ngOnInit - Ejecutando loadAppointments()');
    this.loadAppointments();
    this.cdr.detectChanges();
  }

  loadAppointments(): void {
    console.log('🔍 Solicitando todas las citas...');
    this.loading = true;
    this.appointmentsService.getAllAppointments().subscribe({
      next: (appointments) => {
        console.log('✅ Citas recibidas:', appointments);
        this.appointments = appointments;
        this.filterTodayAppointments();
        this.calculateStats();
        this.loading = false;
        console.log('✨ Estado de carga actualizado a false. Forzando Render.');
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error loading appointments:', err);
        this.toastService.error('Error al cargar las citas');
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  filterTodayAppointments(): void {
    const today = new Date().toISOString().split('T')[0];
    this.todayAppointments = this.appointments.filter(apt =>
      apt.date === today && apt.status !== 'cancelled'
    );
  }

  calculateStats(): void {
    this.stats.total = this.appointments.length;
    this.stats.completed = this.appointments.filter(a => a.status === 'completed').length;
    this.stats.pending = this.appointments.filter(a => a.status === 'confirmed' || a.status === 'pending').length;
    this.stats.cancelled = this.appointments.filter(a => a.status === 'cancelled').length;
  }

  markAsCompleted(appointment: Appointment): void {
    if (!confirm('¿Marcar esta cita como completada?')) {
      return;
    }

    // Actualizar estado (necesitarás un método en el servicio)
    this.appointmentsService.cancelAppointment(appointment.id).subscribe({
      next: () => {
        appointment.status = 'completed';
        this.calculateStats();
        this.toastService.success('Cita marcada como completada');
      },
      error: (err) => {
        console.error('Error updating appointment:', err);
        this.toastService.error('Error al actualizar la cita');
      }
    });
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  formatDateForInput(date: Date): string {
    return date.toISOString().split('T')[0];
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
