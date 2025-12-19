import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ToastService, Toast } from '../../../core/services/toast.service';

@Component({
    selector: 'app-toast',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="toast-container">
      <div *ngFor="let toast of toasts$ | async" 
           class="toast-item" 
           [ngClass]="'toast-' + toast.type"
           (click)="remove(toast.id)">
        <div class="toast-icon">{{ getIcon(toast.type) }}</div>
        <div class="toast-message">{{ toast.message }}</div>
        <button class="toast-close">&times;</button>
      </div>
    </div>
  `,
    styles: [`
    .toast-container {
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 10px;
      pointer-events: none;
    }

    .toast-item {
      pointer-events: auto;
      min-width: 300px;
      max-width: 450px;
      padding: 16px 20px;
      border-radius: 12px;
      background: white;
      box-shadow: 0 10px 30px rgba(0,0,0,0.15);
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: pointer;
      animation: slideIn 0.3s ease-out forwards;
      border-left: 6px solid #ccc;
      position: relative;
    }

    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }

    .toast-success { border-left-color: #2ecc71; }
    .toast-error { border-left-color: #e74c3c; }
    .toast-info { border-left-color: #3498db; }
    .toast-warning { border-left-color: #f1c40f; }

    .toast-icon { font-size: 1.2rem; }
    .toast-message { flex: 1; font-weight: 500; color: #333; }
    
    .toast-close {
      background: none;
      border: none;
      font-size: 1.5rem;
      color: #999;
      cursor: pointer;
      padding: 0;
      line-height: 1;
    }

    /* Responsive */
    @media (max-width: 768px) {
      .toast-container {
        top: auto;
        bottom: 20px;
        right: 20px;
        left: 20px;
      }
      .toast-item {
        min-width: auto;
      }
    }
  `]
})
export class ToastComponent {
    toasts$: any;

    constructor(private toastService: ToastService) {
        this.toasts$ = this.toastService.toasts$;
    }

    remove(id: number): void {
        this.toastService.remove(id);
    }

    getIcon(type: string): string {
        switch (type) {
            case 'success': return '✅';
            case 'error': return '❌';
            case 'warning': return '⚠️';
            case 'info': return 'ℹ️';
            default: return '💬';
        }
    }
}
