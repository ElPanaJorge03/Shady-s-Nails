import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
    console.log(`📡 Interceptando petición: ${req.url}`);
    const token = localStorage.getItem('access_token');

    if (token) {
        console.log('🔑 Token encontrado, adjuntando...');
        const cloned = req.clone({
            headers: req.headers.set('Authorization', `Bearer ${token}`)
        });
        return next(cloned);
    }

    console.warn('⚠️ No se encontró token para la petición');
    return next(req);
};
