import { inject, Service } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { ContactMessageService, ContactMessageRequest } from '@generated';
import { ToastService } from '@shared/services/toast-service/toast-service';
import { ContactSendResponse } from './contact-facade.model';

@Service()
export class ContactFacade {
  private readonly contactMessageService = inject(ContactMessageService);
  private readonly toastService = inject(ToastService);

  sendMessage(data: ContactMessageRequest): Observable<ContactSendResponse> {
    return this.contactMessageService.contactMessageStore({ body: data }).pipe(
      tap({
        next: () =>
          this.toastService.success(
            'Správa bola úspešne odoslaná. Ďakujeme, ozveme sa vám čo najskôr.',
          ),
        error: (err: HttpErrorResponse) => this.toastService.error(this.getErrorMessage(err)),
      }),
    );
  }

  private getErrorMessage(err: HttpErrorResponse): string {
    if (err.status === 422) {
      return 'Skontrolujte prosím vyplnené údaje.';
    }

    if (err.status === 0) {
      return 'Server je nedostupný. Skontrolujte pripojenie.';
    }

    return 'Správu sa nepodarilo odoslať. Skúste to prosím neskôr.';
  }
}
