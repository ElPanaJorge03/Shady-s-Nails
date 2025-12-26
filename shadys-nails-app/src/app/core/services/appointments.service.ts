import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Appointment {
    id: number;
    worker_id: number;
    customer_id: number;
    service_id: number;
    additional_id?: number;
    date: string;
    start_time: string;
    end_time: string;
    status: string;
    notes?: string;
    created_at: string;
    // Información expandida
    worker_name?: string;
    customer_name?: string;
    service_name?: string;
    additional_name?: string;
    service_price?: number;
    additional_price?: number;
}

@Injectable({
    providedIn: 'root'
})
export class AppointmentsService {
    private apiUrl = environment.apiUrl;

    constructor(private http: HttpClient) { }

    getMyAppointments(phone: string): Observable<Appointment[]> {
        return this.http.get<Appointment[]>(`${this.apiUrl}/appointments?phone=${phone}`);
    }

    getAppointmentById(id: number): Observable<Appointment> {
        return this.http.get<Appointment>(`${this.apiUrl}/appointments/${id}`);
    }

    cancelAppointment(id: number): Observable<Appointment> {
        return this.http.put<Appointment>(`${this.apiUrl}/appointments/${id}`, {
            status: 'cancelled'
        });
    }

    getAllAppointments(): Observable<Appointment[]> {
        return this.http.get<Appointment[]>(`${this.apiUrl}/appointments`);
    }

    createAppointment(appointmentData: any): Observable<Appointment> {
        return this.http.post<Appointment>(`${this.apiUrl}/appointment`, appointmentData);
    }
}
