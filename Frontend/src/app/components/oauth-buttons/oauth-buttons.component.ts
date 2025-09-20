import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { OAuthService, OAuthProvider } from '../../services/oauth.service';

@Component({
  selector: 'app-oauth-buttons',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatTooltipModule
  ],
  template: `
    <div class="oauth-buttons-container">
      <div class="oauth-title" *ngIf="showTitle">
        <h3>{{ title }}</h3>
        <p class="subtitle" *ngIf="subtitle">{{ subtitle }}</p>
      </div>

      <div class="oauth-buttons" *ngIf="providers.length > 0">
        <button
          mat-raised-button
          *ngFor="let provider of providers"
          class="oauth-button"
          [style.background-color]="getProviderColor(provider.id)"
          [disabled]="loading"
          [matTooltip]="getProviderTooltip(provider)"
          (click)="onProviderClick(provider)"
        >
          <mat-icon class="provider-icon">{{ getProviderIcon(provider.id) }}</mat-icon>
          <span class="provider-name">{{ getButtonText(provider) }}</span>
          <mat-spinner 
            *ngIf="loading && loadingProvider === provider.id"
            diameter="20"
            color="accent">
          </mat-spinner>
        </button>
      </div>

      <div class="oauth-disabled" *ngIf="providers.length === 0 && !loading">
        <mat-icon>info</mat-icon>
        <p>OAuth authentication is not currently available</p>
        <small>Contact your administrator to enable social login</small>
      </div>

      <div class="oauth-loading" *ngIf="loading && providers.length === 0">
        <mat-spinner diameter="30"></mat-spinner>
        <p>Loading authentication options...</p>
      </div>
    </div>
  `,
  styles: [`
    .oauth-buttons-container {
      width: 100%;
      max-width: 400px;
      margin: 0 auto;
    }

    .oauth-title {
      text-align: center;
      margin-bottom: 24px;
    }

    .oauth-title h3 {
      margin: 0 0 8px 0;
      color: #333;
      font-weight: 500;
    }

    .subtitle {
      color: #666;
      font-size: 14px;
      margin: 0;
    }

    .oauth-buttons {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .oauth-button {
      width: 100%;
      height: 48px;
      border-radius: 8px;
      border: none;
      color: white;
      font-size: 16px;
      font-weight: 500;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      transition: all 0.3s ease;
      position: relative;
      overflow: hidden;
    }

    .oauth-button:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .oauth-button:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }

    .provider-icon {
      font-size: 20px;
      width: 20px;
      height: 20px;
    }

    .provider-name {
      flex: 1;
      text-align: center;
    }

    .oauth-disabled {
      text-align: center;
      padding: 32px;
      color: #666;
      background: #f5f5f5;
      border-radius: 8px;
      border: 2px dashed #ddd;
    }

    .oauth-disabled mat-icon {
      font-size: 48px;
      width: 48px;
      height: 48px;
      margin-bottom: 16px;
      color: #999;
    }

    .oauth-disabled p {
      margin: 0 0 8px 0;
      font-weight: 500;
    }

    .oauth-disabled small {
      color: #999;
    }

    .oauth-loading {
      text-align: center;
      padding: 32px;
      color: #666;
    }

    .oauth-loading p {
      margin-top: 16px;
    }

    /* Provider-specific styling */
    .oauth-button[style*="rgb(66, 133, 244)"] {
      background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
    }

    .oauth-button[style*="rgb(51, 51, 51)"] {
      background: linear-gradient(135deg, #333 0%, #24292e 100%);
    }

    .oauth-button[style*="rgb(0, 0, 0)"] {
      background: linear-gradient(135deg, #000 0%, #333 100%);
    }

    /* Responsive design */
    @media (max-width: 480px) {
      .oauth-buttons-container {
        max-width: 100%;
        padding: 0 16px;
      }

      .oauth-button {
        height: 44px;
        font-size: 15px;
      }

      .provider-icon {
        font-size: 18px;
        width: 18px;
        height: 18px;
      }
    }
  `]
})
export class OAuthButtonsComponent implements OnInit {
  @Input() title: string = 'Continue with';
  @Input() subtitle: string = 'Choose your preferred sign-in method';
  @Input() showTitle: boolean = true;
  @Input() buttonTextPrefix: string = 'Continue with';
  @Output() providerSelected = new EventEmitter<OAuthProvider>();
  @Output() authSuccess = new EventEmitter<any>();
  @Output() authError = new EventEmitter<string>();

