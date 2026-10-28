<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class LotTender extends Model
{
    protected $fillable = [
        'notice_id',
        'lot_reference',
        'lot_id',
        'winning_value',
        'winning_currency',
        'tendering_party_ref',
        'rank',
        'subcontracting',
        'winner_organization_ids',
        'extra_fields',
    ];

    protected $casts = [
        'lot_id' => 'integer',
        'rank' => 'integer',
        'winning_value' => 'decimal:2',
        'winner_organization_ids' => 'array',
        'extra_fields' => 'array',
    ];

    /** @return BelongsTo<NoticeLot, $this> */
    public function lot(): BelongsTo
    {
        return $this->belongsTo(NoticeLot::class, 'lot_id');
    }
}
