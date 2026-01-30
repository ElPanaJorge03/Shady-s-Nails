import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { filter, map, take, of } from 'rxjs';

export const authGuard: CanActivateFn = (route, state) => {
    const router = inject(Router);
    const authService = inject(AuthService);
    const token = authService.getToken();

    if (token) {
        // Esperamos a que el usuario cargue si hay token
        return authService.currentUser$.pipe(
            filter(user => user !== null),
            take(1),
            map(() => true)
        );
    } else {
        router.navigate(['/login']);
        return of(false);
    }
};
