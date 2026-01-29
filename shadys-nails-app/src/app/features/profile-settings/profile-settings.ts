import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, AbstractControl } from '@angular/forms';
import { AuthService, User } from '../../core/services/auth.service';
import { ToastService } from '../../core/services/toast.service';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner';

@Component({
    selector: 'app-profile-settings',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule, LoadingSpinnerComponent],
    templateUrl: './profile-settings.html',
    styleUrl: './profile-settings.scss'
})
export class ProfileSettingsComponent implements OnInit {
    profileForm: FormGroup;
    loading = true;
    submitting = false;
    currentUser: User | null = null;

    constructor(
        private fb: FormBuilder,
        private authService: AuthService,
        private toastService: ToastService
    ) {
        this.profileForm = this.fb.group({
            name: ['', Validators.required],
            phone: ['', Validators.required],
            password: ['', [Validators.minLength(6)]],
            confirmPassword: ['']
        }, { validators: this.passwordMatchValidator });
    }

    ngOnInit(): void {
        this.loadUserData();
    }

    loadUserData(): void {
        // Tomar datos del servicio (ya están en memoria)
        this.currentUser = this.authService.getCurrentUser();

        if (this.currentUser) {
            this.profileForm.patchValue({
                name: this.currentUser.name,
                phone: this.currentUser.phone
            });
            this.loading = false;
        } else {
            // Si no hay user, intentar refetchear o redirigir (pero auth guard debe manejar eso)
            this.loading = false;
        }
    }

    passwordMatchValidator(control: AbstractControl): { [key: string]: boolean } | null {
        const password = control.get('password');
        const confirmPassword = control.get('confirmPassword');

        if (password?.value !== confirmPassword?.value) {
            return { 'mismatch': true };
        }
        return null;
    }

    onSubmit(): void {
        if (this.profileForm.invalid) return;

        this.submitting = true;
        const formVal = this.profileForm.value;

        const updateData: any = {
            name: formVal.name,
            phone: formVal.phone
        };

        if (formVal.password) {
            updateData.password = formVal.password;
        }

        this.authService.updateProfile(updateData).subscribe({
            next: (updatedUser) => {
                this.currentUser = updatedUser;
                this.toastService.success('Perfil actualizado correctamente');
                this.submitting = false;
                // Limpiar passwords
                this.profileForm.patchValue({
                    password: '',
                    confirmPassword: ''
                });
            },
            error: (err) => {
                console.error('Update error:', err);
                this.toastService.error('Error al actualizar perfil');
                this.submitting = false;
            }
        });
    }
}
