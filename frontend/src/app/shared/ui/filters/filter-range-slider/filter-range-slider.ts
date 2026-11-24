import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { FormControl } from '@angular/forms';
import { MatSliderModule } from '@angular/material/slider';
import { startWith, switchMap } from 'rxjs';

@Component({
  selector: 'app-filter-range-slider',
  imports: [MatSliderModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './filter-range-slider.html',
  styleUrl: './filter-range-slider.scss',
})
export class FilterRangeSlider {
  readonly label = input.required<string>();
  readonly fromControl = input.required<FormControl<number | null>>();
  readonly toControl = input.required<FormControl<number | null>>();
  readonly min = input(0);
  readonly max = input.required<number>();
  readonly step = input(1);
  readonly format = input<(value: number) => string>((v) => v.toString());

  private readonly fromValue = toSignal(
    toObservable(this.fromControl).pipe(switchMap((c) => c.valueChanges.pipe(startWith(c.value)))),
  );

  private readonly toValue = toSignal(
    toObservable(this.toControl).pipe(switchMap((c) => c.valueChanges.pipe(startWith(c.value)))),
  );

  protected readonly start = computed(() => this.fromValue() ?? this.min());
  protected readonly end = computed(() => this.toValue() ?? this.max());

  protected readonly summary = computed(() => {
    const fmt = this.format();
    const upper = this.end() >= this.max() ? `${fmt(this.max())}+` : fmt(this.end());

    return `${fmt(this.start())} - ${upper}`;
  });

  protected setFrom(value: number): void {
    this.fromControl().setValue(value <= this.min() ? null : value);
  }

  protected setTo(value: number): void {
    this.toControl().setValue(value >= this.max() ? null : value);
  }
}
