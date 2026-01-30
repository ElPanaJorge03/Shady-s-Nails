import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { map, take, filter, of, switchMap } from 'rxjs';

export const workerGuard: CanActivateFn = (route, state) => {
    const router = inject(Router);
    const authService = inject(AuthService);
    const token = authService.getToken();

    if (!token) {
        router.navigate(['/login']);
        return of(false);
    }

    // Si hay token, esperamos a que el usuario cargue si aún es null
    return authService.currentUser$.pipe(
        // Si el usuario es null y hay token, seguimos esperando
        // Pero si el usuario ya cargó, evaluamos el rol
        filter(user => user !== null),
        take(1),
        map(user => {
            if (user && user.role === 'worker') {
                return true;
            } else {
                router.navigate(['/services']);
                return false;
            }
        })
    );
};
