import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { finalize } from 'rxjs/operators';
import { ApiService, Service } from '../../core/services/api.service';
import { AuthService } from '../../core/services/auth.service';
import { AppointmentsService } from '../../core/services/appointments.service';
import { ToastService } from '../../core/services/toast.service';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner';
import { environment } from '../../../environments/environment';

interface Additional {
  id: number;
  name: string;
  extra_duration: number;
  price: number;
}

interface CalendarDay {
  date: Date;
  day: number;
  dayName: string;
  monthName: string;
  isToday: boolean;
  isSelected: boolean;
  dateString: string;
}

interface TimeSlot {
  time: string;
  available: boolean;
}

interface Worker {
  id: number;
  name: string;
}

@Component({
  selector: 'app-booking',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, LoadingSpinnerComponent],
  templateUrl: './booking.html',
  styleUrl: './booking.scss'
})
export class BookingComponent implements OnInit {
  bookingForm: FormGroup;
  selectedWorkerId?: number;
  services: Service[] = [];
  workers: Worker[] = [];
  additionals: Additional[] = [];
  availableSlots: TimeSlot[] = [];
  selectedService?: Service;
  loading = true; // Iniciar en true
  loadingSlots = false;

  // Calendario - Solo próximos 15 días
  calendarDays: CalendarDay[] = [];
  selectedDate: Date | null = null;

