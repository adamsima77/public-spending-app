import { inject, Service } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';

@Service()
export class ToastService {
  private readonly snackBar = inject(MatSnackBar);

  success(message: string): void {
    this.show(message, 'toast-success');
  }

  info(message: string): void {
    this.show(message, 'toast-info');
  }

  warning(message: string): void {
    this.show(message, 'toast-warning');
  }

  error(message: string): void {
    this.show(message, 'toast-error', 5000);
  }

  private show(message: string, panelClass: string, duration = 3000): void {
    this.snackBar.open(message, '', {
      duration,
      panelClass,
      horizontalPosition: 'center',
      verticalPosition: 'bottom',
    });
  }
}
