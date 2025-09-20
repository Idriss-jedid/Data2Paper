import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, BehaviorSubject } from 'rxjs';
import { map, catchError, debounceTime, distinctUntilChanged, switchMap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface EmailCheckResponse {
  email: string;
  is_available: boolean;
  is_valid: boolean;
  message: string;
}

export interface EmailValidationResult {
  isValid: boolean;
  isAvailable: boolean;
  message: string;
  isChecking: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class EmailValidationService {
  private apiUrl = `${environment.apiUrl}/auth`;
  private validationCache = new Map<string, EmailCheckResponse>();
  
  // Subject to track current validation state
  private validationState = new BehaviorSubject<EmailValidationResult>({
    isValid: false,
    isAvailable: false,
    message: '',
    isChecking: false
  });

  public validationState$ = this.validationState.asObservable();

  constructor(private http: HttpClient) {}

  /**
   * Validate email format locally
   */
  isValidEmailFormat(email: string): boolean {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  }

  /**
   * Check if email is from a disposable email provider
   */
  isDisposableEmail(email: string): boolean {
    const disposableDomains = [
      '10minutemail.com', '10minutemail.net', 'guerrillamail.com',
      'mailinator.com', 'yopmail.com', 'tempmail.org', 'throwaway.email',
      'temp-mail.org', 'getnada.com', 'maildrop.cc', 'sharklasers.com',
      'spam4.me', 'temp-mail.com', 'dispostable.com'
    ];
    
    const domain = email.split('@')[1]?.toLowerCase();
    return domain ? disposableDomains.includes(domain) : false;
  }

  /**
   * Get email domain suggestions for common typos
   */
  getEmailSuggestions(email: string): string[] {
    const commonDomains = [
      'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
      'icloud.com', 'aol.com', 'live.com', 'msn.com'
    ];

    if (!email.includes('@')) return [];

    const [localPart, domain] = email.split('@');
    const suggestions: string[] = [];

    // Check for common typos in popular domains
    const typoMap: { [key: string]: string } = {
      'gmial.com': 'gmail.com',
      'gmai.com': 'gmail.com',
      'yahooo.com': 'yahoo.com',
      'hotmial.com': 'hotmail.com',
      'outlok.com': 'outlook.com'
    };

    if (typoMap[domain]) {
      suggestions.push(`${localPart}@${typoMap[domain]}`);
    }

    // If domain is close to a common domain, suggest it
    commonDomains.forEach(commonDomain => {
      if (this.isCloseMatch(domain, commonDomain)) {
        suggestions.push(`${localPart}@${commonDomain}`);
      }
    });

    return suggestions.slice(0, 3); // Return max 3 suggestions
  }

  /**
   * Check email availability on the server
   */
  checkEmailAvailability(email: string): Observable<EmailCheckResponse> {
    const normalizedEmail = email.trim().toLowerCase();

    // Check cache first
    if (this.validationCache.has(normalizedEmail)) {
      return of(this.validationCache.get(normalizedEmail)!);
    }

    return this.http.post<EmailCheckResponse>(`${this.apiUrl}/check-email`, { email: normalizedEmail })
      .pipe(
        map(response => {
          // Cache the response
          this.validationCache.set(normalizedEmail, response);
          return response;
        }),
        catchError(error => {
          console.error('Email check failed:', error);
          return of({
            email: normalizedEmail,
            is_available: false,
            is_valid: false,
            message: 'Unable to verify email availability'
          });
        })
      );
  }

  /**
   * Comprehensive email validation
   */
  validateEmail(email: string): Observable<EmailValidationResult> {
    this.validationState.next({
      isValid: false,
      isAvailable: false,
      message: 'Checking email...',
      isChecking: true
    });

    const normalizedEmail = email.trim().toLowerCase();

    // Quick format validation
    if (!this.isValidEmailFormat(normalizedEmail)) {
      const result = {
        isValid: false,
        isAvailable: false,
        message: 'Invalid email format',
        isChecking: false
      };
      this.validationState.next(result);
      return of(result);
    }

    // Check for disposable email
    if (this.isDisposableEmail(normalizedEmail)) {
      const result = {
        isValid: false,
        isAvailable: false,
        message: 'Disposable email addresses are not allowed',
        isChecking: false
      };
      this.validationState.next(result);
      return of(result);
    }

    // Check availability on server
    return this.checkEmailAvailability(normalizedEmail).pipe(
      map(response => {
        const result = {
          isValid: response.is_valid,
          isAvailable: response.is_available,
          message: response.message,
          isChecking: false
        };
        this.validationState.next(result);
        return result;
      })
    );
  }

  /**
   * Create a debounced email validator for reactive forms
   */
  createDebouncedValidator(debounceMs: number = 500) {
    return (email: string) => {
      return of(email).pipe(
        debounceTime(debounceMs),
        distinctUntilChanged(),
        switchMap((email: string) => this.validateEmail(email))
      );
    };
  }

  /**
   * Clear validation cache
   */
  clearCache(): void {
    this.validationCache.clear();
  }

  /**
   * Reset validation state
   */
  resetValidationState(): void {
    this.validationState.next({
      isValid: false,
      isAvailable: false,
      message: '',
      isChecking: false
    });
  }

  /**
   * Helper method to check if two strings are close matches
   */
  private isCloseMatch(str1: string, str2: string, threshold: number = 2): boolean {
    return this.levenshteinDistance(str1, str2) <= threshold;
  }

  /**
   * Calculate Levenshtein distance between two strings
   */
  private levenshteinDistance(str1: string, str2: string): number {
    const matrix = [];
    const n = str2.length;
    const m = str1.length;

    if (n === 0) return m;
    if (m === 0) return n;

    for (let i = 0; i <= n; i++) {
      matrix[i] = [i];
    }

    for (let j = 0; j <= m; j++) {
      matrix[0][j] = j;
    }

    for (let i = 1; i <= n; i++) {
      for (let j = 1; j <= m; j++) {
        if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j] + 1
          );
        }
      }
    }

    return matrix[n][m];
  }
}
