import { Component, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { ToastService } from '../../core/services/toast.service';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner';

declare var google: any;

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, LoadingSpinnerComponent, RouterModule],
  templateUrl: './login.html',
  styleUrl: './login.scss'
})
export class LoginComponent implements AfterViewInit {
  loginForm: FormGroup;
  loading = false;
  error = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private toastService: ToastService
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  ngAfterViewInit(): void {
    if (typeof google !== 'undefined') {
      google.accounts.id.initialize({
        client_id: '448238951869-k8n9ddsbgc5odhihscc379qsvp11t50l.apps.googleusercontent.com',
        callback: this.handleGoogleLogin.bind(this)
      });

      google.accounts.id.renderButton(
        document.getElementById('google-btn'),
        { theme: 'outline', size: 'large', width: '100%', text: 'signin_with' }
      );
    }
  }

  handleGoogleLogin(response: any): void {
    if (response.credential) {
      this.loading = true;
      this.authService.googleLogin(response.credential).subscribe({
        next: () => {
          this.toastService.success('¡Sesión iniciada con Google!');
          this.redirectUser();
        },
        error: (err) => {
          console.error('Login con Google falló:', err);
          this.toastService.error('Error al iniciar sesión con Google');
          this.loading = false;
        }
      });
    }
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;
    this.error = '';

    this.authService.login(this.loginForm.value).subscribe({
      next: () => {
        this.toastService.success('¡Bienvenido de nuevo!');
        this.redirectUser();
      },
      error: (err) => {
        console.error('❌ Error en login:', err);
        this.toastService.error('Email o contraseña incorrectos');
        this.loading = false;
      }
    });
  }

  private redirectUser(): void {
    this.authService.currentUser$.subscribe(user => {
      if (user) {
        this.loading = false;
        if (user.role === 'worker') {
          this.router.navigate(['/dashboard']);
        } else {
          this.router.navigate(['/services']);
        }
      }
    });
  }
}
