import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { ToastService } from '../../core/services/toast.service';

@Component({
    selector: 'app-forgot-password',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterModule],
    templateUrl: './forgot-password.html',
    styleUrl: './forgot-password.scss'
})
export class ForgotPasswordComponent {
    email: string = '';
    code: string = '';
    newPassword: string = '';
    confirmPassword: string = '';
    step: number = 1;
    loading: boolean = false;

    constructor(
        private authService: AuthService,
        private toastService: ToastService,
        private router: Router
    ) { }

    onRequestCode(): void {
        if (!this.email) return;

        this.loading = true;
        this.authService.forgotPassword(this.email).subscribe({
            next: (res) => {
                this.toastService.info(res.message);
                this.step = 2;
                this.loading = false;
            },
            error: (err) => {
                console.error('Error in forgotPassword:', err);
                this.toastService.error('Error al procesar la solicitud. Reintenta pronto.');
                this.loading = false;
            }
        });
    }

    onResetPassword(): void {
        if (!this.isValidReset()) return;

        this.loading = true;
        const data = {
            email: this.email,
            code: this.code,
            new_password: this.newPassword
        };

        this.authService.resetPassword(data).subscribe({
            next: (res) => {
                this.toastService.success(res.message);
                this.loading = false;
                setTimeout(() => {
                    this.router.navigate(['/login']);
                }, 2000);
            },
            error: (err) => {
                console.error('Error in resetPassword:', err);
                const errorMsg = err.error?.detail || 'Error al restablecer la contraseña. Verifica el código.';
                this.toastService.error(errorMsg);
                this.loading = false;
            }
        });
    }

    isValidReset(): boolean {
        return (
            this.code.length === 6 &&
            this.newPassword.length >= 6 &&
            this.newPassword === this.confirmPassword
        );
    }
}
