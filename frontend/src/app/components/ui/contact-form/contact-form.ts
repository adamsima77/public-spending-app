import { Component, inject, input, output, ViewChild, effect } from '@angular/core';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { FormBuilder, FormGroupDirective, ReactiveFormsModule, Validators } from '@angular/forms';
import { ContactMessageRequest } from '../../../generated';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  imports: [
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    ReactiveFormsModule,
    MatProgressSpinnerModule,
  ],
  selector: 'app-contact-form',
  styleUrl: './contact-form.scss',
  templateUrl: './contact-form.html',
})
export class ContactForm {
  private fb = inject(FormBuilder);

  isSubmitting = input<boolean>();
  submissionSucceeded = input<boolean>(false);

  form = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(3)]],
    surname: ['', [Validators.required, Validators.minLength(3)]],
    email: ['', [Validators.required, Validators.email]],
    message: ['', [Validators.required, Validators.minLength(10), Validators.maxLength(1000)]],
  });

  @ViewChild(FormGroupDirective) private formDirective!: FormGroupDirective;
  emitForm = output<ContactMessageRequest>();

  constructor() {
    effect(() => {
      if (this.submissionSucceeded()) {
        this.formDirective.resetForm();
      }
    });
  }

  onSubmit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();

      return;
    }

    this.emitForm.emit(this.form.getRawValue() as ContactMessageRequest);
  }
}
