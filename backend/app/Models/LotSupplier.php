<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\Pivot;

class LotSupplier extends Pivot
{
    protected $fillable = [
        'lot_id',
        'organization_id',
        'winning_amount',
    ];

    protected $casts = [
        'lot_id' => 'integer',
        'organization_id' => 'integer',
        'winning_amount' => 'decimal:2',
    ];

    /** @return BelongsTo<NoticeLot, $this> */
    public function lot(): BelongsTo
    {
        return $this->belongsTo(NoticeLot::class, 'lot_id');
    }

    /** @return BelongsTo<Organization, $this> */
    public function organization(): BelongsTo
    {
        return $this->belongsTo(Organization::class, 'organization_id');
    }
}
