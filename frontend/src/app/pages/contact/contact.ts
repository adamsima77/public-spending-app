import { Component, DestroyRef, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { tap, catchError, finalize, EMPTY } from 'rxjs';
import { ContactForm } from '@components/ui/contact-form/contact-form';
import { ContactMessageRequest } from '@generated';
import { ContactFacade } from '@shared/facades/contact-facade/contact-facade';
import { ContentCardShell } from '@shared/ui/wrappers/content-card-shell/content-card-shell';

@Component({
  imports: [CommonModule, MatCardModule, ContactForm, ContentCardShell],
  selector: 'app-contact',
  styleUrl: './contact.scss',
  templateUrl: './contact.html',
})
export class Contact {
  private contactFacade = inject(ContactFacade);
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
        tap(() => this.isSuccess.set(true)),
        catchError(() => EMPTY),
        finalize(() => this.isSubmitting.set(false)),
      )
      .subscribe();
  }
}
