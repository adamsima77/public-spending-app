<?php

declare(strict_types=1);

namespace App\Models\Concerns;

trait HasCodelistAttributes
{
    protected function initializeHasCodelistAttributes(): void
    {
        $this->incrementing = false;
        $this->timestamps = true;
        $this->primaryKey = 'code';
        $this->keyType = 'string';
        $this->fillable = [
            'code',
            'label_sk',
        ];
    }
}
