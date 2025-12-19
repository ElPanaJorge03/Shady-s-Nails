import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const workerGuard: CanActivateFn = (route, state) => {
    const router = inject(Router);
    const authService = inject(AuthService);

    const currentUser = authService.getCurrentUser();

    if (currentUser && currentUser.role === 'worker') {
        return true;
    } else {
        router.navigate(['/services']);
        return false;
    }
};
