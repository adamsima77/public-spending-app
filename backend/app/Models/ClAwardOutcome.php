<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class ClAwardOutcome extends Model
{
    public $incrementing = false;

    public $timestamps = false;

    protected $table = 'cl_award_outcomes';

    protected $primaryKey = 'code';

    protected $keyType = 'string';

    protected $fillable = [
        'code',
        'label_sk',
    ];

    /** @return HasMany<LotResult, $this> */
    public function lotResults(): HasMany
    {
        return $this->hasMany(LotResult::class, 'award_outcome', 'code');
    }
}
