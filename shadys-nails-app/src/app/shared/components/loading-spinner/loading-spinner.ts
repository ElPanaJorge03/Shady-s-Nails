import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-loading-spinner',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="spinner-container" [class.overlay]="overlay">
      <div class="spinner">
        <div class="dot1"></div>
        <div class="dot2"></div>
      </div>
      <p *ngIf="message" class="loading-text">{{ message }}</p>
    </div>
  `,
    styles: [`
    .spinner-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 2rem;
    }

    .spinner-container.overlay {
      position: absolute;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(255, 255, 255, 0.8);
      z-index: 10;
      border-radius: inherit;
    }

    .spinner {
      width: 40px;
      height: 40px;
      position: relative;
      text-align: center;
      animation: sk-rotate 2.0s infinite linear;
    }

    .dot1, .dot2 {
      width: 60%;
      height: 60%;
      display: inline-block;
      position: absolute;
      top: 0;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 100%;
      animation: sk-bounce 2.0s infinite ease-in-out;
    }

    .dot2 {
      top: auto;
      bottom: 0;
      animation-delay: -1.0s;
    }

    @keyframes sk-rotate { 100% { transform: rotate(360deg); } }

    @keyframes sk-bounce {
      0%, 100% { transform: scale(0.0); }
      50% { transform: scale(1.0); }
    }

    .loading-text {
      margin-top: 1rem;
      color: #667eea;
      font-weight: 600;
      font-size: 0.9rem;
    }
  `]
})
export class LoadingSpinnerComponent {
    @Input() message: string = '';
    @Input() overlay: boolean = false;
}
