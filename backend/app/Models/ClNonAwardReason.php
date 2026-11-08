<?php

declare(strict_types=1);

namespace App\Models;

use App\Models\Concerns\HasCodelistAttributes;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class ClNonAwardReason extends Model
{
    use HasCodelistAttributes;

    protected $table = 'cl_non_award_reasons';

    /** @return HasMany<LotResult, $this> */
    public function lotResults(): HasMany
    {
        return $this->hasMany(LotResult::class, 'non_award_reason', 'code');
    }
}
