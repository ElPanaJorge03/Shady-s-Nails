import { Component, signal, OnInit } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService, User } from './core/services/auth.service';
import { filter } from 'rxjs';
import { ToastComponent } from './shared/components/toast/toast';
import { ToastService } from './core/services/toast.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, CommonModule, ToastComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  protected readonly title = signal('shadys-nails-app');
  currentUser: User | null = null;
  currentRoute = '';

  constructor(
    private authService: AuthService,
    private router: Router,
    private toastService: ToastService
  ) {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });

    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      this.currentRoute = event.url;
    });
  }

  ngOnInit(): void {
    // Inicialización si es necesaria
  }

  showHeader(): boolean {
    // No mostrar header en login
    return this.currentRoute !== '/login' && this.currentRoute !== '/';
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  goHome(): void {
    if (this.isWorker()) {
      this.router.navigate(['/dashboard']);
    } else {
      this.router.navigate(['/services']);
    }
  }

  goToMyAppointments(): void {
    this.router.navigate(['/my-appointments']);
  }

  goToDashboard(): void {
    this.router.navigate(['/dashboard']);
  }

  goToSettings(): void {
    this.router.navigate(['/settings']);
  }

  isWorker(): boolean {
    return this.authService.isWorker();
  }

  isCustomer(): boolean {
    return this.authService.isCustomer();
  }
}
