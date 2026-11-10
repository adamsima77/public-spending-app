import { inject, Service } from '@angular/core';
import { ContactMessageService } from '../../../generated';
import { ContactMessageRequest } from '../../../generated';
import { Observable } from 'rxjs/internal/Observable';
import { ContactSendResponse } from './contact-facade.model';

@Service()
export class ContactFacade {
  contactMessageService = inject(ContactMessageService);

  sendMessage(data: ContactMessageRequest): Observable<ContactSendResponse> {
    return this.contactMessageService.contactMessageStore({
      body: data,
    });
  }
}
