import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface LoginRequest {
    email: string;
    password: string;
}

export interface LoginResponse {
    access_token: string;
    token_type: string;
}

export interface User {
    id: number;
    name: string;
    email: string;
    role: string;
    phone?: string;
    business_name?: string;
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private apiUrl = `${environment.apiUrl}/auth`;
    private currentUserSubject = new BehaviorSubject<User | null>(null);
    public currentUser$ = this.currentUserSubject.asObservable();

    constructor(private http: HttpClient) {
        // Cargar usuario si hay token guardado
        const token = this.getToken();
        if (token) {
            this.loadCurrentUser();
        }
    }

    login(credentials: LoginRequest): Observable<LoginResponse> {
        return this.http.post<LoginResponse>(`${this.apiUrl}/login`, credentials)
            .pipe(
                tap(response => {
                    // Guardar token en localStorage
                    localStorage.setItem('access_token', response.access_token);
                    // Cargar datos del usuario
                    this.loadCurrentUser();
                })
            );
    }

    logout(): void {
        localStorage.removeItem('access_token');
        this.currentUserSubject.next(null);
    }

    isWorker(): boolean {
        const user = this.currentUserSubject.value;
        return user?.role === 'worker';
    }

    isCustomer(): boolean {
        const user = this.currentUserSubject.value;
        return user?.role === 'customer';
    }

    getToken(): string | null {
        return localStorage.getItem('access_token');
    }

    isAuthenticated(): boolean {
        return this.getToken() !== null;
    }

    getCurrentUser(): User | null {
        return this.currentUserSubject.value;
    }

    private loadCurrentUser(): void {
        this.http.get<User>(`${this.apiUrl}/me`).subscribe({
            next: (user) => {
                this.currentUserSubject.next(user);
            },
            error: (err) => {
                console.error('Error loading user:', err);
                this.logout();
            }
        });
    }
}