  providers: OAuthProvider[] = [];
  loading: boolean = false;
  loadingProvider: string | null = null;

  constructor(private oauthService: OAuthService) {}

  ngOnInit(): void {
    this.loadProviders();
  }

  private loadProviders(): void {
    this.loading = true;
    this.oauthService.getProviders().subscribe({
      next: (response) => {
        this.providers = response.providers;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading OAuth providers:', error);
        this.providers = [];
        this.loading = false;
      }
    });
  }

  onProviderClick(provider: OAuthProvider): void {
    if (this.loading) return;

    this.loadingProvider = provider.id;
    this.providerSelected.emit(provider);

    // For development, create a test user
    if (provider.id === 'google') {
      this.createTestGoogleUser();
    } else if (provider.id === 'github') {
      this.createTestGitHubUser();
    } else if (provider.id === 'apple') {
      this.createTestAppleUser();
    } else {
      // Use the real OAuth flow
      this.oauthService.loginWithProvider(provider.id);
    }
  }

  private createTestGoogleUser(): void {
    const testUser = {
      id: 'google_' + Date.now(),
      email: 'test.google@example.com',
      name: 'Google Test User',
      first_name: 'Google',
      last_name: 'User',
      username: 'googleuser',
      avatar_url: 'https://via.placeholder.com/100'
    };

    this.oauthService.createTestUser('google', testUser).subscribe({
      next: (response) => {
        this.loadingProvider = null;
        this.authSuccess.emit(response);
        
        // Store token and redirect
        if (response.access_token) {
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('user', JSON.stringify(response.user));
          window.location.href = '/dashboard';
        }
      },
      error: (error) => {
        this.loadingProvider = null;
        this.authError.emit(error.error?.detail || 'Authentication failed');
      }
    });
  }

  private createTestGitHubUser(): void {
    const testUser = {
      id: 'github_' + Date.now(),
      email: 'test.github@example.com',
      name: 'GitHub Test User',
      first_name: 'GitHub',
      last_name: 'User',
      username: 'githubuser',
      avatar_url: 'https://via.placeholder.com/100'
    };

    this.oauthService.createTestUser('github', testUser).subscribe({
      next: (response) => {
        this.loadingProvider = null;
        this.authSuccess.emit(response);
        
        // Store token and redirect
        if (response.access_token) {
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('user', JSON.stringify(response.user));
          window.location.href = '/dashboard';
        }
      },
      error: (error) => {
        this.loadingProvider = null;
        this.authError.emit(error.error?.detail || 'Authentication failed');
      }
    });
  }

  private createTestAppleUser(): void {
    const testUser = {
      id: 'apple_' + Date.now(),
      email: 'test.apple@example.com',
      name: 'Apple Test User',
      first_name: 'Apple',
      last_name: 'User',
      username: 'appleuser',
      avatar_url: 'https://via.placeholder.com/100'
    };

    this.oauthService.createTestUser('apple', testUser).subscribe({
      next: (response) => {
        this.loadingProvider = null;
        this.authSuccess.emit(response);
        
        // Store token and redirect
        if (response.access_token) {
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('user', JSON.stringify(response.user));
          window.location.href = '/dashboard';
        }
      },
      error: (error) => {
        this.loadingProvider = null;
        this.authError.emit(error.error?.detail || 'Authentication failed');
      }
    });
  }

  getProviderIcon(providerId: string): string {
    const iconMap: { [key: string]: string } = {
      google: 'account_circle',
      github: 'code',
      apple: 'phone_iphone'
    };
    return iconMap[providerId] || 'login';
  }

  getProviderColor(providerId: string): string {
    return this.oauthService.getProviderColor(providerId);
  }

  getProviderTooltip(provider: OAuthProvider): string {
    return `Sign in with your ${provider.name} account`;
  }

  getButtonText(provider: OAuthProvider): string {
    return `${this.buttonTextPrefix} ${provider.name}`;
  }
}
