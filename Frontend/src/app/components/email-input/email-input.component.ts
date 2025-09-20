import { Component, Input, Output, EventEmitter, OnInit, OnDestroy, forwardRef } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR, FormControl } from '@angular/forms';
import { Subject, debounceTime, distinctUntilChanged, takeUntil } from 'rxjs';
import { EmailValidationService, EmailValidationResult } from '../../services/email-validation.service';

@Component({
  selector: 'app-email-input',
  templateUrl: './email-input.component.html',
  styleUrls: ['./email-input.component.scss'],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => EmailInputComponent),
      multi: true
    }
  ]
})
export class EmailInputComponent implements OnInit, OnDestroy, ControlValueAccessor {
  @Input() placeholder = 'Enter your email address';
  @Input() label = 'Email';
  @Input() required = true;
  @Input() debounceMs = 500;
  @Input() showSuggestions = true;
  @Output() validationChange = new EventEmitter<EmailValidationResult>();

  emailControl = new FormControl('');
  validationResult: EmailValidationResult = {
    isValid: false,
    isAvailable: false,
    message: '',
    isChecking: false
  };

  suggestions: string[] = [];
  showSuggestionsList = false;
  private destroy$ = new Subject<void>();

  // ControlValueAccessor implementation
  private onChange = (value: string) => {};
  private onTouched = () => {};

  constructor(private emailValidationService: EmailValidationService) {}

  ngOnInit(): void {
    // Subscribe to email changes with debouncing
    this.emailControl.valueChanges
      .pipe(
        debounceTime(this.debounceMs),
        distinctUntilChanged(),
        takeUntil(this.destroy$)
      )
      .subscribe(email => {
        if (email) {
          this.validateEmail(email);
          this.updateSuggestions(email);
        } else {
          this.resetValidation();
        }
        this.onChange(email || '');
      });

    // Subscribe to validation state changes
    this.emailValidationService.validationState$
      .pipe(takeUntil(this.destroy$))
      .subscribe(result => {
        this.validationResult = result;
        this.validationChange.emit(result);
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  // ControlValueAccessor methods
  writeValue(value: string): void {
    this.emailControl.setValue(value, { emitEvent: false });
  }

  registerOnChange(fn: (value: string) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    if (isDisabled) {
      this.emailControl.disable();
    } else {
      this.emailControl.enable();
    }
  }

  onBlur(): void {
    this.onTouched();
    this.showSuggestionsList = false;
  }

  onFocus(): void {
    if (this.suggestions.length > 0) {
      this.showSuggestionsList = true;
    }
  }

  selectSuggestion(suggestion: string): void {
    this.emailControl.setValue(suggestion);
    this.showSuggestionsList = false;
    this.suggestions = [];
    this.validateEmail(suggestion);
  }

  private validateEmail(email: string): void {
    this.emailValidationService.validateEmail(email).subscribe();
  }

  private updateSuggestions(email: string): void {
    if (this.showSuggestions && email.includes('@')) {
      this.suggestions = this.emailValidationService.getEmailSuggestions(email);
      this.showSuggestionsList = this.suggestions.length > 0;
    }
  }

  private resetValidation(): void {
    this.emailValidationService.resetValidationState();
    this.suggestions = [];
    this.showSuggestionsList = false;
  }

  getValidationIcon(): string {
    if (this.validationResult.isChecking) {
      return 'hourglass_empty';
    }
    if (this.validationResult.isValid && this.validationResult.isAvailable) {
      return 'check_circle';
    }
    if (!this.validationResult.isValid || !this.validationResult.isAvailable) {
      return 'error';
    }
    return '';
  }

  getValidationClass(): string {
    if (this.validationResult.isChecking) {
      return 'checking';
    }
    if (this.validationResult.isValid && this.validationResult.isAvailable) {
      return 'valid';
    }
    if (!this.validationResult.isValid || !this.validationResult.isAvailable) {
      return 'invalid';
    }
    return '';
  }
}
