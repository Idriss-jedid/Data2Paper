import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { environment } from '../../environments/environment';

export interface OAuthProvider {
  id: string;
  name: string;
  icon: string;
  color: string;
}

export interface OAuthProvidersResponse {
  providers: OAuthProvider[];
  enabled: boolean;
  message?: string;
}

export interface LinkedProvider {
  id: string;
  name: string;
  icon: string;
}

export interface LinkedProvidersResponse {
  linked_providers: LinkedProvider[];
}

@Injectable({
  providedIn: 'root'
})
export class OAuthService {
  private readonly apiUrl = `${environment.apiUrl}/oauth`;
  private linkedProvidersSubject = new BehaviorSubject<LinkedProvider[]>([]);
  public linkedProviders$ = this.linkedProvidersSubject.asObservable();

  constructor(private http: HttpClient) {}

  /**
   * Get available OAuth providers
   */
  getProviders(): Observable<OAuthProvidersResponse> {
    return this.http.get<OAuthProvidersResponse>(`${this.apiUrl}/providers`);
  }

  /**
   * Initiate OAuth login with a specific provider
   */
  loginWithProvider(provider: string): void {
    // For now, open OAuth login in a popup window
    const popup = window.open(
      `${this.apiUrl}/login/${provider}`,
      'oauth-login',
      'width=500,height=600,scrollbars=yes,resizable=yes'
    );

    // Listen for the popup to close or receive a message
    const checkClosed = setInterval(() => {
      if (popup?.closed) {
        clearInterval(checkClosed);
        // Handle popup closed - could be successful or cancelled
        this.handleOAuthCallback();
      }
    }, 1000);

    // Listen for messages from the popup
    window.addEventListener('message', (event) => {
      if (event.origin !== environment.apiUrl.replace('/api', '')) {
        return;
      }
      
      if (event.data.type === 'oauth-success') {
        clearInterval(checkClosed);
        popup?.close();
        this.handleOAuthSuccess(event.data.token, event.data.user);
      } else if (event.data.type === 'oauth-error') {
        clearInterval(checkClosed);
        popup?.close();
        this.handleOAuthError(event.data.error);
      }
    });
  }

  /**
   * Create a test OAuth user (for development)
   */
  createTestUser(provider: string, userData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/create-test-user/${provider}`, userData);
  }

  /**
   * Get linked OAuth providers for current user
   */
  getLinkedProviders(): Observable<LinkedProvidersResponse> {
    return this.http.get<LinkedProvidersResponse>(`${this.apiUrl}/linked`);
  }

  /**
   * Unlink an OAuth provider from current user
   */
  unlinkProvider(provider: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.apiUrl}/unlink/${provider}`, {});
  }

  /**
   * Update linked providers in the service
   */
  updateLinkedProviders(providers: LinkedProvider[]): void {
    this.linkedProvidersSubject.next(providers);
  }

  /**
   * Load linked providers from API
   */
  loadLinkedProviders(): void {
    this.getLinkedProviders().subscribe({
      next: (response) => {
        this.updateLinkedProviders(response.linked_providers);
      },
      error: (error) => {
        console.error('Error loading linked providers:', error);
        this.updateLinkedProviders([]);
      }
    });
  }

  private handleOAuthCallback(): void {
    // Check URL for OAuth callback parameters
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const provider = urlParams.get('provider');
    
    if (token && provider) {
      // Store token and redirect
      localStorage.setItem('access_token', token);
      window.location.href = '/dashboard';
    }
  }

  private handleOAuthSuccess(token: string, user: any): void {
    // Store token and user info
    localStorage.setItem('access_token', token);
    if (user) {
      localStorage.setItem('user', JSON.stringify(user));
    }
    
    // Redirect to dashboard
    window.location.href = '/dashboard';
  }

  private handleOAuthError(error: string): void {
    console.error('OAuth error:', error);
    // You could show a toast notification here
    alert(`OAuth authentication failed: ${error}`);
  }

  /**
   * Get provider icon class for display
   */
  getProviderIconClass(provider: string): string {
    const iconMap: { [key: string]: string } = {
      google: 'fab fa-google',
      github: 'fab fa-github',
      apple: 'fab fa-apple'
    };
    return iconMap[provider] || 'fas fa-sign-in-alt';
  }

  /**
   * Get provider color for theming
   */
  getProviderColor(provider: string): string {
    const colorMap: { [key: string]: string } = {
      google: '#4285f4',
      github: '#333333',
      apple: '#000000'
    };
    return colorMap[provider] || '#666666';
  }
}