  isLoggedIn = false;
  bookingSuccess = false;
  confirmedAppointment: any = null;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private route: ActivatedRoute,
    private http: HttpClient,
    private apiService: ApiService,
    private cdr: ChangeDetectorRef,
    private toastService: ToastService,
    private authService: AuthService,
    private appointmentsService: AppointmentsService
  ) {
    this.isLoggedIn = !!this.authService.getCurrentUser();

    this.bookingForm = this.fb.group({
      serviceId: ['', Validators.required],
      additionalId: [''],
      date: ['', Validators.required],
      time: ['', Validators.required],
      notes: [''],
      guestName: [''],
      guestEmail: [''],
      guestPhone: ['']
    });

    if (!this.isLoggedIn) {
      this.bookingForm.get('guestName')?.setValidators([Validators.required]);
      this.bookingForm.get('guestEmail')?.setValidators([Validators.required, Validators.email]);
      this.bookingForm.get('guestPhone')?.setValidators([Validators.required, Validators.pattern(/^\d{10}$/)]);
    }
  }

  ngOnInit(): void {
    this.loadWorkers(); // Cargar workers primero
    this.loadServices();
    this.loadAdditionals();
    this.generateCalendar();

    this.route.queryParams.subscribe(params => {
      if (params['serviceId']) {
        this.bookingForm.patchValue({ serviceId: +params['serviceId'] });
        this.onServiceChange();
      }
    });
  }

  loadWorkers(): void {
    this.http.get<Worker[]>(`${environment.apiUrl}/workers`).subscribe({
      next: (workers) => {
        this.workers = workers;
        if (workers.length > 0) {
          this.selectedWorkerId = workers[0].id; // Seleccionar el primer worker por defecto
          console.log('✅ Worker seleccionado por defecto:', this.selectedWorkerId);
        }
      },
      error: (err) => console.error('❌ Error loading workers:', err)
    });
  }

  loadServices(): void {
    console.log('🔍 Cargando servicios...');
    this.apiService.getServices().subscribe({
      next: (services) => {
        console.log('✅ Servicios cargados:', services);
        this.services = services;
        this.loading = false;

        // Si ya hay serviceId en el form, actualizar selectedService
        if (this.bookingForm.get('serviceId')?.value) {
          this.onServiceChange();
        }

        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('❌ Error loading services:', err);
        this.toastService.error('Error al cargar servicios. Reintenta pronto.');
        this.loading = false;
        this.cdr.markForCheck();
      }
    });
  }

  loadAdditionals(): void {
    console.log('🔍 Cargando adicionales...');
    this.http.get<Additional[]>(`${environment.apiUrl}/additionals`).subscribe({
      next: (additionals) => {
        console.log('✅ Adicionales cargados:', additionals);
        this.additionals = additionals;
      },
      error: (err) => console.error('❌ Error loading additionals:', err)
    });
  }

  onServiceChange(): void {
    const serviceId = this.bookingForm.get('serviceId')?.value;
    this.selectedService = this.services.find(s => s.id === +serviceId);

    // Resetear horario si cambia el servicio
    this.bookingForm.patchValue({ time: '' });

    if (this.selectedDate) {
      this.loadAvailableSlots();
    }
  }

  // ==================== CALENDARIO (15 DÍAS) ====================

  generateCalendar(): void {
    this.calendarDays = [];
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Generar los próximos 15 días
    for (let i = 0; i < 15; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);

      const dayNames = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
      const monthNames = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
        'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

      const dateToCheck = new Date(date);
      dateToCheck.setHours(0, 0, 0, 0);

      this.calendarDays.push({
        date: date,
        day: date.getDate(),
        dayName: dayNames[date.getDay()],
        monthName: monthNames[date.getMonth()],
        isToday: i === 0,
        isSelected: this.selectedDate ? dateToCheck.getTime() === this.selectedDate.getTime() : false,
        dateString: this.formatDate(date)
      });
    }
  }

  formatDate(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  selectDate(day: CalendarDay): void {
    if (!this.selectedService) return;

    this.selectedDate = day.date;
    this.bookingForm.patchValue({ date: day.dateString });
    this.generateCalendar();
    this.loadAvailableSlots();
  }

  // ==================== HORARIOS ====================

  loadAvailableSlots(): void {
    const date = this.bookingForm.get('date')?.value;
    const serviceId = this.bookingForm.get('serviceId')?.value;

    if (!date || !serviceId) {
      this.availableSlots = [];
      return;
    }

    const additionalId = this.bookingForm.get('additionalId')?.value;

    // Verificar si tenemos un worker seleccionado, si no, usar 4 como fallback o esperar a que carguen
    const workerId = this.selectedWorkerId ?? (this.workers.length > 0 ? this.workers[0].id : 4);

    console.log(`🔍 Buscando disponibilidad: Worker=${workerId}, Date=${date}, Service=${serviceId}`);

    const params: any = {
      worker_id: workerId,
      date: date,
      service_id: serviceId.toString()
    };

    // Solo agregar additional_id si tiene valor
    if (additionalId) {
      params.additional_id = additionalId.toString();
    }

    this.loadingSlots = true;
    this.availableSlots = [];

    this.http.get<any>(`${environment.apiUrl}/availability`, { params })
      .pipe(finalize(() => {
        this.loadingSlots = false;
        this.cdr.markForCheck();
      }))
      .subscribe({
        next: (response) => {
          console.log('✅ Slots recibidos:', response.available_slots.length);
          this.availableSlots = response.available_slots.map((slot: string) => ({
            time: slot,
            available: true
          }));
        },
        error: (err) => {
          console.error('❌ Error loading slots:', err);
          this.availableSlots = [];
        }
      });
  }

  selectTime(slot: TimeSlot): void {
    this.bookingForm.patchValue({ time: slot.time });
  }

  isTimeSelected(time: string): boolean {
    return this.bookingForm.get('time')?.value === time;
  }

  // Agrupar horarios por periodos (Mañana, Tarde, Noche)
  getTimeSlotGroups(): { label: string, slots: TimeSlot[] }[] {
    const groups: { label: string, slots: TimeSlot[] }[] = [
      { label: 'Mañana', slots: [] },
      { label: 'Tarde', slots: [] },
      { label: 'Noche', slots: [] }
    ];

    this.availableSlots.forEach(slot => {
      const hour = parseInt(slot.time.split(':')[0]);
      if (hour < 12) {
        groups[0].slots.push(slot);
      } else if (hour < 17) {
        groups[1].slots.push(slot);
      } else {
        groups[2].slots.push(slot);
      }
    });

    return groups.filter(g => g.slots.length > 0);
  }

  getEstimatedTotal(): string {
    if (!this.selectedService) return '$0';

    let total = this.selectedService.price;

    const additionalId = this.bookingForm.get('additionalId')?.value;
    if (additionalId) {
      const additional = this.additionals.find(a => a.id === +additionalId);
      if (additional) {
        total += additional.price;
      }
    }

    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(total);
  }

  // ==================== SUBMIT ====================

  onSubmit(): void {
    if (this.bookingForm.invalid) {
      Object.keys(this.bookingForm.controls).forEach(key => {
        this.bookingForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.loading = true;
    const formValue = this.bookingForm.value;
    const currentUser = this.authService.getCurrentUser();

    if (currentUser && currentUser.role !== 'worker') {
      // Usuario autenticado (Google OAuth u otro) — crear/usar customer con sus datos reales
      const customerData = {
        name: currentUser.name || 'Cliente',
        phone: currentUser.phone || '0000000000',
        email: currentUser.email || ''
      };

      this.http.post<any>(`${environment.apiUrl}/customers`, customerData).subscribe({
        next: (customer) => {
          this.createAppointmentForUser(customer.id, formValue);
        },
        error: (err) => {
          console.error('Error creating customer:', err);
          this.toastService.error('Error al registrar tus datos para la cita.');
          this.loading = false;
        }
      });
    } else if (!currentUser) {
      // Invitado sin cuenta — usa los datos del formulario
      const customerData = {
        name: formValue.guestName || 'Invitado',
        phone: formValue.guestPhone || '0000000000',
        email: formValue.guestEmail || ''
      };

      this.http.post<any>(`${environment.apiUrl}/customers`, customerData).subscribe({
        next: (customer) => {
          this.createAppointmentForUser(customer.id, formValue);
        },
        error: (err) => {
          console.error('Error creating customer:', err);
          this.toastService.error('Error al registrar tus datos para la cita.');
          this.loading = false;
        }
      });
    }
  }

  private createAppointmentForUser(customerId: number, formValue: any): void {
    const workerId = this.selectedWorkerId ?? 4; // Gina Paola Martinez Barrera

    const appointmentData = {
      worker_id: workerId,
      customer_id: customerId,
      service_id: +formValue.serviceId,
      additional_id: formValue.additionalId ? +formValue.additionalId : null,
      date: formValue.date,
      start_time: formValue.time,
      notes: formValue.notes || ''
    };

    this.appointmentsService.createAppointment(appointmentData).subscribe({
      next: (appointment) => {
        this.confirmedAppointment = appointment;
        this.bookingSuccess = true;
        this.loading = false;
        this.toastService.success('¡Cita agendada con éxito! Revisa tu correo.');
      },
      error: (err) => {
        console.error('Error creating appointment:', err);
        this.toastService.error('Error al crear la cita. Reintenta de nuevo.');
        this.loading = false;
      }
    });
  }

  resetBooking(): void {
    this.bookingSuccess = false;
    this.confirmedAppointment = null;
    this.bookingForm.reset();
    this.selectedService = undefined;
    this.selectedDate = null;
    this.availableSlots = [];
    this.generateCalendar();
    this.loadServices();
  }

  cancel(): void {
    this.router.navigate(['/services']);
  }

  changeService(): void {
    // Navegar de vuelta a la selección de servicios
    this.router.navigate(['/services']);
  }

  getSelectedServiceInfo(): string {
    if (!this.selectedService) return '';
    const additional = this.additionals.find(a => a.id === +this.bookingForm.get('additionalId')?.value);
    const totalDuration = this.selectedService.duration_minutes + (additional?.extra_duration || 0);
    const totalPrice = this.selectedService.price + (additional?.price || 0);
    return `${this.selectedService.name}${additional ? ' + ' + additional.name : ''} - ${totalDuration} min - $${totalPrice.toLocaleString()}`;
  }
}
