import { Component, OnInit } from '@angular/core';
import { ThemeService, Theme } from '../../services/theme.service';

@Component({
  selector: 'app-theme-toggle',
  template: `
    <button 
      mat-icon-button 
      (click)="toggleTheme()"
      [attr.aria-label]="'Switch to ' + (currentTheme === 'light' ? 'dark' : 'light') + ' mode'"
      class="theme-toggle"
    >
      <mat-icon>{{ currentTheme === 'light' ? 'dark_mode' : 'light_mode' }}</mat-icon>
    </button>
  `,
  styles: [`
    .theme-toggle {
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 1000;
      background: var(--surface-glass) !important;
      backdrop-filter: blur(10px);
      border: 1px solid var(--border-light);
      color: var(--text-primary) !important;
      transition: all 0.3s ease;
      
      &:hover {
        background: var(--surface) !important;
        transform: scale(1.1);
      }
      
      mat-icon {
        color: var(--text-primary);
      }
    }
  `]
})
export class ThemeToggleComponent implements OnInit {
  currentTheme: Theme = 'light';

  constructor(private themeService: ThemeService) {}

  ngOnInit(): void {
    this.themeService.theme$.subscribe((theme: Theme) => {
      this.currentTheme = theme;
    });
  }

  toggleTheme(): void {
    this.themeService.toggleTheme();
  }
}
