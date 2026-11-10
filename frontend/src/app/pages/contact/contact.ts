import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { ContactForm } from '../../components/ui/contact-form/contact-form';
import { ContactMessageRequest } from '../../generated';
import { ContactFacade } from './contact-facade/contact-facade';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { DestroyRef } from '@angular/core';
import { ToastService } from '../../components/ui/toast-notification/toast-service/toast-service';
import { finalize, tap } from 'rxjs';
import { HttpErrorResponse } from '@angular/common/http';

@Component({
  imports: [CommonModule, MatCardModule, ContactForm],
  selector: 'app-contact',
  styleUrl: './contact.scss',
  templateUrl: './contact.html',
})
export class Contact {
  private contactFacade = inject(ContactFacade);
  private toastService = inject(ToastService);
  private destroyRef = inject(DestroyRef);

  isSubmitting = signal<boolean>(false);
  isSuccess = signal<boolean>(false);

  handleFormSubmit(data: ContactMessageRequest): void {
    this.isSuccess.set(false);
    this.isSubmitting.set(true);

    this.contactFacade
      .sendMessage(data)
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        tap({
          next: () => {
            this.isSuccess.set(true);
            this.toastService.success(
              'Správa bola úspešne odoslaná. Ďakujeme, ozveme sa vám čo najskôr.',
            );
          },
          error: (err: HttpErrorResponse) => {
            const message =
              err.status === 422
                ? 'Skontrolujte prosím vyplnené údaje.'
                : err.status === 0
                  ? 'Server je nedostupný. Skontrolujte pripojenie.'
                  : 'Správu sa nepodarilo odoslať. Skúste to prosím neskôr.';

            this.toastService.error(message);
          },
        }),
        finalize(() => this.isSubmitting.set(false)),
      )
      .subscribe();
  }
}
