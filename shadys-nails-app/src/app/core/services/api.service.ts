import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Service {
    id: number;
    worker_id: number;
    name: string;
    duration_minutes: number;
    price: number;
    state: boolean;
}

@Injectable({
    providedIn: 'root'
})
export class ApiService {
    private apiUrl = environment.apiUrl;

    constructor(private http: HttpClient) { }

    getServices(): Observable<Service[]> {
        return this.http.get<Service[]>(`${this.apiUrl}/services`);
    }
}
