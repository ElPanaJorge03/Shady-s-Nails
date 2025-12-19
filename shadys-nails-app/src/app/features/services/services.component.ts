import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ApiService, Service } from '../../core/services/api.service';

@Component({
    selector: 'app-services',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './services.component.html',
    styleUrl: './services.component.scss'
})
export class ServicesComponent implements OnInit {
    services: Service[] = [];
    loading = true;
    error = '';

    constructor(
        private apiService: ApiService,
        private cdr: ChangeDetectorRef,
        private router: Router
    ) { }

    bookService(service: Service): void {
        this.router.navigate(['/booking'], {
            queryParams: { serviceId: service.id }
        });
    }

    ngOnInit() {
        this.loadServices();
    }

    loadServices() {
        console.log('🔍 Iniciando carga de servicios...');
        console.log('📍 Loading inicial:', this.loading);
        this.apiService.getServices().subscribe({
            next: (data) => {
                console.log('✅ Datos recibidos:', data);
                this.services = data;
                this.loading = false;
                console.log('📊 Services array:', this.services);
                console.log('📍 Loading después de asignar:', this.loading);
                console.log('📏 Cantidad de servicios:', this.services.length);
                this.cdr.detectChanges(); // Forzar detección de cambios
                console.log('🔄 Detección de cambios forzada');
            },
            error: (err) => {
                console.error('❌ Error completo:', err);
                this.error = 'Error al cargar servicios. Asegúrate de que el backend esté corriendo.';
                this.loading = false;
                this.cdr.detectChanges();
            }
        });
    }
}
