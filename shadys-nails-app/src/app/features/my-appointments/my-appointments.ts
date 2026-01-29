import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AppointmentsService, Appointment } from '../../core/services/appointments.service';
import { AuthService } from '../../core/services/auth.service';
import { ToastService } from '../../core/services/toast.service';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner';

@Component({
  selector: 'app-my-appointments',
  standalone: true,
  imports: [CommonModule, LoadingSpinnerComponent],
  templateUrl: './my-appointments.html',
  styleUrl: './my-appointments.scss'
})
export class MyAppointmentsComponent implements OnInit {
  upcomingAppointments: Appointment[] = [];
  historyAppointments: Appointment[] = [];
  loading = true;

  constructor(
    private appointmentsService: AppointmentsService,
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef,
    private toastService: ToastService
  ) { }

  ngOnInit(): void {
    this.loadAppointments();
  }

  loadAppointments(): void {
    this.loading = true;
    this.appointmentsService.getAllAppointments().subscribe({
      next: (appointments) => {
        const now = new Date();
        now.setHours(0, 0, 0, 0);

        this.upcomingAppointments = appointments.filter(apt => {
          const aptDate = new Date(apt.date);
          return aptDate >= now && apt.status !== 'cancelled' && apt.status !== 'completed';
        });

        this.historyAppointments = appointments.filter(apt => {
          const aptDate = new Date(apt.date);
          return aptDate < now || apt.status === 'cancelled' || apt.status === 'completed';
        });

        this.historyAppointments = appointments.filter(apt => {
          const aptDate = new Date(apt.date);
          return aptDate < now || apt.status === 'cancelled' || apt.status === 'completed';
        });

        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error loading appointments:', err);
        this.toastService.error('Error al cargar tus citas. Reintenta pronto.');
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  cancelAppointment(appointment: Appointment): void {
    if (!this.canCancel(appointment)) {
      this.toastService.error('Lo sentimos, no puedes cancelar con menos de 2 horas de anticipación.');
      return;
    }

    if (!confirm(`¿Estás seguro de cancelar la cita del ${this.formatDate(appointment.date)} a las ${appointment.start_time}?`)) {
      return;
    }

    this.appointmentsService.cancelAppointment(appointment.id).subscribe({
      next: () => {
        this.upcomingAppointments = this.upcomingAppointments.filter(apt => apt.id !== appointment.id);
        this.toastService.success('Cita cancelada correctamente');
      },
      error: (err) => {
        console.error('Error cancelling appointment:', err);
        const errorMsg = err.error?.detail || 'Error al cancelar la cita. Intenta de nuevo.';
        this.toastService.error(errorMsg);
      }
    });
  }

  canCancel(appointment: Appointment): boolean {
    // Si la cita ya está cancelada o completada, no tiene sentido
    if (appointment.status === 'cancelled' || appointment.status === 'completed') return false;

    try {
      // Combinar fecha y hora
      const aptDate = new Date(appointment.date);
      const timeParts = appointment.start_time.split(':');
      aptDate.setHours(parseInt(timeParts[0]), parseInt(timeParts[1]), 0, 0);

      const now = new Date();
      const diffMs = aptDate.getTime() - now.getTime();
      const diffHours = diffMs / (1000 * 60 * 60);

      return diffHours >= 2;
    } catch (e) {
      return false;
    }
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    const options: Intl.DateTimeFormatOptions = {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    };
    return date.toLocaleDateString('es-ES', options);
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

  goToServices(): void {
    this.router.navigate(['/services']);
  }

  bookNewAppointment(): void {
    this.router.navigate(['/services']);
  }
}
