import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../auth.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { EmailValidationService, EmailValidationResult } from '../../services/email-validation.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent implements OnInit {
  registerForm!: FormGroup;
  isLoading = false;
  hideEmail = false;
  hidePassword = true;
  hideConfirmPassword = true;
  isDarkMode = false;
  emailValidationResult: EmailValidationResult = {
    isValid: false,
    isAvailable: false,
    message: '',
    isChecking: false
  };

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private snackBar: MatSnackBar,
    private emailValidationService: EmailValidationService
  ) {}

  ngOnInit(): void {
    // Initialize theme from localStorage or system preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      this.isDarkMode = savedTheme === 'dark';
      document.documentElement.setAttribute('data-theme', savedTheme);
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      this.isDarkMode = prefersDark;
      const theme = prefersDark ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', theme);
      localStorage.setItem('theme', theme);
    }
    
    // Redirect if already logged in
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/dashboard']);
    }

    this.registerForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6), this.passwordValidator]],
      confirmPassword: ['', [Validators.required]],
      agreeToTerms: [false, [Validators.requiredTrue]]
    }, { validators: this.passwordMatchValidator });
  }

  onEmailValidationChange(result: EmailValidationResult): void {
    this.emailValidationResult = result;
    
    // Update form validation based on email validation result
    const emailControl = this.registerForm.get('email');
    if (emailControl) {
      if (!result.isValid || !result.isAvailable) {
        emailControl.setErrors({ 'emailValidation': true });
      } else if (result.isValid && result.isAvailable) {
        // Clear email validation errors but keep other errors
        const errors = emailControl.errors;
        if (errors) {
          delete errors['emailValidation'];
          emailControl.setErrors(Object.keys(errors).length > 0 ? errors : null);
        }
      }
    }
  }

  onSubmit(): void {
    if (this.registerForm.valid && this.emailValidationResult.isValid && this.emailValidationResult.isAvailable) {
      this.isLoading = true;
      const { name, email, password } = this.registerForm.value;

      this.authService.register({ name, email, password }).subscribe({
        next: (response) => {
          this.isLoading = false;
          this.showSuccess('Registration successful! Please log in.');
          this.router.navigate(['/login']);
        },
        error: (error) => {
          this.isLoading = false;
          this.showError(error.message || 'Registration failed. Please try again.');
        }
      });
    } else {
      this.markFormGroupTouched();
      if (!this.emailValidationResult.isValid || !this.emailValidationResult.isAvailable) {
        this.showError('Please fix the email validation issues before proceeding.');
      }
    }
  }

  getErrorMessage(fieldName: string): string {
    const field = this.registerForm.get(fieldName);
    
    if (field?.hasError('required')) {
      return `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)} is required`;
    }
    if (field?.hasError('email')) {
      return 'Please enter a valid email address';
    }
    if (field?.hasError('minlength')) {
      const requiredLength = field.errors?.['minlength']?.requiredLength;
      return `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)} must be at least ${requiredLength} characters long`;
    }
    if (field?.hasError('passwordStrength')) {
      return 'Password must contain at least one uppercase letter, one lowercase letter, and one number';
    }
    if (fieldName === 'confirmPassword' && this.registerForm.hasError('passwordMismatch')) {
      return 'Passwords do not match';
    }
    
    return '';
  }

  private passwordValidator(control: AbstractControl): { [key: string]: any } | null {
    const password = control.value;
    if (!password) return null;

    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumeric = /[0-9]/.test(password);

    if (hasUpperCase && hasLowerCase && hasNumeric) {
      return null;
    }
    return { passwordStrength: true };
  }

  private passwordMatchValidator(form: AbstractControl): { [key: string]: any } | null {
    const password = form.get('password');
    const confirmPassword = form.get('confirmPassword');
    
    if (!password || !confirmPassword) return null;
    
    if (password.value !== confirmPassword.value) {
      return { passwordMismatch: true };
    }
    return null;
  }

  private markFormGroupTouched(): void {
    Object.keys(this.registerForm.controls).forEach(key => {
      this.registerForm.get(key)?.markAsTouched();
    });
  }

  private showSuccess(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      panelClass: ['success-snackbar']
    });
  }

  private showError(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 5000,
      panelClass: ['error-snackbar']
    });
  }

  toggleTheme(): void {
    this.isDarkMode = !this.isDarkMode;
    const theme = this.isDarkMode ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }
}
